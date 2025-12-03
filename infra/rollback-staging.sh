#!/bin/bash
set -e

echo "🔄 EAIP Staging Rollback Script"
echo "================================"
echo ""

STAGING_DIR="/opt/eaip"
COMPOSE_FILE="docker-compose.staging.yml"

cd "$STAGING_DIR" || exit 1

echo "🛑 Stopping services..."
docker compose -f "$COMPOSE_FILE" down

echo "🧹 Cleaning up..."
docker system prune -f

echo "✅ Rollback completed!"
echo ""

