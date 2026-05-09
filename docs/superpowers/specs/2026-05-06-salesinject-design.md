# SalesInject Production‑Ready Design (2026‑05‑06)

## Overview
We will deliver a **Telegram‑bot‑first** production system that registers user and brand profiles, supports multi‑session conversations, and plugs in open‑source AI agents for intent classification, recommendation, and content generation. The architecture follows a **hybrid REST + Celery** communication pattern that aligns with the existing FastAPI + Celery + Redis stack.

---

## 1. Service Layout
| Service | Responsibility | Tech |
|--------|----------------|------|
| **Telegram Bot** | Handles Telegram webhook, user‑brand onboarding, session state. | FastAPI (Python‑telegram‑bot) |
| **Profile Service** | CRUD for `users`, `influencer_profile`, `brand_profile`, `sessions`. Soft‑delete support. | FastAPI + SQLAlchemy (PostgreSQL) |
| **AI Agent Hub** | Pluggable agents for intent, recommendation, content generation. Exposes generic HTTP API. | FastAPI + Celery workers (GPU/CPU) |
| **Redis** | Pub/Sub for async result delivery, session cache. | redis‑server |
| **PostgreSQL** | Persistent data (profiles, audit, AI task results). | PostgreSQL 15 |

---

## 2. Communication Patterns
### 2.1 REST (fast calls)
* Bot → Profile Service via `POST /profiles`, `GET /profiles/{id}` etc.
* Authentication: **X‑API‑Key** header (shared secret configured in `settings.json`).
* Payloads are JSON; responses include standard `200/201` codes.

### 2.2 Celery Queue (heavy AI)
* Bot enqueues a task (`intent_classification`, `recommend`, `generate`) to **ai_queue**.
* Workers consume, run the selected model, store result in **ai_task_results** (TTL 24 h) and publish to Redis channel `ai:result:{task_id}`.
* Bot subscribes to `bot:updates` and replies to the user when the result is ready.

---

## 3. Database Schema (PostgreSQL)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at TIMESTAMP WITH TIME ZONE   -- soft delete for GDPR
);

CREATE TABLE influencer_profile (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    niche TEXT,
    location TEXT,
    preferred_formats TEXT[]
);

CREATE TABLE brand_profile (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    target_audience TEXT,
    campaign_goals TEXT[]
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE ai_task_results (
    task_id UUID PRIMARY KEY,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    -- TTL handled by a periodic cleanup job
);
```

---

## 4. AI Agent Hub API
```
POST /ai/intent        {"text": "...", "user_id": 123, "async": true}
POST /ai/recommend     {"brand_id": 45, "influencer_id": 12, "async": true}
POST /ai/generate      {"prompt": "...", "model": "openrouter|local|paperclip", "async": true}
GET  /ai/models        -> [{"name": "llama-7b", "type": "local", "capabilities": ["generate"]}, ...]
GET  /ai/result/{task_id}   -> {"status": "ready", "result": {...}}
```
*All POST endpoints accept an optional `async` flag. If `false` (default), the call is processed synchronously (used only for quick tests).
*Results are persisted in `ai_task_results` and also published on Redis channel `ai:result:{task_id}`.

---

## 5. Security & Compliance
* **API‑Key auth** – Bot includes `X‑API‑Key: <secret>` on every internal REST request.
* **Soft delete** – `deleted_at` enables GDPR‑compliant user removal while preserving FK integrity.
* **Result TTL** – AI results auto‑expire after 24 h; a nightly Celery task removes stale rows.

---

## 6. Deployment (Docker‑Compose)
```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
  redis:
    image: redis:7
  bot:
    build: ./backend/app/bot
    env_file: .env
    depends_on: [db, redis]
    command: uvicorn bot:app --host 0.0.0.0 --port 8001
  profile:
    build: ./backend/app/api
    env_file: .env
    depends_on: [db, redis]
    command: uvicorn api:app --host 0.0.0.0 --port 8000
  ai_hub:
    build: ./backend/app/ai_hub
    env_file: .env
    depends_on: [db, redis]
    command: celery -A ai_hub worker -Q ai_queue -n ai@%h
```
*The existing `docker-compose.yml` can be extended with the `bot` and `ai_hub` services.

---

## 7. Testing Strategy
1. **Unit tests** for each FastAPI router (pytest + httpx).  
2. **Integration tests** using a temporary PostgreSQL and Redis (docker‑compose up -d test).  
3. **AI‑hub mock agents** for CI – replace heavy models with deterministic stubs.  
4. **End‑to‑end**: simulate a Telegram webhook request (via `telegram-bot-test` library) and assert the async flow (result channel → bot reply).

---

## 8. Next Steps
1. Commit this spec file (`docs/superpowers/specs/2026-05-06-salesinject-design.md`).
2. Run a **spec self‑review** (placeholders, contradictions, scope).  
3. Ask you to review the spec.  
4. Upon approval, invoke the **writing‑plans** skill to generate an implementation plan.

---

*Spec prepared for review.*