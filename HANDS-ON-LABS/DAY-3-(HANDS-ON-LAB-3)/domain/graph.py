from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from domain.state import ModerationState
from core.config import settings
from core.logger import logger

class AIModerationResult(BaseModel):
    score: float = Field(description="A toxicity score between 0.0 (safe) and 1.0 (highly toxic)")
    reasoning: str = Field(description="Short rationale for the score")

# Initialize LLM
llm = ChatGroq(
    temperature=0,
    model_name=settings.model_name,
    groq_api_key=settings.groq_api_key
)

parser = JsonOutputParser(pydantic_object=AIModerationResult)
prompt = PromptTemplate(
    template="""You are a strict content moderation AI. Analyze the following text and assign a toxicity score from 0.0 to 1.0. 
0.0 is completely safe, 1.0 is highly toxic, offensive, or dangerous.
Provide a short reasoning.

Text to analyze: {text}

{format_instructions}
""",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | llm | parser

def analyze_content(state: ModerationState) -> dict:
    logger.info(f"[{state['job_id']}] Analyzing content: {state['text'][:30]}...")
    try:
        result = chain.invoke({"text": state["text"]})
        score = result.get("score", 0.0)
        reasoning = result.get("reasoning", "No reasoning provided")
    except Exception as e:
        logger.error(f"[{state['job_id']}] LLM Analysis failed: {str(e)}")
        score = 0.5 # Default to ambiguous on failure to force human review
        reasoning = f"Error during AI analysis: {str(e)}"
    
    return {
        "ai_score": score,
        "ai_reasoning": reasoning,
        "messages": [f"AI Score: {score} - {reasoning}"]
    }

def route_content(state: ModerationState) -> str:
    score = state.get("ai_score", 0.0)
    if score < 0.2:
        return "auto_approve"
    elif score > 0.8:
        return "auto_reject"
    else:
        return "human_review"

def auto_approve(state: ModerationState) -> dict:
    logger.info(f"[{state['job_id']}] Auto-approved")
    return {"status": "APPROVED", "messages": ["Auto-approved by threshold"]}

def auto_reject(state: ModerationState) -> dict:
    logger.info(f"[{state['job_id']}] Auto-rejected")
    return {"status": "REJECTED", "messages": ["Auto-rejected by threshold"]}

def human_review(state: ModerationState) -> dict:
    # This node acts as the interruption point. 
    # When resume happens via external API, it will inject 'human_decision' directly into the state updates.
    # We apply the decision to the status.
    decision = state.get("human_decision")
    if decision:
        logger.info(f"[{state['job_id']}] Human decision applied: {decision}")
        return {"status": decision, "messages": [f"Human reviewed and decided: {decision}"]}
    else:
        logger.info(f"[{state['job_id']}] Waiting for human review...")
        return {"status": "PENDING_REVIEW", "messages": ["Paused for human review"]}

# Build Graph
builder = StateGraph(ModerationState)
builder.add_node("analyze_content", analyze_content)
builder.add_node("auto_approve", auto_approve)
builder.add_node("auto_reject", auto_reject)
builder.add_node("human_review", human_review)

builder.set_entry_point("analyze_content")
builder.add_conditional_edges(
    "analyze_content",
    route_content,
    {
        "auto_approve": "auto_approve",
        "auto_reject": "auto_reject",
        "human_review": "human_review"
    }
)

builder.add_edge("auto_approve", END)
builder.add_edge("auto_reject", END)
# We route human review to END because the updated state after interrupt applies the decision
builder.add_edge("human_review", END) 

# Note: We will compile this with a checkpointer in the FastAPI app
