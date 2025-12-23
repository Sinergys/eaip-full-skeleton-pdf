#!/bin/bash

# Скрипт резервного копирования SQLite базы данных
# Использование: ./backup_sqlite.sh [путь_к_базе]

set -e  # Остановить при ошибке

# Определяем путь к БД
if [ -n "$1" ]; then
    DB_PATH="$1"
else
    # Пробуем найти БД в стандартных местах
    if [ -f "eaip_full_skeleton/services/ingest/ingest_data.db" ]; then
        DB_PATH="eaip_full_skeleton/services/ingest/ingest_data.db"
    elif [ -f "data/ingest_data.db" ]; then
        DB_PATH="data/ingest_data.db"
    elif [ -f "ingest_data.db" ]; then
        DB_PATH="ingest_data.db"
    else
        echo "❌ Ошибка: База данных не найдена"
        echo "Использование: $0 [путь_к_базе.db]"
        exit 1
    fi
fi

# Проверяем существование файла
if [ ! -f "$DB_PATH" ]; then
    echo "❌ Ошибка: Файл не найден: $DB_PATH"
    exit 1
fi

# Создаем директорию для бэкапов
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

# Генерируем имя файла с датой и временем
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME=$(basename "$DB_PATH" .db)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.db"

# Выполняем бэкап
echo "📦 Создание резервной копии..."
echo "   Источник: $DB_PATH"
echo "   Назначение: $BACKUP_FILE"

# Используем sqlite3 для создания бэкапа (более надежно, чем cp)
sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"

# Проверяем размер файла
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
ORIGINAL_SIZE=$(du -h "$DB_PATH" | cut -f1)

echo "✅ Резервная копия создана успешно"
echo "   Размер оригинала: $ORIGINAL_SIZE"
echo "   Размер бэкапа: $BACKUP_SIZE"
echo "   Файл: $BACKUP_FILE"

# Опционально: удалить старые бэкапы (старше 30 дней)
if [ -n "$CLEANUP_OLD_BACKUPS" ]; then
    echo "🧹 Очистка старых бэкапов (старше 30 дней)..."
    find "$BACKUP_DIR" -name "${DB_NAME}_*.db" -type f -mtime +30 -delete
    echo "✅ Очистка завершена"
fi

# Показываем список последних бэкапов
echo ""
echo "📋 Последние 5 бэкапов:"
ls -lht "$BACKUP_DIR"/*.db 2>/dev/null | head -5 || echo "   Бэкапы не найдены"

