#!/bin/bash
set -e

echo "🚀 Production Observability Bundle - Launch Script"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1) Сервер и подготовка
echo -e "${BLUE}📁 Step 1: Preparing directories...${NC}"
cd /opt/eaip || { echo -e "${RED}❌ /opt/eaip not found${NC}"; exit 1; }

mkdir -p infra || true
if [ -d "./monitoring" ] && [ ! -d "./infra/monitoring" ]; then
    echo -e "${BLUE}📦 Copying monitoring directory...${NC}"
    cp -r ./monitoring ./infra/monitoring || true
fi

cd infra/monitoring || { echo -e "${RED}❌ infra/monitoring not found${NC}"; exit 1; }

if [ ! -f ".env.prod.monitoring" ]; then
    if [ -f ".env.prod.monitoring.example" ]; then
        echo -e "${BLUE}📝 Creating .env.prod.monitoring from example...${NC}"
        cp .env.prod.monitoring.example .env.prod.monitoring
        echo -e "${YELLOW}⚠️  Please update .env.prod.monitoring with real values!${NC}"
    else
        echo -e "${RED}❌ .env.prod.monitoring.example not found${NC}"
        exit 1
    fi
fi

# 2) Заполнить переменные (единоразово)
echo ""
echo -e "${BLUE}⚙️  Step 2: Checking environment variables...${NC}"
DOMAIN=$(grep ^DOMAIN .env.prod.monitoring | cut -d= -f2)
TELEGRAM_TOKEN=$(grep ^TELEGRAM_BOT_TOKEN .env.prod.monitoring | cut -d= -f2)
TELEGRAM_CHAT=$(grep ^TELEGRAM_CHAT_ID .env.prod.monitoring | cut -d= -f2)

if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "obs.example.com" ]; then
    echo -e "${YELLOW}⚠️  DOMAIN not configured. Update .env.prod.monitoring${NC}"
    echo "   sed -i 's/DOMAIN=.*/DOMAIN=your-domain.com/' .env.prod.monitoring"
fi

if [ -z "$TELEGRAM_TOKEN" ] || [ "$TELEGRAM_TOKEN" = "<PUT_TOKEN>" ]; then
    echo -e "${YELLOW}⚠️  TELEGRAM_BOT_TOKEN not configured. Alerts will not work.${NC}"
    echo "   sed -i 's/TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=your_token/' .env.prod.monitoring"
fi

if [ -z "$TELEGRAM_CHAT" ] || [ "$TELEGRAM_CHAT" = "<PUT_CHAT_ID>" ]; then
    echo -e "${YELLOW}⚠️  TELEGRAM_CHAT_ID not configured. Alerts will not work.${NC}"
    echo "   sed -i 's/TELEGRAM_CHAT_ID=.*/TELEGRAM_CHAT_ID=your_chat_id/' .env.prod.monitoring"
fi

read -p "Press Enter to continue or Ctrl+C to update .env.prod.monitoring first..."

# 3) Сборка финальных конфигов Alertmanager
echo ""
echo -e "${BLUE}📝 Step 3: Processing Alertmanager template...${NC}"
if [ -f "alertmanager/alertmanager.yml.template" ]; then
    source .env.prod.monitoring
    envsubst < alertmanager/alertmanager.yml.template > alertmanager/alertmanager.yml
    echo -e "${GREEN}✅ Alertmanager config processed${NC}"
else
    echo -e "${YELLOW}⚠️  Template not found, using existing alertmanager.yml${NC}"
fi

# 4) Сеть и firewall
echo ""
echo -e "${BLUE}🌐 Step 4: Setting up network and firewall...${NC}"
docker network create monitoring 2>/dev/null || echo -e "${GREEN}✅ Monitoring network already exists${NC}"

echo -e "${BLUE}🔥 Configuring firewall...${NC}"
sudo ufw allow 22 2>/dev/null || true
sudo ufw allow 80 2>/dev/null || true
sudo ufw allow 443 2>/dev/null || true
sudo ufw deny 9090 2>/dev/null || true
sudo ufw deny 9093 2>/dev/null || true
sudo ufw deny 3100 2>/dev/null || true
sudo ufw deny 9115 2>/dev/null || true
sudo ufw deny 3000 2>/dev/null || true
sudo ufw --force enable 2>/dev/null || echo -e "${YELLOW}⚠️  UFW not available or already enabled${NC}"

# 5) Запуск
echo ""
echo -e "${BLUE}🚀 Step 5: Starting services...${NC}"
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml pull
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml up -d

echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 15

# 6) Подключить app-контейнеры к сети monitoring
echo ""
echo -e "${BLUE}🔗 Step 6: Connecting app containers to monitoring network...${NC}"
SERVICES=("gateway-auth" "ingest" "validate" "analytics" "recommend" "reports" "management")

for service in "${SERVICES[@]}"; do
    # Try to find container by service name or common naming patterns
    CONTAINER=$(docker ps --filter "name=$service" --format "{{.Names}}" | head -n1)
    if [ -n "$CONTAINER" ]; then
        docker network connect monitoring "$CONTAINER" 2>/dev/null && \
            echo -e "${GREEN}✅ Connected: $CONTAINER${NC}" || \
            echo -e "${YELLOW}⚠️  Already connected or not found: $service${NC}"
    else
        echo -e "${YELLOW}⚠️  Container not found: $service (may not be running)${NC}"
    fi
done

# 7) Смоук-проверки
echo ""
echo -e "${BLUE}🧪 Step 7: Smoke tests...${NC}"
DOMAIN=$(grep ^DOMAIN .env.prod.monitoring | cut -d= -f2)

echo -e "${BLUE}📊 Container status:${NC}"
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml ps

echo ""
echo -e "${BLUE}🏥 Internal health checks:${NC}"

# Prometheus
if curl -fsS http://127.0.0.1:9090/-/healthy >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus healthy (http://127.0.0.1:9090/-/healthy)${NC}"
else
    echo -e "${RED}❌ Prometheus health check failed${NC}"
fi

# Alertmanager
if curl -fsS http://127.0.0.1:9093/api/v2/status >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Alertmanager accessible (http://127.0.0.1:9093/api/v2/status)${NC}"
else
    echo -e "${RED}❌ Alertmanager check failed${NC}"
fi

# Loki
if curl -fsS http://127.0.0.1:3100/ready >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Loki ready (http://127.0.0.1:3100/ready)${NC}"
else
    echo -e "${RED}❌ Loki check failed${NC}"
fi

# Grafana
if curl -fsS http://127.0.0.1:3000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana healthy (http://127.0.0.1:3000/api/health)${NC}"
else
    echo -e "${YELLOW}⚠️  Grafana may still be starting...${NC}"
fi

# HTTPS checks (if domain configured)
if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "obs.example.com" ] && [ "$DOMAIN" != "localhost" ]; then
    echo ""
    echo -e "${BLUE}🌐 HTTPS endpoint checks:${NC}"
    
    # Grafana
    if curl -fsS "https://$DOMAIN/" -I >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Grafana HTTPS: https://$DOMAIN${NC}"
    else
        echo -e "${YELLOW}⚠️  Grafana HTTPS not accessible yet (SSL may still be provisioning)${NC}"
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
    echo -e "${YELLOW}⚠️  DOMAIN not configured, skipping HTTPS checks${NC}"
fi

# 8) Grafana: первичный вход
echo ""
echo -e "${BLUE}🔐 Step 8: Grafana setup${NC}"
ADMIN_PASSWORD=$(grep ^GF_SECURITY_ADMIN_PASSWORD .env.prod.monitoring | cut -d= -f2)
echo -e "${GREEN}✅ Grafana URL: https://$DOMAIN${NC}"
echo -e "${GREEN}   Username: admin${NC}"
echo -e "${GREEN}   Password: (check .env.prod.monitoring)${NC}"
echo -e "${YELLOW}⚠️  IMPORTANT: Change password on first login!${NC}"

# 9) Тест алертов
echo ""
echo -e "${BLUE}🚨 Step 9: Alert testing${NC}"
read -p "Do you want to test alerts by stopping a service? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Stopping recommend service for 150 seconds...${NC}"
    if [ -f "../docker-compose.staging.yml" ]; then
        docker compose -f ../docker-compose.staging.yml stop recommend 2>/dev/null || \
        docker stop recommend 2>/dev/null || \
        echo -e "${YELLOW}⚠️  Could not stop recommend service${NC}"
        
        echo -e "${BLUE}Waiting 150 seconds for alert to trigger...${NC}"
        sleep 150
        
        echo -e "${BLUE}Checking alerts...${NC}"
        if command -v jq &> /dev/null; then
            curl -fsS "https://$DOMAIN/prometheus/api/v1/alerts" 2>/dev/null | \
                jq '.data.alerts[]?.labels.alertname' | grep -q EAIPServiceDown && \
                echo -e "${GREEN}✅ Alert triggered!${NC}" || \
                echo -e "${YELLOW}⚠️  Alert not found in response${NC}"
        else
            echo -e "${YELLOW}⚠️  jq not installed, skipping alert check${NC}"
        fi
        
        echo -e "${BLUE}Restarting recommend service...${NC}"
        docker compose -f ../docker-compose.staging.yml start recommend 2>/dev/null || \
        docker start recommend 2>/dev/null || \
        echo -e "${YELLOW}⚠️  Could not restart recommend service${NC}"
    else
        echo -e "${YELLOW}⚠️  docker-compose.staging.yml not found${NC}"
    fi
else
    echo -e "${BLUE}Skipping alert test${NC}"
fi

# 10) Фиксация
echo ""
echo -e "${BLUE}💾 Step 10: Git commit${NC}"
read -p "Do you want to commit changes to git? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add . 2>/dev/null || echo -e "${YELLOW}⚠️  Not a git repository${NC}"
    git commit -m "deploy: Production Observability Bundle — launch & alerts enabled" 2>/dev/null || \
        echo -e "${YELLOW}⚠️  Nothing to commit or not a git repository${NC}"
    git push origin main 2>/dev/null || \
        echo -e "${YELLOW}⚠️  Push failed or not configured${NC}"
else
    echo -e "${BLUE}Skipping git commit${NC}"
fi

# Итог
echo ""
echo -e "${GREEN}✅ Production Observability Bundle deployment completed!${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "  - Monitoring services: Running"
echo "  - HTTPS: https://$DOMAIN"
echo "  - Grafana: https://$DOMAIN (admin/<password>)"
echo "  - Prometheus: https://$DOMAIN/prometheus"
echo "  - Alertmanager: https://$DOMAIN/alertmanager"
echo "  - Loki: https://$DOMAIN/loki"
echo ""
echo -e "${YELLOW}⚠️  Next steps:${NC}"
echo "  1. Open Grafana and change admin password"
echo "  2. Verify SSL certificate is issued (may take a few minutes)"
echo "  3. Check dashboards are loading data"
echo "  4. Test Telegram alerts by stopping a service"
echo ""

