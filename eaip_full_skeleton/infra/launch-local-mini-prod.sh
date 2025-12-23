#!/bin/bash
set -e

echo "🚀 EAIP Local Mini-Production Launch"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect working directory
if [ -d "/opt/eaip/infra" ]; then
    WORK_DIR="/opt/eaip/infra"
elif [ -d "$HOME/eaip/infra" ]; then
    WORK_DIR="$HOME/eaip/infra"
else
    WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

cd "$WORK_DIR" || exit 1
echo -e "${BLUE}📁 Working directory: $WORK_DIR${NC}"
echo ""

# 1️⃣ Подготовка окружения
echo -e "${BLUE}📋 Step 1: Preparing environment...${NC}"

# Create .env.local if not exists
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}⚠️  Creating .env.local...${NC}"
    cat > .env.local <<'ENV'
POSTGRES_USER=eaip_user
POSTGRES_PASSWORD=local_secure_pass
POSTGRES_DB=eaip_db
POSTGRES_HOST=postgres

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
ENV
    echo -e "${GREEN}✅ Created .env.local${NC}"
else
    echo -e "${GREEN}✅ .env.local exists${NC}"
fi

# Create monitoring .env if not exists
if [ ! -f "monitoring/.env.local.monitoring" ]; then
    echo -e "${YELLOW}⚠️  Creating monitoring/.env.local.monitoring...${NC}"
    cat > monitoring/.env.local.monitoring <<'ENV'
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
PROM_RETENTION=7d
PROM_MEMORY_TARGET=1GB
LOKI_RETENTION_DAYS=7
DOMAIN=localhost

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
ENV
    echo -e "${GREEN}✅ Created monitoring/.env.local.monitoring${NC}"
else
    echo -e "${GREEN}✅ monitoring/.env.local.monitoring exists${NC}"
fi

# 2️⃣ Создание monitoring сети
echo ""
echo -e "${BLUE}🌐 Step 2: Creating monitoring network...${NC}"
docker network create monitoring 2>/dev/null && \
    echo -e "${GREEN}✅ Monitoring network created${NC}" || \
    echo -e "${GREEN}✅ Monitoring network already exists${NC}"

# 3️⃣ Запуск EAIP-core сервисов
echo ""
echo -e "${BLUE}🚀 Step 3: Starting EAIP core services...${NC}"
docker compose --env-file .env.local -f docker-compose.local.yml pull
docker compose --env-file .env.local -f docker-compose.local.yml up -d

echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 10

# 4️⃣ Запуск мониторинга
echo ""
echo -e "${BLUE}📊 Step 4: Starting monitoring stack...${NC}"
cd monitoring || exit 1

if [ -f ".env.local.monitoring" ]; then
    ENV_FILE=".env.local.monitoring"
else
    ENV_FILE=".env.local.monitoring.example"
fi

docker compose --env-file "$ENV_FILE" -f docker-compose.local.monitoring.yml pull
docker compose --env-file "$ENV_FILE" -f docker-compose.local.monitoring.yml up -d

echo -e "${BLUE}⏳ Waiting for monitoring to start...${NC}"
sleep 15

cd ..

# 5️⃣ Проверки
echo ""
echo -e "${BLUE}🧪 Step 5: Health checks...${NC}"

# Container status
echo -e "${BLUE}📊 Container status:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "eaip-|prometheus|grafana|alertmanager|loki|cadvisor|node-exporter|blackbox" || \
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo -e "${BLUE}🏥 Service health checks:${NC}"

# Gateway-auth
if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ gateway-auth: http://localhost:8000/health${NC}"
else
    echo -e "${YELLOW}⚠️  gateway-auth: not ready yet${NC}"
fi

# Prometheus
if curl -fsS http://localhost:9090/-/healthy >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus: http://localhost:9090/-/healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Prometheus: not ready yet${NC}"
fi

# Grafana
if curl -fsS http://localhost:3000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana: http://localhost:3000/api/health${NC}"
else
    echo -e "${YELLOW}⚠️  Grafana: not ready yet${NC}"
fi

# Alertmanager
if curl -fsS http://localhost:9093/api/v2/status >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Alertmanager: http://localhost:9093/api/v2/status${NC}"
else
    echo -e "${YELLOW}⚠️  Alertmanager: not ready yet${NC}"
fi

# Loki
if curl -fsS http://localhost:3100/ready >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Loki: http://localhost:3100/ready${NC}"
else
    echo -e "${YELLOW}⚠️  Loki: not ready yet${NC}"
fi

# 6️⃣ Smoke-тест
echo ""
echo -e "${BLUE}💨 Step 6: Smoke test - checking logs...${NC}"
echo -e "${BLUE}Recent logs from EAIP services:${NC}"
docker compose --env-file .env.local -f docker-compose.local.yml logs --tail 20 gateway-auth ingest 2>/dev/null || \
    docker compose --env-file .env.local -f docker-compose.local.yml logs --tail 10 2>/dev/null | head -20

# Итог
echo ""
echo -e "${GREEN}✅ Local Mini-Production deployment completed!${NC}"
echo ""
echo -e "${BLUE}🌐 Access URLs:${NC}"
echo "  - Gateway Auth:    http://localhost:8000/health"
echo "  - Ingest:          http://localhost:8001/health"
echo "  - Validate:        http://localhost:8002/health"
echo "  - Analytics:       http://localhost:8003/health"
echo "  - Recommend:       http://localhost:8004/health"
echo "  - Reports:         http://localhost:8005/health"
echo "  - Management:      http://localhost:8006/health"
echo ""
echo "  - Grafana:         http://localhost:3000 (admin/admin)"
echo "  - Prometheus:      http://localhost:9090"
echo "  - Alertmanager:    http://localhost:9093"
echo "  - Loki:            http://localhost:3100"
echo "  - cAdvisor:        http://localhost:8080"
echo ""
echo -e "${YELLOW}⚠️  Next steps:${NC}"
echo "  1. Open Grafana and verify dashboards"
echo "  2. Check Prometheus targets: http://localhost:9090/targets"
echo "  3. Verify all services are healthy"
echo ""

