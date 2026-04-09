import os
from flask import Flask, request, render_template
from groq import Groq

# 1. Initialization
app = Flask(__name__)
# WARNING: Ensure GROQ_API_KEY is set in your environment
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Token-Optimized CoT Prompt
COT_PROMPT = """Solve the math problem step-by-step. Be extremely concise.
Strict Format:
Step 1: [calculation]
Step 2: [calculation]
Final Answer: [result]"""

# 3. API Call Function
def solve_math(question: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Low-cost, fast reasoning model
            messages=[
                {"role": "system", "content": COT_PROMPT},
                {"role": "user", "content": question}
            ],
            temperature=0.0, # Zero temp for deterministic math operations
            max_tokens=200   # Hard-cap token burn per query
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# 4. Minimal Web View
@app.route("/", methods=["GET", "POST"])
def index():
    solution = None
    if request.method == "POST":
        question = request.form.get("question", "")
        if question:
            solution = solve_math(question)
            
    return render_template("index.html", solution=solution, question=request.form.get("question", ""))

# ----------------------------------------------------
# 5. Example Interaction
# 
# INPUT: 
# "If a factory produces 20 cars per hour, how many cars does it make in 3.5 days?"
#
# OUTPUT:
# Step 1: Calculate hours in 3.5 days (3.5 * 24 = 84 hours).
# Step 2: Multiply hours by cars per hour (84 * 20).
# Final Answer: 1680 cars
# ----------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)
