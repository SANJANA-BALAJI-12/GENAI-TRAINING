# Web Search + Answer Agent

This is a production-grade agentic application using OpenAI, RAG, and web search.

## Setup

1. Install dependencies: `pip install -r requirements.txt`

2. Set API keys in `.env`:
   - GROQ_API_KEY: Your Groq API key
   - SERPAPI_KEY: Leave blank unless you want to use SerpAPI

3. Run the app: `python app.py`

4. Open `index.html` in browser to test.

## Architecture

- Backend: FastAPI
- Agent: Groq-compatible OpenAI API for reasoning
- Search: DuckDuckGo keyless fallback (SerpAPI optional)
- RAG: FAISS for vector storage
- UI: Simple HTML/JS

## Features

- Multi-step reasoning: Query → Search → Embed/Store → Retrieve → Summarize → Cite
- Sources included in response
- Persistent vector DB