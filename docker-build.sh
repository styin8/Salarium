#!/bin/bash
# Salarium Docker Build Script

set -e

echo "🐳 Building Salarium with Docker Compose..."
echo ""

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Please review and update values as needed."
    echo ""
fi

# Create data directory if it doesn't exist
if [ ! -d ./data/sqlite ]; then
    echo "📁 Creating data directory for SQLite..."
    mkdir -p ./data/sqlite
    chmod 755 ./data/sqlite
    echo "✅ Data directory created."
    echo ""
fi

# Build and start services
echo "🔨 Building Docker images..."
docker compose build

echo ""
echo "🚀 Starting services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "✅ Salarium is starting!"
echo ""
echo "Frontend: http://localhost:8080"
echo "Backend API: http://localhost:8080/api/docs"
echo ""
echo "View logs: docker compose logs -f"
echo "Stop services: docker compose down"
