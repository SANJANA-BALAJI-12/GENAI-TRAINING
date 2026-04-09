import os
from flask import Flask, request, render_template
from groq import Groq

# 1. Initialization
app = Flask(__name__)
# WARNING: Ensure GROQ_API_KEY is set in your environment
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ----------------------------------------------------
# 2. Token-Optimized Prompt Templates
# ----------------------------------------------------

# Pattern A: ReAct (Used for factual lookups & policies)
REACT_PROMPT = """You are a Support ReAct Agent. Use internal reasoning to find policies.
Thought: [Identify policy needed]
Action: PolicyLookup
Observation: [Simulated policy recall]
Final Answer: [Concise user-facing reply]"""

# Pattern B: Chain-of-Thought (Used for technical troubleshooting)
COT_PROMPT = """You are a Tech Support CoT Agent. Guide the user step-by-step.
Step 1: [Analyze constraints]
Step 2: [Determine best fix]
Final Answer: [Instructional steps 1, 2, 3...]"""

# Pattern C: Self-Reflection (Used for general/billing sensitive queries)
REFLECT_PROMPT = """You are an Empathic Support Agent.
Draft Response: [Initial thought]
Critique: [Is this polite and fully resolving?]
Final Answer: [Highly polished, empathic reply]"""


# ----------------------------------------------------
# 3. Routing & API Logic
# ----------------------------------------------------

def route_query(query: str) -> dict:
    """Super-lightweight router to enforce correct prompt patterns."""
    q = query.lower()
    if any(keyword in q for keyword in ["how to", "fix", "step", "error"]):
        return {"name": "Chain-of-Thought", "prompt": COT_PROMPT}
    elif any(keyword in q for keyword in ["policy", "refund", "rule", "?"]):
        return {"name": "ReAct", "prompt": REACT_PROMPT}
    else:
        return {"name": "Self-Reflection", "prompt": REFLECT_PROMPT}

def process_query(query: str) -> tuple:
    route = route_query(query)
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Low-cost, fast inference tier
            messages=[
                {"role": "system", "content": route["prompt"]},
                {"role": "user", "content": query}
            ],
            temperature=0.2, # Low temperature limits waffle & hallucination
            max_tokens=250   # Strict token cap per conversation
        )
        return route["name"], response.choices[0].message.content
    except Exception as e:
        return "Error", str(e)

# ----------------------------------------------------
# ----------------------------------------------------
# 4. Minimal Presentable Web UI (Moved to Templates)
# ----------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    pattern, ai_resp, q = None, None, ""
    if request.method == "POST":
        q = request.form.get("query", "")
        if q.strip():
            pattern, ai_resp = process_query(q)
            
    return render_template("index.html", query=q, pattern=pattern, response=ai_resp)

if __name__ == "__main__":
    # Host on 5002 to avoid clashing with Math Solver (5000) and Code Reviewer (5001)
    app.run(port=5002, debug=True)
