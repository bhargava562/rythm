---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #f4f6f9
color: #2c3e50
---

# Rythm

## AI-Powered Student Career Workflow Intelligence Platform

**Bhargava & Team**
*Advanced Software Engineering Project*

---

# Slide 2: The Challenge

* **Portals Fragmentation**: Students split attention between LinkedIn, Naukri, AICTE, and University portals.
* **Spreadsheet Fatigue**: Application stages are updated passively, leading to missed deadlines and OAs.
* **Generic ATS Rejections**: Candidates send standard resumes that lack keyword alignment.
* **Outdated Focus**: Students lack real-time indicators on what skills (e.g. Kafka, Redis) are currently trending.

---

# Slide 3: The Philosophy

### "Not Just Another CRUD App"

* Rythm shifts the paradigm from passive tracking to **active state-driven workflow orchestration**.
* Every user action—updating a skill, changing status, or pasting a job—creates structured state, recalibrates priority ratings, and updates cohort-level analytics.
* Builds a continuously evolving intelligence graph.

---

# Slide 4: Architectural Design

* **Layered Clean Architecture**: Presentation (Routers), Business (Services), Persistence (SQLAlchemy), and external integrations (AI engines) are decoupled.
* **UUID Privacy Boundaries**: Utilizes 128-bit UUIDs for all database keys to prevent ID enumeration attacks (`/applications/1`, `/applications/2`).
* **Zero-Dependency Fallbacks**: AI parsing and resume tailoring engines include regex parsing fallbacks if LLM keys are absent.

---

# Slide 5: System Block Diagram

```text
       ┌────────────────────────┐
       │   React/Next.js Client │
       └───────────┬────────────┘
                   │ HTTPS JSON
       ┌───────────▼────────────┐
       │   FastAPI Route Layer  │ (Auth check & GZip)
       └───────────┬────────────┘
                   │
       ┌───────────▼────────────┐
       │ Business Services Layer│ (Priority, AI, Resume, Cache)
       └───────────┬────────────┘
         ┌─────────┴─────────┐
  ┌──────▼──────┐     ┌──────▼──────┐
  │ PostgreSQL  │     │ Gemini API  │ (AI Parsing)
  └─────────────┘     └─────────────┘
```

---

# Slide 6: Relational DB Schema

* **Normalized Skills Catalog**: Separates candidate profiles from skills directory (`skills_master`) via a junction table (`student_skills`).
* **Audited Status History**: Tracks transitions in `application_status_history` to log funnel bottlenecks.
* **Indexes Overlay**:
  * B-Tree index on `students(email)` for logins.
  * Composite index on `applications(student_id, status)` for user pipelines.
  * Index on `applications(priority_score DESC)` for dashboard sorting.

---

# Slide 7: Opportunity Ingestion Engine

* **Copy-Paste Model**: Avoids brittle automated web scrapers.
* Scrapers are susceptible to rate limits, login blockades, and anti-bot measures from LinkedIn/Naukri.
* Copy-pasting raw description text is 100% reliable and allows immediate parsing on the backend.

---

# Slide 8: AI Semantic Parsing Engine

1. **Extraction**: Raw job descriptions are sent to LLM APIs (Gemini/OpenAI).
2. **Structuring**: Extracts technical requirements, primary domains (e.g. Backend), and required experience level.
3. **Database Mapping**: Maps text (e.g. "Spring Boot") to master IDs in the database, populating `application_required_skills`.

---

# Slide 9: Skill Match & Gap Analysis

* Calculates the mathematical intersection:
  $$\text{Match Score} = \frac{|\text{Student Skills} \cap \text{Required Skills}|}{|\text{Required Skills}|}$$
* Calculates the set difference to show candidate skill gaps:
  $$\text{Missing Skills} = \text{Required Skills} - \text{Student Skills}$$
* Displays immediate gaps on the candidate's dashboard.

---

# Slide 10: Dynamic Priority Scoring

Ranks opportunities on the student's dashboard using a multi-factor weighted equation:

$$\text{Priority} = (w_1 \times \text{Urgency}) + (w_2 \times \text{Skill Match}) + (w_3 \times \text{Trends}) + (w_4 \times \text{Interest})$$

* **Urgency**: Linear decay metric based on days left (days <= 0 -> 1.0; days >= 30 -> 0.1).
* **Interest**: Compares job title with student target roles.

---

# Slide 11: Resume Tailoring Engine

* **Context Engineering**: Packages student profile metadata, current resume text, and job requirements into custom prompt templates.
* **Output recommendations**:
  * ATS keyword insertions.
  * Bullet points optimizations showing original vs suggested sentences.
* **Human-in-the-Loop**: Students approve, reject, or request revisions.

---

# Slide 12: Funnel & Deficit Analytics

* **Funnel Rates**: Computes conversion statistics (e.g. Interview Rate, Offer Conversion Rate).
* **Aggregated Deficits**: Scans all active applications to list the user's primary missing requirements (e.g. "Missing Spring Boot in 8 applications"). This acts as a targeted study guide.

---

# Slide 13: Adaptive Trend Intelligence

* **UVP (Unique Value Proposition)**: Scrapes all opportunities ingested across the user cohort.
* **Demand Indicators**: Logs skill frequencies and week-over-week demand surges.
* **Market-Aware Recommendations**: Advises candidates on what to study based on actual local hiring trends.

---

# Slide 14: Security Hardening

* **Bcrypt Hashing**: Secure password processing using Passlib.
* **JWT Access Scopes**: Signed tokens prevent session hijacks.
* **CORS Lockdowns**: Prevents unauthorized domain cross-calls.
* **Rate Limiting**: Sliding-window rate limiter protects resources from API abuse (60 requests/min).
* **Parameterized SQL**: Parameterized queries via SQLAlchemy ORM block SQL Injection.

---

# Slide 15: Performance Optimization

* **Redis Caching**: Cached global endpoints (e.g., market trends) reduce database query loads.
* **Connection Pooling**: Reuses PostgreSQL connections via async pooling.
* **Response Compression**: GZip compression reduces server payload transmission times for large lists.
* **Junction Key Indexes**: Optimizes database intersection checks.

---

# Slide 16: Docker Containerization

* **Dockerfile**: Slim Python runtime setup.
* **Docker Compose**: Orchestrates multi-container services with healthcheck sequences:
  * PostgreSQL (`db`)
  * Redis Cache (`redis`)
  * FastAPI Application (`web`)

---

# Slide 17: Project Board & Roadmap

* **Sprint 1**: Setup Workspace, Postgres, and JWT Authentication.
* **Sprint 2**: Build skills catalog, ingestion router, and AI parsing engine.
* **Sprint 3**: Implement dynamic priority score algorithms and resume tailoring.
* **Sprint 4**: Audit pipelines, funnel analytics, Redis cache, and deploy.

---

# Slide 18: Demo & REST Client Suite

* **Database Seeder**: `seed.py` creates tables and seeds 20 core skills and weekly trends statistics.
* **Automated REST Client HTTP Suite**: `backend/tests/api_tests.http` is preloaded with 17 API requests.
* Run login, update skills, ingest jobs, and tailor resumes directly in the IDE.

---

# Slide 19: Speaking Parts & Team RACI

* **Bhargava (Lead Backend Architect)**: Accountable for database models, priority calculation, and API endpoints.
* **Teammate A (AI & Data Engineer)**: Accountable for Gemini integrations, prompt templates, and caching logic.
* **Teammate B (Frontend Developer)**: Accountable for UI dashboard widgets, pipeline stages, and charts.

---

# Slide 20: Q&A

### Thank You!

* **GitHub Repository**: [github.com/bhargava562/rythm](https://github.com/bhargava562/rythm)
* **API Documentation**: `/docs` (Interactive Swagger UI)
