#!/bin/bash
set -e

echo "🚀 EAIP Staging Deployment Script"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
STAGING_DIR="/opt/eaip"
COMPOSE_FILE="docker-compose.staging.yml"
ENV_FILE=".env"

# Step 1: Check Docker installation
echo "📦 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker installed. Please log out and log back in.${NC}"
    exit 0
fi

docker --version
docker compose version
echo ""

# Step 2: Create directory and setup
echo "📁 Setting up staging directory..."
if [ ! -d "$STAGING_DIR" ]; then
    sudo mkdir -p "$STAGING_DIR"
    sudo chown $USER:$USER "$STAGING_DIR"
fi

cd "$STAGING_DIR"
echo "Working directory: $(pwd)"
echo ""

# Step 3: Create .env file if not exists
if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating .env file..."
    cat > "$ENV_FILE" <<EOF
# PostgreSQL Configuration
POSTGRES_USER=eaip_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_DB=eaip_db
POSTGRES_HOST=postgres

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=$(openssl rand -base64 32)
EOF
    echo -e "${GREEN}.env file created with secure passwords${NC}"
else
    echo -e "${YELLOW}.env file already exists, skipping...${NC}"
fi
echo ""

# Step 4: Copy docker-compose.staging.yml if not exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "📋 docker-compose.staging.yml not found in $STAGING_DIR"
    echo "Please copy it from the repository"
    exit 1
fi

# Step 5: Pull images
echo "⬇️  Pulling Docker images..."
docker compose -f "$COMPOSE_FILE" pull
echo ""

# Step 6: Start services
echo "🚀 Starting services..."
docker compose -f "$COMPOSE_FILE" up -d
echo ""

# Step 7: Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Step 8: Check status
echo "📊 Container status:"
docker compose -f "$COMPOSE_FILE" ps
echo ""

# Step 9: Health check
echo "🏥 Health check:"
if curl -fsS http://127.0.0.1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Gateway health check passed${NC}"
    curl -sS http://127.0.0.1/health | jq .
else
    echo -e "${RED}❌ Gateway health check failed${NC}"
fi
echo ""

# Step 10: Initialize MinIO (optional)
if command -v mc &> /dev/null; then
    echo "📦 Initializing MinIO bucket..."
    source "$ENV_FILE"
    mc alias set eaip http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" || true
    mc mb eaip/eaip-bucket || true
    echo -e "${GREEN}MinIO bucket initialized${NC}"
else
    echo -e "${YELLOW}MinIO client (mc) not installed, skipping bucket initialization${NC}"
fi
echo ""

echo -e "${GREEN}✅ Deployment completed!${NC}"
echo ""
echo "Services are available at:"
echo "  - Gateway: http://$(hostname -I | awk '{print $1}')/health"
echo "  - MinIO Console: http://$(hostname -I | awk '{print $1}'):9001"
echo ""

