# SalesInject (Genesis Market)

*Turn everyday content into viral campaigns, connect influencers with location-based offers, and gamify market share on a living 3D map – all inside Telegram.*

## Features
- **3D War Game Map**: Visualize active influencer tasks, brand offers, and claimed territories using DeckGL and MapLibre GL.
- **AI Scout**: Automated matching between local influencers and location-based brand offers using Exa.ai or mock data.
- **Telegram Mini App**: Deep integration for a seamless mobile experience inside Telegram.
- **AI Content Generator**: Generate ad hooks, scripts, and video captions via OpenRouter APIs.
- **Offers & Bounties**: Brands pin discounts/tasks, influencers claim them and upload proof.

## Tech Stack
- **Frontend**: React + TypeScript + Vite + Tailwind CSS 4 + DeckGL + MapLibre GL
- **Backend**: FastAPI + SQLAlchemy + Alembic + PostgreSQL 15 (pgvector) + Redis + Celery
- **AI Orchestration**: Custom `@tool` agent pattern

## Local Development
1. **Backend**:
    - `cd backend`
    - `cp .env.example .env` (fill in variables)
    - `pip install -r requirements.txt`
    - `uvicorn app.main:app --reload`
2. **Frontend**:
    - `cd frontend`
    - `npm install`
    - `npm run dev`

## Deployment
Use the included `deploy.sh` for one-command deployment using Docker Compose:
```bash
./deploy.sh
```
See `PRODUCTION_CHECKLIST.md` for full deployment verification steps.
