# Project Board: Rythm

This document tracks current project tasks, developmental sprints, and milestones for the Rythm platform.

---

## 📋 Kanban Board

### 📥 Todo (Backlog)
- [ ] Add integration testing pipeline for OpenAI/Gemini mock responses.
- [ ] Implement secure rate-limiting middleware for raw ingestion pasting.
- [ ] Create automated db backup CronJob inside Docker compose.
- [ ] Support PDF file parsing for Direct Resume upload instead of raw text pasting.

### ⏳ In Progress
- [ ] Initialize Python FastAPI backend skeleton (FastAPI, database engines, configuration setup).
- [ ] Map PostgreSQL models to SQLAlchemy structure (`Student`, `Profile`, `Skill`, `Application`).
- [ ] Implement Auth router and password hashing logic.

### 🧪 In Review
- [ ] Write Project Proposal document and compile Word artifact (`proposal.md` and `proposal.docx`).
- [ ] Develop System Architecture and Database ERD charts.
- [ ] Specify API RESTful endpoint schemas.

### 🚀 Done
- [x] Configure repository root variables and project `.gitignore`.
- [x] Create backend deployment configuration file (`Dockerfile`).
- [x] Create project `README.md` file.

---

## 📅 Release Roadmap

### 📦 Sprint 1: Identity & Foundation (Weeks 1-2)
* **Goal**: Establish development workspace, deploy PostgreSQL, and build authentication pipelines.
* **Tasks**:
  - [x] Setup repository, gitignore, and docker base.
  - [ ] Implement database async configuration & models.
  - [ ] Build `/api/v1/auth/register` and `/api/v1/auth/login` (JWT token issuance, bcrypt verification).
  - [ ] Create database migration schema baseline using Alembic.

### 📦 Sprint 2: Opportunity Ingestion & AI Parsing (Weeks 3-4)
* **Goal**: Build the core opportunity ingestion pipeline and connect LLM parsing.
* **Tasks**:
  - [ ] Develop skills catalog directory (`skills_master` pre-loaded seeds).
  - [ ] Create profile initialization API routes.
  - [ ] Develop `/api/v1/applications/ingest` endpoint to receive pasted jobs.
  - [ ] Code AI parser interface (`ai_service.py`) integrating Gemini API for skill extraction.

### 📦 Sprint 3: Intel Engines (Weeks 5-6)
* **Goal**: Code the priority algorithm, gap analyzer, and resume optimization logic.
* **Tasks**:
  - [ ] Program matching algorithms comparing candidate profiles and job requirements.
  - [ ] Implement Priority score computation engine based on urgency, match, trends, and preference.
  - [ ] Create `/api/v1/applications/{id}/resume-tailor` context engine using LLMs.
  - [ ] Hook up automatic priority recalculation hooks when candidate skills change.

### 📦 Sprint 4: Workflow Audits & Trend Insights (Weeks 7-8)
* **Goal**: Build conversion analytics, history logs, macro trend aggregates, and release v1.0.
* **Tasks**:
  - [ ] Develop `/api/v1/applications/{id}/status` transition routing.
  - [ ] Build status audit logs table (`application_status_history`).
  - [ ] Create dashboard analytics (`/api/v1/analytics/overview`).
  - [ ] Code trend intelligence tracking to aggregate system-wide requirements.
  - [ ] Run end-to-end integration and load tests.
