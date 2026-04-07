import os
import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq
import uvicorn
from typing import List, Dict, Any

app = FastAPI()

# Mount static directory to serve frontend assets
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    steps: List[Dict[str, Any]]
    final_answer: str

def web_search(query: str) -> str:
    """Minimal web search using DuckDuckGo HTML."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers, timeout=5)
        
        start_idx = resp.text.find('class="result__snippet')
        if start_idx == -1: return "No results."
        
        start_txt = resp.text.find('>', start_idx) + 1
        end_txt = resp.text.find('</a>', start_txt)
        snippet = resp.text[start_txt:end_txt].replace('<b>', '').replace('</b>', '').strip()
        
        return snippet[:250] + "..." 
    except Exception as e:
        return f"Search error: {e}"

class ReActAgent:
    def __init__(self):
        # SECURITY: Fetches the GROQ_API_KEY from environment variables to avoid leaking it on GitHub
        api_key = os.environ.get("GROQ_API_KEY", "your-api-key-here")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant" 
        
        self.sys_prompt = """You are a concise ReAct AI. Solve tasks strictly via this loop:
Thought: <1-line reasoning>
Action: Search
Action Input: <query>
Observation: <tool output provided by user>
Thought: <reasoning>
Final Answer: <concise answer>

Use 'Search' only if needed. Format exactly as above."""

    def run(self, prompt: str, max_steps: int = 4) -> dict:
        messages = [
            {"role": "system", "content": self.sys_prompt},
            {"role": "user", "content": prompt}
        ]
        
        steps = []

        for _ in range(max_steps):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=150
            ).choices[0].message.content

            messages.append({"role": "assistant", "content": response})

            if "Final Answer:" in response:
                final = response.split("Final Answer:")[-1].strip()
                thought = response.split("Final Answer:")[0].replace("Thought:", "").strip()
                if thought:
                    steps.append({"type": "thought", "content": thought})
                return {"steps": steps, "final_answer": final}

            if "Action: Search" in response and "Action Input:" in response:
                query = response.split("Action Input:")[-1].split("\n")[0].strip()
                thought = response.split("Action:")[0].replace("Thought:", "").strip()
                
                if thought:
                    steps.append({"type": "thought", "content": thought})
                    
                steps.append({"type": "action", "content": f"Query: {query}"})
                
                # Execute tool
                observation = web_search(query)
                steps.append({"type": "observation", "content": observation})
                
                obs_msg = f"Observation: {observation}"
                messages.append({"role": "user", "content": obs_msg})
            else:
                steps.append({"type": "error", "content": "Format deviation"})
                return {"steps": steps, "final_answer": "Error: Agent deviated from ReAct format."}
                
        return {"steps": steps, "final_answer": "Error: Max reasoning steps reached."}

agent = ReActAgent()

@app.post("/api/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest):
    return agent.run(req.prompt)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
