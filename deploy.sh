#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# SalesInject — One-Command VPS Deploy Script
# Tested on: Ubuntu 22.04 LTS (Hostinger KVM 1)
#
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh
#
# Requirements on VPS before first run:
#   sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
#   sudo usermod -aG docker $USER && newgrp docker
# ─────────────────────────────────────────────────────────────────────────────

set -e  # exit immediately on error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SalesInject — Production Deploy"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. Verify .env exists ─────────────────────────────────────────────────────
if [ ! -f "./backend/.env" ]; then
    echo "❌ backend/.env not found!"
    echo "   Run: cp .env.example backend/.env && nano backend/.env"
    exit 1
fi

echo "✅ backend/.env found"

# ── 2. Pull latest code ───────────────────────────────────────────────────────
echo ""
echo "📥 Pulling latest code..."
git pull origin main

# ── 3. Stop old containers ────────────────────────────────────────────────────
echo ""
echo "🛑 Stopping existing containers..."
docker compose -f docker-compose.prod.yml down --remove-orphans

# ── 4. Build all images ───────────────────────────────────────────────────────
echo ""
echo "🔨 Building images (this takes 2-4 minutes on first run)..."
docker compose -f docker-compose.prod.yml build --no-cache

# ── 5. Start services ─────────────────────────────────────────────────────────
echo ""
echo "🚀 Starting services..."
docker compose -f docker-compose.prod.yml up -d

# ── 6. Wait for backend to be healthy ─────────────────────────────────────────
echo ""
echo "⏳ Waiting for backend to start..."
sleep 8

MAX_RETRIES=15
RETRY=0
until curl -sf http://localhost/health > /dev/null 2>&1 || [ $RETRY -eq $MAX_RETRIES ]; do
    echo "   waiting... ($RETRY/$MAX_RETRIES)"
    sleep 4
    RETRY=$((RETRY+1))
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo ""
    echo "⚠️  Health check timed out. Showing logs:"
    docker compose -f docker-compose.prod.yml logs --tail=30 backend
    exit 1
fi

# ── 7. Done ───────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Deployment complete!"
echo ""
echo "  App:    http://$(curl -sf ifconfig.me 2>/dev/null || echo YOUR_VPS_IP)"
echo "  Logs:   docker compose -f docker-compose.prod.yml logs -f"
echo "  Status: docker compose -f docker-compose.prod.yml ps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
