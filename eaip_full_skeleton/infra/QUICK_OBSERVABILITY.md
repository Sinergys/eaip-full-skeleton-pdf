# 🚀 Быстрый старт Observability Bundle

## Развертывание за 3 шага

### 1. Подготовка

```bash
cd /opt/eaip/infra
```

Убедитесь, что основные сервисы запущены:
```bash
docker compose -f docker-compose.staging.yml ps
```

### 2. Запуск мониторинга

```bash
chmod +x setup-monitoring.sh
bash setup-monitoring.sh
```

### 3. Проверка

```bash
# Статус контейнеров
docker compose -f docker-compose.monitoring.yml ps

# Health checks
curl -fsS http://127.0.0.1:9090/-/healthy  # Prometheus
curl -fsS http://127.0.0.1:3000/api/health # Grafana
curl -fsS http://127.0.0.1:9115/metrics    # Blackbox
```

---

## 🌐 Доступ

- **Grafana:** http://your-host:3000 (admin/admin)
- **Prometheus:** http://your-host:9090
- **Alertmanager:** http://your-host:9093

---

## ✅ Что проверить

1. ✅ Все контейнеры в статусе "Up"
2. ✅ Prometheus targets → все UP
3. ✅ Grafana → Datasources настроены
4. ✅ Grafana → Dashboards загружены
5. ✅ Prometheus → Alerts видны

---

## 📚 Подробная документация

См. `OBSERVABILITY_BUNDLE.md` для полного руководства.

