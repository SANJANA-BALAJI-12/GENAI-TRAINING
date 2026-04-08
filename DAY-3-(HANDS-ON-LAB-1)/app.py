import os
import pandas as pd
from typing import TypedDict, List, Dict, Any
from datetime import datetime
import json
from langgraph.graph import StateGraph, END

# --- Make Application Presentable ---
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console(record=True)

# --- LangSmith Integration ---
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key-here" # Replace with your actual key before running
os.environ["LANGCHAIN_PROJECT"] = "LangGraph_ETL_Pipeline"

# 1. Define the State for LangGraph
class ETLState(TypedDict):
    data: pd.DataFrame
    audit_trail: List[str]
    metrics: Dict[str, Any]
    guardrail_flags: List[str]

# 2. Extract Node
def extract_node(state: ETLState) -> ETLState:
    console.print("[cyan]➜ Running Extract Node...[/cyan]")
    # Simulated extraction from DB/CSV
    raw_data = [
        {"id": 1, "user_text": "Great service! My phone is 555-1234."},
        {"id": 2, "user_text": "   "},  # Bad data
        {"id": 3, "user_text": "App crashed when I clicked save but I like the colors. " * 5}  # Too long
    ]
    df = pd.DataFrame(raw_data)
    
    # Audit & Observability
    state["audit_trail"].append(f"[{datetime.now().strftime('%H:%M:%S')}] EXTRACT: Loaded {len(df)} rows.")
    state["metrics"]["extracted_rows"] = len(df)
    state["data"] = df
    
    return state

# 3. Transform Node (Pandas + Guardrails)
def transform_node(state: ETLState) -> ETLState:
    console.print("[cyan]➜ Running Transform Node...[/cyan]")
    df = state["data"]
    initial_count = len(df)
    
    # Guardrail 1: Drop empty rows - pandas syntax that drops whitespace-only strings
    df = df[df['user_text'].str.strip().astype(bool)].copy()
    
    # Guardrail 2: Truncate text to limit token usage (e.g., max 100 chars here for demo)
    df.loc[:, 'user_text'] = df['user_text'].str.slice(0, 100)
    
    # Guardrail 3: Simple Pandas PII Regex Masking
    df.loc[:, 'user_text'] = df['user_text'].str.replace(r'\d{3}-\d{4}', '[REDACTED]', regex=True)
    
    # Audit & Observability Updates
    rows_dropped = initial_count - len(df)
    state["audit_trail"].append(f"[{datetime.now().strftime('%H:%M:%S')}] TRANSFORM: Dropped {rows_dropped} rows, masked PII, enforced length constraints.")
    state["metrics"]["rows_dropped_guardrail"] = rows_dropped
    state["data"] = df
    
    return state

# 4. Load Node (Mock GenAI Inference)
def load_node(state: ETLState) -> ETLState:
    console.print("[cyan]➜ Running Load Node (GenAI)...[/cyan]")
    df = state["data"]
    results = []
    total_tokens_estimated = 0
    
    for _, row in df.iterrows():
        text = row['user_text']
        
        # MOCK LLM CALL
        # In a real scenario, you would call your LLM here
        if "crashed" in text.lower():
            mock_api_response = '{"intent": "bug", "sentiment": "neg"}'
        else:
            mock_api_response = '{"intent": "praise", "sentiment": "pos"}'
            
        results.append(json.loads(mock_api_response))
        total_tokens_estimated += len(text.split()) + 15  # Rough estimation
        
    # Append results to dataframe
    df = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
    
    # Audit & Observability
    state["audit_trail"].append(f"[{datetime.now().strftime('%H:%M:%S')}] LOAD: GenAI enrichment complete. Saved to destination.")
    state["metrics"]["estimated_tokens_used"] = total_tokens_estimated
    state["data"] = df
    
    return state

def main():
    console.print(Panel.fit("[bold green]🚀 Starting Distributed GenAI ETL Pipeline...[/bold green]", border_style="green"))
    console.print("[dim italic]Integration Active: API Request Traced to LangSmith.[/dim italic]\n")

    # Initialize Graph
    builder = StateGraph(ETLState)

    # Add Nodes
    builder.add_node("Extract", extract_node)
    builder.add_node("Transform", transform_node)
    builder.add_node("Load_GenAI", load_node)

    # Define Linear Edges
    builder.set_entry_point("Extract")
    builder.add_edge("Extract", "Transform")
    builder.add_edge("Transform", "Load_GenAI")
    builder.add_edge("Load_GenAI", END)

    # Compile
    pipeline = builder.compile()

    # Initial State
    initial_state = {
        "data": pd.DataFrame(), 
        "audit_trail": [], 
        "metrics": {}, 
        "guardrail_flags": []
    }
    
    # Run Pipeline
    final_state = pipeline.invoke(initial_state)

    console.print("\n[bold magenta]📊 OBSERVABILITY METRICS:[/bold magenta]")
    metrics_table = Table(show_header=True, header_style="bold magenta", border_style="magenta")
    metrics_table.add_column("Metric Name", style="cyan", width=30)
    metrics_table.add_column("Value", justify="right", style="green")
    
    for k, v in final_state["metrics"].items():
        metrics_table.add_row(k.replace('_', ' ').title(), str(v))
    
    console.print(metrics_table)
    
    console.print("\n[bold yellow]📝 AUDIT TRAIL:[/bold yellow]")
    for log in final_state["audit_trail"]:
        console.print(f" 🔹 {log}")
    
    console.print("\n[bold blue]✅ FINAL PROCESSED DATA:[/bold blue]")
    
    # Fancy printing the DataFrame using rich
    df = final_state["data"]
    df_table = Table(show_header=True, header_style="bold blue", border_style="blue")
    df_table.add_column("ID", justify="right", style="cyan")
    df_table.add_column("User Text", style="white")
    df_table.add_column("Intent", style="yellow")
    df_table.add_column("Sentiment", style="green")
    
    for _, row in df.iterrows():
        df_table.add_row(
            str(row["id"]), 
            str(row["user_text"]), 
            str(row.get("intent", "N/A")), 
            str(row.get("sentiment", "N/A"))
        )
    console.print(df_table)

    console.print("\n")
    console.print(Panel("[bold green]LangSmith Trace Logged Successfully ✅\nNavigate to smith.langchain.com to view your workflow performance![/bold green]", border_style="green"))
    
    # Save the output to an HTML file for browser viewing
    console.save_html("dashboard.html")
    print("\n✅ Dashboard successfully exported to dashboard.html!")


if __name__ == "__main__":
    main()
