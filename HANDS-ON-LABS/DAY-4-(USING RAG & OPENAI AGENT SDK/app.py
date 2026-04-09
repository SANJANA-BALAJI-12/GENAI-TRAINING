import hashlib
import os
import re
import json
import faiss
import numpy as np
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

if SERPAPI_KEY and SERPAPI_KEY.startswith("your_"):
    SERPAPI_KEY = None

if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY")

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

# FAISS index file
INDEX_FILE = "faiss_index.idx"
METADATA_FILE = "metadata.json"

dimension = 1536
if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
    index = faiss.read_index(INDEX_FILE)
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)
else:
    index = faiss.IndexFlatL2(dimension)
    metadata = []

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str


def local_embedding(text: str) -> list:
    tokens = re.findall(r"\w+", text.lower())
    vector = np.zeros(dimension, dtype="float32")
    for token in tokens:
        index_value = int.from_bytes(hashlib.md5(token.encode("utf-8")).digest(), "little") % dimension
        vector[index_value] += 1.0

    norm = np.linalg.norm(vector)
    if norm > 0:
        vector /= norm
    return vector.tolist()


def get_embedding(text: str) -> list:
    return local_embedding(text)


def web_search(query: str) -> list:
    if SERPAPI_KEY:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
        }
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Search API error")
        results = response.json().get("organic_results", [])
        return [
            {"title": r.get("title", "Untitled"), "snippet": r.get("snippet", ""), "link": r.get("link", "")}
            for r in results[:5]
        ]

    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers=headers,
        timeout=15,
    )
    if response.status_code not in (200, 202):
        with open("search_debug.log", "a", encoding="utf-8") as f:
            f.write(f"DuckDuckGo status={response.status_code} url={response.url}\n")
            f.write(response.text[:1000].replace("\n", " ") + "\n---\n")
        raise HTTPException(status_code=500, detail=f"DuckDuckGo search error {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for result in soup.select("div.result")[:5]:
        title_tag = result.select_one("a.result__a")
        snippet_tag = result.select_one("a.result__snippet") or result.select_one("div.result__snippet")
        if title_tag and title_tag.get("href"):
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            results.append({"title": title, "snippet": snippet, "link": link})

    if not results:
        with open("search_debug.log", "a", encoding="utf-8") as f:
            f.write(f"DuckDuckGo parsed results empty for query={query}\n")
            f.write(response.text[:1000].replace("\n", " ") + "\n---\n")
        return [
            {
                "title": "Sample source for fallback testing",
                "snippet": "Live DuckDuckGo search returned no results. This is a fallback placeholder.",
                "link": "https://example.com/fallback-source",
            }
        ]

    with open("search_debug.log", "a", encoding="utf-8") as f:
        f.write(f"DuckDuckGo parsed {len(results)} results for query={query}\n")
        f.write(str(results[:3]) + "\n---\n")

    return results


def store_in_faiss(texts: list, sources: list):
    global index, metadata
    if not texts:
        return

    embeddings = [get_embedding(text) for text in texts]
    embeddings_np = np.array(embeddings, dtype="float32")
    index.add(embeddings_np)

    for text, source in zip(texts, sources):
        metadata.append({"text": text, "source": source})

    faiss.write_index(index, INDEX_FILE)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def retrieve_similar(query_emb: list, top_k: int = 5) -> list:
    if index.ntotal == 0:
        return []

    query_emb_np = np.array([query_emb], dtype="float32")
    distances, indices = index.search(query_emb_np, top_k)
    results = []
    for idx in indices[0]:
        if idx < len(metadata):
            results.append(metadata[idx])
    return results


def summarize_with_model(query: str, context: str) -> str:
    prompt = (
        f"You are a research assistant. Answer the query using only the provided sources. "
        f"Cite each source explicitly using markdown links.\n\nQuery: {query}\n\nContext:\n{context}\n\nAnswer:"
    )

    response = client.responses.create(
        model="openai/gpt-oss-20b",
        input=prompt,
        max_output_tokens=500,
    )

    text = ""
    if hasattr(response, "output_text") and response.output_text:
        text = response.output_text
    elif getattr(response, "output", None):
        output_blocks = response.output
        if isinstance(output_blocks, list) and output_blocks:
            first_block = output_blocks[0]
            if isinstance(first_block, dict):
                content = first_block.get("content", [])
                if isinstance(content, list) and content:
                    text = content[0].get("text", "")

    return text.strip()


@app.post("/search")
async def search_answer(request: QueryRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    search_results = web_search(query)
    texts = [r["snippet"] for r in search_results if r.get("snippet")]
    sources = [{"title": r["title"], "link": r["link"]} for r in search_results]

    store_in_faiss(texts, sources)

    context = "\n".join(
        [f"Source: {src['title']} ({src['link']})\n{r['snippet']}" for r, src in zip(search_results, sources) if r.get("snippet")]
    )
    if not context:
        context = "No search snippets are available."

    answer = summarize_with_model(query, context)
    sources_list = [f"- [{src['title']}]({src['link']})" for src in sources]

    return {
        "answer": answer,
        "sources": sources_list,
        "search_results": search_results,
        "used_fallback_search": SERPAPI_KEY is None,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
