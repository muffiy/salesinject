---
description: 
---

# 🧠 Master Build Prompt: SalesInject – AI Influencer War Game (Step‑by‑Step)

You are an expert full‑stack AI engineer. Your task is to **build the complete SalesInject application** from scratch, following the instructions below. Deliver a fully functional, production‑ready codebase that can be deployed on a VPS. Follow the steps **sequentially**. Each step includes specific files to create and modify. Verify each step before moving to the next.

---

## 📌 Step 0 – Project Overview

**App name:** SalesInject (also called Genesis Market)  
**One‑liner:** *Turn everyday content into viral campaigns, connect influencers with location‑based offers, and gamify market share on a living 3D map – all inside Telegram.*

**Core features:**
- Telegram Mini App with 3D/2D map (DeckGL + MapLibre)
- AI Scout: discover influencers by niche/location (Exa.ai or mock)
- AI Content Generator: produce hooks, scripts, captions (OpenRouter)
- Location‑based offers: brands pin discounts/bounties on map; influencers claim and complete tasks
- Commission tracking via unique promo codes and webhooks
- Gamification: leaderboards, streaks, growing bubbles
- No external agent orchestrator (OpenClaw removed) – use custom `@tool` decorator + Celery

**Tech stack (strict):**
- Frontend: React + TypeScript + Vite + Tailwind CSS 4 + DeckGL + MapLibre GL
- Backend: FastAPI + SQLAlchemy + Alembic + PostgreSQL 15 (pgvector) + Redis + Celery
- AI: OpenRouter API (any model), Exa.ai API (optional)
- Deployment: Docker Compose + Nginx + GitHub Actions (optional)
- Telegram Bot: aiogram 3.x (polling or webhook)

---

## 🗂️ Step 1 – Project Initialization

Create the directory structure and initial configuration files.

### 1.1 Root files

Create the following files in the project root `/salesinject`:

- `README.md` – project description, setup instructions, deployment guide.
- `.gitignore` – ignore `node_modules`, `.env`, `__pycache__`, `*.pyc`, `dist`, `.vscode`, etc.
- `docker-compose.prod.yml` – production compose (will fill later).
- `deploy.sh` – one‑command deploy script (will write later).

### 1.2 Backend initialization

Inside `/salesinject/backend`:

- `requirements.txt` – list all Python dependencies:
  ```
  fastapi==0.115.0
  uvicorn[standard]==0.30.0
  gunicorn==22.0.0
  sqlalchemy==2.0.35
  alembic==1.13.0
  psycopg2-binary==2.9.9
  redis==5.0.1
  celery==5.3.6
  python-jose[cryptography]==3.3.0
  python-dotenv==1.0.0
  aiogram==3.3.0
  httpx==0.27.0
  pydantic==2.7.0
  pgvector==0.3.0
  numpy==1.26.0
  ```
- `Dockerfile` – multi‑stage build for production.
- `.env.example` – template for environment variables:
  ```
  DEBUG=False
  SECRET_KEY=CHANGE_ME
  DATABASE_URL=postgresql://salesinject:password@db:5432/salesinject
  REDIS_URL=redis://redis:6379/0
  BOT_TOKEN=
  OPENROUTER_API_KEY=
  EXA_API_KEY=
  MINI_APP_URL=http://localhost
  USE_WEBHOOK=False
  WEBHOOK_URL=
  ```

### 1.3 Frontend initialization

Inside `/salesinject/frontend`:

- `package.json` – React + Vite + DeckGL + MapLibre + Tailwind + Telegram SDK.
- `vite.config.ts` – configure proxy for API, host, etc.
- `tailwind.config.js` – include all Gen‑Z design tokens.
- `Dockerfile` – multi‑stage (build + nginx).

---

## 🔧 Step 2 – Backend Core (FastAPI + DB)

Create the fundamental backend structure.

### 2.1 Entry point

`backend/app/main.py`:
- Create FastAPI app.
- Add CORS middleware.
- Include health endpoint `/health`.
- Include router from `api/v1/router.py` with prefix `/api/v1`.
- Startup event: start Telegram bot polling (if `USE_WEBHOOK=False`).
- Shutdown event: close DB connections, Redis.

### 2.2 Configuration

`backend/app/core/config.py`:
- Load environment variables via `pydantic_settings`.
- Define `Settings` class with `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `BOT_TOKEN`, etc.

### 2.3 Database

`backend/app/core/database.py`:
- SQLAlchemy engine, session local, declarative base.

`backend/app/models/models.py`:
- Define models: `User`, `AgentSession`, `AgentMemory`, `PaperclipItem`, `Job`, `Offer`, `OfferClaim`, `OfferPerformance`, `PayoutTransaction`.
- Use `UUID` as primary keys, `pgvector` for `AgentMemory.embedding`.
- Relationships as per earlier design.

`backend/alembic/` – initialize with `alembic init` and generate initial migration.

### 2.4 Authentication

`backend/app/core/security.py`:
- `create_jwt_token`, `decode_jwt_token`.
- `verify_telegram_init_data` – validate Telegram WebApp initData.

`backend/app/api/v1/endpoints/auth.py`:
- `POST /auth/telegram` – accepts `initData`, returns JWT.

### 2.5 API Router

`backend/app/api/v1/router.py`:
- Include all endpoint sub‑routers (auth, users, agents, tasks, scout, offers, telegram webhook).

### 2.6 Telegram Bot

`backend/app/bot/dispatcher.py`:
- Create `aiogram` `Dispatcher` and `Router`.
- Register commands: `/start`, `/scout`, `/generate`, `/offers near`, `/claim`, `/complete`.
- Implement handlers that call Celery tasks or directly call services.

`backend/app/bot/__init__.py` – initialise bot and dispatcher.

### 2.7 Celery Setup

`backend/app/worker.py`:
- Create Celery app with `REDIS_URL` as broker and backend.
- Import tasks from `tasks.py`.

`backend/app/tasks.py`:
- Define `run_scout_mission(niche, location, user_id)` – calls `scout_influencers`, `analyze_and_rank`, saves results.
- Define `generate_ad_idea(user_id, prompt)` – calls OpenRouter API or local RAG.
- Add `expire_offers`, `send_offer_alerts` etc.

### 2.8 Services & Tools

`backend/app/services/exa_service.py`:
- `find_influencers(niche, location)` – Exa API call (or mock if no key).

`backend/app/services/openrouter_service.py`:
- `call_llm(prompt, system)` – calls OpenRouter API.

`backend/app/services/embedding_service.py`:
- Generate embeddings via sentence‑transformers or OpenRouter.

`backend/app/services/paperclip_service.py`:
- CRUD for `PaperclipItem`.

`backend/app/tools/paperclip_tools.py`:
- Implement `@tool` decorator.
- Define `scout_influencers`, `analyze_and_rank`, `save_scout_results`.
- Define `generate_ad_idea` using RAG (query `AgentMemory` and `PaperclipItem`).

---

## 🎨 Step 3 – Frontend (React + Map + Telegram)

### 3.1 Base App

`frontend/src/main.tsx` – mount React app.
`frontend/src/App.tsx` – routing:
- `/` → `Landing`
- `/app` → `AppShell` (protected by `TelegramGuard`)
- `/onboarding` → `Onboarding`

### 3.2 Auth Context

`frontend/src/context/AuthContext.tsx`:
- Store JWT, refresh logic, axios interceptor.
- Fetch user from Telegram initData.

### 3.3 API Client

`frontend/src/services/api.ts`:
- Axios instance with base URL from `VITE_API_BASE_URL`.
- Endpoints: `auth`, `scout`, `tasks`, `offers`, `paperclips`.

### 3.4 Pages

`frontend/src/pages/Landing.tsx` – splash screen, call to action to open bot.
`frontend/src/pages/MapPage.tsx` – main map view:
- Use `GlobalMap` component that wraps `DeckGLMap`.
- Fetch map data (scout results, offers) from API.
- Filter bar, bottom sheet for actions.

`frontend/src/pages/Dashboard.tsx` – stats, hot tasks.
`frontend/src/pages/Tasks.tsx` – list of scout missions / offers claimed.
`frontend/src/pages/Agents.tsx` – marketplace of AI agents (mock).
`frontend/src/pages/Profile.tsx` – influencer profile, earnings, rank.
`frontend/src/pages/PaperclipSidebar.tsx` – feed of generated content and scout intel.

### 3.5 Map Component

`frontend/src/components/DeckGLMap.tsx`:
- DeckGL with ScatterplotLayer and TextLayer.
- MapLibre GL with dark tiles.
- Accept `data` prop (array of points with lat, lon, type, name, etc.).
- Click handler – opens `GenZBottomSheet` or `MapProfileCard`.

`frontend/src/components/GenZOverlay.tsx`:
- Floating filter bar, action buttons, bottom sheet for offer details.

`frontend/src/components/UI.tsx`:
- Reusable buttons, cards, loaders, errors.

### 3.6 Tailwind & Design System

`frontend/src/index.css` – include all CSS variables, glassmorphism, glitch effects, responsive utilities. Use the provided war‑game theme (neon colors, gradients, monospace fonts).

---

## 🏗️ Step 4 – Offers System (Differentiator)

### 4.1 Database tables (already in models)

Ensure `Offers`, `OfferClaim`, `OfferPerformance`, `PayoutTransaction` are created via migration.

### 4.2 API Endpoints

`backend/app/api/v1/endpoints/offers.py`:
- `POST /offers` – brand creates offer (requires JWT, role=brand).
- `GET /offers/nearby` – returns offers near lat/lon within radius.
- `POST /offers/{id}/claim` – influencer claims an offer.
- `POST /offers/{id}/complete` – upload proof, trigger review/payout.
- `POST /webhooks/sale` – receive sale event from brand’s POS/Shopify (webhook).

### 4.3 Frontend Integration

- Add “Offers” layer toggle in `GenZOverlay`.
- Render offer bubbles as diamond shapes with gold glow.
- On click, show offer details (discount, bounty, distance) and “Claim” button.
- After claim, show “Navigate” button (opens Google Maps) and “Complete” button (to upload video).

### 4.4 Celery Tasks

- `offer_expiry` – runs every 15 min, expires unclaimed offers.
- `send_offer_notifications` – pushes Telegram alerts to influencers in zone.
- `process_payout` – after approval, sends money using Stripe Connect.

---

## 🤖 Step 5 – AI Agent System (No OpenClaw)

### 5.1 `@tool` decorator

`backend/app/tools/paperclip_tools.py`:
```python
_TOOL_REGISTRY = {}
def tool(func):
    func.is_tool = True
    func.tool_name = func.__name__
    func.tool_description = func.__doc__
    _TOOL_REGISTRY[func.__name__] = func
    return func
```

### 5.2 Implement tools

- `@tool def scout_influencers(niche, location)` – calls `exa_service.find_influencers`.
- `@tool def analyze_and_rank(influencers, niche)` – uses OpenRouter to rank them.
- `@tool def save_scout_results(user_id, task_id, influencers, report, db)` – stores in `paperclip_items`.
- `@tool def generate_ad_idea(user_id, prompt)` – RAG: fetch memories + examples, call LLM, store result.

### 5.3 Celery task integration

In `run_scout_mission`, call the tools sequentially, committing to DB only at the end.

---

## 🐳 Step 6 – Docker Compose & Deployment

### 6.1 `docker-compose.prod.yml`

Define services:
- `db` – image: `pgvector/pgvector:pg15`, environment, volumes, healthcheck.
- `redis` – image: `redis:7-alpine`.
- `backend` – build context `./backend`, environment, depends on db+redis, command: gunicorn.
- `celery-worker` – same image as backend, command: celery worker.
- `celery-beat` – same image, command: celery beat.
- `frontend` – build context `./frontend`, serve static via nginx.
- `nginx` – public reverse proxy, serves both API and frontend.

Set resource limits (2 workers, 500M memory for 2GB VPS).

### 6.2 `deploy.sh`

Script that:
- Checks for `.env` in backend/.
- Runs `docker compose -f docker-compose.prod.yml down`.
- Pulls latest code (git pull).
- Builds images (`docker compose build`).
- Starts services (`docker compose up -d`).
- Waits for health endpoint.

### 6.3 Nginx config

`nginx/nginx.conf`:
- Proxy `/api/` to `backend:8000`.
- Serve frontend static files from `/usr/share/nginx/html`.
- Return index.html for SPA routing.

---

## ✅ Step 7 – Verification & Documentation

Create `PRODUCTION_CHECKLIST.md` listing:
- Set environment variables in `backend/.env` (BOT_TOKEN, DB password, API keys).
- Run `alembic upgrade head` (manually or via init container).
- Set Telegram webhook if `USE_WEBHOOK=True`.
- Point domain and run Certbot.
- Enable UFW, fail2ban, backups.

Create `TESTING.md` with sample commands:
```bash
curl -X POST http://localhost/api/v1/auth/telegram -d '{"initData":"..."}'
curl http://localhost/api/v1/health/
```

---

## 📦 Step 8 – Deliverables

Produce the entire codebase as a zip or a set of files. Include:

- All backend Python files.
- All frontend React/TypeScript files.
- All configuration (`.env.example`, `docker-compose.prod.yml`, `nginx.conf`, `deploy.sh`).
- `README.md` with quick start and deployment instructions.
- `PRODUCTION_CHECKLIST.md`.

Do not skip any file.** The app must run after follow