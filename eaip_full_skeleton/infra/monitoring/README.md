# 🚀 Production Observability Bundle

Полный стек наблюдаемости для EAIP production с HTTPS, закрытыми метриками и реальными уведомлениями.

## 📋 Быстрый старт

### 1. Подготовка

```bash
ssh user@prod-host
sudo mkdir -p /opt/eaip/infra/monitoring && sudo chown -R $USER /opt/eaip
cd /opt/eaip/infra/monitoring
docker network create monitoring || true
```

### 2. Копирование файлов

```bash
scp -r infra/monitoring/* user@prod-host:/opt/eaip/infra/monitoring/
```

### 3. Настройка .env.prod.monitoring

```bash
cd /opt/eaip/infra/monitoring
nano .env.prod.monitoring
```

Обязательно обновите:
- `GF_SECURITY_ADMIN_PASSWORD` - сгенерируйте: `openssl rand -base64 24`
- `DOMAIN` - ваш домен
- `TELEGRAM_BOT_TOKEN` - токен бота
- `TELEGRAM_CHAT_ID` - ID чата

### 4. Развертывание

**Автоматический запуск (рекомендуется):**
```bash
chmod +x launch-prod-observability.sh
bash launch-prod-observability.sh
```

**Или используйте отдельный скрипт:**
```bash
chmod +x deploy-prod-monitoring.sh
bash deploy-prod-monitoring.sh
```

## 🌐 Доступ

- **Grafana:** https://your-domain.com
- **Prometheus:** https://your-domain.com/prometheus
- **Alertmanager:** https://your-domain.com/alertmanager
- **Loki:** https://your-domain.com/loki

## 📚 Документация

Подробное руководство: [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)

## ✅ Что включено

- ✅ Prometheus с retention 30 дней
- ✅ Grafana с автоматической настройкой
- ✅ Loki с retention 14 дней
- ✅ Promtail для сбора логов
- ✅ Alertmanager с Telegram уведомлениями
- ✅ cAdvisor для метрик контейнеров
- ✅ Node Exporter для метрик хоста
- ✅ Blackbox Exporter для health checks
- ✅ Caddy для HTTPS (автоматический Let's Encrypt)
- ✅ Закрытые внутренние порты (только 80/443 открыты)

## 🔐 Безопасность

- Все сервисы доступны только через HTTPS
- Внутренние порты закрыты firewall
- Автоматический SSL через Let's Encrypt
- Сильные пароли через переменные окружения

## 📁 Структура

```
monitoring/
├── .env.prod.monitoring              # Переменные окружения
├── docker-compose.prod.monitoring.yml # Docker Compose
├── deploy-prod-monitoring.sh          # Скрипт развертывания
├── prometheus/                        # Конфигурация Prometheus
├── alertmanager/                      # Конфигурация Alertmanager
├── loki/                              # Конфигурация Loki
├── promtail/                          # Конфигурация Promtail
├── grafana/                           # Конфигурация Grafana
└── caddy/                             # Конфигурация Caddy
```

---

**Версия:** v0.3.0  
**Дата:** 2025-11-08

