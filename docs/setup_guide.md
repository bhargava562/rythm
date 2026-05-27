# Development Environment Setup Guide: Rythm

This guide outlines the steps required to configure and run the Rythm backend application locally on your system.

---

## 📋 Prerequisites

Before proceeding, ensure you have the following software installed:
* **Python**: Version 3.12 or 3.14 (Ensure it is added to your system `PATH`)
* **PostgreSQL**: Version 15+ (Running locally or via Docker)
* **Docker & Docker Compose**: (Optional, for containerized execution)
* **Git**: For version control management

---

## 🛠️ Step-by-Step Local Installation

### 1. Initialize Virtual Environment
Navigate to the backend directory and create a python virtual environment to isolate project dependencies:

```powershell
# Windows PowerShell
cd D:/rythm/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

```bash
# macOS/Linux Terminal
cd /path/to/rythm/backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Package Dependencies
Install all required libraries including FastAPI, database utilities, security packages, and document builders:

```bash
pip install -r requirements.txt
```

### 3. Establish Local Environment Settings
Duplicate the template configuration file and configure your local settings:

```powershell
# Windows
copy .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

Open `.env` in your editor and configure the parameters:
* Set `DATABASE_URL` to point to your active PostgreSQL instance.
* Insert your `GEMINI_API_KEY` or `OPENAI_API_KEY` to enable AI parsing and recommendation utilities.
* Update `JWT_SECRET` with a secure cryptographic string.

### 4. Setup PostgreSQL Database
Ensure a PostgreSQL database named `rythm` exists. You can initialize it using `psql` or an admin GUI (like pgAdmin or DBeaver):

```sql
CREATE DATABASE rythm;
```

Alternatively, you can run PostgreSQL in a Docker container:
```bash
docker run --name rythm-postgres -e POSTGRES_DB=rythm -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16-alpine
```

### 5. Execute Core Database Migrations
Once the database is running, initialize schemas by running our FastAPI setup process (or Alembic migrations in production):
```bash
# Skeletons create tables automatically on start during development
```

### 6. Run the Uvicorn ASGI Server
Start the development server with live reload enabled. The application will monitor file changes and auto-restart:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

* **Interactive API documentation**: Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger UI) or [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) (ReDoc) to browse endpoints and test routes.

---

## 🧪 Testing

To run automated unit and integration tests using pytest:

```bash
# Execute tests in the backend folder
pytest
```

---

## 🐳 Docker Deployment (Alternate Method)

To build and run the entire multi-container service (FastAPI + PostgreSQL DB) automatically:

1. Compile the containers:
   ```bash
   docker-compose up --build
   ```
2. The server will run at [http://localhost:8000](http://localhost:8000).
3. The database port `5432` will be forwarded for external inspection.
