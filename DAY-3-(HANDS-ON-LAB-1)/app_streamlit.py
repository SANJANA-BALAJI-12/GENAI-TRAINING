import os
import pandas as pd
from typing import TypedDict, List, Dict, Any
from datetime import datetime
import streamlit as st
import plotly.express as px
from langgraph.graph import StateGraph, END

# --- LangSmith Integration ---
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key-here" # Replace with your actual key before running
os.environ["LANGCHAIN_PROJECT"] = "LangGraph_ETL_Pipeline"

# Streamlit Page Config MUST be first
st.set_page_config(page_title="GenAI ETL Dashboard", page_icon="🚀", layout="wide")

# 1. Define the State for LangGraph
class ETLState(TypedDict):
    data: pd.DataFrame
    audit_trail: List[str]
    metrics: Dict[str, Any]
    guardrail_flags: List[str]

# 2. Extract Node
def extract_node(state: ETLState) -> ETLState:
    # Adding more diverse mocked data for better interactive dashboard representation
    raw_data = [
        {"id": 1, "user_text": "Great service! My phone is 555-1234."},
        {"id": 2, "user_text": "   "},  # Bad data
        {"id": 3, "user_text": "App crashed when I clicked save but I like the colors. " * 5}, # Too long
        {"id": 4, "user_text": "I really love the new update. Everything is instantly fast and beautiful."},
        {"id": 5, "user_text": "Terrible experience. The system logs me out constantly every 5 minutes."},
        {"id": 6, "user_text": "How do I reset my password? Please help, I am locked out."}
    ]
    df = pd.DataFrame(raw_data)
    state["audit_trail"].append(f"[{datetime.now().strftime('%H:%M:%S')}] EXTRACT: Loaded {len(df)} incoming tickets.")
    state["metrics"]["Total Rows Extracted"] = len(df)
    state["data"] = df
    return state

# 3. Transform Node (Pandas + Guardrails)
def transform_node(state: ETLState) -> ETLState:
    df = state["data"]
    initial_count = len(df)
    
    # Guardrail 1: Drop empty rows
    df = df[df['user_text'].str.strip().astype(bool)].copy()
    
    # Guardrail 2: Truncate text to limit token usage
    df.loc[:, 'user_text'] = df['user_text'].str.slice(0, 100)
    
    # Guardrail 3: Simple Pandas PII Regex Masking
    mask = r'\d{3}-\d{4}'
    df.loc[:, 'user_text'] = df['user_text'].str.replace(mask, '[REDACTED]', regex=True)
    
    rows_dropped = initial_count - len(df)
    state["audit_trail"].append(f"[{datetime.now().strftime('%H:%M:%S')}] TRANSFORM: Dropped {rows_dropped} bad row(s), masked PII, truncated long text.")
    state["metrics"]["Bad Rows Dropped (Guardrail)"] = rows_dropped
    state["data"] = df
    return state

# 4. Load Node (Mock GenAI Inference)
def load_node(state: ETLState) -> ETLState:
    df = state["data"]
    results = []
    total_tokens_estimated = 0
    
    for _, row in df.iterrows():
        text = row['user_text'].lower()
        if "crash" in text or "terrible" in text or "logout" in text:
            intent, sentiment = "bug", "negative"
        elif "help" in text or "reset" in text or "how" in text:
            intent, sentiment = "support", "neutral"
        else:
            intent, sentiment = "praise", "positive"
            
        results.append({"intent": intent, "sentiment": sentiment})
        total_tokens_estimated += len(text.split()) + 15
        
    df = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
    
    state["audit_trail"].append(f"[{datetime.now().strftime('%H:%M:%S')}] LOAD: GenAI analysis and sentiment extraction complete.")
    state["metrics"]["Estimated GenAI Token Cost"] = total_tokens_estimated
    state["data"] = df
    return state

@st.cache_resource
def build_pipeline():
    builder = StateGraph(ETLState)
    builder.add_node("Extract", extract_node)
    builder.add_node("Transform", transform_node)
    builder.add_node("Load_GenAI", load_node)
    builder.set_entry_point("Extract")
    builder.add_edge("Extract", "Transform")
    builder.add_edge("Transform", "Load_GenAI")
    builder.add_edge("Load_GenAI", END)
    return builder.compile()

def run_pipeline():
    pipeline = build_pipeline()
    initial_state = {"data": pd.DataFrame(), "audit_trail": [], "metrics": {}, "guardrail_flags": []}
    return pipeline.invoke(initial_state)

# --- Streamlit UI ---
st.title("🚀 GenAI Customer Triage Dashboard")
st.markdown("Interactive observability and decision-making dashboard powered by **LangGraph** and **Streamlit**.")

# Run Pipeline on load
with st.spinner('Executing LangGraph Data Pipeline...'):
    result_state = run_pipeline()

df_result = result_state["data"]

# Top Metrics Row
st.header("📊 Pipeline Observability Metrics", divider='rainbow')
col1, col2, col3 = st.columns(3)
with col1:
    st.info("Ingestion Metrics")
    st.metric("Total Rows Extracted", result_state["metrics"].get("Total Rows Extracted", 0))
with col2:
    st.warning("Data Guardrails")
    st.metric("Rows Dropped by Guardrail", result_state["metrics"].get("Bad Rows Dropped (Guardrail)", 0))
with col3:
    st.error("Operation Cost")
    st.metric("Estimated GenAI Tokens Used", result_state["metrics"].get("Estimated GenAI Token Cost", 0))

st.markdown("---")

# Data Visualization and Decisions
st.header("📈 Data Insights & Actionable Trends", divider='gray')
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Ticket Category Distribution")
    fig_intent = px.pie(df_result, names='intent', hole=0.4, color_discrete_sequence=['#4B8BBE', '#FFE873', '#FF6B6B'])
    st.plotly_chart(fig_intent, use_container_width=True)

with col_chart2:
    st.subheader("Customer Sentiment Breakdown")
    fig_sent = px.bar(df_result, x='sentiment', color='sentiment', title='Volume by Sentiment Level', 
                      color_discrete_map={'positive': 'green', 'neutral': 'gray', 'negative': 'red'})
    st.plotly_chart(fig_sent, use_container_width=True)

# Interactive Dataframe
st.header("✅ Processed Intelligence (Interactive Data)", divider='blue')
st.markdown("You can sort, filter, and search through the processed dataset to make immediate decisions.")
st.dataframe(
    df_result,
    use_container_width=True,
    column_config={
        "id": "Ticket ID",
        "user_text": st.column_config.TextColumn("Customer Request Text", width="large"),
        "intent": st.column_config.TextColumn("Detected Category"),
        "sentiment": "Overall Sentiment"
    },
    hide_index=True
)

st.divider()

# Audit Trail Expander
with st.expander("📝 View Execution Audit Trail & Logs"):
    for log in result_state["audit_trail"]:
        st.code(log, language="bash")

st.success("☁️ LangSmith Tracing Active! Live execution trace mapped securely to user profile.")
