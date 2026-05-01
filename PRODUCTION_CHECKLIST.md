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
