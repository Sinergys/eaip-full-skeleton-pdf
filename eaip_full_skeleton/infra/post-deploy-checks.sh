#!/bin/bash
set -e

echo "🔍 EAIP Post-Deploy Checks"
echo "=========================="
echo ""

STAGING_DIR="/opt/eaip"
COMPOSE_FILE="$STAGING_DIR/docker-compose.staging.yml"
ENV_FILE="$STAGING_DIR/.env"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo -e "${RED}❌ .env file not found at $ENV_FILE${NC}"
    exit 1
fi

# 1. Check container status
echo "📊 1. Checking container status..."
cd "$STAGING_DIR"
if docker compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Containers are running${NC}"
    docker compose -f "$COMPOSE_FILE" ps
else
    echo -e "${RED}❌ Some containers are not running${NC}"
    docker compose -f "$COMPOSE_FILE" ps
    exit 1
fi
echo ""

# 2. Health check - localhost
echo "🏥 2. Health check (localhost)..."
if curl -fsS http://127.0.0.1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed (127.0.0.1)${NC}"
    curl -fsS http://127.0.0.1/health | jq . 2>/dev/null || curl -fsS http://127.0.0.1/health
else
    echo -e "${RED}❌ Health check failed (127.0.0.1)${NC}"
    exit 1
fi
echo ""

# 3. Health check - port 80
echo "🏥 3. Health check (port 80)..."
if curl -fsS http://127.0.0.1:80/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed (port 80)${NC}"
    curl -fsS http://127.0.0.1:80/health | jq . 2>/dev/null || curl -fsS http://127.0.0.1:80/health
else
    echo -e "${RED}❌ Health check failed (port 80)${NC}"
    exit 1
fi
echo ""

# 4. Check MinIO bucket
echo "📦 4. Checking MinIO bucket..."
if command -v mc &> /dev/null; then
    mc alias set eaip http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" 2>/dev/null || true
    
    if mc ls eaip/eaip-bucket > /dev/null 2>&1; then
        echo -e "${GREEN}✅ MinIO bucket 'eaip-bucket' exists${NC}"
    else
        echo -e "${YELLOW}⚠️  Creating MinIO bucket 'eaip-bucket'...${NC}"
        mc mb eaip/eaip-bucket || true
        if mc ls eaip/eaip-bucket > /dev/null 2>&1; then
            echo -e "${GREEN}✅ MinIO bucket created${NC}"
        else
            echo -e "${RED}❌ Failed to create MinIO bucket${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  MinIO client (mc) not installed, skipping bucket check${NC}"
fi
echo ""

# 5. Check firewall
echo "🔥 5. Checking firewall..."
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "Status: active"; then
        echo -e "${GREEN}✅ UFW firewall is active${NC}"
        sudo ufw status | grep -E "(80|9000|9001)" || echo -e "${YELLOW}⚠️  Ports 80, 9000, 9001 may not be configured${NC}"
    else
        echo -e "${YELLOW}⚠️  UFW firewall is not active${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  UFW not installed, skipping firewall check${NC}"
fi
echo ""

# 6. Check backup cron job
echo "💾 6. Checking backup cron job..."
if sudo crontab -l 2>/dev/null | grep -q "eaip-pg-backup" || [ -f "/etc/cron.d/eaip-pg-backup" ]; then
    echo -e "${GREEN}✅ Backup cron job exists${NC}"
    if [ -f "/etc/cron.d/eaip-pg-backup" ]; then
        cat /etc/cron.d/eaip-pg-backup
    fi
else
    echo -e "${YELLOW}⚠️  Backup cron job not found${NC}"
fi
echo ""

echo -e "${GREEN}✅ Post-deploy checks completed!${NC}"
echo ""

