# SalesInject Production Readiness Design

## Overview
Production-hardening plan for SalesInject AI — an influencer marketing platform (FastAPI + React + Telegram Mini App). This plan addresses security, testability, and observability gaps identified by comparing the current codebase against the requirements in `implementationcore.guide`, `backend.review`, and `IMPLEMENTATION_PLAN.md`.

## Phase 1: Infrastructure Hardening

### 1.1 CORS Restriction
- **Current:** `allow_origins=["*"]` in `backend/app/main.py`
- **Target:** Read allowed origins from `ALLOWED_ORIGINS` env var (comma-separated). Default to `http://localhost:5173` for dev, require explicit config in production.
- **Files:** `backend/app/main.py`, `backend/app/core/config.py`

### 1.2 Rate Limiting
- **Current:** `slowapi` imported in `agent.py` only
- **Target:** Apply rate limiting to auth endpoints (POST /auth/*, 5/min) and Telegram webhook (10/min). Use Redis-backed limiter in production.
- **Files:** `backend/app/main.py`, `backend/app/api/v1/endpoints/auth.py`, `backend/app/api/v1/endpoints/telegram.py`

### 1.3 Structured Logging
- **Current:** No structured logging middleware
- **Target:** Add middleware that injects `trace_id` (uuid per request), `user_id` (from JWT if available), `mission_id` (from path/query if available). Use Python `structlog` or `logging` with JSON formatter.
- **Files:** New `backend/app/core/logging.py`, modify `backend/app/main.py`

### 1.4 Security Headers & Middleware
- **Current:** Nginx has X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- **Target:** Add API Key auth middleware for internal service-to-service calls (as specified in `2026-05-06-salesinject-design.md`). Verify nginx headers cover production needs.
- **Files:** New `backend/app/api/middleware/auth.py`

### 1.5 Health Probes
- **Current:** Single `/health` endpoint returning `{"status": "ok"}`
- **Target:** Add `/health/ready` that checks DB connectivity, Redis ping, and Celery worker heartbeat. `docker-compose.prod.yml` already defines healthchecks for DB and Redis — wire these through.
- **Files:** `backend/app/api/v1/endpoints/health.py`

### 1.6 .env & BOT_TOKEN
- **Current:** `.env` has `dummy_token_will_set_later` for BOT_TOKEN, real Postgres credentials
- **Target:** Document where to obtain each secret. BOT_TOKEN must come from @BotFather. Verify all env vars are correctly referenced in both compose files.
- **Files:** `PRODUCTION_CHECKLIST.md`, `backend/.env`

## Phase 2: Testing & Quality

### 2.1 Test Infrastructure
- Create `tests/conftest.py` with: test DB session (SQLite or separate PostgreSQL), Redis mock, test client with API key fixture, test user fixtures
- Create `pytest.ini` / `pyproject.toml` config for coverage
- **Files:** New `tests/conftest.py`, `tests/pytest.ini`

### 2.2 Unit Tests
- Models: User creation, Offer claims, payout transactions
- Services: mission_service (claim, geofence, competition resolution), payout_service, memory_service
- **Files:** `tests/test_models.py`, `tests/test_services.py`

### 2.3 API Integration Tests
- Auth: password-login, token refresh, missing/bad credentials
- Users: CRUD, soft-delete
- Offers: create, claim, discover (geolocation queries)
- Health: /health, /health/ready endpoints
- **Files:** `tests/test_api_auth.py`, `tests/test_api_offers.py`, `tests/test_api_health.py`

### 2.4 Coverage Configuration
- Target: 75%+ coverage
- `.coveragerc` to exclude migrations, tests themselves
- CI-ready: `pytest --cov=app --cov-report=term-missing`

## Phase 3: Observability & Deployment Polish

### 3.1 Prometheus Metrics
- Add `prometheus-client` to requirements
- Add `/metrics` endpoint exposing: request count, duration histogram, active Celery tasks, DB pool size
- Use middleware to auto-instrument requests
- **Files:** New `backend/app/core/metrics.py`, modify `backend/app/main.py`

### 3.2 Sentry Error Tracking
- Add `sentry-sdk` to requirements
- Initialize in `main.py` with `SENTRY_DSN` env var
- **Files:** `backend/app/main.py`

### 3.3 Deployment Documentation
- Update `PRODUCTION_CHECKLIST.md` with verified steps
- Add SSL setup instructions (Certbot, domain config)
- Add backup/restore instructions for PostgreSQL
- **Files:** `PRODUCTION_CHECKLIST.md`

### 3.4 Final Verification
- `docker compose -f docker-compose.prod.yml build` passes
- All containers start without errors
- `/health` and `/health/ready` respond 200
- Alembic migrations apply cleanly to fresh DB

## Files Modified/Created Summary

| File | Action | Phase |
|------|--------|-------|
| `backend/app/main.py` | Modify | 1 |
| `backend/app/core/config.py` | Modify | 1 |
| `backend/app/core/logging.py` | Create | 1 |
| `backend/app/api/middleware/auth.py` | Create | 1 |
| `backend/app/api/v1/endpoints/health.py` | Modify | 1 |
| `backend/app/api/v1/endpoints/auth.py` | Modify | 1 |
| `backend/app/api/v1/endpoints/telegram.py` | Modify | 1 |
| `tests/conftest.py` | Create | 2 |
| `tests/pytest.ini` | Create | 2 |
| `tests/test_models.py` | Create | 2 |
| `tests/test_services.py` | Create | 2 |
| `tests/test_api_auth.py` | Create | 2 |
| `tests/test_api_offers.py` | Create | 2 |
| `tests/test_api_health.py` | Create | 2 |
| `backend/app/core/metrics.py` | Create | 3 |
| `PRODUCTION_CHECKLIST.md` | Modify | 3 |

Total: ~16 files, 3 phases, no architectural changes.