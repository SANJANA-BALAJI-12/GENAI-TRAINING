# 🚀 Human-in-the-Loop Content Moderation System

## 🌟 System Overview
The **Human-in-the-Loop (HITL) Content Moderation System** is a robust, event-driven pipeline designed to automatically analyze user-generated content and escalate ambiguous or high-risk cases to human moderators. Built with **LangGraph** for resilient state management and **FastAPI** for a snappy, intuitive reviewer API, it ensures both speed and safety in content publishing.

The system is split into three main roles:
- **System**: Handles automated ingestion, AI-based pre-screening, and final actions.
- **Moderator**: Reviews flagged content with pending states.
- **Admin**: Manages moderation policies, thresholds, and role assignments.

---

## 🏛 Architecture Diagram

```mermaid
graph TD
    classDef user fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    classDef api fill:#2ecc71,stroke:#27ae60,stroke-width:2px,color:#fff
    classDef agent fill:#9b59b6,stroke:#8e44ad,stroke-width:2px,color:#fff
    classDef human fill:#e74c3c,stroke:#c0392b,stroke-width:2px,color:#fff
    classDef db fill:#f1c40f,stroke:#f39c12,stroke-width:2px,color:#333
    
    subgraph Client
        U[User App]:::user
        M[Moderator Dashboard]:::human
    end

    subgraph API Gateway
        F[FastAPI Server]:::api
    end

    subgraph State Machine
        LG[LangGraph Moderation Workflow]:::agent
    end

    subgraph Infrastructure
        DB[(PostgreSQL / Audit DB)]:::db
        LS[(LangSmith Observability)]:::db
    end

    U -- "Submits Content" --> F
    M -- "Reviews Flagged Content" --> F
    
    F -- "Triggers Graph" --> LG
    F -- "Approval/Rejection" --> LG
    
    LG -- "Tracks Traces" --> LS
    LG -- "Reads/Writes State" --> DB
    
    %% Internal LangGraph Workflow Details
    A[Initial State] --> B{AI Moderation Node}
    B -- "Safe" --> C[Auto Approve Node]
    B -- "Toxic/Violative" --> D[Auto Reject Node]
    B -- "Flagged/Ambiguous" --> E[Human Review Node]
    
    E -- "Review Pending" --> F
    E -. "Moderator Acts" .-> G[Commit Decision]
```

---

## 🛤 Workflow Explanation

### Step-by-Step Flow

1. **📥 Ingestion Node:**
   Content arrives via the FastAPI `/moderate/submit` endpoint. A unique ID is generated, and initial metrics (timestamp, source user) are captured.

2. **🤖 AI Moderation Node (The Arbiter):**
   LangGraph invokes an LLM to evaluate the text against strict moderation rules (e.g., hate speech, PII leaks, spam, self-harm). 
   - **Threshold > 0.9:** Content is explicitly banned. Fast-tracked to rejection.
   - **Threshold < 0.2:** Content is benign. Fast-tracked to approval.
   - **Threshold 0.2 - 0.9 (Ambiguous):** Content is flagged and moved to the *Waiting for Human* state.

3. **⏸ Human Review Node (The Pause):**
   LangGraph interrupts execution using an explicit Wait State (`interrupt_before=["human_review"]`).
   The content's status is saved as `"PENDING_REVIEW"` in the database. Notifications can be triggered.

4. **🧑‍⚖️ Moderator Action:**
   A human uses the FastAPI `/moderate/{job_id}/review` endpoint (via a simple dashboard) to read the flagged content and the AI's reason for flagging. They POST their decision (Approve or Reject).

5. **🏁 Final Action Node:**
   LangGraph receives the human input, resumes the state machine, updates the final disposition in the database, and concludes the workflow.
