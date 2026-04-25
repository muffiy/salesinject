# 🚀 SalesInject Deployment Cheat Sheet

## Quick Commands

### Initial Deployment
```bash
# Server setup
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER && newgrp docker

# Clone & deploy
git clone https://github.com/muffiy/salesinject.git
cd salesinject
cp .env.example backend/.env
nano backend/.env  # Fill in your values
chmod +x deploy.sh
./deploy.sh
```

### Daily Operations
```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml logs --tail=100 backend

# Restart services
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml restart celery-worker

# Check status
docker compose -f docker-compose.prod.yml ps
curl http://localhost/health
```

### Database
```bash
# Backup
docker exec salesinject-db pg_dump -U salesinject_user salesinject > backup.sql

# Restore
cat backup.sql | docker exec -i salesinject-db psql -U salesinject_user salesinject

# Run migrations
docker compose -f docker-compose.prod.yml run --rm migrate
```

### Updates
```bash
# Update code
git pull origin main
./deploy.sh

# Rebuild from scratch
docker compose -f docker-compose.prod.yml build --no-cache
./deploy.sh
```

## 🔧 Environment Variables (backend/.env)

**Required:**
```env
POSTGRES_PASSWORD=strong_password_here
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
BOT_TOKEN=your_telegram_bot_token
OPENCLAW_URL=http://OPENCLAW_VPS_IP:18789
```

**Optional but recommended:**
```env
EXA_API_KEY=your_exa_api_key
MINI_APP_URL=https://yourdomain.com  # When SSL ready
DEBUG=false
```

## 🌐 Ports & Services

| Service | Internal Port | Public Port | Purpose |
|---------|--------------|-------------|---------|
| Nginx | 80, 443 | 80, 443 | Reverse proxy |
| Backend | 8000 | - | FastAPI API |
| Frontend | 80 | - | React SPA |
| PostgreSQL | 5432 | - | Database |
| Redis | 6379 | - | Cache & queues |

## 📞 Health Checks

```bash
# Overall health
curl http://localhost/health

# Backend API
curl http://localhost/api/v1/health/

# Database connectivity
docker exec salesinject-db pg_isready -U salesinject_user

# Redis
docker exec salesinject-redis redis-cli ping
```

## 🐛 Quick Troubleshooting

### "Cannot connect to API"
1. Check backend logs: `docker logs salesinject-backend --tail=50`
2. Verify nginx routing: `curl http://localhost/api/v1/health/`
3. Check `VITE_API_BASE_URL` in docker-compose.prod.yml

### High memory usage
1. Monitor: `docker stats`
2. Adjust in docker-compose.prod.yml:
   - Backend workers: `--workers 2` (for 2GB RAM)
   - Celery concurrency: `--concurrency=2`

### Telegram webhook issues
```bash
# Check webhook status
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"

# Set webhook manually
curl "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://yourdomain.com/webhook/telegram"
```

## 🔒 SSL Setup (Once you have domain)

```bash
# 1. Uncomment HTTPS block in nginx/nginx.conf
# 2. Install Certbot
sudo apt install -y certbot python3-certbot-nginx
# 3. Get certificate
sudo certbot --nginx -d yourdomain.com
# 4. Update .env
MINI_APP_URL=https://yourdomain.com
# 5. Redeploy
./deploy.sh
```

## 💾 Backup Script

Save as `/opt/backup_salesinject.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/salesinject_backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
docker exec salesinject-db pg_dump -U salesinject_user salesinject > $BACKUP_DIR/db_$DATE.sql
cp /home/ubuntu/salesinject/backend/.env $BACKUP_DIR/env_$DATE
find $BACKUP_DIR -type f -mtime +7 -delete
```

**Cron job (daily at 2AM):**
```bash
0 2 * * * /opt/backup_salesinject.sh
```

## 📚 Documentation

- **Full Hosting Guide:** `knowledge/hosting_guide.md`
- **Project Architecture:** `knowledge/project_business_and_architecture_guide.md`
- **Progress Tracker:** `knowledge/project_tracker.md`
- **Development Logs:** `knowledge/memories.md`

## 🚨 Emergency Stop

```bash
# Stop everything
docker compose -f docker-compose.prod.yml down

# Start everything
docker compose -f docker-compose.prod.yml up -d

# Remove all data (DANGER!)
docker compose -f docker-compose.prod.yml down -v
```

---
*Keep this cheatsheet handy for quick reference during deployment and maintenance.*
*Last Updated: $(date +%Y-%m-%d)*