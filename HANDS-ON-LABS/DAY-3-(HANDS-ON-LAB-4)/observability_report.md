# 👁️ Observability Report: LangSmith Tracing

## 1. LangSmith Logging Strategy
In robust Multi-Agent systems, blind execution is dangerous. Our strategy integrates **LangSmith** natively via standard LangChain SDKs.

- **Global Tracing Enablement**: Tracing runs globally by setting `LANGCHAIN_TRACING_V2=true` in our `.env`.
- **Project Isolation**: All traces for this application are grouped under `LANGCHAIN_PROJECT=Multi_Agent_Research`.
- **Explicit Inputs/Outputs**: FastAPI enforces structured `pydantic` parsing which provides perfectly clean metadata to LangSmith at the graph’s entry points.

## 2. Agent-Level Traces
Through the LangGraph integration, LangSmith dynamically captures an overarching graph run, but also breaks down into specialized traces:

1. **Researcher Node Invoke**: Captures the input prompt (topic) and output schema (bulleted facts). Measures latency for gathering data.
2. **Writer Node Invoke**: Displays the injected context from the state `research_data` explicitly, allowing us to debug if the Writer hallucinates or drops context.
3. **Editor Node Invoke**: Tracks the before-and-after string delta of the draft to the final output, giving visibility into how effectively the editor is doing its job.

## 3. Workflow Visibility Explanation
By utilizing the UI telemetry features on the Streamlit dashboard, end users interact comfortably. Behind the scenes:
- Developers can check LangSmith and see the exact graph visualization of `Researcher -> Writer -> Editor`.
- **Token Management**: You can query the aggregate token usage per Run directly inside LangSmith, ensuring the pipeline remains cost-effective.
- **Graceful Error Tracking**: Any ChromaDB read/write failures log via Python's standard `logging` and are visible on the server stdout, without disrupting the state machine in LangSmith.
