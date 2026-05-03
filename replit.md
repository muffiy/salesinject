# SalesInject — Genesis Market (Telegram Mini App)

## Overview
AI-powered influencer marketing platform built as a Telegram Mini App. Creators discover and claim geo-located brand missions on a DeckGL map, earn rewards, and level up via an Agent OS system.

## Architecture
- **Frontend**: React + Vite (TypeScript), runs on port 5000
- **Backend**: FastAPI (Python), runs on port 8000
- **Database**: PostgreSQL (Replit-managed, via `DATABASE_URL`)
- **Cache/Queue**: Redis (optional — falls back to no-op stub if unavailable)
- **Bot**: Telegram Bot via aiogram (optional — gracefully disabled if `BOT_TOKEN` is invalid)

## Workflows
| Workflow | Command | Port |
|---|---|---|
| `Start application` | `cd frontend && npm run dev` | 5000 |
| `Backend API` | `cd backend && uvicorn app.main:app --host localhost --port 8000` | 8000 |

## Project Structure
```
frontend/       React + Vite Mini App
  src/
    components/ UI components (Map, LiveTicker, etc.)
    pages/      Route-based pages
    services/   API clients (api.ts, osApi.ts)

backend/
  app/
    api/v1/
      endpoints/  REST endpoints (agents, auth, earnings, missions, offers, scout, tasks, users)
      ws/         WebSocket endpoints (live ticker, scout, stream, telemetry)
      router.py   Central API router
    agent_os/   Distributed agent pipeline (budget, concurrency, cost_engine, tracer)
    bot/        Telegram bot dispatcher (aiogram)
    core/       Config, database, redis_client
    models/     SQLAlchemy ORM models
    services/   Business logic services
    tasks.py    Celery task definitions
```

## Key API Endpoints (prefix: /api/v1)
| Path | Description |
|---|---|
| `GET /health/` | Health check |
| `POST /auth/telegram` | Telegram WebApp auth |
| `GET /users/me` | Current user profile |
| `GET /users/me/profile` | Rich profile for Agent OS |
| `GET /users/leaderboard` | Global leaderboard |
| `GET /earnings/` | Earnings summary |
| `GET /missions/history` | User mission history |
| `GET /offers/` | Available offers |
| `GET /offers/nearby` | Location-based offers |
| `GET /scout/latest` | Latest scout report |
| `POST /scout/mission/v2` | Run an Agent OS scout mission |
| `GET /agents/` | User's AI agents |
| `GET /tasks/` | Available tasks |
| `WS /ws/live-ticker` | Live event stream |

## Environment Variables
| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection (auto-managed by Replit) |
| `SECRET_KEY` | JWT signing secret |
| `BOT_TOKEN` | Telegram bot token (set to "dummy" to disable bot) |
| `REDIS_URL` | Redis URL (defaults to localhost:6379, optional) |
| `USE_WEBHOOK` | Use webhook instead of polling (default: false) |
| `MINI_APP_URL` | Telegram Mini App URL |
| `VITE_API_BASE_URL` | Frontend API base URL (default: /api/v1) |
| `PLATFORM_COMMISSION_RATE` | Commission rate for payouts |

## Database
- All tables created via SQLAlchemy `Base.metadata.create_all()`
- Alembic migrations in `backend/alembic/`
- Key models: User, Agent, Task, UserTask, Offer, OfferClaim, ScoutReport, PayoutTransaction, Leaderboard, MissionShare

## Notable Fixes Applied During Import
- Redis client made optional with no-op fallback stub
- Telegram bot gracefully disabled when BOT_TOKEN is invalid
- Missing `Map.tsx` component created (DeckGLMap wrapper)
- Duplicate model classes resolved in `models_agent_os.py`
- Event bus Kafka import made optional
- Added missing Celery tasks: `send_offer_alerts`, `process_payout`, `run_scout_mission`, `generate_ad_idea`
- Added missing API endpoints: `GET /missions/history`, `GET /earnings/`, `GET /users/me/profile`
