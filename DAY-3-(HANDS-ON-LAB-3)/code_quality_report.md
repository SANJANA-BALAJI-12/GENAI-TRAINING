# 📁 Code Quality & Architecture Report

## 🗂 Proposed Folder Structure

A well-organized codebase is essential for maintainability and team collaboration. We propose a domain-driven structure decoupling the FastAPI transport layer, the LangGraph workflow, and the supporting infrastructure.

```text
hitl_moderation_system/
│
├── core/                       # Shared configurations and constants
│   ├── config.py               # Pydantic BaseSettings (env vars, API keys)
│   ├── dependencies.py         # FastAPI dependency injections (DB sessions, graph client)
│   └── logger.py               # Centralized JSON logging setup
│
├── domain/                     # Business Logic (LangGraph & AI)
│   ├── graph.py                # LangGraph state machine definition (nodes, edges, compilation)
│   ├── state.py                # TypedDict definitions for graph state
│   ├── prompts.py              # LLM system prompts and guidelines
│   └── models.py               # LLM interaction layer (LangChain wrappers)
│
├── api/                        # Transport Layer / Endpoints
│   ├── routers/
│   │   ├── submit.py           # User ingestion router
│   │   ├── review.py           # Human-in-the-loop router
│   │   └── admin.py            # Dashboard/metrics routing
│   ├── schemas.py              # Pydantic models for REST requests/responses
│   └── main.py                 # FastAPI application entry point
│
├── infrastructure/             # External adapters
│   ├── database.py             # SQLAlchemy setup, async engine
│   └── orm_models.py           # SQLAlchemy declarative base models
│
├── tests/                      # Pytest suite
│   ├── test_api.py             # Endpoint tests (TestClient)
│   └── test_graph.py           # Unit tests for LangGraph nodes (mocking LLMs)
│
├── .env.example
├── requirements.txt            # Or pyproject.toml / poetry
└── README.md
```

---

## 🏗 Best Practices

1. **Separation of Concerns:** 
   - HTTP logic (FastAPI) handles validation and permissions but delegates the complex state transitions directly to the LangGraph application.
   - Using Dependency Injection in FastAPI ensures that the LangGraph setup (and the memory checkpointing) is initialized securely and mapped per request appropriately.

2. **Strong Typing & Validation:**
   - Both LangGraph State (using `TypedDict` or Pydantic) and FastAPI endpoints (Pydantic `BaseModel`) must enforce strict schemas. If an LLM returns ill-formatted output, Pydantic's structured output parsers will catch it gracefully.

3. **Stateless Nodes & Graph State:**
   - Keep LangGraph nodes small and focused. A node should only read the incoming state and `return` the delta updates. Side-effects (like Database saves) are isolated or handled in final terminal nodes.

4. **Security & Role-Based Access (RBAC):**
   - Endpoints like `/moderate/{id}/review` must require Moderator or Admin token validation via FastAPI's `Depends(get_current_user)`.
   - Never expose system configuration endpoints without strict Admin checks.

---

## 🚀 Scalability & Maintainability Notes

- **Horizontal Scaling:** FastAPI is stateless and can be scaled infinitely across stateless horizontal pods (Kubernetes). The crucial element is centralized checkpointing. By switching LangGraph from `MemorySaver` to the `AsyncPostgresSaver`, any web pod can resume any interrupted workflow seamlessly.
- **Asynchronous Execution:** Heavy network calls to the LLM must utilize `async/await` (`ainvoke` in LangChain/LangGraph) to avoid blocking FastAPI's async event loop.
- **Versioning:** If moderation policies change drastically, introduce `/v2/` API namespaces and instantiate a uniquely versioned LangGraph instance (e.g., `moderation_graph_v2`). This allows safe A/B testing of prompt efficacy without breaking current workflows.
