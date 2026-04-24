# 🚀 SalesInject: Project Tracker

This file serves as the central hub for tracking the development progress of the SalesInject project. Update this file whenever a major milestone is hit, so any developer (or AI) picking up the project knows exactly where we stopped and what comes next.

---

## ✅ Completed Phases

### 1. Foundation
- [x] Initial Repo Scaffold (`/frontend` and `/backend`).
- [x] **Frontend:** React + Vite + TailwindCSS (`@tailwindcss/postcss`) configured.
- [x] **Frontend:** Telegram Web App SDK (`@twa-dev/sdk`) integrated.
- [x] **Frontend UI Shells:** Built the `Dashboard`, `Tasks`, `Agents`, `Profile`, and the core `MapPage` (DeckGL).
- [x] **Backend:** FastAPI foundation created (`app/main.py`), including the base database models for Users, Agents, Tasks, Memories, and PaperclipItems (`app/models.py`).
- [x] **Documentation:** Created the `project_business_and_architecture_guide.md` (Blueprint).

### 2. Backend Infrastructure
- [x] uvicorn / requirements.txt stabilized
- [x] PostgreSQL + pgvector + Redis via Docker
- [x] JWT auth + RLS middleware
- [x] Celery + Redis task queue
- [x] run_scout_mission orchestrator (Exa + Agent Zero stub + Paperclip)
- [x] PaperclipItem model + Alembic migration
- [x] Telegram Bot (aiogram, webhook + polling)

### 3. Alpha MVP
- [x] Dashboard/Map wired to real FastAPI data
- [x] Telegram initData JWT auth working
- [x] SCOUT button → Celery → pollUntilDone → map update

### 4. VPS Deployment — Hostinger KVM 1
- [x] `backend/Dockerfile` — multi-stage Python build (non-root, gunicorn)
- [x] `frontend/Dockerfile` — Node build + nginx static serve (SPA fallback)
- [x] `nginx/nginx.conf` — reverse proxy: `/api/*` → backend, `/*` → frontend
- [x] `docker-compose.prod.yml` — production compose (2 gunicorn workers, celery concurrency 2, memory limits, migrate init container)
- [x] `backend/.dockerignore` + `frontend/.dockerignore`
- [x] `.env.example` updated (OPENCLAW_URL external VPS, USE_WEBHOOK, DEBUG)
- [x] `deploy.sh` — one-command deploy script with health check polling
- [x] `gunicorn` added to `requirements.txt`
- [x] Debug `/api/v1/debug/rls` endpoint guarded behind `if settings.DEBUG`
- [ ] **Pending:** Get domain → uncomment HTTPS block in `nginx/nginx.conf` → run Certbot
- [ ] **Pending:** Set Telegram webhook URL to `http://VPS_IP/webhook/telegram` (or domain when ready)

---

## 🚧 Still genuinely in progress

- [ ] Paperclip sidebar rendering in frontend
- [ ] Agent Zero stub → real LLM swap
- [ ] scout_reports → map pins fully rendering

---

## 🎯 Next Steps (The Backlog)

- [ ] Rank Decay Celery Beat task
- [ ] Spy Satellite (competitor targeting in scout)
- [ ] AI General natural language endpoint

---

## 📝 Developer Notes
*When resuming work, always check the **Currently In Progress** section. If you encounter bugs (like the Vite UI failing to load or Python modules missing), add them to the "In Progress" section and resolve them before starting a new feature.*
