#!/bin/bash
set -e

echo "🔍 Production Observability - Verification Script"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

cd /opt/eaip/infra/monitoring || exit 1

# Load domain from .env
if [ -f ".env.prod.monitoring" ]; then
    DOMAIN=$(grep ^DOMAIN .env.prod.monitoring | cut -d= -f2)
else
    DOMAIN="localhost"
fi

echo -e "${BLUE}📊 Step 1: Container Status${NC}"
docker compose -f docker-compose.prod.monitoring.yml ps

echo ""
echo -e "${BLUE}🏥 Step 2: Health Checks${NC}"

# Prometheus
if curl -fsS http://127.0.0.1:9090/-/healthy >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus healthy${NC}"
else
    echo -e "${RED}❌ Prometheus health check failed${NC}"
fi

# Alertmanager
if curl -fsS http://127.0.0.1:9093/api/v2/status >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Alertmanager accessible${NC}"
else
    echo -e "${RED}❌ Alertmanager check failed${NC}"
fi

# Loki
if curl -fsS http://127.0.0.1:3100/ready >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Loki ready${NC}"
else
    echo -e "${RED}❌ Loki check failed${NC}"
fi

# Grafana
if curl -fsS http://127.0.0.1:3000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Grafana may still be starting...${NC}"
fi

# Blackbox Exporter
if curl -fsS http://127.0.0.1:9115/metrics >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Blackbox Exporter accessible${NC}"
else
    echo -e "${RED}❌ Blackbox Exporter check failed${NC}"
fi

echo ""
echo -e "${BLUE}🌐 Step 3: HTTPS Access (if domain configured)${NC}"
if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "obs.example.com" ] && [ "$DOMAIN" != "localhost" ]; then
    # Grafana
    if curl -fsS "https://$DOMAIN/" -I >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Grafana HTTPS: https://$DOMAIN${NC}"
    else
        echo -e "${YELLOW}⚠️  Grafana HTTPS not accessible (SSL may still be provisioning)${NC}"
    fi
    
    # Prometheus
    if curl -fsS "https://$DOMAIN/prometheus/-/healthy" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Prometheus HTTPS: https://$DOMAIN/prometheus${NC}"
    else
        echo -e "${YELLOW}⚠️  Prometheus HTTPS not accessible${NC}"
    fi
    
    # Alertmanager
    if curl -fsS "https://$DOMAIN/alertmanager/api/v2/status" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Alertmanager HTTPS: https://$DOMAIN/alertmanager${NC}"
    else
        echo -e "${YELLOW}⚠️  Alertmanager HTTPS not accessible${NC}"
    fi
    
    # Loki
    if curl -fsS "https://$DOMAIN/loki/ready" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Loki HTTPS: https://$DOMAIN/loki${NC}"
    else
        echo -e "${YELLOW}⚠️  Loki HTTPS not accessible${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Domain not configured, skipping HTTPS checks${NC}"
fi

echo ""
echo -e "${BLUE}📈 Step 4: Prometheus Targets${NC}"
TARGETS_UP=$(curl -sS http://127.0.0.1:9090/api/v1/targets 2>/dev/null | grep -o '"health":"up"' | wc -l || echo "0")
echo -e "${GREEN}✅ Prometheus targets UP: $TARGETS_UP${NC}"

echo ""
echo -e "${BLUE}🔍 Step 5: Blackbox Probes${NC}"
PROBES_SUCCESS=$(curl -sS http://127.0.0.1:9115/metrics 2>/dev/null | grep -c "probe_success 1" || echo "0")
echo -e "${GREEN}✅ Successful probes: $PROBES_SUCCESS${NC}"

echo ""
echo -e "${BLUE}🚨 Step 6: Alert Rules${NC}"
ALERTS_COUNT=$(curl -sS http://127.0.0.1:9090/api/v1/alerts 2>/dev/null | grep -o '"alertname"' | wc -l || echo "0")
echo -e "${GREEN}✅ Configured alerts: $ALERTS_COUNT${NC}"

echo ""
echo -e "${GREEN}✅ Verification completed!${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "  - Containers: Check status above"
echo "  - Health checks: See results above"
echo "  - HTTPS: https://$DOMAIN (if configured)"
echo "  - Prometheus targets: $TARGETS_UP UP"
echo "  - Blackbox probes: $PROBES_SUCCESS successful"
echo ""

