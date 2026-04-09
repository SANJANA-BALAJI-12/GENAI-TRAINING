import uuid
from fastapi import APIRouter, Request, HTTPException
from api.schemas import SubmitRequest, SubmitResponse
from domain.graph import builder
from langgraph.checkpoint.memory import MemorySaver

router = APIRouter()

@router.post("/submit", response_model=SubmitResponse)
async def submit_content(request: Request, bg_task: SubmitRequest):
    # App state access to the graph
    app_graph = request.app.state.graph
    
    job_id = str(uuid.uuid4())
    
    # Initialize State
    initial_state = {
        "job_id": job_id,
        "text": bg_task.text,
        "ai_score": 0.0,
        "ai_reasoning": "",
        "status": "PROCESSING",
        "human_decision": None,
        "messages": ["Ingested via API"]
    }
    
    # Run the graph
    config = {"configurable": {"thread_id": job_id}}
    
    try:
        # We run the graph until it reaches an explicit interrupt or END
        final_state = app_graph.invoke(initial_state, config=config)
        
        # It's possible the graph returned early due to interruption or auto-resolved
        return SubmitResponse(
            job_id=job_id,
            status=final_state.get("status", "UNKNOWN"),
            ai_score=final_state.get("ai_score"),
            ai_reasoning=final_state.get("ai_reasoning")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
