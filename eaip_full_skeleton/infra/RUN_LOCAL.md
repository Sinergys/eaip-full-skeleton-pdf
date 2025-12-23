# 🚀 Запуск локального mini-production стенда EAIP

## Выполнение

```bash
cd /opt/eaip/infra || cd ~/eaip/infra

chmod +x launch-local-mini-prod.sh

bash launch-local-mini-prod.sh
```

## Проверки после запуска

### Автоматическая проверка

```bash
chmod +x verify-local-deployment.sh
bash verify-local-deployment.sh
```

### Ручные проверки

```bash
# Статус контейнеров
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Health checks
curl http://localhost:8000/health     # gateway-auth
curl http://localhost:8005/health     # reports
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/login      # Grafana

# Все EAIP сервисы
for port in 8000 8001 8002 8003 8004 8005 8006; do
  echo "Testing port $port..."
  curl -s http://localhost:$port/health
  echo ""
done
```

## Ожидаемый результат

✅ **Все контейнеры в статусе Up**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
# Должно быть 18 контейнеров в статусе "Up"
```

✅ **`/health` эндпоинты отвечают `{"status":"ok"}` или `{"service":"...","status":"ok"}`**
```bash
curl http://localhost:8000/health
# Ожидается: {"service":"gateway-auth","status":"ok"} или {"status":"ok"}
```

✅ **Grafana доступна на `http://localhost:3000`**
- Логин: admin
- Пароль: admin (из .env.local.monitoring)

✅ **Prometheus собирает метрики со всех сервисов**
- Откройте: http://localhost:9090/targets
- Все targets должны быть в статусе UP

## Troubleshooting

### Если контейнеры не запускаются

```bash
# Проверить логи
docker compose --env-file .env.local -f docker-compose.local.yml logs

# Проверить статус
docker compose --env-file .env.local -f docker-compose.local.yml ps
```

### Если health checks не проходят

```bash
# Проверить, что сервисы запущены
docker ps | grep eaip-

# Проверить логи конкретного сервиса
docker logs eaip-gateway-auth-local
```

### Если Prometheus не видит сервисы

```bash
# Проверить сеть
docker network inspect monitoring

# Проверить доступность из Prometheus контейнера
docker exec prometheus-local wget -O- http://gateway-auth:8000/health
```

---

**Готово к запуску!** 🚀

