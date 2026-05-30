# Production Deployment Guide: Rythm

This guide outlines instructions, configuration parameters, security checklists, and known architectural boundaries for deploying the Rythm platform into production environments.

---

## 🚀 Deployment Checklists

### 1. Hardening Environmental Variables
Ensure your production `.env` is securely loaded. **Never** reuse development values.
* **`DEBUG`**: Set to `false`. This disables Swagger debug traces and suppresses verbose DB execution logging.
* **`JWT_SECRET`**: Generate a cryptographically secure 64-character hexadecimal key:
  ```bash
  openssl rand -hex 32
  ```
* **`DATABASE_URL`**: Point to a production-grade managed PostgreSQL cluster (e.g. AWS RDS, GCP Cloud SQL, or DigitalOcean Managed DBs). Ensure the connection parameters use connection pooling (e.g. PgBouncer) if scaling to numerous instances.

### 2. HTTPS & Reverse Proxy Architecture
* **Nginx Configuration**: FastAPI should run behind a reverse proxy like Nginx or Traefik, which handles:
  * SSL/TLS certificate termination (via Let's Encrypt).
  * Request payload limits (limiting pastes size).
  * CORS security locks.
* **Gunicorn/Uvicorn**: In production, run Uvicorn wrapped with Gunicorn to manage multiple worker processes:
  ```bash
  gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
  ```

### 3. Containerized Deployment (Docker Compose)
To spin up the service stack in production:
```bash
# Build and run containers in detached daemon mode
docker-compose -f docker-compose.yml up -d --build
```
Verify container status:
```bash
docker-compose ps
```

---

## 🛡️ OWASP Top 10 Security Mitigations

1. **Broken Access Control (A01:2021)**: Mitigated by UUIDv4 resource boundaries. Endpoints like `/api/v1/applications/{uuid}` prevent enumeration. Route calls are locked behind a role-based check (`check_role`).
2. **Cryptographic Failures (A02:2021)**: Sensitive client credentials (passwords) are hashed on the API server via `bcrypt` (using `passlib`) before hitting the storage disk. JWT tokens use modern HMAC-SHA256 signatures.
3. **Injection (A03:2021)**: Mitigated using SQLAlchemy ORM's parameterized queries, which prevents SQL Injection by design.
4. **Security Misconfiguration (A05:2021)**: Strict CORS headers are enabled, and `DEBUG` options hide traceback payloads from client-facing REST responses.
5. **Vulnerable Components (A06:2021)**: All dependency requirements in `requirements.txt` are locked to explicit versions to prevent supply-chain updates issues.

---

## ⚠️ Known Limitations & Workarounds

### 1. In-Memory Sliding-Window Rate Limiter
* **Limitation**: The current rate-limiter utilizes an in-memory Python dictionary (`request_history`). This works perfectly for single-node deployments. However, in a distributed/scaled multi-worker environment (e.g. behind a Load Balancer or in Kubernetes), the rate limits are isolated per instance.
* **Workaround**: For multi-node scaling, replace the in-memory dictionary in `app/main.py` with the shared Redis instance (`redis-py` client) to maintain cluster-wide sliding windows.

### 2. Background Task Volatility
* **Limitation**: FastAPI's built-in `BackgroundTasks` executes tasks (like sending reset emails) on the local event loop. If the container process restarts during execution, pending tasks are lost.
* **Workaround**: For highly critical asynchronous workloads, integrate a persistent message queue like **Celery** or **ARQ** backed by our Redis service container.

### 3. Automatic Schema Creation
* **Limitation**: During development, `Base.metadata.create_all` creates schemas automatically on startup.
* **Workaround**: For production systems, disable this automatic creation step and configure **Alembic** to manage structured migration playbooks.
