from app import extract_node, transform_node, load_node, ETLState
from langgraph.graph import StateGraph, END

def main():
    builder = StateGraph(ETLState)
    builder.add_node("Extract", extract_node)
    builder.add_node("Transform", transform_node)
    builder.add_node("Load_GenAI", load_node)
    builder.set_entry_point("Extract")
    builder.add_edge("Extract", "Transform")
    builder.add_edge("Transform", "Load_GenAI")
    builder.add_edge("Load_GenAI", END)
    
    pipeline = builder.compile()
    
    png_bytes = pipeline.get_graph().draw_mermaid_png()
    with open("infographic.png", "wb") as f:
        f.write(png_bytes)
    
    print("Infographic explicitly saved to infographic.png")

if __name__ == "__main__":
    main()
