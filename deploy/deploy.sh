#!/usr/bin/env bash
set -euo pipefail

# ── Config (edit these) ──────────────────────────────────────────────────
APP_DIR=/opt/salesinject
DOMAIN=your.domain.com
PG_USER=salesinject
PG_PASSWORD=CHANGE_ME

# ── 1. System packages ───────────────────────────────────────────────────
echo "📦 Installing system packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# ── 2. Redis ─────────────────────────────────────────────────────────────
echo "🔴 Starting Redis..."
sudo systemctl enable --now redis-server

# ── 3. PostgreSQL + pgvector ─────────────────────────────────────────────
echo "🐘 Setting up PostgreSQL + pgvector..."
sudo -u postgres psql -c "CREATE DATABASE salesinject;" || true
sudo -u postgres psql -c "CREATE USER ${PG_USER} WITH ENCRYPTED PASSWORD '${PG_PASSWORD}';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE salesinject TO ${PG_USER};" || true
sudo -u postgres psql -c "ALTER DATABASE salesinject OWNER TO ${PG_USER};"
sudo -u postgres psql -d salesinject -c "CREATE EXTENSION IF NOT EXISTS vector;"

# ── 4. Clone & setup app ─────────────────────────────────────────────────
echo "📥 Cloning repo..."
sudo git clone https://github.com/<your-org>/salesinject.git "$APP_DIR" || true
sudo chown -R salesinject:salesinject "$APP_DIR"

sudo -u salesinject bash -c "
    cd $APP_DIR
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r backend/requirements.txt

    # Create .env from template if missing
    if [ ! -f .env ]; then
        cp .env.example .env
        echo '⚠️  Edit .env before proceeding!'
        exit 1
    fi

    # Run migrations
    cd backend
    ../.venv/bin/alembic upgrade head
"

# ── 5. Frontend build ────────────────────────────────────────────────────
echo "🎨 Building frontend..."
sudo -u salesinject bash -c "
    cd $APP_DIR/frontend
    npm install
    npm run build
"

# ── 6. Backend systemd service ───────────────────────────────────────────
echo "⚙️  Installing backend systemd service..."
sudo cp "$APP_DIR/deploy/salesinject-backend.service" /etc/systemd/system/ 2>/dev/null || \
sudo tee /etc/systemd/system/salesinject.service <<'EOF'
[Unit]
Description=SalesInject FastAPI service
After=network.target postgresql.service redis-server.service

[Service]
User=salesinject
Group=salesinject
WorkingDirectory=/opt/salesinject/backend
EnvironmentFile=/opt/salesinject/.env
ExecStart=/opt/salesinject/.venv/bin/gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 app.main:app
Restart=on-failure
RestartSec=5
TimeoutSec=120

[Install]
WantedBy=multi-user.target
EOF

# ── 7. Celery worker systemd service ─────────────────────────────────────
echo "🔧 Installing Celery worker service..."
sudo tee /etc/systemd/system/salesinject-celery.service <<'EOF'
[Unit]
Description=SalesInject Celery worker
After=network.target redis-server.service

[Service]
User=salesinject
Group=salesinject
WorkingDirectory=/opt/salesinject/backend
EnvironmentFile=/opt/salesinject/.env
ExecStart=/opt/salesinject/.venv/bin/celery -A app.worker.celery_app worker -l info -c 4
Restart=on-failure
RestartSec=10
TimeoutSec=300

[Install]
WantedBy=multi-user.target
EOF

# ── 8. Celery Beat systemd service ───────────────────────────────────────
echo "⏰ Installing Celery Beat service..."
sudo tee /etc/systemd/system/salesinject-beat.service <<'EOF'
[Unit]
Description=SalesInject Celery Beat scheduler
After=network.target redis-server.service

[Service]
User=salesinject
Group=salesinject
WorkingDirectory=/opt/salesinject/backend
EnvironmentFile=/opt/salesinject/.env
ExecStart=/opt/salesinject/.venv/bin/celery -A app.worker.celery_app beat -l info
Restart=on-failure
RestartSec=10
TimeoutSec=120

[Install]
WantedBy=multi-user.target
EOF

# ── 9. Nginx reverse proxy ───────────────────────────────────────────────
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/salesinject.conf <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    root ${APP_DIR}/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /webhook/telegram {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/salesinject.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# ── 10. Start all services ───────────────────────────────────────────────
echo "🚀 Starting all services..."
sudo systemctl daemon-reload
sudo systemctl enable --now salesinject.service
sudo systemctl enable --now salesinject-celery.service
sudo systemctl enable --now salesinject-beat.service

echo ""
echo "✅ SalesInject deployed."
echo "   API health:  curl http://${DOMAIN}/api/v1/health"
echo "   Frontend:    http://${DOMAIN}"
echo ""
echo "⚠️  Reminders:"
echo "   - Edit .env and set SECRET_KEY, BOT_TOKEN, EXA_API_KEY"
echo "   - Run: certbot --nginx -d ${DOMAIN}    (for HTTPS)"
echo "   - If USE_WEBHOOK=true: curl 'https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://${DOMAIN}/webhook/telegram'"