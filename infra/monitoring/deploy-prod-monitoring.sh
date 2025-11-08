#!/bin/bash
set -e

echo "🚀 EAIP Production Observability Deployment"
echo "============================================"
echo ""

MONITORING_DIR="/opt/eaip/infra/monitoring"
ENV_FILE="$MONITORING_DIR/.env.prod.monitoring"
COMPOSE_FILE="$MONITORING_DIR/docker-compose.prod.monitoring.yml"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$MONITORING_DIR" || exit 1

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ .env.prod.monitoring not found${NC}"
    echo "Please create .env.prod.monitoring file with required variables"
    exit 1
fi

# Source environment variables
set -a
source "$ENV_FILE"
set +a

# Check required variables
if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "obs.example.com" ]; then
    echo -e "${YELLOW}⚠️  DOMAIN not set or using default. Please update .env.prod.monitoring${NC}"
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "<PUT_TOKEN>" ]; then
    echo -e "${YELLOW}⚠️  TELEGRAM_BOT_TOKEN not set. Alerts will not work.${NC}"
fi

# Check if monitoring network exists
if ! docker network ls | grep -q "^.* monitoring "; then
    echo -e "${BLUE}📡 Creating monitoring network...${NC}"
    docker network create monitoring || true
else
    echo -e "${GREEN}✅ Monitoring network exists${NC}"
fi

# Process alertmanager.yml template if exists
if [ -f "$MONITORING_DIR/alertmanager/alertmanager.yml.template" ]; then
    echo -e "${BLUE}📝 Processing alertmanager.yml template...${NC}"
    envsubst < "$MONITORING_DIR/alertmanager/alertmanager.yml.template" > "$MONITORING_DIR/alertmanager/alertmanager.yml"
fi

# Check ports
echo -e "${BLUE}🔍 Checking ports...${NC}"
PORTS=(80 443)
PORT_NAMES=("HTTP" "HTTPS")
PORT_IN_USE=false

for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠️  Port $PORT ($NAME) is already in use${NC}"
        PORT_IN_USE=true
    else
        echo -e "${GREEN}✅ Port $PORT ($NAME) is available${NC}"
    fi
done

# Check required files
echo -e "${BLUE}📋 Checking required files...${NC}"
REQUIRED_FILES=(
    "prometheus/prometheus.yml"
    "prometheus/blackbox.yml"
    "prometheus/rules/health.yml"
    "alertmanager/alertmanager.yml"
    "loki/loki-config.yml"
    "promtail/promtail-config.yml"
    "grafana/provisioning/datasources/datasources.yml"
    "grafana/provisioning/dashboards/dashboards.yml"
    "caddy/Caddyfile"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$MONITORING_DIR/$file" ]; then
        echo -e "${RED}❌ Required file not found: $file${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Found: $file${NC}"
    fi
done

# Pull images
echo ""
echo -e "${BLUE}⬇️  Pulling images...${NC}"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull

# Start services
echo ""
echo -e "${BLUE}🚀 Starting services...${NC}"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d

# Wait for services
echo ""
echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 20

# Health checks
echo ""
echo -e "${BLUE}🏥 Health checks:${NC}"

# Prometheus
if docker exec prometheus-prod wget --quiet --tries=1 --spider http://localhost:9090/-/healthy 2>/dev/null; then
    echo -e "${GREEN}✅ Prometheus is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Prometheus may still be starting...${NC}"
fi

# Grafana
if docker exec grafana-prod wget --quiet --tries=1 --spider http://localhost:3000/api/health 2>/dev/null; then
    echo -e "${GREEN}✅ Grafana is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Grafana may still be starting...${NC}"
fi

# Loki
if docker exec loki-prod wget --quiet --tries=1 --spider http://localhost:3100/ready 2>/dev/null; then
    echo -e "${GREEN}✅ Loki is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Loki may still be starting...${NC}"
fi

# Caddy
if curl -fsS "http://127.0.0.1/.well-known/acme-challenge/test" >/dev/null 2>&1 || curl -fsS "https://$DOMAIN" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Caddy is responding${NC}"
else
    echo -e "${YELLOW}⚠️  Caddy may still be starting or domain not configured...${NC}"
fi

# Status
echo ""
echo -e "${BLUE}📊 Container status:${NC}"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps

echo ""
echo -e "${GREEN}✅ Production Observability deployment completed!${NC}"
echo ""
echo -e "${BLUE}🌐 Access URLs:${NC}"
echo "  - Grafana:        https://$DOMAIN"
echo "  - Prometheus:     https://$DOMAIN/prometheus"
echo "  - Alertmanager:   https://$DOMAIN/alertmanager"
echo "  - Loki:           https://$DOMAIN/loki"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "  1. Change Grafana admin password on first login"
echo "  2. Verify SSL certificate is issued (may take a few minutes)"
echo "  3. Configure firewall: sudo ufw allow 80 && sudo ufw allow 443"
echo "  4. Close internal ports: sudo ufw deny 9090,9093,3100,9115,3000"
echo ""

