# Presentation: AgriBlast AI Capstone Project

Here is the structured content for your PowerPoint presentation based on your workflow. You can easily copy and paste these into your slides.

---

## Slide 1: Title Slide
**Title:** AgriBlast AI – Intelligent Smart Farming Advisor 
**Subtitle:** Capstone Project Presentation
**Footer:** [Your Name / Team Name]
**Visual Idea:** A high-quality image of modern, technology-driven agriculture (e.g., a drone over a field or a tablet displaying a dashboard in front of crops).

---

## Slide 2: Project Workflow Overview
**Title:** Our Approach to Building AgriBlast
**Content:**
- **Phase 1: Design** – Laying the required foundation and architecture.
- **Phase 2: Build** – Intelligent RAG Agents, seamless deployment, and monitoring.
- **Phase 3: Test** – Ensuring scalability, accuracy, and performance.
- **Phase 4: Present** – Deliverables, Demonstration, and Q&A.
**Visual Idea:** A 4-step horizontal process chevron displaying the four phases.

---

## Slide 3: Phase 1 - Design
**Title:** Phase 1: Design & Planning
**Content:**
- **User Personas:** Modern Farmers, Agronomists, and Agricultural Consultants.
- **Use Cases:** Disease detection via images, real-time weather forecasting, community knowledge sharing, and actionable farming insights.
- **Tech Stack:** 
  - *Frontend:* React / Vite / Tailwind
  - *Backend:* FastAPI / Python
  - *Intelligence:* Groq/OpenAI, CrewAI Multi-Agent System, ChromaDB (Local RAG)
  - *Database:* MongoDB

---

## Slide 4: System Architecture
**Title:** System Architecture Diagram
*(Use the following diagram in your presentation. You can recreate this or screenshot the generated chart below)*

```mermaid
graph TD
    User([Farmer / User]) -->|UI Interacts| Frontend[React / Vite Frontend]
    Frontend -->|API Calls (HTTPS)| FastAPI[FastAPI Backend]
    
    subgraph AI Engine
        FastAPI -->|Queries| CrewAI[CrewAI Agent System]
        CrewAI -->|Fetches context| ChromaDB[(ChromaDB / RAG)]
        FastAPI -->|Image Processing| OpenAI[Vision LLM]
    end

    subgraph Data Layer
        FastAPI --> MongoDB[(MongoDB Database)]
        MongoDB -->|Stores| Posts[Community Posts]
    end
```

---

## Slide 5: Phase 2 - Build
**Title:** Phase 2: Build & Implementation
**Content:**
- **RAG & Agent Implementation:** Seamlessly integrating ChromaDB for agricultural context retrieval, processed by our tailored CrewAI agents.
- **Version Control:** Continuous integration and repository management via GitHub.
- **Monitoring & Observability:** Tracked API reliability, model latency, and prompt traces using tools like LangSmith (if applicable).
- **Cloud Deployment:** Ready-to-scale deployment endpoints preparing the web application for live usage (Azure/AWS).

---

## Slide 6: Phase 3 - Test
**Title:** Phase 3: Testing & Evaluation
**Content:**
- **Accuracy:** Validated the AI Vision model's crop disease detection against established agricultural baselines.
- **Latency & Cost:** Optimized prompt token counts and API calls to keep latency low (<2s) while minimizing external API expenditures. 
- **User Testing:** Conducted feedback sessions with peers and instructors to refine dashboard UI/UX and enhance data readability.

---

## Slide 7: Deliverables
**Title:** Capstone Deliverables
**Content:**
- **Code Repository:** Fully documented GitHub repository with clear startup instructions.
- **Deployment URL:** Live web application hosted on cloud infrastructure.
- **Presentation Materials:** This slide deck and supporting documentation.
- **Future Enhancements:** Extending to native mobile platforms and integrating IoT soil sensors.

---

## Slide 8: Demo & Q&A
**Title:** Live Demonstration & Q&A
**Content:**
- Unveiling the 10-Minute Live Demo:
  1. Image-based Crop Disease Analysis
  2. The Community Knowledge board
  3. Dynamic Dashboard Insights & Weather
- **Thank You! Any Questions?** 
- **Contact Info:** [Your Email / GitHub Profile]

---

> [!TIP]
> **Speaker Note:** For the architecture diagram on Slide 4, you can copy the Mermaid code into a tool like [Mermaid Live Editor](https://mermaid.live/) to export a beautiful high-resolution image tailored for PowerPoint!
