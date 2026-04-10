# Comprehensive Project Documentation: AgriBlast AI 🌾🤖

## Overview
AgriBlast AI is a state-of-the-art intelligent agricultural dashboard built seamlessly with a **React (Vite)** frontend and a **FastAPI** backend. It offers real-time local farm networking, crop disease analytics with dummy/mock endpoints for demonstrations, dynamic insights, and AI chat endpoints powered by Groq and OpenAI infrastructures.

---

## Technical Stack
### Frontend
- **Framework:** React + Vite
- **Styling:** TailwindCSS + Framer Motion for micro-animations
- **Routing:** React State Management (Single Page App configuration)
- **Icons:** Lucide React

### Backend
- **Framework:** FastAPI
- **Database Logic:** MongoDB utilizing explicit `motor` driver (with full built-in in-memory fallback capabilities)
- **AI Libraries:** CrewAI, LangChain, OpenAI, Groq

---

## Backend API Endpoints

The backend handles heavy logic decoupled from UI performance bottlenecks:

| Method | Endpoint | Description | Expected Payload/Response |
|---|---|---|---|
| **GET** | `/api/posts` | Fetch Community Posts | Returns array of `Post`. Uses Mongo or In-Memory fallback. |
| **POST** | `/api/posts` | Create new Post | `{"author": "...", "content": "..."}` |
| **POST** | `/api/posts/{id}/like` | Increment Like count | Dynamically pushes upvote. |
| **POST** | `/api/posts/{id}/comment` | Add nested comment | Requires `CommentCreate` mapping string content. |
| **POST** | `/api/upload` | Crop Image Analysis | Takes multi-part parsed image and returns `ImageUploadResponse`. **Note:** Simulated by robust dummy algorithm to bypass OpenAI errors. |
| **GET** | `/api/insights` | Farm Dashboard Alerts | Returns yield tracking and disease mock summaries. |
| **POST** | `/api/chat` | AI Advice Chat | Communicates with automated CrewAI multi-agent logic based on the user prompt |

---

## Database Configuration

We designed this project for extreme resiliency during presentations:
If you have **MongoDB Compass or an active local server on port 27017**, your dashboard automatically indexes arrays using BSON mapping securely.
If MongoDB fails, **it will seamlessly default to an `IN_MEMORY_POSTS` local Python dictionary.** This is why your Community Posts process instantly without crashes.

## System Workflow Diagram

1. **User Action:** The client (Vite frontend) opens and requests `GET /api/insights`.
2. **Server Interpretation:** FastAPI evaluates and queries OpenAI for alerts. If OpenAI times out, the backend injects realistic fallback JSON objects automatically.
3. **Frontend Rendering:** Framer Motion catches the returned API array and smoothly animates the dashboard.
4. **Community Push:** User types post -> `POST /api/posts` -> Fastapi intercepts the JSON -> Writes securely to the database pool. 

---

## Instructions for Restarting Services

Should you shut down your PC, simply launch:
1. **To start visual components:**
   Within `frontend` directory: `npm run dev`
2. **To initiate API logic pool:**
   Within `backend` directory (using virtual env explicitly): `.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload`
