from typing import TypedDict, Optional
from typing_extensions import Annotated
import operator

class ModerationState(TypedDict):
    job_id: str
    text: str
    ai_score: float
    ai_reasoning: str
    status: str
    human_decision: Optional[str]
    # This keeps track of logs or steps, though simple for this use case
    messages: Annotated[list, operator.add]
