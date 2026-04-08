from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from api.routers import submit, review
from domain.graph import builder
from core.config import settings
from langgraph.checkpoint.memory import MemorySaver

app = FastAPI(title=settings.app_name)
templates = Jinja2Templates(directory="templates")

# Initialize Checkpointer and Compile Graph
# We do this globally in app.state so the memory is preserved while FastAPI runs.
checkpointer = MemorySaver()
compiled_graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]
)
app.state.graph = compiled_graph
app.state.checkpointer = checkpointer

app.include_router(submit.router, prefix="/moderate", tags=["Moderation"])
app.include_router(review.router, prefix="/moderate", tags=["Human Review"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Main portal: A simple UI to submit content and see links.
    """
    # Fetch all threads from memory saver to show pending queue (For Demo Purposes)
    # MemorySaver doesn't expose easy iteration by default, so we'll just show the form
    return templates.TemplateResponse(request=request, name="index.html")
