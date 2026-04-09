import streamlit as st
import requests
import json
import time

st.set_page_config(
    page_title="Multi-Agent Research Pipeline",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a stunning UI
st.markdown("""
    <style>
    /* Global Styling */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling with gradient */
    h1 {
        background: -webkit-linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 3rem !important;
        padding-bottom: 20px;
    }
    
    /* Input Box */
    .stTextInput>div>div>input {
        background-color: #161b22;
        color: #ffffff;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        font-size: 1.1rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #4ECDC4;
        box-shadow: 0 0 10px rgba(78, 205, 196, 0.4);
    }
    
    /* Submit Button */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 1px;
        padding: 10px 24px;
        transition: all 0.3s ease 0s;
        width: 100%;
        margin-top: 10px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 14px rgba(0,0,0,0.25), 0 5px 5px rgba(0,0,0,0.22);
    }
    
    /* Cards for pipeline stages */
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: scale(1.02);
        border-color: #4ECDC4;
    }
    
    .card-title {
        color: #8b949e;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .card-content {
        color: #c9d1d9;
        font-size: 1.1rem;
    }
    
    /* Final output box */
    .final-output {
        background-color: #1a1e24;
        border-left: 4px solid #4ECDC4;
        padding: 25px;
        border-radius: 0 8px 8px 0;
        margin-top: 30px;
        line-height: 1.6;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Multi-Agent Research Studio")
st.markdown("Automate your research, drafting, and editing with LangGraph and OpenAI. Enter a topic below to kick off the pipeline.")

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>🔍 Define Topic</div>", unsafe_allow_html=True)
    topic = st.text_input("", placeholder="e.g., The Future of Quantum Computing in 2026")
    submit = st.button("Generate Report")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if submit and topic:
        with st.status("Initializing Multi-Agent Pipeline...", expanded=True) as status:
            try:
                # 1. Researcher Phase
                st.write("🕵️‍♂️ **Researcher Agent** is gathering facts...")
                
                # We call the FastAPI backend
                # Note: Timeouts might occur for very long requests, realistically we should stream or poll, 
                # but for simplicity we'll await the synchronous response.
                response = requests.post(
                    "http://localhost:8000/generate_report", 
                    json={"topic": topic},
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.write("✍️ **Writer Agent** is drafting the content...")
                    time.sleep(1) # Visual pacing
                    st.write("📝 **Editor Agent** is refining formatting...")
                    time.sleep(1) # Visual pacing
                    
                    status.update(label="Report Generated Successfully!", state="complete", expanded=False)
                    
                    st.session_state['report_data'] = data
                else:
                    status.update(label="API Error", state="error")
                    st.error(f"Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                status.update(label="Connection Error", state="error")
                st.error(f"Could not connect to FastAPI server. Ensure it's running on port 8000. \n Error: {e}")

with col2:
    if 'report_data' in st.session_state:
        data = st.session_state['report_data']
        
        st.subheader("Final Polished Report")
        st.markdown(f"<div class='final-output'>{data['final_report']}</div>", unsafe_allow_html=True)
        
        st.divider()
        st.subheader("Pipeline Telemetry")
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title'>🕵️‍♂️ Researcher Preview</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-content'><i>{data['workflow_state'].get('research_data_preview', '')}</i></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with t_col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title'>✍️ Draft Preview</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-content'><i>{data['workflow_state'].get('draft_preview', '')}</i></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.info("💡 Trace details for this run are available in LangSmith.")
    else:
        st.markdown(
            "<div style='text-align: center; margin-top: 100px; color: #8b949e;'>"
            "<h3>Waiting for input...</h3>"
            "<p>Your finalized, cleanly formatted report will appear here.</p>"
            "</div>", 
            unsafe_allow_html=True
        )
