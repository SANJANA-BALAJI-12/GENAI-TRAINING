from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging

from .agent_workflow import research_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Agent Research Pipeline")

class QueryRequest(BaseModel):
    topic: str

class QueryResponse(BaseModel):
    final_report: str
    workflow_state: Dict[str, Any]

@app.post("/generate_report", response_model=QueryResponse)
async def generate_report(request: QueryRequest):
    try:
        logger.info(f"Received request for topic: {request.topic}")
        initial_state = {
            "topic": request.topic,
            "research_data": "",
            "draft": "",
            "final_report": "",
            "messages": []
        }
        
        # Run the workflow
        # The LangSmith tags are automatically handled if `LANGCHAIN_TRACING_V2=true` is set.
        final_state = research_app.invoke(initial_state)
        
        return QueryResponse(
            final_report=final_state.get("final_report", ""),
            workflow_state={
                "research_data_preview": final_state.get("research_data", "")[:200] + "...",
                "draft_preview": final_state.get("draft", "")[:200] + "..."
            }
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
