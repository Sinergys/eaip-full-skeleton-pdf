#!/bin/bash
set -e

echo "📊 EAIP Observability Bundle Setup"
echo "===================================="
echo ""

STAGING_DIR="/opt/eaip"
COMPOSE_FILE="$STAGING_DIR/docker-compose.monitoring.yml"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$STAGING_DIR" || exit 1

# Check if ports are available
echo "🔍 Checking if ports are available..."
PORTS=(3000 9090 3100 8080 9100 9115 9093)
PORT_NAMES=("Grafana" "Prometheus" "Loki" "cAdvisor" "Node Exporter" "Blackbox Exporter" "Alertmanager")
PORT_IN_USE=false

for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}❌ Port $PORT ($NAME) is already in use${NC}"
        PORT_IN_USE=true
    else
        echo -e "${GREEN}✅ Port $PORT ($NAME) is available${NC}"
    fi
done

if [ "$PORT_IN_USE" = true ]; then
    echo -e "${RED}❌ Some ports are already in use. Please free them before continuing.${NC}"
    exit 1
fi
echo ""

# Check if main services are running (network must exist)
if ! docker network ls | grep -q "infra_default"; then
    echo -e "${YELLOW}⚠️  Network 'infra_default' not found${NC}"
    echo "Please start main services first:"
    echo "  docker compose -f docker-compose.staging.yml up -d"
    exit 1
fi

# Check if monitoring compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ docker-compose.monitoring.yml not found${NC}"
    echo "Please copy monitoring files to $STAGING_DIR"
    exit 1
fi

# Check if config files exist
echo "📋 Checking required configuration files..."
REQUIRED_FILES=(
    "prometheus.yml"
    "alerts.yml"
    "alertmanager.yml"
    "promtail-config.yml"
    "loki-config.yml"
    "prometheus/blackbox.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$STAGING_DIR/$file" ]; then
        echo -e "${RED}❌ Required file not found: $file${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Found: $file${NC}"
    fi
done

# Create directories if they don't exist
echo ""
echo "📁 Creating required directories..."
mkdir -p "$STAGING_DIR/grafana-datasources"
mkdir -p "$STAGING_DIR/grafana-dashboards"
mkdir -p "$STAGING_DIR/prometheus/rules"
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Pull images
echo "⬇️  Pulling monitoring images..."
docker compose -f "$COMPOSE_FILE" pull
echo ""

# Start services
echo "🚀 Starting monitoring services..."
docker compose -f "$COMPOSE_FILE" up -d
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check status
echo "📊 Container status:"
docker compose -f "$COMPOSE_FILE" ps
echo ""

# Health checks
echo "🏥 Health checks:"

# Prometheus
if curl -fsS http://127.0.0.1:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus is healthy${NC}"
else
    echo -e "${RED}❌ Prometheus health check failed${NC}"
fi

# Grafana
if curl -fsS http://127.0.0.1:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Grafana may still be starting...${NC}"
fi

# Loki
if curl -fsS http://127.0.0.1:3100/ready > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Loki is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Loki may still be starting...${NC}"
fi

# Blackbox Exporter
if curl -fsS http://127.0.0.1:9115/metrics > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Blackbox Exporter is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Blackbox Exporter may still be starting...${NC}"
fi

# cAdvisor
if curl -fsS http://127.0.0.1:8080/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}✅ cAdvisor is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  cAdvisor may still be starting...${NC}"
fi

# Node Exporter
if curl -fsS http://127.0.0.1:9100/metrics > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Node Exporter is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Node Exporter may still be starting...${NC}"
fi

# Alertmanager
if curl -fsS http://127.0.0.1:9093/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Alertmanager is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Alertmanager may still be starting...${NC}"
fi

echo ""
echo -e "${BLUE}🔍 Checking Prometheus targets...${NC}"
sleep 5
TARGETS=$(curl -sS http://127.0.0.1:9090/api/v1/targets 2>/dev/null | grep -o '"health":"[^"]*"' | grep -c '"health":"up"' || echo "0")
echo -e "${GREEN}✅ Prometheus targets UP: $TARGETS${NC}"

echo ""
echo -e "${BLUE}🔍 Testing Blackbox Exporter probes...${NC}"
BLACKBOX_TESTS=(
    "http://gateway-auth:8000/health"
    "http://analytics:8003/health"
)
for target in "${BLACKBOX_TESTS[@]}"; do
    PROBE_RESULT=$(curl -sS "http://127.0.0.1:9115/probe?target=$target&module=http_2xx" 2>/dev/null | grep -o 'probe_success 1' || echo "")
    if [ -n "$PROBE_RESULT" ]; then
        echo -e "${GREEN}✅ Probe successful: $target${NC}"
    else
        echo -e "${YELLOW}⚠️  Probe failed or service not available: $target${NC}"
    fi
done

echo ""
echo -e "${GREEN}✅ Observability Bundle setup completed!${NC}"
echo ""
echo "🌐 Access URLs:"
HOST_IP=$(hostname -I | awk '{print $1}' || echo "localhost")
echo "  - Prometheus:     http://$HOST_IP:9090"
echo "  - Grafana:        http://$HOST_IP:3000 (admin/admin)"
echo "  - Alertmanager:   http://$HOST_IP:9093"
echo "  - Loki:           http://$HOST_IP:3100"
echo "  - Blackbox:       http://$HOST_IP:9115"
echo "  - cAdvisor:       http://$HOST_IP:8080"
echo "  - Node Exporter:  http://$HOST_IP:9100/metrics"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Change Grafana admin password on first login!${NC}"
echo ""
echo -e "${BLUE}📊 Next steps:${NC}"
echo "  1. Open Grafana and verify datasources (Prometheus, Loki)"
echo "  2. Check EAIP Dashboards folder in Grafana"
echo "  3. Verify alerts in Prometheus → Alerts"
echo "  4. Test alert by stopping a service temporarily"
echo ""

