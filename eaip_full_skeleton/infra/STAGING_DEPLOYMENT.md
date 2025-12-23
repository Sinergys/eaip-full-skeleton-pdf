# 🚀 EAIP Staging Deployment Guide

## Обзор

Это руководство по развертыванию EAIP Full Skeleton на staging сервере с использованием Docker Compose и образов из Docker Hub.

---

## 📋 Предварительные требования

- Linux сервер (Ubuntu/Debian рекомендуется)
- Доступ по SSH
- Права sudo
- Минимум 4GB RAM
- 20GB свободного места на диске

---

## 🚀 Быстрый старт

### Вариант 1: Автоматический скрипт

```bash
# Скопируйте скрипт на сервер
scp infra/deploy-staging.sh user@staging-host:/tmp/

# Подключитесь к серверу
ssh user@staging-host

# Запустите скрипт
chmod +x /tmp/deploy-staging.sh
/tmp/deploy-staging.sh
```

### Вариант 2: Ручная установка

#### 1. Подключение к серверу

```bash
ssh user@staging-host
```

#### 2. Установка Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Выйдите и войдите снова для применения изменений группы
docker --version && docker compose version
```

#### 3. Создание директории и .env

```bash
sudo mkdir -p /opt/eaip && sudo chown $USER /opt/eaip
cd /opt/eaip

# Создайте .env файл с безопасными паролями
cat > .env <<EOF
POSTGRES_USER=eaip_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_DB=eaip_db
POSTGRES_HOST=postgres

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=$(openssl rand -base64 32)
EOF
```

#### 4. Копирование docker-compose.staging.yml

```bash
# Скопируйте файл с локальной машины
scp infra/docker-compose.staging.yml user@staging-host:/opt/eaip/
```

#### 5. Запуск сервисов

```bash
cd /opt/eaip
docker compose -f docker-compose.staging.yml pull
docker compose -f docker-compose.staging.yml up -d
```

#### 6. Проверка статуса

```bash
docker compose -f docker-compose.staging.yml ps
curl -sS http://127.0.0.1/health
```

---

## 🔧 Конфигурация

### Переменные окружения (.env)

Файл `.env` содержит следующие переменные:

- `POSTGRES_USER` - пользователь PostgreSQL
- `POSTGRES_PASSWORD` - пароль PostgreSQL (генерируется автоматически)
- `POSTGRES_DB` - имя базы данных
- `POSTGRES_HOST` - хост PostgreSQL (обычно `postgres`)
- `MINIO_ROOT_USER` - пользователь MinIO
- `MINIO_ROOT_PASSWORD` - пароль MinIO (генерируется автоматически)

**⚠️ Важно:** Используйте сильные пароли в production!

### Порты

- **80** - Gateway (публичный доступ)
- **9000** - MinIO API
- **9001** - MinIO Console

Остальные сервисы доступны только внутри Docker сети.

---

## 📦 Используемые образы

Все образы загружаются с Docker Hub:

- `ecosinergys/eaip-full-skeleton-gateway-auth:v0.3.0`
- `ecosinergys/eaip-full-skeleton-ingest:v0.3.0`
- `ecosinergys/eaip-full-skeleton-validate:v0.3.0`
- `ecosinergys/eaip-full-skeleton-analytics:v0.3.0`
- `ecosinergys/eaip-full-skeleton-recommend:v0.3.0`
- `ecosinergys/eaip-full-skeleton-reports:v0.3.0`
- `ecosinergys/eaip-full-skeleton-management:v0.3.0`

---

## 🏥 Health Checks

### Проверка всех сервисов

```bash
# Gateway (публичный)
curl http://localhost/health

# Внутренние сервисы (через docker exec)
docker compose -f docker-compose.staging.yml exec gateway-auth curl http://localhost:8000/health
docker compose -f docker-compose.staging.yml exec ingest curl http://localhost:8001/health
# и т.д.
```

### Проверка статуса контейнеров

```bash
docker compose -f docker-compose.staging.yml ps
```

---

## 🔄 Обновление

### Обновление до новой версии

```bash
cd /opt/eaip

# Обновите версию в docker-compose.staging.yml
# Замените v0.3.0 на новую версию (например, v0.4.0)

# Загрузите новые образы
docker compose -f docker-compose.staging.yml pull

# Перезапустите сервисы
docker compose -f docker-compose.staging.yml up -d
```

### Откат к предыдущей версии

```bash
cd /opt/eaip

# Измените версию обратно в docker-compose.staging.yml
# Загрузите старые образы
docker compose -f docker-compose.staging.yml pull

# Перезапустите
docker compose -f docker-compose.staging.yml up -d
```

---

## 🛑 Откат (Rollback)

### Полный откат

```bash
cd /opt/eaip
./rollback-staging.sh

# Или вручную:
docker compose -f docker-compose.staging.yml down
docker system prune -f
```

---

## 📊 Мониторинг

### Логи

```bash
# Все сервисы
docker compose -f docker-compose.staging.yml logs -f

# Конкретный сервис
docker compose -f docker-compose.staging.yml logs -f gateway-auth
```

### Использование ресурсов

```bash
docker stats
```

---

## 🔐 Безопасность

### Рекомендации для production:

1. **Измените пароли** в `.env` на сильные
2. **Настройте firewall** (только порты 80, 443, 9001)
3. **Используйте HTTPS** (настройте reverse proxy с SSL)
4. **Ограничьте доступ** к MinIO Console (9001)
5. **Регулярно обновляйте** образы
6. **Настройте бэкапы** для PostgreSQL

---

## 🐛 Troubleshooting

### Сервисы не запускаются

```bash
# Проверьте логи
docker compose -f docker-compose.staging.yml logs

# Проверьте статус
docker compose -f docker-compose.staging.yml ps
```

### Health check не проходит

```bash
# Проверьте, что контейнеры запущены
docker ps

# Проверьте логи конкретного сервиса
docker compose -f docker-compose.staging.yml logs gateway-auth
```

### Проблемы с MinIO

```bash
# Проверьте доступность
curl http://localhost:9000/minio/health/live

# Проверьте логи
docker compose -f docker-compose.staging.yml logs minio
```

---

## 📝 Инициализация MinIO (опционально)

Если установлен MinIO Client (`mc`):

```bash
source .env
mc alias set eaip http://127.0.0.1:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
mc mb eaip/eaip-bucket
```

---

## 🔗 Полезные ссылки

- **Docker Hub:** https://hub.docker.com/u/ecosinergys
- **GitHub:** https://github.com/Sinergys/eaip-full-skeleton-pdf
- **Документация:** `SESSION_SUMMARY.md`

---

## ✅ Чеклист развертывания

- [ ] Docker установлен
- [ ] Директория `/opt/eaip` создана
- [ ] Файл `.env` создан с безопасными паролями
- [ ] `docker-compose.staging.yml` скопирован
- [ ] Образы загружены (`docker compose pull`)
- [ ] Сервисы запущены (`docker compose up -d`)
- [ ] Health checks проходят
- [ ] Логи проверены
- [ ] Firewall настроен
- [ ] Бэкапы настроены (опционально)

---

## 🛡️ Post-Deploy Checks & Hardening

После развертывания выполните проверки и настройку безопасности:

### Автоматический hardening (все шаги сразу)

```bash
cd /opt/eaip
chmod +x infra/harden-staging.sh
sudo bash infra/harden-staging.sh
```

### Или пошагово:

#### 1. Post-Deploy Checks

```bash
chmod +x infra/post-deploy-checks.sh
bash infra/post-deploy-checks.sh
```

Проверяет:
- Статус всех контейнеров
- Health endpoints (localhost и port 80)
- MinIO bucket
- Firewall статус
- Backup cron job

#### 2. MinIO Setup

```bash
chmod +x infra/setup-minio.sh
bash infra/setup-minio.sh
```

- Устанавливает MinIO client (если нужно)
- Настраивает alias
- Создает bucket `eaip-bucket`

#### 3. Firewall Setup

```bash
chmod +x infra/setup-firewall.sh
sudo bash infra/setup-firewall.sh
```

- Устанавливает UFW (если нужно)
- Открывает порты: 80, 443, 9000, 9001, 22
- Активирует firewall

#### 4. Backup Setup

```bash
chmod +x infra/setup-backups.sh
sudo bash infra/setup-backups.sh
```

- Создает директорию для бэкапов (`/var/backups/eaip`)
- Создает скрипт бэкапа
- Настраивает cron job (ежедневно в 2:00 AM)
- Хранит бэкапы 7 дней

#### 5. Update Version

```bash
chmod +x infra/update-version.sh
bash infra/update-version.sh v0.4.0
```

- Обновляет версию в docker-compose.staging.yml
- Создает backup конфигурации
- Загружает новые образы
- Обновляет сервисы без даунтайма
- Проверяет health после обновления

---

## 📝 Скрипты

Все скрипты находятся в директории `infra/`:

- `deploy-staging.sh` - Полное развертывание
- `post-deploy-checks.sh` - Проверки после развертывания
- `setup-minio.sh` - Настройка MinIO
- `setup-firewall.sh` - Настройка firewall
- `setup-backups.sh` - Настройка бэкапов
- `update-version.sh` - Обновление версии
- `harden-staging.sh` - Выполняет все шаги hardening
- `rollback-staging.sh` - Откат развертывания

---

**Последнее обновление:** 2025-11-08  
**Версия:** v0.3.0

