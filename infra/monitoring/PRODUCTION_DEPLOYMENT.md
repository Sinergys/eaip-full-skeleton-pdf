# 🚀 Production Observability Deployment Guide

## Обзор

Полное руководство по развертыванию Observability Bundle в production с HTTPS, закрытыми метриками и реальными уведомлениями.

---

## 📋 Предварительные требования

- Linux сервер (Ubuntu/Debian)
- Docker и Docker Compose установлены
- Домен настроен и указывает на сервер
- Минимум 4GB RAM, 20GB свободного места
- Основные EAIP сервисы запущены

---

## 🚀 Быстрый старт

### 1. Подготовка окружения

```bash
ssh user@prod-host
sudo mkdir -p /opt/eaip/infra/monitoring && sudo chown -R $USER /opt/eaip
cd /opt/eaip/infra/monitoring
docker network create monitoring || true
```

### 2. Копирование файлов

Скопируйте всю директорию `infra/monitoring` на production сервер:

```bash
scp -r infra/monitoring/* user@prod-host:/opt/eaip/infra/monitoring/
```

### 3. Настройка переменных окружения

```bash
cd /opt/eaip/infra/monitoring
nano .env.prod.monitoring
```

Обновите следующие переменные:
- `GF_SECURITY_ADMIN_PASSWORD` - сгенерируйте: `openssl rand -base64 24`
- `DOMAIN` - ваш домен (например, `obs.example.com`)
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `TELEGRAM_CHAT_ID` - ID чата для уведомлений

### 4. Развертывание

```bash
chmod +x deploy-prod-monitoring.sh
bash deploy-prod-monitoring.sh
```

---

## 🔧 Ручное развертывание

### 1. Обработка шаблона Alertmanager

```bash
cd /opt/eaip/infra/monitoring
source .env.prod.monitoring
envsubst < alertmanager/alertmanager.yml.template > alertmanager/alertmanager.yml
```

### 2. Запуск сервисов

```bash
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml pull
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml up -d
```

### 3. Проверка статуса

```bash
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml ps
```

### 4. Health checks

```bash
# Prometheus
curl -fsS https://$DOMAIN/prometheus/-/healthy

# Grafana
curl -fsS https://$DOMAIN/api/health

# Alertmanager
curl -fsS https://$DOMAIN/alertmanager/api/v2/status

# Loki
curl -fsS https://$DOMAIN/loki/ready
```

---

## 🔐 Безопасность

### Настройка Firewall

```bash
# Разрешить только HTTP/HTTPS
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443

# Закрыть внутренние порты
sudo ufw deny 9090  # Prometheus
sudo ufw deny 9093  # Alertmanager
sudo ufw deny 3100  # Loki
sudo ufw deny 9115  # Blackbox
sudo ufw deny 3000  # Grafana

sudo ufw enable
```

### Проверка портов

```bash
sudo lsof -i :80 -i :443
```

---

## 🌐 Доступ к сервисам

Все сервисы доступны через HTTPS через Caddy:

- **Grafana:** https://obs.example.com
- **Prometheus:** https://obs.example.com/prometheus
- **Alertmanager:** https://obs.example.com/alertmanager
- **Loki:** https://obs.example.com/loki

---

## 📊 Конфигурация

### Prometheus

- **Retention:** 30 дней (настраивается через `PROM_RETENTION`)
- **Memory limit:** 2GB (настраивается через `PROM_MEMORY_TARGET`)
- **Scrape interval:** 15 секунд

### Loki

- **Retention:** 14 дней (336 часов)
- **Ingestion rate:** 16 MB/s
- **Compaction:** каждые 10 минут

### Grafana

- **Admin user:** настраивается через `GF_SECURITY_ADMIN_USER`
- **Admin password:** настраивается через `GF_SECURITY_ADMIN_PASSWORD`
- **Datasources:** автоматически настроены
- **Dashboards:** автоматически загружены

---

## 🔔 Настройка Telegram уведомлений

### 1. Создание Telegram бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте `/newbot` и следуйте инструкциям
3. Сохраните токен бота

### 2. Получение Chat ID

1. Откройте [@userinfobot](https://t.me/userinfobot)
2. Отправьте любое сообщение
3. Сохраните ваш Chat ID

### 3. Настройка в .env.prod.monitoring

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### 4. Обновление Alertmanager

```bash
cd /opt/eaip/infra/monitoring
source .env.prod.monitoring
envsubst < alertmanager/alertmanager.yml.template > alertmanager/alertmanager.yml
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml restart alertmanager
```

---

## 🔄 Обновление

### Обновление версий

```bash
cd /opt/eaip/infra/monitoring
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml pull
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml up -d
```

### Обновление конфигурации

После изменения конфигурационных файлов:

```bash
# Prometheus
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml restart prometheus

# Alertmanager
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml restart alertmanager

# Loki
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml restart loki

# Caddy (для обновления Caddyfile)
docker compose --env-file .env.prod.monitoring -f docker-compose.prod.monitoring.yml restart caddy
```

---

## 🐛 Troubleshooting

### SSL сертификат не выдается

1. Проверьте, что домен указывает на сервер:
   ```bash
   dig $DOMAIN
   ```

2. Проверьте логи Caddy:
   ```bash
   docker logs caddy-prod
   ```

3. Убедитесь, что порты 80 и 443 открыты

### Алерты не приходят в Telegram

1. Проверьте токен и Chat ID в `.env.prod.monitoring`
2. Проверьте логи Alertmanager:
   ```bash
   docker logs alertmanager-prod
   ```
3. Убедитесь, что шаблон обработан:
   ```bash
   cat alertmanager/alertmanager.yml | grep -i telegram
   ```

### Сервисы не доступны через HTTPS

1. Проверьте статус Caddy:
   ```bash
   docker ps | grep caddy
   ```
2. Проверьте Caddyfile:
   ```bash
   docker exec caddy-prod cat /etc/caddy/Caddyfile
   ```
3. Проверьте логи:
   ```bash
   docker logs caddy-prod
   ```

---

## 📁 Структура файлов

```
monitoring/
├── .env.prod.monitoring              # Переменные окружения
├── docker-compose.prod.monitoring.yml # Docker Compose конфигурация
├── deploy-prod-monitoring.sh          # Скрипт развертывания
├── prometheus/
│   ├── prometheus.yml                 # Конфигурация Prometheus
│   ├── blackbox.yml                   # Конфигурация Blackbox
│   └── rules/
│       └── health.yml                 # Правила алертов
├── alertmanager/
│   ├── alertmanager.yml.template      # Шаблон с переменными
│   └── alertmanager.yml               # Обработанный файл
├── loki/
│   └── loki-config.yml                # Конфигурация Loki (14 дней retention)
├── promtail/
│   └── promtail-config.yml            # Конфигурация Promtail
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── datasources.yml       # Автоконфигурация datasources
│   │   └── dashboards/
│   │       └── dashboards.yml        # Автоконфигурация dashboards
│   └── dashboards/
│       └── eaip-services.json         # Dashboard
└── caddy/
    └── Caddyfile                      # Конфигурация Caddy
```

---

## ✅ Чеклист развертывания

- [ ] Директория `/opt/eaip/infra/monitoring` создана
- [ ] Все файлы скопированы на сервер
- [ ] `.env.prod.monitoring` настроен с реальными значениями
- [ ] Monitoring сеть создана
- [ ] Firewall настроен (только 80/443 открыты)
- [ ] Сервисы запущены
- [ ] SSL сертификат выдан
- [ ] Grafana доступна по HTTPS
- [ ] Prometheus доступен через `/prometheus`
- [ ] Telegram уведомления настроены и работают
- [ ] Dashboards загружены и отображают данные

---

## 🔗 Полезные ссылки

- **Caddy Docs:** https://caddyserver.com/docs/
- **Prometheus Docs:** https://prometheus.io/docs/
- **Grafana Docs:** https://grafana.com/docs/
- **Alertmanager Telegram:** https://prometheus.io/docs/alerting/latest/configuration/#telegram_config

---

**Последнее обновление:** 2025-11-08  
**Версия:** v0.3.0

