# 🔗 Bolna Custom Headers for Webhooks

<div align="center">

![Bolna Webhook Dashboard](https://github.com/user-attachments/assets/f1eb88e4-c637-46ed-aaf0-7e3a42980e85)

**A production-ready webhook receiver for Bolna's Analytics tab custom headers feature.**
Send `Authorization`, `X-API-Key`, and `X-Tenant-ID` headers alongside execution-data webhooks — no proxy needed.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat&logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://docker.com)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Bolna Analytics Tab Setup](#bolna-analytics-tab-setup)
- [Dashboard](#dashboard)
- [Presentation](#presentation)

---

## 🎯 Overview

Bolna natively supports custom HTTP headers on the Analytics tab webhook (shipped **May 5, 2026**). This project builds the **receiving end** — a FastAPI backend that:

- ✅ Accepts Bolna's enriched webhook POSTs
- ✅ Verifies `Authorization`, `X-API-Key`, `X-Tenant-ID` headers
- ✅ Routes execution data by tenant
- ✅ Stores all execution logs in PostgreSQL
- ✅ Forwards to downstream services (CRM, etc.)
- ✅ React + Vite dashboard with live auto-refresh

> **No proxy needed** — Bolna injects the headers natively from the Analytics tab.

---

## 🏗 Architecture

```
Bolna Analytics Tab
    │
    │  POST /webhook/bolna
    │  Authorization: Bearer <token>
    │  X-API-Key: <key>
    │  X-Tenant-ID: tenant_a
    ▼
┌─────────────────────┐
│   FastAPI Receiver  │  ← verify headers immediately
│   /webhook/bolna    │  ← return 200 OK to Bolna
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐     ┌──────────────────┐
│   PostgreSQL DB     │     │   Redis Cache    │
│   execution_logs    │     │   TTL 5 min      │
│   tenants           │     │   Celery broker  │
└─────────────────────┘     └──────────────────┘
         │
         ▼
┌─────────────────────┐
│   Celery Worker     │  ← async downstream forwarding
│   Background Tasks  │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  React Dashboard    │  ← live execution log viewer
│  localhost:5173     │  ← auto-refresh every 10s
└─────────────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | FastAPI 0.115 | Async webhook receiver |
| **Task Queue** | Celery + Redis | Background processing |
| **Database** | PostgreSQL 15 | Execution logs + tenant config |
| **Cache** | Redis 7 | Header config cache (TTL 5min) |
| **HTTP Client** | httpx | Async downstream forwarding |
| **Validation** | Pydantic v2 | Request/response schemas |
| **Auth** | python-jose | Bearer token verification |
| **Frontend** | React + Vite | Execution log dashboard |
| **State** | TanStack Query | Auto-refresh server state |
| **Tunnel** | ngrok | Public URL for Bolna delivery |
| **Infra** | Docker Compose | PostgreSQL + Redis containers |

---

## 📁 Project Structure

```
Custom-Headers-Webhooks/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app factory
│   │   ├── config.py             # Pydantic settings
│   │   ├── db.py                 # SQLAlchemy async engine
│   │   ├── cache.py              # Redis client
│   │   ├── tasks.py              # Celery background tasks
│   │   ├── middleware.py         # IP whitelist + logging
│   │   ├── dependencies.py       # FastAPI Depends() providers
│   │   ├── exceptions.py         # Custom exceptions + handlers
│   │   ├── models/
│   │   │   ├── base.py           # SQLAlchemy Base + timestamps
│   │   │   ├── execution_log.py  # Execution log ORM
│   │   │   └── tenant.py         # Tenant config ORM
│   │   ├── schemas/
│   │   │   ├── webhook.py        # Bolna payload schemas
│   │   │   └── tenant.py         # Tenant CRUD schemas
│   │   ├── routes/
│   │   │   ├── webhook.py        # POST /webhook/bolna
│   │   │   ├── executions.py     # GET /executions
│   │   │   └── health.py         # GET /health
│   │   └── services/
│   │       ├── webhook_service.py  # Save + query execution logs
│   │       └── tenant_service.py   # Tenant CRUD + cache
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   ├── integration/
│   │   └── security/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── services/api.js
│       ├── hooks/useExecutions.js
│       ├── components/
│       │   ├── ExecutionTable.jsx
│       │   ├── ExecutionDetail.jsx
│       │   └── StatusBadge.jsx
│       ├── pages/Dashboard.jsx
│       ├── App.jsx
│       └── main.jsx
└── docker-compose.yml
```

---

## 🚀 Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker Desktop

### Backend

```bash
cd backend

# Create and activate venv
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy and fill env
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
```

### Docker (PostgreSQL + Redis)

```bash
docker run --name bolna-postgres \
  -e POSTGRES_USER=bolna \
  -e POSTGRES_PASSWORD=bolna123 \
  -e POSTGRES_DB=bolna_webhooks \
  -p 5432:5432 -d postgres:15

docker run --name bolna-redis \
  -p 6379:6379 -d redis:7-alpine
```

### Run Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

### Public URL (for Bolna)

```bash
ngrok http 8000
```

Copy the `https://` URL for the Bolna Analytics tab.

---

## ⚙️ Configuration

Copy `backend/.env.example` to `backend/.env` and fill in:

```env
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://bolna:bolna123@localhost:5432/bolna_webhooks
REDIS_URL=redis://localhost:6379/0
BOLNA_API_KEY=your-bolna-api-key
BOLNA_WEBHOOK_SECRET=your-webhook-secret
BOLNA_SENDER_IP=13.203.39.153
SECRET_KEY=your-secret-key
X_API_KEY=your-api-key-value
ALLOWED_TENANT_IDS=tenant_a
```

Generate strong secrets:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📡 API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/webhook/bolna` | Bolna headers | Main receiver — paste this URL in Bolna Analytics tab |
| `GET` | `/health` | None | Basic health check |
| `GET` | `/health/deep` | None | DB + Redis connectivity check |
| `GET` | `/executions` | Bearer + X-API-Key | Paginated execution logs |
| `GET` | `/executions/{id}` | Bearer + X-API-Key | Single execution log |
| `GET` | `/docs` | None | Swagger UI |

### Test webhook

```bash
curl -X POST "http://localhost:8000/webhook/bolna" \
  -H "Authorization: Bearer <SECRET_KEY>" \
  -H "X-API-Key: <X_API_KEY>" \
  -H "X-Tenant-ID: tenant_a" \
  -H "Content-Type: application/json" \
  -d '{"execution_id":"test_001","agent_id":"agent_001","status":"completed","duration":45.5}'
```

---

## 🔧 Bolna Analytics Tab Setup

1. Go to `app.bolna.ai` → Agent Setup → your agent → **Analytics tab**
2. Set **Webhook URL**:
   ```
   https://your-ngrok-url.ngrok-free.dev/webhook/bolna
   ```
3. Toggle **Add headers** → paste:
   ```json
   {
     "Authorization": "Bearer <your SECRET_KEY>",
     "X-API-Key": "<your X_API_KEY>",
     "X-Tenant-ID": "tenant_a"
   }
   ```
4. Click **Save agent**

Bolna will now inject these headers on every webhook POST automatically.

---

## 📊 Dashboard

![Bolna Webhook Dashboard](https://github.com/user-attachments/assets/f1eb88e4-c637-46ed-aaf0-7e3a42980e85)

The React dashboard at `http://localhost:5173` shows:

- **Total executions** counter
- **Filter** by Agent ID and Status
- **Execution table** with auth verification status
- **Detail modal** — click View on any row
- **Auto-refresh** every 10 seconds

---

## 📈 Evaluation Results

| Benchmark | Key Metric | Result |
|---|---|---|
| **Auth Speed** | Header verification | 11,057,054 checks/sec — 0.0001ms per check |
| **Cache Hit Rate** | Redis GET performance | 100% hit rate — 7,023 GETs/sec — 0.14ms per GET |
| **DB Write Speed** | PostgreSQL throughput | 316 writes/sec — 3.16ms per write |
| **Load Test** | 50 concurrent users | 27.84 req/s — 766 requests — 0% failures |
| **Security** | Auth scenarios | 6/6 checks passed |
| **p50 Latency** | Under load (local Windows) | 1,100ms |
| **p95 Latency** | Under load (local Windows) | 3,700ms |

> All benchmarks run locally on Windows with Docker (PostgreSQL + Redis).
> Production Linux deployment expected to show ~22x improvement on DB latency.

---

## 📑 Presentation

The full 10-slide presentation covers the complete project:

| Slide | Topic |
|---|---|
| 1 | Title — Custom Headers for Webhooks |
| 2 | Problem & Solution |
| 3 | Tech Stack Breakdown |
| 4 | System Architecture |
| 5 | File Structure |
| 6 | PostgreSQL Data Model |
| 7 | API Endpoints |
| 8 | Demo Results |
| 9 | Bolna Analytics Tab Setup |
| 10 | Project Complete |

---

## 👤 Author

**Aryan Pandey** — ML / AI Engineer

- GitHub: [@Aryan8912](https://github.com/Aryan8912)
- Kaggle: [aryanpandey8912](https://kaggle.com/aryanpandey8912)
