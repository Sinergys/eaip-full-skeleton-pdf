# 📊 EAIP Monitoring & Observability Guide

## Обзор

Полный observability stack для EAIP Full Skeleton staging окружения:
- **Prometheus** - сбор метрик
- **Grafana** - визуализация и дашборды
- **Loki** - агрегация логов
- **Promtail** - сбор логов из контейнеров
- **Alertmanager** - управление алертами
- **cAdvisor** - метрики контейнеров
- **Node Exporter** - метрики хоста

---

## 🚀 Быстрый старт

### 1. Копирование файлов на сервер

```bash
# Скопируйте все файлы мониторинга
scp infra/docker-compose.monitoring.yml \
    infra/prometheus.yml \
    infra/alerts.yml \
    infra/alertmanager.yml \
    infra/promtail-config.yml \
    infra/loki-config.yml \
    infra/setup-monitoring.sh \
    user@staging-host:/opt/eaip/

# Скопируйте Grafana конфигурацию
scp -r infra/grafana-datasources infra/grafana-dashboards \
    user@staging-host:/opt/eaip/
```

### 2. Запуск мониторинга

```bash
ssh user@staging-host
cd /opt/eaip
chmod +x setup-monitoring.sh
bash setup-monitoring.sh
```

### 3. Проверка

```bash
# Статус контейнеров
docker compose -f docker-compose.monitoring.yml ps

# Health check Prometheus
curl -fsS http://127.0.0.1:9090/-/healthy

# Health check Grafana
curl -fsS http://127.0.0.1:3000/api/health
```

---

## 🌐 Доступ к сервисам

### Prometheus
- **URL:** http://staging-host:9090
- **Назначение:** Просмотр метрик, запросы PromQL
- **Примеры запросов:**
  - `up{job="eaip-gateway-auth"}` - статус gateway-auth
  - `rate(container_cpu_usage_seconds_total[5m])` - использование CPU

### Grafana
- **URL:** http://staging-host:3000
- **Логин:** `admin` / `admin` (⚠️ смените пароль!)
- **Назначение:** Дашборды, визуализация метрик и логов
- **Datasources:** Prometheus и Loki настроены автоматически

### Alertmanager
- **URL:** http://staging-host:9093
- **Назначение:** Просмотр и управление алертами

### Loki
- **URL:** http://staging-host:3100
- **Назначение:** API для запросов логов
- **Использование:** Через Grafana Explore

### cAdvisor
- **URL:** http://staging-host:8080
- **Назначение:** Метрики контейнеров Docker

### Node Exporter
- **URL:** http://staging-host:9100/metrics
- **Назначение:** Метрики хоста (CPU, память, диск)

---

## 📈 Мониторинг сервисов

### Health Checks

Все EAIP сервисы мониторятся через Prometheus:
- `eaip-gateway-auth` (порт 8000)
- `eaip-ingest` (порт 8001)
- `eaip-validate` (порт 8002)
- `eaip-analytics` (порт 8003)
- `eaip-recommend` (порт 8004)
- `eaip-reports` (порт 8005)
- `eaip-management` (порт 8006)

### Метрики

Prometheus собирает метрики каждые 15 секунд:
- Health status всех сервисов
- CPU и память контейнеров
- Метрики хоста (диск, сеть)
- Логи всех контейнеров

---

## 🚨 Алерты

### Настроенные алерты

1. **Service Down Alerts** (Critical)
   - Срабатывают, если сервис недоступен более 1 минуты
   - Для всех 7 EAIP сервисов

2. **System Alerts** (Warning)
   - High CPU Usage (>90% в течение 5 минут)
   - High Memory Usage (>90% в течение 5 минут)
   - Low Disk Space (<10%)
   - Container Restarting (частые перезапуски)

### Настройка уведомлений

Отредактируйте `alertmanager.yml` для настройки:
- Email уведомления
- Slack webhooks
- PagerDuty
- Другие интеграции

---

## 📊 Grafana Dashboards

### Предустановленные дашборды

1. **EAIP Services Overview**
   - Статус здоровья сервисов
   - Использование CPU и памяти
   - Графики метрик

### Создание своих дашбордов

1. Войдите в Grafana (admin/admin)
2. Перейдите в Dashboards → New Dashboard
3. Добавьте панели с метриками из Prometheus
4. Сохраните дашборд

### Полезные запросы PromQL

```promql
# Статус всех сервисов
up{job=~"eaip-.*"}

# CPU usage по контейнерам
rate(container_cpu_usage_seconds_total{name=~"infra-.*"}[5m]) * 100

# Memory usage
container_memory_usage_bytes{name=~"infra-.*"} / 1024 / 1024

# Количество перезапусков
rate(container_start_time_seconds{name=~"infra-.*"}[15m])
```

---

## 📝 Логи в Grafana

### Просмотр логов

1. Откройте Grafana → Explore
2. Выберите datasource: **Loki**
3. Используйте LogQL запросы:

```logql
# Логи конкретного сервиса
{service="gateway-auth"}

# Логи с ошибками
{service=~"infra-.*"} |= "error"

# Логи за последний час
{service=~"infra-.*"} [1h]
```

### Фильтры

- По сервису: `{service="gateway-auth"}`
- По контейнеру: `{container="infra-gateway-auth-1"}`
- По уровню: `|= "ERROR"` или `|= "WARN"`

---

## 🔧 Конфигурация

### Prometheus (`prometheus.yml`)

- **Scrape interval:** 15 секунд
- **Retention:** 30 дней
- **Targets:** Все EAIP сервисы + системные метрики

### Alertmanager (`alertmanager.yml`)

- **Group wait:** 10 секунд
- **Repeat interval:** 12 часов
- **Routes:** Critical и Warning раздельно

### Loki (`loki-config.yml`)

- **Retention:** 30 дней (720h)
- **Ingestion rate:** 16 MB/s
- **Compaction:** каждые 10 минут

### Promtail (`promtail-config.yml`)

- Собирает логи из всех Docker контейнеров
- Автоматически определяет сервисы по labels
- Отправляет в Loki

---

## 🛠️ Управление

### Остановка мониторинга

```bash
cd /opt/eaip
docker compose -f docker-compose.monitoring.yml down
```

### Перезапуск

```bash
docker compose -f docker-compose.monitoring.yml restart
```

### Просмотр логов

```bash
# Все сервисы
docker compose -f docker-compose.monitoring.yml logs -f

# Конкретный сервис
docker compose -f docker-compose.monitoring.yml logs -f prometheus
```

### Обновление конфигурации

После изменения конфигурационных файлов:

```bash
# Перезагрузить Prometheus
docker compose -f docker-compose.monitoring.yml restart prometheus

# Перезагрузить Alertmanager
docker compose -f docker-compose.monitoring.yml restart alertmanager

# Перезагрузить Promtail
docker compose -f docker-compose.monitoring.yml restart promtail
```

---

## 🔐 Безопасность

### Рекомендации для production:

1. **Измените пароль Grafana** сразу после первого входа
2. **Настройте HTTPS** через reverse proxy (nginx/traefik)
3. **Ограничьте доступ** к портам мониторинга (firewall)
4. **Настройте аутентификацию** для Prometheus и Grafana
5. **Используйте VPN** для доступа к мониторингу

### Firewall правила

```bash
# Разрешить только локальный доступ
sudo ufw allow from 10.0.0.0/8 to any port 9090  # Prometheus
sudo ufw allow from 10.0.0.0/8 to any port 3000  # Grafana
sudo ufw allow from 10.0.0.0/8 to any port 9093  # Alertmanager
```

---

## 📊 Метрики и алерты

### Ключевые метрики

- **Service Availability:** `up{job="eaip-*"}`
- **Response Time:** Можно добавить через custom metrics
- **Error Rate:** Через логи Loki
- **Resource Usage:** CPU, Memory, Disk

### Настройка новых алертов

1. Отредактируйте `alerts.yml`
2. Добавьте новые правила
3. Перезапустите Prometheus:
   ```bash
   docker compose -f docker-compose.monitoring.yml restart prometheus
   ```

---

## 🐛 Troubleshooting

### Prometheus не собирает метрики

```bash
# Проверьте конфигурацию
docker compose -f docker-compose.monitoring.yml exec prometheus \
  promtool check config /etc/prometheus/prometheus.yml

# Проверьте targets
curl http://localhost:9090/api/v1/targets
```

### Grafana не показывает данные

1. Проверьте datasources в Grafana UI
2. Убедитесь, что Prometheus доступен из сети Grafana
3. Проверьте логи Grafana:
   ```bash
   docker compose -f docker-compose.monitoring.yml logs grafana
   ```

### Логи не появляются в Loki

1. Проверьте статус Promtail:
   ```bash
   docker compose -f docker-compose.monitoring.yml ps promtail
   ```

2. Проверьте логи Promtail:
   ```bash
   docker compose -f docker-compose.monitoring.yml logs promtail
   ```

3. Убедитесь, что Docker socket доступен:
   ```bash
   ls -la /var/run/docker.sock
   ```

---

## 📚 Полезные ссылки

- **Prometheus Docs:** https://prometheus.io/docs/
- **Grafana Docs:** https://grafana.com/docs/
- **Loki Docs:** https://grafana.com/docs/loki/
- **PromQL Guide:** https://prometheus.io/docs/prometheus/latest/querying/basics/

---

## ✅ Чеклист настройки

- [ ] Все файлы скопированы на сервер
- [ ] Мониторинг запущен (`setup-monitoring.sh`)
- [ ] Все контейнеры в статусе "Up"
- [ ] Prometheus health check проходит
- [ ] Grafana доступна (admin/admin)
- [ ] Пароль Grafana изменен
- [ ] Дашборды загружены
- [ ] Алерты настроены
- [ ] Логи видны в Grafana Explore
- [ ] Firewall настроен (опционально)

---

**Последнее обновление:** 2025-11-08  
**Версия:** v0.3.0

