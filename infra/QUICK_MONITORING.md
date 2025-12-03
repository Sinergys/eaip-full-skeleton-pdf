# ⚡ Quick Monitoring Setup

## 🚀 Быстрый старт

### Предварительные требования

**Важно:** Основные сервисы должны быть запущены первыми!

```bash
# 1. Запустите основные сервисы
cd /opt/eaip
docker compose -f docker-compose.staging.yml up -d

# 2. Затем запустите мониторинг
bash setup-monitoring.sh
```

### Проверка

```bash
# Статус
docker compose -f docker-compose.monitoring.yml ps

# Health checks
curl -fsS http://127.0.0.1:9090/-/healthy  # Prometheus
curl -fsS http://127.0.0.1:3000/api/health # Grafana
```

### Доступ

- **Prometheus:** http://staging-host:9090
- **Grafana:** http://staging-host:3000 (admin/admin)
- **Alertmanager:** http://staging-host:9093
- **Loki:** http://staging-host:3100

---

## 📊 Что мониторится

- ✅ Все 7 EAIP сервисов (health checks)
- ✅ CPU и память контейнеров
- ✅ Метрики хоста (диск, сеть)
- ✅ Логи всех контейнеров
- ✅ Алерты при недоступности сервисов

---

**Подробная документация:** `MONITORING.md`

