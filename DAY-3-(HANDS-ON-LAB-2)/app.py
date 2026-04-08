import streamlit as st
import logging
import os
from transformers import pipeline
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# ==========================================
# 1. SETUP LOGGING & OBSERVABILITY
# ==========================================
# We log to a backend file to maintain an audit trail and observability logs.
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend_audit.log')
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# ==========================================
# 2. LOAD HUGGING FACE MODEL
# ==========================================
@st.cache_resource
def load_sentiment_model():
    """
    Loads a multi-class sentiment analysis model from Hugging Face.
    This default model outputs `positive`, `neutral`, `negative` labels.
    """
    logger.info("Initializing Hugging Face sentiment model...")
    # 'lxyuan/distilbert-base-multilingual-cased-sentiments-student' returns positive, neutral, negative
    return pipeline("text-classification", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student")

try:
    classifier = load_sentiment_model()
except Exception as e:
    st.error("Failed to load the Sentiment Analysis model.")
    logger.error(f"Model initialization error: {e}")
    st.stop()

# ==========================================
# 3. DEFINE LANGGRAPH STATE & BEHAVIOR
# ==========================================
class AgentState(TypedDict):
    """LangGraph State definition."""
    user_query: str
    sentiment: str
    confidence: float
    routing_decision: str
    error: str

def analyze_sentiment_node(state: AgentState):
    """Analyzes the sentiment of the text and updates the state."""
    query = state["user_query"]
    logger.info(f"Node [analyze_sentiment_node] - analyzing query: {query}")
    
    # Pre-LLM Guardrail checking
    if not query or len(query.strip()) < 3:
        error_msg = "Query is too short or invalid."
        logger.warning(f"Guardrail triggered: {error_msg}")
        return {"error": error_msg, "sentiment": "Unknown"}
        
    try:
        # Run model inference
        result = classifier(query)[0]
        label = result['label'].lower()
        score = result['score']
        
        # Capitalize and normalize labels
        if label == "positive":
            sentiment = "Positive"
        elif label == "negative":
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        logger.info(f"Node [analyze_sentiment_node] - Result: {sentiment} (Confidence: {score:.2f})")
        return {"sentiment": sentiment, "confidence": score}
    except Exception as e:
        logger.error(f"Sentiment inference failed: {e}")
        return {"error": "Failed to analyze sentiment", "sentiment": "Error"}

def route_positive_node(state: AgentState):
    """Node for handling positive sentiment queries."""
    decision = "Routed to 'Customer Success & Referrals' Team (Positive)"
    logger.info(f"Node [route_positive_node] triggered -> {decision}")
    return {"routing_decision": decision}

def route_neutral_node(state: AgentState):
    """Node for handling neutral sentiment queries."""
    decision = "Routed to 'General Support & Q&A' Team (Neutral)"
    logger.info(f"Node [route_neutral_node] triggered -> {decision}")
    return {"routing_decision": decision}

def route_negative_node(state: AgentState):
    """Node for handling negative sentiment queries."""
    decision = "Routed to 'Priority Escalations & Retention' Team (Negative)"
    logger.info(f"Node [route_negative_node] triggered -> {decision}")
    return {"routing_decision": decision}

def error_node(state: AgentState):
    """Fallback node for errors/guardrails."""
    decision = "Error - Cannot route query. System alert generated."
    logger.warning("Node [error_node] executed.")
    return {"routing_decision": decision}

def choose_route(state: AgentState):
    """Conditional Edge function for LangGraph to pick the branch."""
    if state.get("error"):
        logger.info("Routing Condition -> Error Branch")
        return "error_node"
    
    sent = state.get("sentiment", "")
    if sent == "Positive":
        logger.info("Routing Condition -> Positive Branch")
        return "route_positive"
    elif sent == "Negative":
        logger.info("Routing Condition -> Negative Branch")
        return "route_negative"
    elif sent == "Neutral":
        logger.info("Routing Condition -> Neutral Branch")
        return "route_neutral"
    else:
        logger.info("Routing Condition -> Unknown/Error Branch")
        return "error_node"

# ----------------- Build LangGraph -----------------
builder = StateGraph(AgentState)

builder.add_node("analyze_sentiment", analyze_sentiment_node)
builder.add_node("route_positive", route_positive_node)
builder.add_node("route_neutral", route_neutral_node)
builder.add_node("route_negative", route_negative_node)
builder.add_node("error_node", error_node)

# Set Graph entry point
builder.add_edge(START, "analyze_sentiment")

# Define conditional branching
builder.add_conditional_edges(
    "analyze_sentiment",
    choose_route,
    {
        "route_positive": "route_positive",
        "route_neutral": "route_neutral",
        "route_negative": "route_negative",
        "error_node": "error_node",
    }
)

# Connect end edges
builder.add_edge("route_positive", END)
builder.add_edge("route_neutral", END)
builder.add_edge("route_negative", END)
builder.add_edge("error_node", END)

workflow = builder.compile()

# ==========================================
# 4. STREAMLIT UI & INTERACTION
# ==========================================
st.set_page_config(page_title="AI Query Router", page_icon="🔀", layout="centered")

# Modern Premium UI Design via Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Sleek gradient background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Sleek text areas */
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(129, 140, 248, 0.3) !important;
        color: #0f172a !important;
        font-size: 1.05rem !important;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 15px rgba(129, 140, 248, 0.8) !important;
        background-color: #ffffff !important;
    }
    
    /* Glowing button styling */
    div.stButton > button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: transform 0.2s, box-shadow 0.2s;
        width: 100%;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -10px rgba(124, 58, 237, 0.8);
        color: white;
        border: none;
    }

    /* Vibrant Sentiment Indicators */
    .pos-sentiment { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.4);
        animation: pop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .neu-sentiment { 
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(245, 158, 11, 0.4);
        animation: pop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .neg-sentiment { 
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.4);
        animation: pop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    /* Titles and Text */
    .app-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    .app-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
    }
    
    @keyframes pop {
        0% { transform: scale(0.9); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Metrics panel glassmorphism styling */
    .metric-panel {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Streamlit overrides */
    h3, p, span, div {
        font-family: 'Outfit', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='app-title'>🔀 AI Support Router</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>Real-time Sentiment Analysis via <b>Hugging Face</b> combined with Autonomous Workflow Routing using <b>LangGraph</b>.</p>", unsafe_allow_html=True)

# Interface
user_query = st.text_area("Enter Customer Query:", placeholder="e.g., I'm extremely frustrated, my device is broken and nobody is helping me!", height=120)

if st.button("Analyze & Route", type="primary"):
    # UI-level guardrail
    if not user_query.strip():
        st.error("⚠️ Please enter a query before analyzing!")
        logger.warning("UI Guardrail: User attempted to run with empty input.")
    else:
        with st.spinner("Processing request through LangGraph pipeline..."):
            logger.info("=========================================")
            logger.info("--- New LangGraph Execution Triggered ---")
            
            # Setup State
            initial_state = {
                "user_query": user_query,
                "sentiment": "",
                "confidence": 0.0,
                "routing_decision": "",
                "error": ""
            }
            
            # Execute Graph
            final_state = workflow.invoke(initial_state)
            
            logger.info(f"--- Workflow Execution Finished ---")
            
            # Handle results
            error = final_state.get("error", "")
            if error:
                st.error(f"⚠️ Validation or System Error: {error}")
            else:
                sentiment = final_state.get("sentiment")
                confidence = final_state.get("confidence")
                decision = final_state.get("routing_decision")
                
                st.markdown("### 📊 Automated Analysis Results")
                
                # Setup Display variables
                if sentiment == "Positive":
                    div_class = "pos-sentiment"
                    emoji = "✅ 😊"
                elif sentiment == "Neutral":
                    div_class = "neu-sentiment"
                    emoji = "⚖️ 😐"
                else:  # Negative
                    div_class = "neg-sentiment"
                    emoji = "🚨 😠"
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"<div class='{div_class}'><span style='font-size: 0.9rem; opacity: 0.9; font-weight: 300;'>Detected Sentiment</span><h2 style='margin:0; font-weight:700;'>{emoji} {sentiment}</h2></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='metric-panel'><span style='font-size: 0.9rem; color:#94a3b8; font-weight: 300;'>AI Confidence Level</span><h2 style='margin:0; color:#38bdf8; font-weight:700;'>{confidence:.2%}</h2></div>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"<div style='background: linear-gradient(90deg, rgba(56, 189, 248, 0.1), rgba(129, 140, 248, 0.1)); border-left: 5px solid #818cf8; padding: 20px; border-radius: 10px;'><h3 style='margin:0; color:#f8fafc; font-weight:600;'>🚀 AI Routing Decision</h3><p style='margin-top:10px; font-size:1.2rem; margin-bottom:0px; color:#38bdf8; font-weight:400;'>{decision}</p></div>", unsafe_allow_html=True)
                
                # Show an expander with the JSON state trace for transparency
                with st.expander("Show Graph State (Audit Trace)"):
                    st.json(final_state)
