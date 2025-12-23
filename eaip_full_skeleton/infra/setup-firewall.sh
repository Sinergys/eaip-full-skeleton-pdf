#!/bin/bash
set -e

echo "🔥 EAIP Firewall Setup"
echo "======================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if UFW is installed
if ! command -v ufw &> /dev/null; then
    echo -e "${YELLOW}⚠️  UFW not found. Installing...${NC}"
    
    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        echo -e "${RED}❌ Cannot detect OS${NC}"
        exit 1
    fi
    
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        sudo apt-get update
        sudo apt-get install -y ufw
    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        sudo yum install -y ufw || sudo dnf install -y ufw
    else
        echo -e "${RED}❌ Unsupported OS: $OS${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ UFW installed${NC}"
fi

# Allow required ports
echo "🔓 Configuring firewall rules..."

# HTTP (Gateway)
sudo ufw allow 80/tcp comment 'EAIP Gateway HTTP'
echo -e "${GREEN}✅ Port 80 (HTTP) allowed${NC}"

# HTTPS (if needed in future)
sudo ufw allow 443/tcp comment 'EAIP Gateway HTTPS'
echo -e "${GREEN}✅ Port 443 (HTTPS) allowed${NC}"

# MinIO API
sudo ufw allow 9000/tcp comment 'MinIO API'
echo -e "${GREEN}✅ Port 9000 (MinIO API) allowed${NC}"

# MinIO Console
sudo ufw allow 9001/tcp comment 'MinIO Console'
echo -e "${GREEN}✅ Port 9001 (MinIO Console) allowed${NC}"

# SSH (important!)
sudo ufw allow 22/tcp comment 'SSH'
echo -e "${GREEN}✅ Port 22 (SSH) allowed${NC}"

# Enable firewall
echo ""
echo "🛡️  Enabling firewall..."
sudo ufw --force enable

# Show status
echo ""
echo "📊 Firewall status:"
sudo ufw status verbose

echo ""
echo -e "${GREEN}✅ Firewall setup completed!${NC}"
echo -e "${YELLOW}⚠️  Make sure SSH access is working before disconnecting!${NC}"

