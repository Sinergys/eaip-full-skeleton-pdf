#!/bin/bash
# Скрипт для проверки создания таблиц в БД

echo "🔍 Проверка структуры базы данных EAIP"
echo "========================================"
echo ""

# Проверяем, запущен ли контейнер postgres
if ! docker compose ps postgres | grep -q "Up"; then
    echo "❌ Контейнер PostgreSQL не запущен"
    echo "   Запустите: docker compose up -d postgres"
    exit 1
fi

echo "✅ Контейнер PostgreSQL запущен"
echo ""

# Получаем переменные окружения
source .env 2>/dev/null || true
POSTGRES_USER=${POSTGRES_USER:-eaip_user}
POSTGRES_DB=${POSTGRES_DB:-eaip_db}

echo "📊 Проверка таблиц в базе данных '$POSTGRES_DB'..."
echo ""

# Проверяем список таблиц
TABLES=$(docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
")

if [ -z "$TABLES" ]; then
    echo "❌ Таблицы не найдены!"
    echo "   Возможно, init.sql не выполнился или БД не инициализирована"
    exit 1
fi

echo "✅ Найдено таблиц:"
echo "$TABLES" | grep -v '^$' | while read table; do
    COUNT=$(docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' ')
    echo "   - $table ($COUNT записей)"
done

echo ""
echo "📋 Детальная информация:"
docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;
"

echo ""
echo "✅ Проверка завершена!"

