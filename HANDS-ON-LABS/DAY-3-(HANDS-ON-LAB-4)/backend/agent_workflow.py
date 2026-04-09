import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

from .memory import memory_store

load_dotenv()

# Initialize LLM
# Using Groq API connection, configured via .env
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

# Define State Schema
class AgentState(TypedDict):
    topic: str
    research_data: str
    draft: str
    final_report: str
    messages: Annotated[Sequence[BaseMessage], "messages"]

# Node: Researcher
def researcher_node(state: AgentState):
    topic = state.get("topic", "")
    
    # Prompting the LLM to act as a researcher. 
    # In a full deployment, this could use tools (Tavily/DuckDuckGo), but we simulate it perfectly with LLM's vast knowledge.
    prompt = PromptTemplate.from_template(
        "You are a Senior AI Researcher. Gather structured and factual bullet points about the following topic: {topic}. "
        "Focus on key concepts, architecture, and current trends."
    )
    chain = prompt | llm
    
    response = chain.invoke({"topic": topic})
    research_content = response.content
    
    # Store research in memory (ChromaDB / Fallback)
    memory_store.store(text=research_content, metadata={"role": "researcher", "topic": topic})
    
    return {"research_data": research_content}

# Node: Writer
def writer_node(state: AgentState):
    topic = state.get("topic", "")
    research_data = state.get("research_data", "")
    
    # Optional: Retrieve extra context if we had multiple passes, here we retrieve all available memory
    context_from_memory = memory_store.retrieve_all()
    
    prompt = PromptTemplate.from_template(
        "You are an Expert Technical Writer. Using the following research data, write a well-structured drafted report about {topic}.\n\n"
        "Research Data:\n{research_data}\n\n"
    )
    chain = prompt | llm
    
    response = chain.invoke({"topic": topic, "research_data": research_data})
    draft_content = response.content
    
    return {"draft": draft_content}

# Node: Editor
def editor_node(state: AgentState):
    draft = state.get("draft", "")
    
    prompt = PromptTemplate.from_template(
        "You are a Senior Editor. Refine the following draft for clarity, correctness, and Markdown formatting. "
        "Ensure it looks highly professional, concise, and easy to read.\n\n"
        "Draft:\n{draft}\n\n"
        "Return only the final formatted markdown report."
    )
    chain = prompt | llm
    
    response = chain.invoke({"draft": draft})
    final_content = response.content
    
    return {"final_report": final_content}

# Build LangGraph Workflow
def build_research_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("Researcher", researcher_node)
    workflow.add_node("Writer", writer_node)
    workflow.add_node("Editor", editor_node)
    
    # Set edges
    workflow.add_edge(START, "Researcher")
    workflow.add_edge("Researcher", "Writer")
    workflow.add_edge("Writer", "Editor")
    workflow.add_edge("Editor", END)
    
    # Compile graph
    app = workflow.compile()
    return app

research_app = build_research_graph()
