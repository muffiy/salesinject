# SalesInject Project Memories

## Core Directives
- **tunisian_founder_business_plan**: Strategic focus on the Tunisian digital ecosystem and MENA expansion. Building an AI-powered Telegram Mini App platform connecting influencers with brands through gamified 3D visualization.

## Conversation Log

### [2026-04-25] — VPS Deployment
- **Target:** Hostinger KVM 1 (2GB RAM, 1 vCPU Ubuntu 22.04)
- **OpenClaw:** Running on a separate VPS — removed from local compose, configured via `OPENCLAW_URL` env var
- **Frontend:** Served from same nginx on VPS (not Vercel/Netlify)
- **No domain yet** — nginx serves HTTP on port 80; HTTPS block pre-written and commented out for when domain is added
- **Files created:**
  - `backend/Dockerfile` — multi-stage Python build, non-root user
  - `frontend/Dockerfile` — Node build + nginx static serve with SPA fallback
  - `nginx/nginx.conf` — reverse proxy (`/api/*` → backend, `/*` → frontend, `/webhook/telegram` → backend)
  - `docker-compose.prod.yml` — gunicorn (2 workers), celery concurrency 2, migrate init container, memory limits tuned for 2GB RAM
  - `backend/.dockerignore` + `frontend/.dockerignore`
  - `.env.example` updated (OPENCLAW_URL, USE_WEBHOOK, DEBUG vars)
  - `deploy.sh` — one-command deploy: pulls → builds → starts → health-polls `/health`
  - `gunicorn` added to `requirements.txt`
- **Production hardening:** Debug RLS endpoint guarded behind `if settings.DEBUG`; no host port exposed for backend (only nginx public); Postgres credentials moved to env vars
- **To activate HTTPS when domain is ready:** Uncomment HTTPS block in `nginx/nginx.conf`, run `certbot --nginx -d yourdomain.com`
- **Source Control:** Initialized Git, created `.gitignore`, and pushed code to GitHub (`muffiy/salesinject`).
- **AI Tooling:** Configured Anthropic Claude Code CLI to route through OpenRouter (`openrouter/free`) by formatting `~/.claude/settings.json` properly with the user's API key.

### [2026-04-24]
- **Backend Intelligence Pipeline — Scout Mission**: Completed the full tool-use layer for Scout missions.
  - Created `backend/app/tools/paperclip_tools.py` with 5 `@tool`-decorated functions: `scout_influencers`, `analyze_and_rank`, `save_scout_results`, `save_scout_report`, `notify_telegram`.
  - Created `backend/app/services/paperclip_agent.py` — `run_scout_mission()` orchestrator that chains all 5 tools sequentially with one shared SQLAlchemy session and a single `db.commit()` at the end.
  - Created `backend/app/services/agent_zero_service.py` — deterministic stub (sorted by followers, `# TODO: replace with LLM call`).
  - Created `backend/app/services/exa_service.py` — Exa neural search with mock fallback when API key is missing.
  - Created `backend/app/services/paperclip_service.py` — writes `mission_log`, `pinned_profile`, `ad_copy` rows, accepts `db` session from caller.
  - Updated `tasks.py` `run_agent_task` — replaced 50-line inline simulation block with a clean `run_scout_mission()` call.
  - Added `PaperclipItem` model to `models.py` (JSONB `content`, `item_type` enum field).
  - Added `exa_py` to `requirements.txt`.
  - Added `backend/app/api/v1/endpoints/health.py` with `/health` DB connectivity check.
  - Hardened `routers/agent.py` with `db.flush()` before Celery enqueue and `db.commit()` only after — safe credit deduction pattern.
  - `notify_telegram` uses `asyncio.run()` to call the async `telegram_service.send_message()` synchronously from Celery without event loop conflicts. Fails silently.
- **Model in use**: Claude Sonnet 4.6 (Thinking mode).

### [2026-04-23]
- **fix the mcp error**: Troubleshooting GitHub MCP server Docker connection issues.
- **what task we're in this project**: Realigning with current project status.

### [2026-04-21]
- **i need to set the telegram access token**: Configuring Telegram bots for the platform.

### [2026-04-20]
- **Enhancing Backend System Architecture**: High-level architectural assessment for production deployment and multi-user subscription management on VPS.

### [2026-04-16]
- **Implementing Paperclip Sidebar UI**: Finalizing frontend implementation of the Paperclip sidebar to render data in the UI.

### [2026-04-14]
- **i want a full review for this project**: Comprehensive project review.

### [2026-04-09]
- **Implementing SalesInject Scout Pipeline**: Stabilizing development tracking and finalizing the Paperclip sidebar rendering.

### [2026-04-04]
- **Increasing Restaurant Sales Revenue**: Brainstorming strategies to leverage existing infrastructure for restaurant sales.

### [2026-04-01]
- **Fixing DeckGL Map Import**: Stabilizing the backend intelligence pipeline (Scout mission, Exa, Agent Zero, Paperclip) and DeckGL frontend map imports.

### [2026-03-29]
- **Project Understanding And UI Analysis**: Generating context for AI assistants to understand the current SalesInject project structure and UI components.