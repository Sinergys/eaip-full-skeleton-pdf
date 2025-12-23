# 🚀 Быстрый локальный запуск EAIP Mini-Production

## Запуск за 3 команды

```bash
cd /opt/eaip/infra  # или ~/eaip/infra

chmod +x launch-local-mini-prod.sh
bash launch-local-mini-prod.sh
```

## Что запускается

- ✅ 7 EAIP сервисов (порты 8000-8006)
- ✅ PostgreSQL, Redis, MinIO
- ✅ Prometheus, Grafana, Loki, Alertmanager
- ✅ cAdvisor, Node Exporter, Blackbox Exporter

## Доступ

- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **EAIP Services:** http://localhost:8000-8006/health

## Остановка

```bash
cd monitoring && docker compose -f docker-compose.local.monitoring.yml down
cd .. && docker compose -f docker-compose.local.yml down
```

---

**Подробности:** [LOCAL_MINI_PROD.md](LOCAL_MINI_PROD.md)

