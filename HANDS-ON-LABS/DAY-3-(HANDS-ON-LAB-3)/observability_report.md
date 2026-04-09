# 🔍 Observability & Auditing Report

## 📊 Logging Strategy

A production-grade moderation system requires structured, actionable, and persistent logs. The logging strategy follows a multi-level approach tailored to different stakeholders:

1. **Structured JSON Logs (System Level):**
   - **Tool:** Python `logging` coupled with `python-json-logger`.
   - **Format:** Every log entry is a JSON object. This ensures seamless ingestion into log aggregators (ELK, Datadog).
   - **Key Fields:** Always include `timestamp`, `log_level`, `job_id`, `node_name`, `user_id` (if known), and `action`.

2. **Audit Trails (Business Level):**
   - **Tool:** Database tables (e.g., SQLAlchemy Event Observers).
   - **Purpose:** Who did what and when? 
   - **Action:** Any human moderator action (Approve/Reject) captures the `moderator_id`, `original_ai_score`, `human_decision`, and `timestamp`. This is critical for regulatory compliance and QA auditing of moderators.

3. **Log Levels:**
   - `INFO`: Standard lifecycle events (Graph started, Node transitioned, Moderation completed).
   - `WARNING`: High rate limit usage, ambiguous AI outputs requiring parsing retries.
   - `ERROR`: FastAPI exceptions, DB connection drops, unreachable LLM APIs.
   - `DEBUG`: Full LangGraph state payloads (only enabled during active debugging).

---

## 📈 Workflow Tracing

Tracking the journey of a single text submission through LangGraph is critical for continuous improvement.

1. **LangSmith Integration:**
   - **Visual Tracing:** We utilize LangSmith to record every execution chain. It provides a visual timeline of the graph's nodes, showing input/output parameters at each step.
   - **Latency Tracking:** Pinpointing bottlenecks (e.g., is the LLM taking 5 seconds to evaluate the text, or is the DB write slow?).
   - **Token Usage:** Tracking the exact cost of the automated moderation phase per query.

2. **State Machine Checkpointing:**
   - LangGraph's native `MemorySaver` or Postgres Checkpointers ensure that the exact state of the graph prior to a human interruption is preserved. 
   - If the FastAPI server crashes while waiting for human review, the workflow can resume exactly where it paused thanks to persistent checkpoints.

---

## 🛠 Debugging Insights

To rapidly resolve incidents, the system must expose clear debugging vectors:

1. **Trace IDs (Correlation):**
   Every API request to `/moderate/submit` is assigned a unique `X-Request-ID`. This UUID is passed into the LangGraph state and appended to *all* logs. You can grep `X-Request-ID=12345` across logs, LangSmith, and the DB to reconstruct the entire lifecycle.

2. **Dead Letter Queues (DLQ) / Fallback Modes:**
   If the LLM fails 3 times, LangGraph routes the state to a `DLQ_Node`. The status is marked as `"SYSTEM_ERROR"`, bypassing standard human queues and alerting an Admin.

3. **Prompt Drift Analysis:**
   By capturing both the *AI's decision text* and the *Human's final override* in the database, analysts can build dashboards comparing AI accuracy. If human overwrite rates spike from 5% to 25%, it signals prompt degradation or a shift in user behavior, allowing engineers to recalibrate the system.
