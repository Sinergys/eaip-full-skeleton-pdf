# 📊 Применение init.sql к базе данных

## Важно!

Если PostgreSQL контейнер уже был запущен до добавления `init.sql`, скрипт **не выполнится автоматически**.

PostgreSQL выполняет скрипты из `/docker-entrypoint-initdb.d/` **только при первом создании БД**.

## Решения

### Вариант 1: Пересоздать контейнер (рекомендуется для тестирования)

```bash
cd infra

# Остановить и удалить контейнер с данными
docker compose down -v

# Запустить заново (init.sql выполнится автоматически)
docker compose up -d postgres

# Проверить таблицы
docker compose exec postgres psql -U eaip_user -d eaip_db -c "\dt"
```

### Вариант 2: Применить скрипт вручную к существующей БД

```bash
cd infra/db

# Применить init.sql
docker compose -f ../docker-compose.yml exec -T postgres psql -U eaip_user -d eaip_db < init.sql

# Или через psql
docker compose exec postgres psql -U eaip_user -d eaip_db -f /docker-entrypoint-initdb.d/init.sql
```

### Вариант 3: Использовать скрипт apply_init.sh

```bash
cd infra/db
chmod +x apply_init.sh
bash apply_init.sh
```

## Проверка

После применения скрипта проверьте создание таблиц:

```bash
# Список таблиц
docker compose exec postgres psql -U eaip_user -d eaip_db -c "\dt"

# Или используйте test_db.sh
cd infra/db
bash test_db.sh
```

## На сервере

При первом деплое на сервере init.sql выполнится автоматически, так как БД будет создаваться с нуля.

Если нужно применить к существующей БД:

```bash
cd /opt/eaip/infra/db
docker compose -f ../docker-compose.staging.yml exec -T postgres psql -U eaip_user -d eaip_db < init.sql
```

