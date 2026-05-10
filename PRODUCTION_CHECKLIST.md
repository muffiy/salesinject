# 🚀 SalesInject Production Checklist

This checklist must be fully executed before making SalesInject publicly available.

## 1. 🔐 Security & Secrets
- [ ] Rename `backend/.env.example` to `backend/.env` on the VPS.
- [ ] Set a strong `SECRET_KEY` (e.g., run `openssl rand -hex 32`).
- [ ] Fill in `BOT_TOKEN` from @BotFather.
- [ ] Fill in `OPENROUTER_API_KEY` and `EXA_API_KEY`.
- [ ] Ensure `DEBUG=False` in `.env`.
- [ ] Change the default Postgres password (`password`) in both `.env` and `docker-compose.prod.yml`.

## 2. 🌐 Networking & Domain
- [ ] Point your domain (e.g., `salesinject.tn`) to the VPS IP via A-Record.
- [ ] Run Certbot to generate SSL certificates:
      `sudo certbot --nginx -d salesinject.tn`
- [ ] Update `nginx/nginx.conf` to use the SSL certificates (uncomment the HTTPS block).
- [ ] Set `MINI_APP_URL=https://salesinject.tn` in `.env`.
- [ ] Set `USE_WEBHOOK=True` and `WEBHOOK_URL=https://salesinject.tn/api/v1/telegram/webhook` in `.env`.

## 3. 🐘 Database & Migrations
- [ ] Execute Docker Compose to start the DB: `docker compose -f docker-compose.prod.yml up -d db`
- [ ] Run Alembic migrations: `docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head`

## 4. 🤖 AI & Tasks
- [ ] Verify Celery worker is running: `docker compose -f docker-compose.prod.yml logs celery-worker`
- [ ] Verify Celery beat is running: `docker compose -f docker-compose.prod.yml logs celery-beat`
- [ ] Ensure Redis is healthy (required for Celery).

## 5. 📱 Telegram Integration
- [ ] Link the Mini App in BotFather using your domain (`https://salesinject.tn`).
- [ ] Use Postman or curl to manually trigger the webhook endpoint and ensure it returns 200 OK.
- [ ] Send `/start` to the bot to verify the Welcome Message and Mini App button appear.

## 6. 🚀 Final Deployment
- [ ] Build & Start all services: `docker compose -f docker-compose.prod.yml up -d --build`
- [ ] Check Nginx logs for any proxy errors: `docker compose -f docker-compose.prod.yml logs nginx`
- [ ] Access the app via Telegram and test a Scout Mission to verify end-to-end functionality.

## 0. Pre-Deployment Verification
- [ ] Run pytest suite: `cd backend && python -m pytest ../tests/ -v --cov=app --cov-report=term-missing`
- [ ] Verify coverage >= 75%
- [ ] No critical security warnings from `bandit -r backend/app/`
- [ ] `docker compose -f docker-compose.prod.yml build` succeeds
- [ ] All `.env` variables are filled (no dummy values)

## 7. Observability
- [ ] Verify Prometheus `/metrics` endpoint returns data
- [ ] Set up Sentry DSN in `.env` (`SENTRY_DSN=...`)
- [ ] Verify Sentry captures a test error
- [ ] Set up Grafana dashboard using metrics from `/metrics`
- [ ] Configure log aggregation (e.g., Loki, ELK) for structured JSON logs

## 8. Backup & Recovery
- [ ] Set up automated PostgreSQL backups:
      ```bash
      docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres salesinject > backup_$(date +%Y%m%d).sql
      ```
- [ ] Schedule daily backups via cron
- [ ] Verify backup file is restorable:
      ```bash
      docker compose -f docker-compose.prod.yml exec -T db psql -U postgres salesinject < backup.sql
      ```
- [ ] Document recovery procedure in runbook

## 9. SSL/Domain Setup
- [ ] Point domain A-record to VPS IP
- [ ] Run Certbot: `sudo certbot --nginx -d yourdomain.com`
- [ ] Uncomment HTTPS block in `nginx/nginx.conf`
- [ ] Set `MINI_APP_URL=https://yourdomain.com` in `.env`
- [ ] Verify HTTPS redirect works (HTTP → HTTPS)
- [ ] Test Telegram Mini App loads over HTTPS
