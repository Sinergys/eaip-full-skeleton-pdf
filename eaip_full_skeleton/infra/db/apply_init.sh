#!/bin/bash
# Скрипт для применения init.sql к существующей БД

echo "📊 Применение init.sql к существующей БД"
echo "========================================"
echo ""

# Проверяем наличие файла
if [ ! -f "init.sql" ]; then
    echo "❌ Файл init.sql не найден"
    exit 1
fi

# Получаем переменные окружения
source ../.env 2>/dev/null || true
POSTGRES_USER=${POSTGRES_USER:-eaip_user}
POSTGRES_DB=${POSTGRES_DB:-eaip_db}

echo "📝 Применяю init.sql к БД '$POSTGRES_DB'..."
echo ""

# Применяем скрипт
docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < init.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ init.sql успешно применен!"
    echo ""
    echo "📋 Проверка созданных таблиц:"
    docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"
else
    echo ""
    echo "❌ Ошибка при применении init.sql"
    exit 1
fi

