from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from api.schemas import ReviewDecision

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/{job_id}/review", response_class=HTMLResponse)
async def review_page(request: Request, job_id: str):
    app_graph = request.app.state.graph
    config = {"configurable": {"thread_id": job_id}}
    
    # Get the current state of the thread
    state_snapshot = app_graph.get_state(config)
    
    if not state_snapshot or not state_snapshot.values:
        raise HTTPException(status_code=404, detail="Job not found")
        
    state_data = state_snapshot.values
    
    if state_data.get("status") not in ["PENDING_REVIEW", "PROCESSING"]:
        pass # It might already be decided, we still render but lock actions
    
    return templates.TemplateResponse(
        request=request,
        name="review.html", 
        context={
            "job_id": job_id,
            "text": state_data.get("text"),
            "ai_score": state_data.get("ai_score"),
            "ai_reasoning": state_data.get("ai_reasoning"),
            "status": state_data.get("status", "UNKNOWN")
        }
    )

@router.post("/{job_id}/review")
async def submit_review(request: Request, job_id: str, decision: str = Form(...)):
    if decision not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Invalid decision")
        
    app_graph = request.app.state.graph
    config = {"configurable": {"thread_id": job_id}}
    
    state_snapshot = app_graph.get_state(config)
    if not state_snapshot or not state_snapshot.values:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if state_snapshot.values.get("status") not in ["PENDING_REVIEW", "PROCESSING"]:
        return RedirectResponse(url=f"/moderate/{job_id}/review", status_code=303)
        
    # We update the state with the human's decision
    app_graph.update_state(config, {
        "human_decision": decision,
        "status": decision,
        "messages": [f"Human reviewed and decided: {decision}"]
    }, as_node="human_review")
    
    # Resume graph processing from the interrupt
    # Passing None to invoke basically tells it "resume with current state"
    final_state = app_graph.invoke(None, config=config)
    
    return RedirectResponse(url=f"/moderate/{job_id}/review", status_code=303)
