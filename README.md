# Rythm — AI-Powered Student Career Workflow Intelligence Platform

Rythm is a state-driven career workflow orchestration system designed to support students throughout their career preparation and opportunity tracking. Rather than acting as a simple spreadsheet or CRUD job tracker, Rythm operates as a continuously evolving intelligence graph. Every action a student takes generates structured state, skill gap analytics, priority recommendations, and adaptive resume tailoring suggestions.

---

## 🚀 Key Features

* **Student Registration & Secure Identity**: Hashed passwords using `bcrypt` and JWT session tracking, with UUID protection against enumeration attacks.
* **Unified Career Profile**: Centralized, queryable skills catalog (`skills_master`) mapping profile strength, target roles, and performance links (LeetCode, GitHub).
* **Frictionless Ingestion (No unstable scrapers)**: Copy-paste job descriptions and details from LinkedIn, Naukri, AICTE, etc. for local storage.
* **AI Parsing & Semantic Extraction**: Auto-extracts required skills, experience levels, and domains from raw description texts.
* **Skill Match & Gap Analysis Engine**: Compares candidate skills against job requirements to calculate matching metrics and identify specific areas of development.
* **Priority Intelligence Engine**: Mathematically ranks opportunities by urgency, skill alignment, market trends, and candidate preference using a normalized weighted formula.
* **Resume Tailoring Engine**: Context-engineered LLM recommendations suggesting additions/removals to maximize relevance for target roles.
* **Status History Tracking**: Comprehensive audit trail of application stages (`Saved`, `Applied`, `OA Scheduled`, `Interview`, `Rejected`, `Offer`) to compute funnel metrics.
* **Adaptive Trend Intelligence**: Continually scrapes system-wide ingestion trends to show what skills (e.g., Redis, Kafka, Spring Boot) are currently seeing hiring surges.

---

## 🛠️ Technology Stack

* **Backend**: Python 3.14+ with FastAPI (Asynchronous API endpoints, Pydantic data validation)
* **Database**: PostgreSQL (Relational schema for normalized skills and status tracking)
* **ORM**: SQLAlchemy (Async Engine) with Alembic for migrations
* **Security**: PyJWT, Passlib (with bcrypt)
* **AI Engine**: LangChain / Direct API Integrations (Gemini / OpenAI) for semantic analysis
* **Containerization**: Docker & Docker Compose

---

## 📂 Repository Structure

* [docs/proposal.md](file:///D:/rythm/docs/proposal.md) — Platform proposal and business/technical workflow detail.
* [docs/proposal.docx](file:///D:/rythm/docs/proposal.docx) — Compiled Microsoft Word version of the proposal for review.
* [docs/architecture.md](file:///D:/rythm/docs/architecture.md) — Layered backend system architecture & Mermaid flow diagrams.
* [docs/database_erd.md](file:///D:/rythm/docs/database_erd.md) — Schema definitions and Entity-Relationship diagram.
* [docs/api_specification.md](file:///D:/rythm/docs/api_specification.md) — Complete REST API endpoint reference.
* [docs/roles_responsibilities.md](file:///D:/rythm/docs/roles_responsibilities.md) — Team organization, roles, and RACI matrix.
* [docs/project_board.md](file:///D:/rythm/docs/project_board.md) — Interactive task list and development milestones.
* [docs/setup_guide.md](file:///D:/rythm/docs/setup_guide.md) — Local development and environment setup instructions.
* [backend/](file:///D:/rythm/backend/) — The FastAPI source code repository skeleton.

---

## 🛠️ Quick Start

To set up the backend application locally:

1. **Pre-requisites**: Ensure you have Python 3.12+, PostgreSQL, and Docker installed.
2. **Follow the Setup Guide**: Refer to [docs/setup_guide.md](file:///D:/rythm/docs/setup_guide.md) for full commands.
3. **Environment Setup**:
   ```bash
   cd backend
   cp .env.example .env
   # Update variables in .env
   ```
4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run Development Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 🛡️ License

This project is proprietary and confidential. Developed under the codename **Rythm**.
