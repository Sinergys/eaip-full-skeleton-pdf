#!/bin/bash
set -e

echo "🛡️  EAIP Staging Hardening Script"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run all hardening steps
echo "Running post-deploy checks and hardening..."
echo ""

# 1. Post-deploy checks
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Post-Deploy Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "$SCRIPT_DIR/post-deploy-checks.sh" ]; then
    bash "$SCRIPT_DIR/post-deploy-checks.sh"
else
    echo -e "${YELLOW}⚠️  post-deploy-checks.sh not found, skipping...${NC}"
fi
echo ""

# 2. MinIO setup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  MinIO Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "$SCRIPT_DIR/setup-minio.sh" ]; then
    bash "$SCRIPT_DIR/setup-minio.sh"
else
    echo -e "${YELLOW}⚠️  setup-minio.sh not found, skipping...${NC}"
fi
echo ""

# 3. Firewall setup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Firewall Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "$SCRIPT_DIR/setup-firewall.sh" ]; then
    bash "$SCRIPT_DIR/setup-firewall.sh"
else
    echo -e "${YELLOW}⚠️  setup-firewall.sh not found, skipping...${NC}"
fi
echo ""

# 4. Backup setup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Backup Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "$SCRIPT_DIR/setup-backups.sh" ]; then
    bash "$SCRIPT_DIR/setup-backups.sh"
else
    echo -e "${YELLOW}⚠️  setup-backups.sh not found, skipping...${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Hardening completed!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

