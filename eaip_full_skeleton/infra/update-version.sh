#!/bin/bash
set -e

echo "🔄 EAIP Version Update Script"
echo "============================="
echo ""

STAGING_DIR="/opt/eaip"
COMPOSE_FILE="$STAGING_DIR/docker-compose.staging.yml"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <new_version>"
    echo "Example: $0 v0.4.0"
    exit 1
fi

NEW_VERSION=$1
OLD_VERSION=$(grep -oP 'v\d+\.\d+\.\d+' "$COMPOSE_FILE" | head -1)

if [ -z "$OLD_VERSION" ]; then
    echo -e "${RED}❌ Could not detect current version${NC}"
    exit 1
fi

echo "Current version: $OLD_VERSION"
echo "New version: $NEW_VERSION"
echo ""

# Confirm
read -p "Do you want to update from $OLD_VERSION to $NEW_VERSION? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Update cancelled"
    exit 0
fi

cd "$STAGING_DIR"

# Backup current compose file
echo "💾 Backing up current configuration..."
cp "$COMPOSE_FILE" "${COMPOSE_FILE}.backup.$(date +%F_%H%M%S)"
echo -e "${GREEN}✅ Backup created${NC}"
echo ""

# Update version in compose file
echo "📝 Updating version in docker-compose.staging.yml..."
sed -i "s/:${OLD_VERSION}/:${NEW_VERSION}/g" "$COMPOSE_FILE"
echo -e "${GREEN}✅ Version updated${NC}"
echo ""

# Pull new images
echo "⬇️  Pulling new images..."
docker compose -f "$COMPOSE_FILE" pull
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to pull images${NC}"
    echo "Restoring backup..."
    mv "${COMPOSE_FILE}.backup."* "$COMPOSE_FILE"
    exit 1
fi
echo -e "${GREEN}✅ Images pulled${NC}"
echo ""

# Update services (zero-downtime)
echo "🚀 Updating services..."
docker compose -f "$COMPOSE_FILE" up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to update services${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Services updated${NC}"
echo ""

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Health check
echo "🏥 Health check..."
if curl -fsS http://127.0.0.1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    curl -fsS http://127.0.0.1/health | jq . 2>/dev/null || curl -fsS http://127.0.0.1/health
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "Consider rolling back..."
    exit 1
fi
echo ""

# Show status
echo "📊 Container status:"
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo -e "${GREEN}✅ Update completed successfully!${NC}"
echo ""
echo "Current version: $NEW_VERSION"
echo "Backup saved: ${COMPOSE_FILE}.backup.*"

