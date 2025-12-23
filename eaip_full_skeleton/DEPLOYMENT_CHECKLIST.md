# ✅ Чеклист готовности к деплою на сервер

## 📋 Предварительная подготовка

### 1. Docker образы на Docker Hub
- [x] Все 7 сервисов опубликованы на Docker Hub
- [x] Версия: `v0.3.0` и `latest`
- [x] Репозиторий: `ecosinergys/eaip-full-skeleton-{service}`
- [x] CI/CD настроен для автоматической публикации

**Проверка:**
```bash
# Проверить наличие образов
docker pull ecosinergys/eaip-full-skeleton-gateway-auth:v0.3.0
docker pull ecosinergys/eaip-full-skeleton-ingest:v0.3.0
docker pull ecosinergys/eaip-full-skeleton-validate:v0.3.0
docker pull ecosinergys/eaip-full-skeleton-analytics:v0.3.0
docker pull ecosinergys/eaip-full-skeleton-recommend:v0.3.0
docker pull ecosinergys/eaip-full-skeleton-reports:v0.3.0
docker pull ecosinergys/eaip-full-skeleton-management:v0.3.0
```

### 2. Конфигурационные файлы
- [x] `infra/docker-compose.staging.yml` - конфигурация для staging
- [x] `infra/deploy-staging.sh` - скрипт автоматического деплоя
- [x] `infra/harden-staging.sh` - скрипт безопасности
- [x] `infra/post-deploy-checks.sh` - проверки после деплоя
- [x] `infra/rollback-staging.sh` - скрипт отката
- [x] `infra/update-version.sh` - обновление версии

### 3. Документация
- [x] `infra/STAGING_DEPLOYMENT.md` - подробное руководство
- [x] `infra/QUICK_STAGING.md` - быстрая инструкция
- [x] `infra/MONITORING.md` - документация по мониторингу

## 🚀 Что нужно подготовить на сервере

### 1. Системные требования
- [ ] Linux сервер (Ubuntu 20.04+ / Debian 11+)
- [ ] Минимум 4GB RAM (рекомендуется 8GB)
- [ ] 20GB+ свободного места на диске
- [ ] Доступ по SSH
- [ ] Права sudo

### 2. Установка Docker
```bash
# Проверить установлен ли Docker
docker --version
docker compose version

# Если не установлен:
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Выйти и войти снова
```

### 3. Подготовка файлов на сервере

#### Вариант A: Клонирование репозитория
```bash
# На сервере
cd /opt
sudo git clone https://github.com/Sinergys/eaip-full-skeleton-pdf.git eaip
sudo chown -R $USER:$USER /opt/eaip
cd /opt/eaip
```

#### Вариант B: Копирование только нужных файлов
```bash
# На локальной машине - создать архив
tar -czf eaip-staging.tar.gz \
  infra/docker-compose.staging.yml \
  infra/deploy-staging.sh \
  infra/harden-staging.sh \
  infra/post-deploy-checks.sh \
  infra/rollback-staging.sh \
  infra/update-version.sh \
  infra/QUICK_STAGING.md \
  infra/STAGING_DEPLOYMENT.md

# Скопировать на сервер
scp eaip-staging.tar.gz user@server:/tmp/
ssh user@server
cd /opt
sudo mkdir -p eaip
sudo tar -xzf /tmp/eaip-staging.tar.gz -C eaip
sudo chown -R $USER:$USER /opt/eaip
cd /opt/eaip/infra
```

### 4. Переменные окружения

Скрипт `deploy-staging.sh` автоматически создаст `.env` файл с безопасными паролями.

**Или создать вручную:**
```bash
cd /opt/eaip/infra
cat > .env <<EOF
# PostgreSQL Configuration
POSTGRES_USER=eaip_user
POSTGRES_PASSWORD=<сгенерировать_безопасный_пароль>
POSTGRES_DB=eaip_db
POSTGRES_HOST=postgres

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=<сгенерировать_безопасный_пароль>

# AI Configuration (опционально, для ИИ распознавания)
AI_PROVIDER=deepseek  # deepseek, openai, anthropic, gemini, local
AI_ENABLED=true
DEEPSEEK_API_KEY=sk-...  # DeepSeek (рекомендуется - дешевле в 200+ раз!)
# OPENAI_API_KEY=sk-...  # Если используете OpenAI
# ANTHROPIC_API_KEY=sk-ant-...  # Если используете Anthropic
# GOOGLE_API_KEY=...  # Если используете Gemini
EOF
```

**Примечание:** Для использования ИИ распознавания нужно:
1. Выбрать провайдера (OpenAI, Anthropic, Gemini)
2. Получить API ключ
3. Добавить в .env файл
4. Обновить образы сервисов с поддержкой ИИ

Подробнее: `AI_INTEGRATION_PLAN.md`

## 📝 Пошаговый деплой

### Шаг 1: Развертывание
```bash
cd /opt/eaip/infra
chmod +x *.sh
bash deploy-staging.sh
```

### Шаг 2: Проверка работоспособности
```bash
# Проверить статус контейнеров
docker compose -f docker-compose.staging.yml ps

# Проверить health endpoints
curl http://localhost/health  # gateway-auth
curl http://localhost:8001/health  # ingest
curl http://localhost:8002/health  # validate
# и т.д.

# Проверить логи
docker compose -f docker-compose.staging.yml logs -f
```

### Шаг 3: Настройка безопасности (Hardening)
```bash
cd /opt/eaip/infra
sudo bash harden-staging.sh
```

Это включает:
- Настройку firewall
- Создание MinIO buckets
- Настройку бэкапов
- Проверку безопасности

### Шаг 4: Настройка мониторинга (опционально)
```bash
cd /opt/eaip/infra
bash setup-monitoring.sh
```

## ⚠️ Важные моменты

### Проблемы с большими файлами и OCR
- **Проблема:** OCR обработка больших PDF файлов может занимать много времени и ресурсов
- **Решение:** 
  - Использовать более мощный сервер для production
  - Рассмотреть асинхронную обработку через Celery
  - Ограничить размер файлов или количество страниц для OCR

### Порты на сервере
- `80` - gateway-auth (основной вход)
- `8001-8006` - остальные сервисы (внутренние)
- `9000` - MinIO API
- `9001` - MinIO Console
- `5432` - PostgreSQL (только внутри сети)
- `6379` - Redis (только внутри сети)

### Безопасность
- [ ] Настроить firewall (только нужные порты открыты)
- [ ] Изменить дефолтные пароли MinIO
- [ ] Настроить SSL/TLS (через reverse proxy)
- [ ] Регулярные бэкапы БД
- [ ] Мониторинг логов и алертов

## 🔄 Обновление версии

```bash
cd /opt/eaip/infra
bash update-version.sh v0.4.0
```

Скрипт автоматически:
1. Обновит версии в docker-compose.staging.yml
2. Pull новых образов
3. Перезапустит сервисы

## 🔙 Откат версии

```bash
cd /opt/eaip/infra
bash rollback-staging.sh
```

## 📊 Мониторинг

После деплоя можно настроить:
- Prometheus + Grafana для метрик
- Loki для логов
- Alertmanager для алертов

Подробнее: `infra/MONITORING.md`

## ✅ Финальная проверка

После деплоя проверить:
- [ ] Все сервисы запущены и здоровы
- [ ] Health endpoints отвечают
- [ ] Веб-интерфейс доступен
- [ ] MinIO buckets созданы
- [ ] Firewall настроен
- [ ] Бэкапы работают
- [ ] Мониторинг настроен (если используется)

## 🆘 Полезные команды

```bash
# Статус всех сервисов
docker compose -f docker-compose.staging.yml ps

# Логи конкретного сервиса
docker compose -f docker-compose.staging.yml logs -f ingest

# Перезапуск сервиса
docker compose -f docker-compose.staging.yml restart ingest

# Остановка всех сервисов
docker compose -f docker-compose.staging.yml down

# Запуск всех сервисов
docker compose -f docker-compose.staging.yml up -d

# Проверка использования ресурсов
docker stats

# Проверка дискового пространства
df -h
```

## 🤖 Интеграция ИИ (опционально)

Для использования ИИ для распознавания и обработки файлов:

1. **Выбрать провайдера ИИ:**
   - **DeepSeek API** (рекомендуется - дешевле в 200+ раз, OpenAI-совместимый)
   - OpenAI GPT-4 Vision (максимальная точность)
   - Anthropic Claude 3
   - Google Gemini
   - Локальные модели (Ollama)

2. **Добавить API ключи в .env:**
   ```bash
   AI_PROVIDER=deepseek
   AI_ENABLED=true
   DEEPSEEK_API_KEY=sk-...
   ```

3. **Обновить сервисы** с поддержкой ИИ (требуется пересборка образов)

4. **Подробная документация:** `AI_INTEGRATION_PLAN.md`

## 📚 Дополнительная документация

- `infra/STAGING_DEPLOYMENT.md` - подробное руководство
- `infra/QUICK_STAGING.md` - быстрая инструкция
- `infra/MONITORING.md` - настройка мониторинга
- `AI_INTEGRATION_PLAN.md` - план интеграции ИИ
- `SESSION_SUMMARY.md` - общая информация о проекте

