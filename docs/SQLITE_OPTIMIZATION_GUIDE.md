# 🚀 Оптимизация SQLite для продуктивной работы

## ✅ Статус: ОПТИМИЗАЦИЯ ВЫПОЛНЕНА (2025-12-01)

Все оптимизации применены и работают автоматически:
- ✅ WAL режим включен
- ✅ 29 индексов создано
- ✅ Настройки производительности применяются при каждом подключении

**Проверка:** `python tools/check_optimization.py`

---

## Контекст
- Запуск вручную (не 24/7)
- 30 предприятий
- 5 пользователей
- ~10GB данных
- SQLite работает стабильно, нужны базовые улучшения

---

## 📋 Инструкция запуска (3 шага)

> **Примечание:** Если оптимизация уже выполнена, эти шаги можно пропустить.  
> Для проверки текущего состояния используйте: `python tools/check_optimization.py`

### Шаг 1: Включить WAL режим

```bash
# Windows PowerShell
sqlite3 eaip_full_skeleton\services\ingest\ingest_data.db "PRAGMA journal_mode=WAL;"

# Linux/Mac
sqlite3 eaip_full_skeleton/services/ingest/ingest_data.db "PRAGMA journal_mode=WAL;"
```

**Результат:** `wal` (Write-Ahead Logging включен)

**Что это дает:**
- ✅ Лучшая производительность при конкурентном доступе
- ✅ Читатели не блокируют писателей
- ✅ Быстрее запись данных

---

### Шаг 2: Создать индексы

```bash
# Windows PowerShell
sqlite3 eaip_full_skeleton\services\ingest\ingest_data.db < tools\optimize_sqlite.sql

# Linux/Mac
sqlite3 eaip_full_skeleton/services/ingest/ingest_data.db < tools/optimize_sqlite.sql
```

**Или вручную через sqlite3:**
```bash
sqlite3 ingest_data.db
.read tools/optimize_sqlite.sql
.quit
```

**Что создается:**
- 25+ индексов для оптимизации запросов
- Индексы для всех частых WHERE/JOIN/ORDER BY
- Составные индексы для сложных запросов

**Проверка:**
```sql
-- Проверить созданные индексы
SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%';
```

---

### Шаг 3: Настроить автоматический бэкап

#### Windows PowerShell:
```powershell
# Сделать скрипт исполняемым (если нужно)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Запустить бэкап
.\tools\backup_sqlite.ps1

# Или с указанием пути
.\tools\backup_sqlite.ps1 "eaip_full_skeleton\services\ingest\ingest_data.db"
```

#### Linux/Mac:
```bash
# Сделать скрипт исполняемым
chmod +x tools/backup_sqlite.sh

# Запустить бэкап
./tools/backup_sqlite.sh

# Или с указанием пути
./tools/backup_sqlite.sh eaip_full_skeleton/services/ingest/ingest_data.db
```

**Результат:**
- Создается файл `backups/ingest_data_YYYYMMDD_HHMMSS.db`
- Показывается размер и список последних бэкапов

---

## 📊 Созданные индексы

### Таблица `uploads` (5 индексов)
- `idx_uploads_batch_id` - поиск по batch_id (очень часто)
- `idx_uploads_enterprise_id` - фильтрация по предприятию
- `idx_uploads_created_at` - сортировка по дате
- `idx_uploads_enterprise_filename_size` - поиск дубликатов
- `idx_uploads_status` - фильтрация по статусу

### Таблица `parsed_data` (2 индекса)
- `idx_parsed_data_upload_id` - JOIN с uploads
- `idx_parsed_data_updated_at` - сортировка по дате обновления

### Таблица `enterprises` (1 индекс)
- `idx_enterprises_name` - поиск по имени (COLLATE NOCASE)

### Таблица `aggregated_data` (4 индекса)
- `idx_aggregated_data_enterprise_resource_period` - составной (основной запрос)
- `idx_aggregated_data_enterprise_id` - фильтрация
- `idx_aggregated_data_period` - сортировка
- `idx_aggregated_data_batch_id` - связь с uploads

### Таблица `node_consumption` (3 индекса)
- `idx_node_consumption_enterprise_node_period_type` - составной (уникальный поиск)
- `idx_node_consumption_enterprise_id` - фильтрация
- `idx_node_consumption_period` - сортировка

### Таблица `normative_documents` (3 индекса)
- `idx_normative_documents_file_hash` - поиск дубликатов
- `idx_normative_documents_uploaded_at` - сортировка
- `idx_normative_documents_status` - фильтрация

### Таблица `normative_rules` (3 индекса)
- `idx_normative_rules_document_id` - JOIN
- `idx_normative_rules_rule_type` - фильтрация
- `idx_normative_rules_type_confidence_created` - составной для сортировки

### Таблица `normative_references` (3 индекса)
- `idx_normative_references_rule_id` - JOIN
- `idx_normative_references_field_name` - поиск
- `idx_normative_references_field_sheet` - составной поиск

### Таблица `normative_violations` (4 индекса)
- `idx_normative_violations_enterprise_id` - фильтрация
- `idx_normative_violations_batch_id` - фильтрация
- `idx_normative_violations_status` - фильтрация
- `idx_normative_violations_created_at` - сортировка

### Таблица `uploads_storage` (1 индекс)
- `idx_uploads_storage_file_hash` - поиск дубликатов

**Всего: 29 индексов**

---

## 🔧 Дополнительные настройки производительности

**✅ Применено автоматически** в `database.py` → `get_connection()`:

```python
# Оптимизация производительности SQLite
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
conn.execute("PRAGMA cache_size=-64000")  # 64MB
conn.execute("PRAGMA temp_store=MEMORY")
conn.execute("PRAGMA mmap_size=268435456")  # 256MB
```

**Преимущество:** Настройки применяются при каждом подключении к БД, не требуют ручной настройки.

---

## 📅 Рекомендации по бэкапам

### Ручной бэкап:
```bash
# Перед важными операциями
./tools/backup_sqlite.sh
```

### Автоматический бэкап (cron/task scheduler):

#### Windows (Task Scheduler):
1. Открыть "Планировщик заданий"
2. Создать задачу
3. Триггер: ежедневно в 2:00
4. Действие: `powershell.exe -File "C:\eaip\tools\backup_sqlite.ps1"`

#### Linux (cron):
```bash
# Добавить в crontab (crontab -e)
0 2 * * * /path/to/eaip/tools/backup_sqlite.sh >> /var/log/sqlite_backup.log 2>&1
```

---

## ✅ Проверка оптимизации

### До оптимизации:
```sql
-- Проверить текущий режим
PRAGMA journal_mode;
-- Результат: delete (по умолчанию)

-- Проверить индексы
SELECT COUNT(*) FROM sqlite_master WHERE type='index';
-- Результат: ~5-10 (только PRIMARY KEY и UNIQUE)
```

### После оптимизации:
```sql
-- Проверить WAL режим
PRAGMA journal_mode;
-- Результат: wal ✅

-- Проверить индексы
SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%';
-- Результат: 29 ✅

-- Проверить настройки
PRAGMA cache_size;
-- Результат: -64000 (64MB) ✅
```

---

## 📈 Ожидаемые улучшения

- **Скорость запросов:** +50-200% (зависит от запроса)
- **Конкурентный доступ:** +300% (благодаря WAL)
- **Поиск по индексам:** +500-1000% (для больших таблиц)
- **Размер БД:** +5-10% (из-за индексов, но это нормально)

---

## ⚠️ Важные замечания

1. **WAL режим:** После включения создаются файлы `.db-wal` и `.db-shm`. Не удаляйте их!
2. **Индексы:** Занимают место, но значительно ускоряют запросы
3. **Бэкапы:** Делайте перед важными операциями и регулярно
4. **Размер БД:** При 10GB индексы займут ~500MB-1GB (приемлемо)

---

## 🆘 Решение проблем

### Проблема: "database is locked"
**Решение:** WAL режим решает эту проблему. Если все еще возникает:
```sql
PRAGMA busy_timeout=30000;  -- 30 секунд ожидания
```

### Проблема: Медленные запросы
**Решение:** Проверить, используются ли индексы:
```sql
EXPLAIN QUERY PLAN SELECT * FROM uploads WHERE batch_id = 'xxx';
-- Должно показать: "SEARCH TABLE uploads USING INDEX idx_uploads_batch_id"
```

### Проблема: Большой размер БД
**Решение:** Периодически делать VACUUM:
```sql
VACUUM;
-- Оптимизирует БД, уменьшает размер
```

---

## 📚 Дополнительные ресурсы

- [SQLite Performance Tuning](https://www.sqlite.org/performance.html)
- [WAL Mode](https://www.sqlite.org/wal.html)
- [Index Usage](https://www.sqlite.org/queryplanner.html)

