#!/bin/bash
set -e

echo "🚀 Starting Deployment of SalesInject..."

if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env file not found. Please create one from backend/.env.example"
    exit 1
fi

echo "📦 Pulling latest code..."
git pull origin main

echo "🛑 Stopping existing services..."
docker compose -f docker-compose.prod.yml down

echo "🏗️ Building Docker images..."
docker compose -f docker-compose.prod.yml build

echo "🟢 Starting services in detached mode..."
docker compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for the health endpoint to become available..."
max_retries=30
counter=0
until curl -sSf http://localhost/api/v1/health > /dev/null; do
    counter=$((counter+1))
    if [ $counter -ge $max_retries ]; then
        echo "❌ Health check failed after $max_retries attempts. Check logs with: docker compose -f docker-compose.prod.yml logs backend"
        exit 1
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "✅ Deployment completed successfully! SalesInject is up and running."
