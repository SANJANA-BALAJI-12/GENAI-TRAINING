import os
import ast
from flask import Flask, request, render_template
from groq import Groq

# 1. Initialization
app = Flask(__name__)
# WARNING: Ensure GROQ_API_KEY is set in your environment
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Token-Optimized Self-Reflection Prompt
REVIEW_PROMPT = """You are a highly efficient self-reflecting code reviewer.
Step 1: Analyze the provided code and AST context.
Step 2: Generate concise suggestions (bugs, style, performance).
Step 3: Critically reflect on your suggestions. Are they truly necessary?
Step 4: Output FINAL REFINED SUGGESTIONS.
Be extremely concise.

Code to Review:
{code}

AST Context:
{ast_context}
"""

def analyze_ast(code_str: str) -> str:
    """Uses Python AST to safely parse code and detect deterministic issues before LLM processing."""
    try:
        tree = ast.parse(code_str)
        # Low-token static analysis
        funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
        return f"Syntax: Valid. Found functions: {funcs}. Imports: {imports}."
    except SyntaxError as e:
        return f"Syntax Error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return f"AST Parsing Error: {str(e)}"

def reflect_and_review(code_str: str) -> str:
    """Builds prompt, executes reflection loop via LLaMA, and returns refined result."""
    ast_ctx = analyze_ast(code_str)
    prompt = REVIEW_PROMPT.format(code=code_str, ast_context=ast_ctx)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Optimized for high-speed, cost-effective reflection
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, # Low temp for deterministic logic
            max_tokens=350   # Hard-cap token burn per reflection loop
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"

# 3. Presentable Web View
@app.route("/", methods=["GET", "POST"])
def index():
    review_output = None
    code_input = ""
    
    if request.method == "POST":
        code_input = request.form.get("code", "")
        if code_input.strip():
            review_output = reflect_and_review(code_input)
            
    return render_template("index.html", code_input=code_input, review_output=review_output)

if __name__ == "__main__":
    # Runs on port 5001 to prevent conflicts if your math solver is still active on 5000
    app.run(port=5001, debug=True)
