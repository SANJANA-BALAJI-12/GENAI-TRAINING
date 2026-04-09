from pydantic import BaseModel, Field

class SubmitRequest(BaseModel):
    text: str = Field(..., title="The user generated content to moderate", min_length=1)

class SubmitResponse(BaseModel):
    job_id: str
    status: str
    ai_score: float | None = None
    ai_reasoning: str | None = None

class ReviewDecision(BaseModel):
    decision: str = Field(..., description="Must be 'APPROVED' or 'REJECTED'")
