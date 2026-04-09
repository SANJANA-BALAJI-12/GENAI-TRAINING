import os
import sys
import json
import subprocess
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from fpdf import FPDF
from app import extract_node, transform_node, load_node, ETLState
from langgraph.graph import StateGraph, END
import pandas as pd

console = Console()

def run_pylint():
    console.print("[bold blue]Analyzing code quality with pylint...[/bold blue]")
    result = subprocess.run([sys.executable, "-m", "pylint", "app.py"], capture_output=True, text=True)
    return result.stdout

def create_pdf(title, content, filename, image_path=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=title, ln=True, align="C")
    pdf.ln(10)
    
    if image_path and os.path.exists(image_path):
        # We assume image might fit on A4 nicely
        pdf.image(image_path, x=10, w=190)
        pdf.ln(10)
        
    pdf.set_font("Arial", size=10)
    
    # Clean the content for FPDF since standard aerial doesn't support complex unicode
    if content:
        content = content.encode('latin-1', 'replace').decode('latin-1')
        for line in content.split('\n'):
            pdf.cell(200, 6, txt=line, ln=True)
        
    pdf.output(filename)

def generate_infographic(pipeline):
    try:
        png_bytes = pipeline.get_graph().draw_mermaid_png()
        with open("infographic.png", "wb") as f:
            f.write(png_bytes)
        create_pdf("LangGraph ETL Infographic", "Workflow Visualization for LangGraph Pipeline", "infographic.pdf", "infographic.png")
        console.print("[bold green]✅ Generated infographic.pdf[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Failed to generate infographic: {e}[/bold red]")
        create_pdf("LangGraph ETL Infographic", f"Failed to generate graphic because of missing dependencies: {e}\n\nWorkflow:\n1. Extract\n2. Transform\n3. Load_GenAI", "infographic.pdf")

def run_pipeline():
    builder = StateGraph(ETLState)
    builder.add_node("Extract", extract_node)
    builder.add_node("Transform", transform_node)
    builder.add_node("Load_GenAI", load_node)
    builder.set_entry_point("Extract")
    builder.add_edge("Extract", "Transform")
    builder.add_edge("Transform", "Load_GenAI")
    builder.add_edge("Load_GenAI", END)
    pipeline = builder.compile()

    generate_infographic(pipeline)

    initial_state = {
        "data": pd.DataFrame(), 
        "audit_trail": [], 
        "metrics": {}, 
        "guardrail_flags": []
    }
    
    console.print(Panel.fit("[bold green]🚀 Running the LangGraph Application...[/bold green]"))
    final_state = pipeline.invoke(initial_state)
    return final_state

def display_dashboard(final_state, pylint_output):
    console.print("\n")
    table = Table(title="📊 Pipeline Observability Metrics", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", width=30)
    table.add_column("Value", justify="right", style="green")
    
    for k, v in final_state["metrics"].items():
        table.add_row(k, str(v))
        
    console.print(table)
    
    console.print("\n")
    audit_table = Table(title="📝 Audit Trail", show_header=True, header_style="bold yellow")
    audit_table.add_column("Log Entry", style="dim")
    for log in final_state["audit_trail"]:
        audit_table.add_row(log)
        
    console.print(audit_table)
    
    console.print("\n")
    
    # Process Pylint Output Summary
    summary = "\n".join(pylint_output.split("\n")[-6:]) if pylint_output else "No Summary"
    console.print(Panel(summary, title="🔍 Code Quality Summary (PyLint)", border_style="blue"))
    
def main():
    # 1. Code Quality
    pylint_output = run_pylint()
    create_pdf("Code Quality Report - app.py", pylint_output, "code_quality.pdf")
    console.print("[bold green]✅ Generated code_quality.pdf[/bold green]")
    
    # 2. Application Run 
    state = run_pipeline()
    
    # 3. Observability Report
    obs_content = "METRICS:\n" + json.dumps(state['metrics'], indent=2) + "\n\nAUDIT TRAIL:\n" + "\n".join(state['audit_trail'])
    create_pdf("Observability Report", obs_content, "observability_report.pdf")
    console.print("[bold green]✅ Generated observability_report.pdf[/bold green]")
    
    # 4. Colorful Dashboard
    display_dashboard(state, pylint_output)
    
    console.print("\n[bold yellow]To visualize this workflow in LangSmith:[/bold yellow]")
    console.print("[cyan]1. Set environment variables:[/cyan]")
    console.print("   $env:LANGCHAIN_TRACING_V2=\"true\"")
    console.print("   $env:LANGCHAIN_API_KEY=\"<your-langsmith-api-key>\"")
    console.print("   $env:LANGCHAIN_PROJECT=\"<your-project-name>\"")
    console.print("[cyan]2. Run the application:[/cyan]")
    console.print("   python app.py")
    console.print("[cyan]3. Navigate to https://smith.langchain.com to view the traces.[/cyan]")

if __name__ == "__main__":
    main()
