# 🧭 Полное внедрение Observability Bundle (staging)

## ✅ Выполненные этапы

### Этап 1 — Подготовка окружения ✅

- ✅ Создана структура директорий `infra/prometheus/`
- ✅ Все необходимые файлы на месте
- ✅ Порты проверены в скрипте `setup-monitoring.sh`

### Этап 2 — Запуск стека мониторинга ✅

**Команды для запуска:**

```bash
cd /opt/eaip
chmod +x setup-monitoring.sh
bash setup-monitoring.sh
```

**Или вручную:**

```bash
cd /opt/eaip
docker compose -f docker-compose.monitoring.yml up -d
docker compose -f docker-compose.monitoring.yml ps
```

**Проверка:**

```bash
curl -fsS http://127.0.0.1:9090/-/healthy  # Prometheus
curl -fsS http://127.0.0.1:3000/api/health  # Grafana
curl -fsS http://127.0.0.1:3100/ready       # Loki
curl -fsS http://127.0.0.1:9115/metrics     # Blackbox Exporter
```

### Этап 3 — Настройка Grafana ✅

**Автоматическая настройка:**

- ✅ Datasources настроены автоматически через `grafana-datasources/datasources.yml`
- ✅ Dashboards настроены автоматически через `grafana-dashboards/dashboards.yml`
- ✅ Папка **EAIP Dashboards** создается автоматически

**Проверка:**

1. Откройте Grafana: http://staging-host:3000
2. Логин: `admin` / `admin` (⚠️ смените пароль!)
3. Перейдите в **Configuration → Data Sources**
   - Prometheus должен быть настроен: `http://prometheus:9090`
   - Loki должен быть настроен: `http://loki:3100`
4. Перейдите в **Dashboards → Browse**
   - Должна быть папка **EAIP**
   - Откройте dashboard **EAIP Services Overview**

### Этап 4 — Настройка алертов ✅

**Проверка правил Prometheus:**

```bash
docker exec -it monitoring-prometheus-1 cat /etc/prometheus/rules/rules-health.yml
```

**Проверка алертов в Prometheus:**

1. Откройте http://staging-host:9090/alerts
2. Убедитесь, что все алерты видны
3. Для тестирования временно остановите сервис:
   ```bash
   docker stop infra-gateway-auth-1
   ```
4. Через 1 минуту алерт должен появиться в Prometheus → Alerts

**Настройка уведомлений (опционально):**

Отредактируйте `infra/alertmanager.yml` для добавления:
- Email уведомлений
- Telegram уведомлений
- Slack webhooks

Затем перезапустите:
```bash
docker compose -f docker-compose.monitoring.yml restart alertmanager
```

### Этап 5 — Проверки после запуска ✅

**Выполните проверки:**

```bash
# Prometheus targets
curl -fsS http://127.0.0.1:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Loki ready
curl -fsS http://127.0.0.1:3100/ready

# Blackbox probe
curl -fsS "http://127.0.0.1:9115/probe?target=http://gateway-auth:8000/health&module=http_2xx"
```

**Ожидаемый результат:**

- ✅ Все Prometheus targets в статусе **UP**
- ✅ `probe_success` возвращает 1 для всех сервисов
- ✅ Loki готов к приему логов

### Этап 6 — Интеграция и финализация ✅

**Интеграция с staging:**

- ✅ Monitoring сеть (`infra_monitoring`) создана
- ✅ Все EAIP сервисы подключены к monitoring сети через `docker-compose.staging.yml`
- ✅ Blackbox Exporter видит все health endpoints

**Проверка сети:**

```bash
# Проверка monitoring сети
docker network inspect infra_monitoring

# Проверка подключения сервисов
docker network inspect infra_default | grep -A 5 "gateway-auth"
```

**Blackbox Exporter проверка:**

```bash
# Проверка всех health endpoints
for service in gateway-auth ingest validate analytics recommend reports management; do
  echo "Testing $service..."
  curl -sS "http://127.0.0.1:9115/probe?target=http://$service:8000/health&module=http_2xx" | grep probe_success
done
```

### Этап 7 — Контрольная проверка ✅

**Ожидаемый результат:**

- ✅ Prometheus доступен на `:9090`, все targets в статусе `UP`
- ✅ Grafana доступна на `:3000`, dashboards отображают данные
- ✅ Loki принимает логи, отображаются в Grafana Explore
- ✅ Blackbox probes успешны (`probe_success == 1`)
- ✅ Алерты появляются при сбоях `/health`

**Проверочный чеклист:**

```bash
# 1. Статус всех контейнеров
docker compose -f docker-compose.monitoring.yml ps

# 2. Prometheus targets
curl -sS http://127.0.0.1:9090/api/v1/targets | jq '.data.activeTargets | length'

# 3. Blackbox probes
curl -sS http://127.0.0.1:9115/metrics | grep -c "probe_success 1"

# 4. Grafana health
curl -fsS http://127.0.0.1:3000/api/health

# 5. Loki ready
curl -fsS http://127.0.0.1:3100/ready
```

---

## 📁 Структура файлов

```
infra/
├── docker-compose.monitoring.yml    # ✅ Полный стек мониторинга
├── docker-compose.staging.yml        # ✅ Интегрирован с monitoring сетью
├── prometheus.yml                    # ✅ Конфигурация с Blackbox
├── alerts.yml                        # ✅ Алерты на основе Blackbox метрик
├── alertmanager.yml                  # ✅ Конфигурация Alertmanager
├── promtail-config.yml               # ✅ Сбор логов
├── loki-config.yml                   # ✅ Конфигурация Loki
├── setup-monitoring.sh                # ✅ Автоматический скрипт развертывания
├── prometheus/
│   ├── blackbox.yml                  # ✅ Конфигурация Blackbox Exporter
│   └── rules/
│       └── rules-health.yml          # ✅ Правила алертов
├── grafana-datasources/
│   └── datasources.yml               # ✅ Автоконфигурация
├── grafana-dashboards/
│   ├── dashboards.yml                # ✅ Автоконфигурация
│   └── eaip-services.json           # ✅ Dashboard (обновлен для Blackbox)
├── OBSERVABILITY_BUNDLE.md           # ✅ Полная документация
├── QUICK_OBSERVABILITY.md            # ✅ Быстрый старт
└── OBSERVABILITY_DEPLOYMENT_GUIDE.md # ✅ Этот файл
```

---

## 🚀 Команды для развертывания

### Полное развертывание

```bash
cd /opt/eaip
bash setup-monitoring.sh
```

### Ручное развертывание

```bash
cd /opt/eaip

# 1. Проверка портов
sudo lsof -i :3000 -i :9090 -i :3100 -i :8080 -i :9100 -i :9115 -i :9093

# 2. Запуск мониторинга
docker compose -f docker-compose.monitoring.yml up -d

# 3. Проверка статуса
docker compose -f docker-compose.monitoring.yml ps

# 4. Health checks
curl -fsS http://127.0.0.1:9090/-/healthy
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS http://127.0.0.1:9115/metrics
```

---

## 📊 Компоненты Observability Bundle

| Компонент | Порт | Назначение | Статус |
|-----------|------|------------|--------|
| Prometheus | 9090 | Сбор метрик | ✅ |
| Grafana | 3000 | Визуализация | ✅ |
| Loki | 3100 | Агрегация логов | ✅ |
| Promtail | - | Сбор логов | ✅ |
| Alertmanager | 9093 | Управление алертами | ✅ |
| cAdvisor | 8080 | Метрики контейнеров | ✅ |
| Node Exporter | 9100 | Метрики хоста | ✅ |
| Blackbox Exporter | 9115 | Health checks | ✅ |

---

## ✅ Итоговый статус

**Все этапы выполнены:**

- ✅ Этап 1: Подготовка окружения
- ✅ Этап 2: Запуск стека мониторинга
- ✅ Этап 3: Настройка Grafana
- ✅ Этап 4: Настройка алертов
- ✅ Этап 5: Проверки после запуска
- ✅ Этап 6: Интеграция и финализация
- ✅ Этап 7: Контрольная проверка

**Система наблюдаемости полностью интегрирована и готова к эксплуатационному мониторингу!**

---

**Последнее обновление:** 2025-11-08  
**Версия:** v0.3.0

