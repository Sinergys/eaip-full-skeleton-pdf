#!/bin/bash
set -e

echo "📦 EAIP MinIO Setup"
echo "==================="
echo ""

STAGING_DIR="/opt/eaip"
ENV_FILE="$STAGING_DIR/.env"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if MinIO client is installed
if ! command -v mc &> /dev/null; then
    echo -e "${YELLOW}⚠️  MinIO client (mc) not found. Installing...${NC}"
    
    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        echo -e "${RED}❌ Cannot detect OS${NC}"
        exit 1
    fi
    
    # Install mc based on OS
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /tmp/mc
        chmod +x /tmp/mc
        sudo mv /tmp/mc /usr/local/bin/mc
    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /tmp/mc
        chmod +x /tmp/mc
        sudo mv /tmp/mc /usr/local/bin/mc
    else
        echo -e "${RED}❌ Unsupported OS: $OS${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ MinIO client installed${NC}"
fi

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo -e "${RED}❌ .env file not found at $ENV_FILE${NC}"
    exit 1
fi

# Wait for MinIO to be ready
echo "⏳ Waiting for MinIO to be ready..."
for i in {1..30}; do
    if curl -fsS http://127.0.0.1:9000/minio/health/live > /dev/null 2>&1; then
        echo -e "${GREEN}✅ MinIO is ready${NC}"
        break
    fi
    sleep 1
done

# Set alias
echo "🔗 Setting MinIO alias..."
mc alias set eaip http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" || {
    echo -e "${RED}❌ Failed to set MinIO alias${NC}"
    exit 1
}
echo -e "${GREEN}✅ MinIO alias set${NC}"

# Create bucket
echo "🪣 Creating bucket 'eaip-bucket'..."
mc mb eaip/eaip-bucket || {
    if mc ls eaip/eaip-bucket > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Bucket already exists${NC}"
    else
        echo -e "${RED}❌ Failed to create bucket${NC}"
        exit 1
    fi
}
echo -e "${GREEN}✅ Bucket created${NC}"

# List buckets
echo ""
echo "📋 Available buckets:"
mc ls eaip/

echo ""
echo -e "${GREEN}✅ MinIO setup completed!${NC}"

