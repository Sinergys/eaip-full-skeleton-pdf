#!/bin/bash
set -e

echo "🔍 Local Mini-Production - Verification"
echo "======================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Container status
echo -e "${BLUE}📊 Container Status:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "eaip-|prometheus|grafana|alertmanager|loki|cadvisor|node-exporter|blackbox" || \
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo -e "${BLUE}🏥 Health Checks:${NC}"

# Gateway-auth
if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    RESPONSE=$(curl -fsS http://localhost:8000/health 2>/dev/null)
    echo -e "${GREEN}✅ gateway-auth: http://localhost:8000/health${NC}"
    echo "   Response: $RESPONSE"
else
    echo -e "${RED}❌ gateway-auth: not accessible${NC}"
fi

# Reports
if curl -fsS http://localhost:8005/health >/dev/null 2>&1; then
    RESPONSE=$(curl -fsS http://localhost:8005/health 2>/dev/null)
    echo -e "${GREEN}✅ reports: http://localhost:8005/health${NC}"
    echo "   Response: $RESPONSE"
else
    echo -e "${RED}❌ reports: not accessible${NC}"
fi

# Prometheus
if curl -fsS http://localhost:9090/-/healthy >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus: http://localhost:9090/-/healthy${NC}"
else
    echo -e "${RED}❌ Prometheus: not accessible${NC}"
fi

# Grafana
if curl -fsS http://localhost:3000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana: http://localhost:3000/api/health${NC}"
elif curl -fsS http://localhost:3000/login >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana: http://localhost:3000/login (accessible)${NC}"
else
    echo -e "${RED}❌ Grafana: not accessible${NC}"
fi

# All EAIP services
echo ""
echo -e "${BLUE}🔍 Checking all EAIP services:${NC}"
SERVICES=("8000:gateway-auth" "8001:ingest" "8002:validate" "8003:analytics" "8004:recommend" "8005:reports" "8006:management")

for service in "${SERVICES[@]}"; do
    PORT=$(echo $service | cut -d: -f1)
    NAME=$(echo $service | cut -d: -f2)
    if curl -fsS "http://localhost:$PORT/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $NAME (port $PORT)${NC}"
    else
        echo -e "${YELLOW}⚠️  $NAME (port $PORT) - not ready${NC}"
    fi
done

# Prometheus targets
echo ""
echo -e "${BLUE}📈 Prometheus Targets:${NC}"
if command -v jq &> /dev/null; then
    TARGETS_UP=$(curl -sS http://localhost:9090/api/v1/targets 2>/dev/null | jq '.data.activeTargets[] | select(.health=="up") | .labels.job' | wc -l || echo "0")
    TARGETS_TOTAL=$(curl -sS http://localhost:9090/api/v1/targets 2>/dev/null | jq '.data.activeTargets | length' || echo "0")
    echo -e "${GREEN}✅ Targets UP: $TARGETS_UP / $TARGETS_TOTAL${NC}"
else
    echo -e "${YELLOW}⚠️  jq not installed, skipping target count${NC}"
    echo "   Check manually: http://localhost:9090/targets"
fi

# Summary
echo ""
echo -e "${GREEN}✅ Verification completed!${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "  - Check container status above"
echo "  - All health endpoints should be accessible"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo "  - Prometheus: http://localhost:9090"
echo ""

