# 🧭 EAIP Observability Bundle - Полное руководство

## Обзор

Полный стек наблюдаемости для EAIP staging окружения, включающий:

- **Prometheus** - сбор и хранение метрик
- **Grafana** - визуализация метрик и логов
- **Loki** - агрегация логов
- **Promtail** - сбор логов из контейнеров
- **Alertmanager** - управление алертами
- **cAdvisor** - метрики контейнеров Docker
- **Node Exporter** - метрики хоста (CPU, память, диск)
- **Blackbox Exporter** - HTTP/HTTPS/TCP health checks

---

## 📋 Предварительные требования

- Linux сервер (Ubuntu/Debian рекомендуется)
- Docker и Docker Compose установлены
- Минимум 4GB RAM
- 20GB свободного места на диске
- Основные EAIP сервисы запущены (docker-compose.staging.yml)

---

## 🚀 Быстрый старт

### Вариант 1: Автоматический скрипт (рекомендуется)

```bash
cd /opt/eaip
chmod +x setup-monitoring.sh
bash setup-monitoring.sh
```

### Вариант 2: Ручная установка

#### 1. Проверка портов

```bash
sudo lsof -i :3000 -i :9090 -i :3100 -i :8080 -i :9100 -i :9115 -i :9093
```

#### 2. Запуск мониторинга

```bash
cd /opt/eaip
docker compose -f docker-compose.monitoring.yml up -d
```

#### 3. Проверка статуса

```bash
docker compose -f docker-compose.monitoring.yml ps
```

#### 4. Health checks

```bash
curl -fsS http://127.0.0.1:9090/-/healthy  # Prometheus
curl -fsS http://127.0.0.1:3000/api/health  # Grafana
curl -fsS http://127.0.0.1:3100/ready        # Loki
curl -fsS http://127.0.0.1:9115/metrics     # Blackbox Exporter
```

---

## 🌐 Доступ к сервисам

### Prometheus
- **URL:** http://staging-host:9090
- **Назначение:** Просмотр метрик, запросы PromQL, алерты
- **Примеры запросов:**
  - `probe_success{job="blackbox-http"}` - статус health checks
  - `up{job="eaip-gateway-auth"}` - статус сервиса
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

### Blackbox Exporter
- **URL:** http://staging-host:9115
- **Назначение:** HTTP/HTTPS/TCP health checks
- **Пример:** `http://staging-host:9115/probe?target=http://gateway-auth:8000/health&module=http_2xx`

### cAdvisor
- **URL:** http://staging-host:8080
- **Назначение:** Метрики контейнеров Docker

### Node Exporter
- **URL:** http://staging-host:9100/metrics
- **Назначение:** Метрики хоста (CPU, память, диск)

---

## 📊 Мониторинг сервисов

### Health Checks через Blackbox Exporter

Все EAIP сервисы мониторятся через Blackbox Exporter:

- `gateway-auth:8000/health`
- `ingest:8001/health`
- `validate:8002/health`
- `analytics:8003/health`
- `recommend:8004/health`
- `reports:8005/health`
- `management:8006/health`

### Метрики

Prometheus собирает метрики каждые 15 секунд:
- Health status всех сервисов (через Blackbox)
- CPU и память контейнеров (через cAdvisor)
- Метрики хоста (через Node Exporter)
- Логи всех контейнеров (через Promtail → Loki)

---

## 🚨 Алерты

### Настроенные алерты

1. **Service Down Alerts** (Critical)
   - Срабатывают, если `probe_success == 0` более 1 минуты
   - Для всех 7 EAIP сервисов
   - Для инфраструктурных сервисов (PostgreSQL, Redis, MinIO)

2. **System Alerts** (Warning)
   - High CPU Usage (>90% в течение 5 минут)
   - High Memory Usage (>90% в течение 5 минут)
   - Low Disk Space (<10%)
   - Container Restarting (частые перезапуски)
   - High Response Time (>2 секунды)

### Настройка уведомлений

Отредактируйте `alertmanager.yml` для настройки:

#### Email уведомления

```yaml
receivers:
  - name: critical-receiver
    email_configs:
      - to: 'admin@eaip.example.com'
        headers:
          Subject: 'EAIP Critical Alert: {{ .GroupLabels.alertname }}'
```

#### Telegram уведомления

```yaml
receivers:
  - name: telegram
    telegram_configs:
      - bot_token: '<BOT_TOKEN>'
        chat_id: <CHAT_ID>
        message: '{{ template "telegram.default.message" . }}'
```

#### Slack webhook

```yaml
receivers:
  - name: slack
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: 'EAIP Alert'
```

После изменения конфигурации:

```bash
docker compose -f docker-compose.monitoring.yml restart alertmanager
```

---

## 📈 Grafana Dashboards

### Предустановленные дашборды

1. **EAIP — Service Health**
   - Статус здоровья всех сервисов
   - Использование CPU и памяти
   - Графики метрик

### Создание своих дашбордов

1. Войдите в Grafana (admin/admin)
2. Перейдите в **Dashboards → New Dashboard**
3. Добавьте панели с метриками из Prometheus
4. Сохраните дашборд

### Полезные запросы PromQL

```promql
# Статус всех сервисов через Blackbox
probe_success{job="blackbox-http"}

# CPU usage по контейнерам
rate(container_cpu_usage_seconds_total{name=~"infra-.*"}[5m]) * 100

# Memory usage
container_memory_usage_bytes{name=~"infra-.*"} / 1024 / 1024

# Response time
probe_http_duration_seconds{job="blackbox-http"}

# Количество перезапусков
rate(container_start_time_seconds{name=~"infra-.*"}[15m])
```

---

## 📝 Логи в Grafana

### Просмотр логов

1. Откройте Grafana → **Explore**
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

### Структура файлов

```
infra/
├── docker-compose.monitoring.yml  # Основной compose файл
├── prometheus.yml                 # Конфигурация Prometheus
├── alerts.yml                     # Правила алертов
├── alertmanager.yml               # Конфигурация Alertmanager
├── promtail-config.yml            # Конфигурация Promtail
├── loki-config.yml                # Конфигурация Loki
├── prometheus/
│   ├── blackbox.yml               # Конфигурация Blackbox Exporter
│   └── rules/
│       └── rules-health.yml       # Правила алертов (копия)
├── grafana-datasources/
│   └── datasources.yml            # Автоконфигурация datasources
└── grafana-dashboards/
    ├── dashboards.yml             # Автоконфигурация dashboards
    └── eaip-services.json         # Dashboard EAIP Services
```

### Prometheus

- **Scrape interval:** 15 секунд
- **Retention:** 30 дней
- **Targets:** Все EAIP сервисы + системные метрики + Blackbox probes

### Alertmanager

- **Group wait:** 10 секунд
- **Repeat interval:** 12 часов
- **Routes:** Critical и Warning раздельно

### Loki

- **Retention:** 30 дней (720h)
- **Ingestion rate:** 16 MB/s
- **Compaction:** каждые 10 минут

### Promtail

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

## 🔍 Проверки после запуска

### Проверка Prometheus targets

```bash
curl -fsS http://127.0.0.1:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

Убедитесь, что все targets в состоянии **UP**.

### Проверка Blackbox probes

```bash
# Проверка health endpoint
curl -fsS "http://127.0.0.1:9115/probe?target=http://gateway-auth:8000/health&module=http_2xx"

# Проверка метрик
curl -fsS http://127.0.0.1:9115/metrics | grep probe_success
```

### Проверка алертов

```bash
# В Prometheus UI: http://staging-host:9090/alerts
# Или через API:
curl -fsS http://127.0.0.1:9090/api/v1/alerts | jq '.data.alerts[] | {name: .labels.alertname, state: .state}'
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

### Blackbox Exporter не работает

1. Проверьте доступность Blackbox:
   ```bash
   curl http://127.0.0.1:9115/metrics
   ```

2. Проверьте конфигурацию:
   ```bash
   docker compose -f docker-compose.monitoring.yml exec blackbox-exporter \
     cat /etc/blackbox_exporter/config.yml
   ```

3. Проверьте сеть:
   ```bash
   docker network inspect infra_monitoring
   docker network inspect infra_default
   ```

---

## 📚 Полезные ссылки

- **Prometheus Docs:** https://prometheus.io/docs/
- **Grafana Docs:** https://grafana.com/docs/
- **Loki Docs:** https://grafana.com/docs/loki/
- **PromQL Guide:** https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Blackbox Exporter:** https://github.com/prometheus/blackbox_exporter

---

## ✅ Чеклист развертывания

- [ ] Docker установлен
- [ ] Основные EAIP сервисы запущены
- [ ] Порты мониторинга свободны
- [ ] Все конфигурационные файлы на месте
- [ ] Мониторинг запущен (`setup-monitoring.sh`)
- [ ] Все контейнеры в статусе "Up"
- [ ] Prometheus health check проходит
- [ ] Grafana доступна (admin/admin)
- [ ] Пароль Grafana изменен
- [ ] Datasources настроены автоматически
- [ ] Дашборды загружены
- [ ] Алерты настроены
- [ ] Логи видны в Grafana Explore
- [ ] Blackbox probes успешны
- [ ] Firewall настроен (опционально)

---

**Последнее обновление:** 2025-11-08  
**Версия:** v0.3.0

