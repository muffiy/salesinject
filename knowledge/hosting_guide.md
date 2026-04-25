# 🚀 SalesInject: Comprehensive Hosting Guide

## 📋 Overview

This guide provides complete instructions for deploying and hosting the SalesInject project on a production VPS. SalesInject is an AI-powered Telegram Mini App platform connecting influencers with brands through a gamified 3D visualization experience.

**Project Architecture:**
- **Frontend:** React 19 + TypeScript + Vite + TailwindCSS + Telegram Web App SDK
- **Backend:** FastAPI (Python) + PostgreSQL + Redis + Celery
- **Infrastructure:** Docker + Docker Compose + Nginx
- **AI Components:** OpenClaw (separate VPS), Exa Search API, Agent Zero

---

## 🎯 Prerequisites

### 1. VPS Requirements
- **Minimum:** 2GB RAM, 1 vCPU, 20GB SSD (Tested on Hostinger KVM 1)
- **Recommended:** 4GB RAM, 2 vCPU, 40GB SSD for production scaling
- **OS:** Ubuntu 22.04 LTS (Debian-based distributions also work)
- **Open Ports:** 80 (HTTP), 443 (HTTPS), 22 (SSH)

### 2. Domain Name (Optional for initial deployment)
- Required for HTTPS/SSL certificates
- Can start with IP address and add domain later

### 3. API Keys & External Services
- **Telegram Bot Token:** From [@BotFather](https://t.me/botfather)
- **Exa API Key:** For neural search (get from [exa.ai](https://exa.ai))
- **OpenClaw VPS:** Separate VPS running OpenClaw agent framework

### 4. Local Development Setup (for testing)
- Git, Docker, Docker Compose
- Node.js 20+, Python 3.11+
- PostgreSQL 15+ with pgvector extension

---

## 🚀 Quick Start Deployment

### Step 1: Initial Server Setup

```bash
# Update system and install prerequisites
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-plugin git curl

# Add current user to docker group (requires re-login)
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker installation
docker --version
docker compose version
```

### Step 2: Clone the Repository

```bash
# Clone the SalesInject repository
git clone https://github.com/muffiy/salesinject.git
cd salesinject
```

### Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example backend/.env

# Edit with your actual values
nano backend/.env
```

**Critical `.env` variables to configure:**

```env
# Database
POSTGRES_USER=salesinject_user
POSTGRES_PASSWORD=CHANGE_ME_strong_password_here

# Auth (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your_64_character_secret_key_here

# External Services
OPENCLAW_URL=http://YOUR_OPENCLAW_VPS_IP:18789
EXA_API_KEY=your-exa-api-key-here
BOT_TOKEN=your-telegram-bot-token

# VPS Configuration
MINI_APP_URL=http://YOUR_VPS_IP  # Update to https://yourdomain.com when SSL ready
USE_WEBHOOK=true
DEBUG=false
```

### Step 4: Deploy with One Command

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The deploy script will:
1. Verify `.env` file exists
2. Pull latest code changes
3. Stop any existing containers
4. Build Docker images
5. Start all services
6. Wait for backend health check (up to 60 seconds)
7. Output success message with your VPS IP

### Step 5: Verify Deployment

```bash
# Check running containers
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Test health endpoint
curl http://localhost/health
```

---

## 🔧 Detailed Configuration

### Docker Compose Architecture

The production setup (`docker-compose.prod.yml`) includes:

| Service | Purpose | Port | Resource Limits |
|---------|---------|------|----------------|
| `db` | PostgreSQL with pgvector | 5432 (internal) | 500M memory |
| `redis` | Redis cache & Celery broker | 6379 (internal) | 100M memory |
| `migrate` | Database migrations | - | Runs once |
| `backend` | FastAPI with gunicorn | 8000 (internal) | 800M memory, 3 workers |
| `celery-worker` | Background task processing | - | 600M memory, 3 concurrency |
| `celery-beat` | Scheduled tasks | - | 150M memory |
| `frontend` | React static files | 80 (internal) | 100M memory |
| `nginx` | Reverse proxy | 80/443 (public) | 50M memory |

### Nginx Configuration

The `nginx/nginx.conf` file handles:
- **API Routing:** `/api/*` → backend service
- **Telegram Webhooks:** `/webhook/telegram` → backend
- **Frontend SPA:** All other routes → frontend
- **Health Checks:** `/health` endpoint for monitoring
- **Security Headers:** X-Frame-Options, XSS protection, etc.

### Resource Tuning for Your VPS

**For 2GB RAM VPS (default):**
```yaml
# In docker-compose.prod.yml
backend:
  command: gunicorn ... --workers 2  # Reduced from 3
  
celery-worker:
  command: celery ... --concurrency=2  # Reduced from 3
```

**For 4GB+ RAM VPS:**
```yaml
backend:
  command: gunicorn ... --workers 4
  deploy:
    limits:
      memory: 1.5G
      
celery-worker:
  command: celery ... --concurrency=4
  deploy:
    limits:
      memory: 1G
```

---

## 🔒 SSL/HTTPS Setup (Domain Required)

### Step 1: Update DNS Records
1. Point your domain (A record) to your VPS IP
2. Wait for DNS propagation (up to 48 hours, usually less)

### Step 2: Configure Nginx for SSL

```bash
# Edit nginx configuration
nano nginx/nginx.conf
```

Uncomment the HTTPS server block (lines 54-72) and update:
- `server_name yourdomain.com;` → Your actual domain
- `ssl_certificate` and `ssl_certificate_key` paths remain as-is (Certbot will populate)

### Step 3: Install Certbot and Obtain SSL Certificate

```bash
# Stop nginx container temporarily
docker stop salesinject-nginx

# Install Certbot on host
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate (interactive)
sudo certbot --nginx -d yourdomain.com

# Restart nginx container
docker start salesinject-nginx
```

### Step 4: Update Environment Variables

```bash
# Update backend/.env
MINI_APP_URL=https://yourdomain.com
USE_WEBHOOK=true

# Update docker-compose.prod.yml for frontend build arg
# Change VITE_API_BASE_URL to use HTTPS
VITE_API_BASE_URL: https://yourdomain.com/api/v1
```

### Step 5: Redeploy with SSL

```bash
# Rebuild frontend with new API URL
./deploy.sh
```

### Step 6: Configure Telegram Webhook

```bash
# Set Telegram webhook to HTTPS endpoint
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://yourdomain.com/webhook/telegram"
```

---

## 📡 OpenClaw Integration

SalesInject uses OpenClaw for AI agent capabilities running on a **separate VPS**.

### OpenClaw VPS Setup
1. Deploy OpenClaw on another VPS (minimum 2GB RAM)
2. Ensure it's accessible via `OPENCLAW_URL` in your `.env`
3. Default OpenClaw port is `18789`

### Health Check
```bash
# Test OpenClaw connectivity from SalesInject VPS
curl http://OPENCLAW_VPS_IP:18789/health
```

### Troubleshooting
- **Connection refused:** Check OpenClaw VPS firewall (`sudo ufw allow 18789`)
- **Timeout:** Verify network connectivity between VPS instances
- **Authentication:** OpenClaw may require API key authentication

---

## 🐳 Docker Management Commands

### Common Operations

```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml logs --tail=50 backend
docker compose -f docker-compose.prod.yml logs --tail=50 celery-worker

# Restart services
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml restart celery-worker

# Stop all services
docker compose -f docker-compose.prod.yml down

# Start services
docker compose -f docker-compose.prod.yml up -d

# View resource usage
docker stats

# Enter container shell
docker exec -it salesinject-backend /bin/sh

# Backup database
docker exec salesinject-db pg_dump -U salesinject_user salesinject > backup_$(date +%Y%m%d).sql
```

### Database Operations

```bash
# Run migrations manually
docker compose -f docker-compose.prod.yml run --rm migrate

# Create superuser (if auth system supports it)
docker exec -it salesinject-backend python -c "from app.database import SessionLocal; from app.models import User; db = SessionLocal(); # ..."

# View database logs
docker logs salesinject-db
```

### Cleanup Operations

```bash
# Remove unused Docker resources
docker system prune -f
docker volume prune -f

# Clear Redis cache
docker exec salesinject-redis redis-cli FLUSHALL
```

---

## 📊 Monitoring & Maintenance

### Health Monitoring

**Built-in endpoints:**
- `http://yourdomain.com/health` - Overall system health
- `http://yourdomain.com/api/v1/health/` - Backend health with DB check
- `http://yourdomain.com/api/v1/debug/rls` - RLS debug (DEBUG mode only)

**External monitoring tools:**
- **Uptime Kuma:** Self-hosted status page
- **Prometheus + Grafana:** Metrics collection
- **Logtail/Papertrail:** Centralized logging

### Log Management

```bash
# Follow all logs
docker compose -f docker-compose.prod.yml logs -f

# Export logs to file
docker compose -f docker-compose.prod.yml logs --no-color > salesinject_logs_$(date +%Y%m%d).txt

# Log rotation with Docker
# Add to daemon.json: {"log-driver": "json-file", "log-opts": {"max-size": "10m", "max-file": "3"}}
```

### Backup Strategy

**Daily automated backup script (`/opt/backup_salesinject.sh`):**

```bash
#!/bin/bash
BACKUP_DIR="/opt/salesinject_backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec salesinject-db pg_dump -U salesinject_user salesinject > $BACKUP_DIR/db_$DATE.sql

# Backup Docker volumes
docker run --rm -v salesinject_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/volumes_$DATE.tar.gz /data

# Backup environment files
cp /home/ubuntu/salesinject/backend/.env $BACKUP_DIR/env_$DATE

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

**Set up cron job:**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/backup_salesinject.sh
```

### Scaling Considerations

**Vertical Scaling (Upgrade VPS):**
1. Increase RAM from 2GB → 4GB+
2. Increase CPU cores
3. Adjust Docker Compose resource limits accordingly

**Horizontal Scaling (Future):**
1. Separate database to dedicated server
2. Add Celery worker replicas
3. Implement Redis cluster
4. Use CDN for frontend assets

---

## 🐛 Troubleshooting Guide

### Common Issues & Solutions

**1. Deployment fails with database connection error**
```bash
# Check if PostgreSQL container is running
docker ps | grep salesinject-db

# Check PostgreSQL logs
docker logs salesinject-db

# Verify credentials in .env match docker-compose.prod.yml
```

**2. Frontend shows "Cannot connect to API"**
- Check `VITE_API_BASE_URL` in frontend build args
- Verify nginx routing: `curl http://localhost/api/v1/health/`
- Check backend logs: `docker logs salesinject-backend`

**3. Celery tasks not executing**
```bash
# Check Celery worker status
docker logs salesinject-celery

# Check Redis connection
docker exec salesinject-redis redis-cli ping

# Test task manually
docker exec salesinject-backend python -c "from app.worker import test_task; test_task.delay('test')"
```

**4. Telegram webhook not receiving updates**
```bash
# Check webhook status
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"

# Verify nginx configuration for /webhook/telegram
docker exec salesinject-nginx nginx -t

# Check backend logs for webhook requests
docker logs salesinject-backend --tail=100 | grep webhook
```

**5. High memory usage**
```bash
# Identify memory-hungry containers
docker stats --no-stream

# Adjust resource limits in docker-compose.prod.yml
# Reduce gunicorn workers or celery concurrency
```

**6. SSL certificate renewal**
```bash
# Certbot auto-renewal
sudo certbot renew --dry-run

# Manual renewal
sudo certbot renew
docker restart salesinject-nginx
```

### Debug Mode

For development debugging, enable DEBUG mode:

```bash
# In backend/.env
DEBUG=true

# Restart backend
docker compose -f docker-compose.prod.yml restart backend
```

**Debug endpoints available:**
- `/api/v1/debug/rls` - Row Level Security debug
- Database queries logged at INFO level
- Detailed error responses

---

## 🔄 Update & Maintenance

### Updating to Latest Code

```bash
# From salesinject directory
git pull origin main
./deploy.sh
```

### Applying Database Migrations

```bash
# Manual migration if auto-migrate fails
docker compose -f docker-compose.prod.yml run --rm migrate
```

### Upgrading Docker Images

```bash
# Rebuild with latest base images
docker compose -f docker-compose.prod.yml build --no-cache --pull
./deploy.sh
```

### Security Updates

1. **Monthly:** Update system packages
   ```bash
   sudo apt update && sudo apt upgrade -y
   docker system prune -f
   ```

2. **Quarterly:** Review Docker image tags
3. **Bi-annually:** Update Python/Node.js versions in Dockerfiles

---

## 📞 Support & Resources

### Project Documentation
- **Business & Architecture:** `knowledge/project_business_and_architecture_guide.md`
- **Project Tracker:** `knowledge/project_tracker.md`  
- **Memories:** `knowledge/memories.md`
- **This Guide:** `knowledge/hosting_guide.md`

### Key Files Reference
| File | Purpose | Location |
|------|---------|----------|
| `deploy.sh` | One-command deployment | Project root |
| `docker-compose.prod.yml` | Production services | Project root |
| `nginx/nginx.conf` | Reverse proxy config | `nginx/` directory |
| `backend/Dockerfile` | Backend container build | `backend/` directory |
| `frontend/Dockerfile` | Frontend container build | `frontend/` directory |
| `.env.example` | Environment template | Project root |

### Getting Help
1. Check logs: `docker compose -f docker-compose.prod.yml logs`
2. Review this guide's troubleshooting section
3. Check GitHub Issues: [muffiy/salesinject](https://github.com/muffiy/salesinject)
4. Contact: Project maintainers

---

## 🎉 Deployment Complete!

Your SalesInject platform should now be running at:
- **HTTP:** `http://YOUR_VPS_IP`
- **HTTPS:** `https://yourdomain.com` (if configured)

**Next Steps:**
1. Test the Telegram Mini App: `t.me/YourBotUsername`
2. Add initial test users and influencers
3. Monitor system health for 24 hours
4. Configure backups and monitoring
5. Plan scaling based on user growth

**Remember:** Always test deployment changes in a staging environment before applying to production.

---
*Last Updated: $(date +%Y-%m-%d)*
*Guide Version: 1.0*
*SalesInject Hosting Guide - Comprehensive deployment reference*