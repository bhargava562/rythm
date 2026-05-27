# Team Roles & Responsibilities: Rythm

This document defines the team organization, architectural boundaries, and a RACI matrix mapping roles to the 10 core phases of the Rythm platform.

---

## 1. Role Definitions

### 👥 Product Manager / Scrum Master (PM)
* **Responsibility**: Scope management, feature prioritization, requirements mapping, sprint coordination, and educational stakeholder alignment.
* **Core Focus**: Translating the educational value loop (from job tracking to job landing) into clear engineering directives.

### 💻 Lead Backend Architect (BE)
* **Responsibility**: Database modeling (PostgreSQL, indexes, UUIDs), API development (FastAPI), secure token issuance (JWT), and execution of core logic engines (Priority Intelligence formula, status audit logging).
* **Core Focus**: Maintaining the performance, safety, and transactional boundaries of our state-driven workflow backend.

### 🎨 Frontend Developer (FE)
* **Responsibility**: Responsive user interface construction (Web dashboard), state management (handling pipeline transitions), and data visualization (analytics dashboards, charts).
* **Core Focus**: Building an intuitive, interactive frontend experience that visualizes gaps, priorities, and funnel statistics.

### 🧠 AI & Data Engineer (AI)
* **Responsibility**: Prompt engineering templates, LLM API response parsing, integration of LLMs for skill extraction and resume recommendations, and consolidation of trend intelligence aggregates.
* **Core Focus**: Maximizing parsing accuracy, minimizing LLM latency, and optimizing context windows.

### ⚙️ DevOps / Site Reliability Engineer (DevOps)
* **Responsibility**: Continuous Integration/Continuous Deployment (CI/CD) pipelines, Docker infrastructure, PostgreSQL database administration (backups, pooling), and hosting.
* **Core Focus**: Maintaining environment consistency, uptime, scalability, and security parameters.

### 🧪 QA Engineer (QA)
* **Responsibility**: End-to-end API testing, security testing (SQL injection/JWT integrity audits), unit tests (pytest coverage), and UI accessibility testing.
* **Core Focus**: Ensuring zero regressions, verifying status transition bounds, and verifying error response schemas.

---

## 2. RACI Matrix

* **R (Responsible)**: The role that performs the activity.
* **A (Accountable)**: The role with final approval and decision-making authority.
* **C (Consulted)**: The role that provides input or expertise.
* **I (Informed)**: The role kept updated on progress/decisions.

| Core Platform Phase | PM | BE | FE | AI | DevOps | QA |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 1: Student Identity (Auth)** | C | A | R | I | C | R |
| **Phase 2: Profile Initialization** | A | R | R | I | I | R |
| **Phase 3: Opportunity Ingestion** | A | R | R | C | I | R |
| **Phase 4: AI Parsing Engine** | C | R | I | A | C | R |
| **Phase 5: Match & Gap Engine** | A | R | R | C | I | R |
| **Phase 6: Priority Intelligence** | A | R | I | C | I | R |
| **Phase 7: Resume Tailoring** | C | I | R | A | I | R |
| **Phase 8: Workflow Tracking** | A | R | R | I | I | R |
| **Phase 9: Analytics Dashboard** | A | C | R | I | I | R |
| **Phase 10: Trend Intelligence** | A | R | R | C | C | R |

---

## 3. Communication & Deliverable Sign-Offs

To maintain engineering velocity and architectural alignment, the team adheres to these practices:
1. **API Changes**: All changes to `/api/v1` routes must be drafted in [api_specification.md](file:///D:/rythm/docs/api_specification.md) and approved by the BE and FE roles before execution.
2. **Schema Migrations**: Database changes must be accompanied by an Alembic migration script, reviewed by the BE Architect, and executed in staging by DevOps.
3. **AI Prompt Updates**: Prompt templates must undergo evaluation (temperature, token cost, parsing reliability) by the AI engineer before merging.
