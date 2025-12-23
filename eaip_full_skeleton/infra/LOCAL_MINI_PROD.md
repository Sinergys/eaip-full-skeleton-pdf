# 🚀 Локальный Mini-Production запуск EAIP

## Обзор

Полный запуск EAIP системы локально с мониторингом, имитирующий production-среду.

**Включает:**
- 7 EAIP сервисов (gateway-auth, ingest, validate, analytics, recommend, reports, management)
- Инфраструктура (PostgreSQL, Redis, MinIO)
- Полный мониторинг (Prometheus, Grafana, Loki, Alertmanager, cAdvisor, Node Exporter, Blackbox)

---

## 🚀 Быстрый старт

### Автоматический запуск

```bash
cd /opt/eaip/infra  # или ~/eaip/infra
chmod +x launch-local-mini-prod.sh
bash launch-local-mini-prod.sh
```

### Ручной запуск

#### 1. Подготовка

```bash
cd /opt/eaip/infra  # или ~/eaip/infra

# Создать .env.local
cp .env.local.example .env.local
# Отредактировать при необходимости

# Создать monitoring .env
cd monitoring
cp .env.local.monitoring.example .env.local.monitoring
cd ..
```

#### 2. Создание сети

```bash
docker network create monitoring || true
```

#### 3. Запуск EAIP сервисов

```bash
docker compose --env-file .env.local -f docker-compose.local.yml up -d
```

#### 4. Запуск мониторинга

```bash
cd monitoring
docker compose --env-file .env.local.monitoring -f docker-compose.local.monitoring.yml up -d
cd ..
```

#### 5. Проверки

```bash
# Статус контейнеров
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Health checks
curl http://localhost:8000/health     # gateway-auth
curl http://localhost:9090/-/healthy  # prometheus
curl http://localhost:3000/api/health # grafana
```

---

## 🌐 Доступ к сервисам

### EAIP Сервисы
- Gateway Auth: http://localhost:8000/health
- Ingest: http://localhost:8001/health
- Validate: http://localhost:8002/health
- Analytics: http://localhost:8003/health
- Recommend: http://localhost:8004/health
- Reports: http://localhost:8005/health
- Management: http://localhost:8006/health

### Мониторинг
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093
- Loki: http://localhost:3100
- cAdvisor: http://localhost:8080
- Node Exporter: http://localhost:9100/metrics
- Blackbox Exporter: http://localhost:9115/metrics

### Инфраструктура
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)
- MinIO API: http://localhost:9000

---

## 📊 Проверка мониторинга

### Prometheus Targets

```bash
# Откройте в браузере
http://localhost:9090/targets

# Или через curl
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

### Grafana Dashboards

1. Откройте http://localhost:3000
2. Войдите (admin/admin)
3. Перейдите в Dashboards → Browse
4. Откройте "EAIP Services Overview"

### Логи в Grafana

1. Откройте Grafana → Explore
2. Выберите datasource: Loki
3. Используйте запрос: `{container=~"eaip-.*"}`

---

## 🛑 Остановка

```bash
# Остановить мониторинг
cd monitoring
docker compose -f docker-compose.local.monitoring.yml down

# Остановить EAIP сервисы
cd ..
docker compose -f docker-compose.local.yml down

# Удалить volumes (опционально)
docker volume prune -f
```

---

## 🔧 Troubleshooting

### Сервисы не запускаются

```bash
# Проверить логи
docker compose -f docker-compose.local.yml logs

# Проверить статус
docker compose -f docker-compose.local.yml ps
```

### Мониторинг не видит сервисы

```bash
# Проверить сеть
docker network inspect monitoring

# Проверить, что сервисы в сети
docker network inspect monitoring | grep -A 5 "eaip-"
```

### Prometheus targets DOWN

```bash
# Проверить конфигурацию
docker exec prometheus-local cat /etc/prometheus/prometheus.yml

# Проверить доступность сервисов из Prometheus
docker exec prometheus-local wget -O- http://gateway-auth:8000/health
```

---

## 📁 Структура файлов

```
infra/
├── docker-compose.local.yml              # EAIP сервисы для локального запуска
├── .env.local.example                    # Пример переменных окружения
├── launch-local-mini-prod.sh            # Скрипт автоматического запуска
└── monitoring/
    ├── docker-compose.local.monitoring.yml  # Мониторинг для локального запуска
    ├── .env.local.monitoring.example        # Пример переменных мониторинга
    └── prometheus/
        └── prometheus.local.yml             # Prometheus конфигурация для локального использования
```

---

## ✅ Ожидаемый результат

- ✅ Все 10 сервисов EAIP работают локально
- ✅ Мониторинг собирает метрики
- ✅ Доступ к Grafana → http://localhost:3000
- ✅ Все `/health` эндпоинты = OK
- ✅ Prometheus targets в статусе UP
- ✅ Dashboards отображают данные

---

**Версия:** v0.3.0  
**Дата:** 2025-11-08

