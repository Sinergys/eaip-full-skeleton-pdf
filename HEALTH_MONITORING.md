# 🏥 Мониторинг здоровья системы АТЛАС

## 📋 Содержание

1. [Health Check эндпоинты](#health-check-эндпоинты)
2. [Метрики системы](#метрики-системы)
3. [Логирование](#логирование)
4. [Алертинг](#алертинг)
5. [Дашборды](#дашборды)

---

## 🔍 Health Check эндпоинты

### Базовые health checks

Все сервисы предоставляют `/health` эндпоинт:

```bash
# Gateway-Auth
curl http://localhost:8000/health

# Ingest
curl http://localhost:8001/health

# Validate
curl http://localhost:8002/health

# Analytics
curl http://localhost:8003/health

# Recommend
curl http://localhost:8004/health

# Reports
curl http://localhost:8005/health

# Management
curl http://localhost:8006/health
```

### Расширенный health check

```bash
# Детальная информация о здоровье системы
curl http://localhost:8001/health/detailed
```

Ответ включает:
- Статус сервиса
- Версия
- Время работы (uptime)
- Использование ресурсов
- Статус зависимостей (БД, Redis, MinIO)

---

## 📊 Метрики системы

### Метрики производительности

```python
# Получение метрик AI кэша
from utils.ai_cache import get_ai_cache
cache = get_ai_cache()
cache_stats = cache.get_stats()

# Получение метрик connection pool
from utils.connection_pool import get_db_pool
pool = get_db_pool()
pool_stats = pool.get_pool_stats()
```

### Метрики обработки файлов

```bash
# Количество обработанных файлов
curl http://localhost:8001/metrics/files/processed

# Среднее время обработки
curl http://localhost:8001/metrics/processing/time

# Количество ошибок
curl http://localhost:8001/metrics/errors
```

### Метрики AI

```bash
# Статистика AI запросов
curl http://localhost:8001/metrics/ai/requests

# Использование токенов
curl http://localhost:8001/metrics/ai/tokens

# Стоимость API (если применимо)
curl http://localhost:8001/metrics/ai/cost
```

---

## 📝 Логирование

### Конфигурация логирования

Логи настраиваются через переменные окружения:

```bash
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json             # json или text
LOG_FILE=/var/log/eaip/app.log
LOG_MAX_SIZE=10485760      # 10 MB
LOG_BACKUP_COUNT=5
```

### Структура логов

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "ingest",
  "message": "File processed successfully",
  "batch_id": "123e4567-e89b-12d3-a456-426614174000",
  "file_type": "pdf",
  "processing_time": 5.23
}
```

### Просмотр логов

```bash
# Все логи
docker compose -f docker-compose.prod.yml logs -f

# Логи конкретного сервиса
docker compose -f docker-compose.prod.yml logs -f ingest

# Логи с фильтром
docker compose -f docker-compose.prod.yml logs ingest | grep ERROR

# Последние 100 строк
docker compose -f docker-compose.prod.yml logs --tail=100 ingest
```

---

## 🚨 Алертинг

### Настройка алертов

Создайте скрипт для мониторинга и алертинга:

```bash
#!/bin/bash
# scripts/health_check.sh

SERVICES=("gateway-auth:8000" "ingest:8001" "validate:8002")
ALERT_EMAIL="admin@example.com"

for service in "${SERVICES[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if ! curl -f -s "http://localhost:$port/health" > /dev/null; then
        echo "ALERT: Service $name is down!" | mail -s "Service Alert" $ALERT_EMAIL
    fi
done
```

### Критерии алертов

1. **Сервис недоступен** - HTTP статус != 200
2. **Высокое использование памяти** - > 80% от лимита
3. **Высокое использование CPU** - > 90% в течение 5 минут
4. **Ошибки обработки** - > 10 ошибок в минуту
5. **Медленная обработка** - среднее время > 30 секунд

### Настройка cron для проверок

```bash
# Проверка каждые 5 минут
*/5 * * * * /path/to/scripts/health_check.sh
```

---

## 📈 Дашборды

### Prometheus метрики (опционально)

Если используется Prometheus, добавьте экспорт метрик:

```python
# В main.py
from prometheus_client import Counter, Histogram, generate_latest

files_processed = Counter('files_processed_total', 'Total processed files')
processing_time = Histogram('processing_time_seconds', 'Processing time')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Grafana дашборд

Пример конфигурации Grafana для визуализации метрик:

```json
{
  "dashboard": {
    "title": "АТЛАС System Metrics",
    "panels": [
      {
        "title": "Files Processed",
        "targets": [
          {
            "expr": "rate(files_processed_total[5m])"
          }
        ]
      },
      {
        "title": "Processing Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, processing_time_seconds_bucket)"
          }
        ]
      }
    ]
  }
}
```

---

## 🔧 Ручной мониторинг

### Проверка статуса контейнеров

```bash
# Статус всех контейнеров
docker compose -f docker-compose.prod.yml ps

# Использование ресурсов
docker stats

# Проверка здоровья через Docker
docker inspect --format='{{.State.Health.Status}}' <container_name>
```

### Проверка базовых сервисов

```bash
# PostgreSQL
docker compose -f docker-compose.prod.yml exec postgres pg_isready -U eaip_user

# Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli -a $REDIS_PASSWORD ping

# MinIO
curl http://localhost:9000/minio/health/live
```

### Проверка дискового пространства

```bash
# Использование диска
df -h

# Размер данных
du -sh infra/data/*
```

---

## 📋 Чеклист мониторинга

- [ ] Health checks настроены и работают
- [ ] Логирование настроено и ротируется
- [ ] Метрики собираются и доступны
- [ ] Алерты настроены и тестируются
- [ ] Дашборды созданы и обновляются
- [ ] Резервное копирование работает
- [ ] Документация актуальна

---

## 🆘 Что делать при проблемах

1. **Проверьте логи** - начните с логов проблемного сервиса
2. **Проверьте health checks** - убедитесь что все сервисы доступны
3. **Проверьте ресурсы** - CPU, память, диск
4. **Проверьте зависимости** - БД, Redis, MinIO
5. **См. TROUBLESHOOTING.md** - для детальной диагностики

---

**Важно**: Регулярно проверяйте здоровье системы и реагируйте на алерты своевременно!

