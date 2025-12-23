# 🚀 Руководство по развертыванию проекта АТЛАС

## 📋 Содержание

1. [Требования](#требования)
2. [Подготовка окружения](#подготовка-окружения)
3. [Установка и настройка](#установка-и-настройка)
4. [Развертывание](#развертывание)
5. [Проверка работоспособности](#проверка-работоспособности)
6. [Обновление системы](#обновление-системы)
7. [Резервное копирование](#резервное-копирование)

---

## 🔧 Требования

### Аппаратные требования

- **CPU**: Минимум 4 ядра (рекомендуется 8+)
- **RAM**: Минимум 8 GB (рекомендуется 16 GB+)
- **Диск**: Минимум 100 GB свободного места (SSD рекомендуется)
- **Сеть**: Стабильное интернет-соединение для AI API

### Программное обеспечение

- **Docker**: версия 20.10+
- **Docker Compose**: версия 2.0+
- **Операционная система**: Linux (Ubuntu 20.04+ / CentOS 8+ / Debian 11+)

### Внешние зависимости

- Доступ к AI API (DeepSeek, OpenAI или Anthropic)
- Доменное имя (для продакшена)
- SSL сертификат (Let's Encrypt рекомендуется)

---

## 📦 Подготовка окружения

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd eaip_full_skeleton
```

### 2. Создание директорий

```bash
mkdir -p infra/data/{inbox,aggregated,postgres,minio}
mkdir -p infra/backups
mkdir -p infra/nginx/{conf.d,ssl,logs}
```

### 3. Настройка прав доступа

```bash
chmod -R 755 infra/data
chmod -R 755 infra/backups
```

---

## ⚙️ Установка и настройка

### 1. Копирование конфигурации

```bash
cd infra
cp .env.example .env.prod
```

### 2. Редактирование переменных окружения

Откройте `.env.prod` и настройте следующие параметры:

#### Обязательные параметры:

```bash
# База данных
POSTGRES_PASSWORD=<strong_password>
POSTGRES_USER=eaip_user
POSTGRES_DB=eaip_production

# Redis
REDIS_PASSWORD=<strong_redis_password>

# MinIO
MINIO_ROOT_PASSWORD=<strong_minio_password>

# AI API
DEEPSEEK_API_KEY=<your_deepseek_api_key>
# или
OPENAI_API_KEY=<your_openai_api_key>
# или
ANTHROPIC_API_KEY=<your_anthropic_api_key>

# JWT
JWT_SECRET_KEY=<min_32_chars_random_string>
```

#### Опциональные параметры:

```bash
# Версия системы
EAIP_VERSION=v0.3.0

# Логирование
LOG_LEVEL=INFO

# Производительность
BATCH_MAX_WORKERS=4
UVICORN_WORKERS=4
```

### 3. Настройка Nginx

Создайте конфигурацию Nginx в `infra/nginx/conf.d/eaip.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://gateway-auth:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Установка SSL сертификата

```bash
# Используя Let's Encrypt
certbot certonly --standalone -d yourdomain.com
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem infra/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem infra/nginx/ssl/key.pem
```

---

## 🚀 Развертывание

### 1. Сборка образов

```bash
cd infra
docker compose -f docker-compose.prod.yml build
```

### 2. Запуск сервисов

```bash
# Запуск всех сервисов
docker compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker compose -f docker-compose.prod.yml ps
```

### 3. Инициализация базы данных

```bash
# База данных инициализируется автоматически при первом запуске
# Проверка подключения
docker compose -f docker-compose.prod.yml exec postgres psql -U eaip_user -d eaip_production -c "SELECT 1;"
```

### 4. Проверка логов

```bash
# Логи всех сервисов
docker compose -f docker-compose.prod.yml logs -f

# Логи конкретного сервиса
docker compose -f docker-compose.prod.yml logs -f ingest
```

---

## ✅ Проверка работоспособности

### 1. Health checks

```bash
# Проверка health endpoints
curl http://localhost:8000/health  # gateway-auth
curl http://localhost:8001/health  # ingest
curl http://localhost:8002/health  # validate
curl http://localhost:8003/health  # analytics
curl http://localhost:8004/health  # recommend
curl http://localhost:8005/health  # reports
curl http://localhost:8006/health  # management
```

### 2. Проверка базовых сервисов

```bash
# PostgreSQL
docker compose -f docker-compose.prod.yml exec postgres pg_isready -U eaip_user

# Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli -a $REDIS_PASSWORD ping

# MinIO
curl http://localhost:9000/minio/health/live
```

### 3. Тестовый запрос

```bash
# Загрузка тестового файла
curl -X POST http://localhost/api/enterprises \
  -H "Content-Type: application/json" \
  -d '{"name": "Тестовое предприятие"}'
```

---

## 🔄 Обновление системы

### 1. Подготовка к обновлению

```bash
# Создание резервной копии
./scripts/backup.sh

# Остановка сервисов
docker compose -f docker-compose.prod.yml down
```

### 2. Обновление кода

```bash
git pull origin main
cd infra
docker compose -f docker-compose.prod.yml build
```

### 3. Миграция базы данных (если требуется)

```bash
docker compose -f docker-compose.prod.yml exec ingest python -m alembic upgrade head
```

### 4. Запуск обновленной системы

```bash
docker compose -f docker-compose.prod.yml up -d

# Проверка работоспособности
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

### 5. Откат (если требуется)

```bash
# Восстановление из резервной копии
./scripts/restore.sh <backup_file>

# Откат к предыдущей версии
git checkout <previous_version>
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

---

## 💾 Резервное копирование

### Автоматическое резервное копирование

Настройте cron для автоматических бэкапов:

```bash
# Добавьте в crontab
0 2 * * * /path/to/eaip_full_skeleton/scripts/backup.sh
```

### Ручное резервное копирование

```bash
# База данных
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U eaip_user eaip_production > backup_$(date +%Y%m%d).sql

# Данные MinIO
docker compose -f docker-compose.prod.yml exec minio \
  mc mirror /data /backups/minio_$(date +%Y%m%d)
```

### Восстановление из резервной копии

```bash
# База данных
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U eaip_user eaip_production < backup_20240101.sql

# Данные MinIO
docker compose -f docker-compose.prod.yml exec minio \
  mc mirror /backups/minio_20240101 /data
```

---

## 🔒 Безопасность

### Рекомендации

1. **Используйте сильные пароли** для всех сервисов
2. **Ограничьте доступ** к портам (используйте firewall)
3. **Регулярно обновляйте** систему и зависимости
4. **Мониторьте логи** на предмет подозрительной активности
5. **Используйте HTTPS** для всех внешних соединений
6. **Ограничьте CORS** только необходимыми доменами

### Проверка безопасности

```bash
# Проверка открытых портов
netstat -tulpn | grep LISTEN

# Проверка SSL сертификата
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

---

## 📊 Мониторинг

См. [HEALTH_MONITORING.md](./HEALTH_MONITORING.md) для детальной информации о мониторинге системы.

---

## 🆘 Поддержка

При возникновении проблем см. [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

## 📝 Чеклист развертывания

- [ ] Все требования выполнены
- [ ] Переменные окружения настроены
- [ ] SSL сертификат установлен
- [ ] База данных инициализирована
- [ ] Все сервисы запущены
- [ ] Health checks проходят успешно
- [ ] Резервное копирование настроено
- [ ] Мониторинг настроен
- [ ] Документация изучена

---

**Готово!** Система развернута и готова к использованию. 🎉

