# 🚀 Финальный запуск Production Observability

## Выполнение на production сервере

```bash
ssh user@prod-host

cd /opt/eaip/infra/monitoring

chmod +x launch-prod-observability.sh

bash launch-prod-observability.sh
```

## Проверки после запуска

### Автоматическая проверка

```bash
chmod +x verify-deployment.sh
bash verify-deployment.sh
```

### Ручные проверки

```bash
# Статус контейнеров
docker compose -f docker-compose.prod.monitoring.yml ps

# Health checks
curl -fsS http://127.0.0.1:9090/-/healthy  # Prometheus
curl -fsS http://127.0.0.1:9093/api/v2/status  # Alertmanager
curl -fsS http://127.0.0.1:3100/ready  # Loki
curl -fsS http://127.0.0.1:3000/api/health  # Grafana
curl -fsS http://127.0.0.1:9115/metrics  # Blackbox Exporter
```

## Ожидаемый результат

✅ **Все контейнеры `Up`**
```bash
docker compose -f docker-compose.prod.monitoring.yml ps
# Все должны быть в статусе "Up"
```

✅ **Prometheus / Grafana / Alertmanager доступны**
- Prometheus: http://127.0.0.1:9090 или https://domain/prometheus
- Grafana: http://127.0.0.1:3000 или https://domain
- Alertmanager: http://127.0.0.1:9093 или https://domain/alertmanager

✅ **`/health` сервисов = OK**
```bash
# Проверка через Blackbox
curl -fsS "http://127.0.0.1:9115/probe?target=http://gateway-auth:8000/health&module=http_2xx" | grep probe_success
# Должно быть: probe_success 1
```

✅ **Алерты работают (Telegram уведомления приходят)**
```bash
# Проверка алертов в Prometheus
curl -fsS http://127.0.0.1:9090/api/v1/alerts | jq '.data.alerts[]?.labels.alertname'

# Тест: остановить сервис на 2 минуты
docker compose -f ../docker-compose.staging.yml stop recommend
sleep 120
# Проверить, что алерт появился и Telegram уведомление пришло
docker compose -f ../docker-compose.staging.yml start recommend
```

## Troubleshooting

### Если контейнеры не запускаются
```bash
docker compose -f docker-compose.prod.monitoring.yml logs
```

### Если HTTPS не работает
```bash
docker logs caddy-prod
# Проверьте, что домен указывает на сервер
dig your-domain.com
```

### Если алерты не работают
```bash
docker logs alertmanager-prod
# Проверьте Telegram токены в .env.prod.monitoring
cat .env.prod.monitoring | grep TELEGRAM
```

---

**Готово к запуску!** 🚀

