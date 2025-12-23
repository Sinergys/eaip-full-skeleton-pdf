-- ============================================
-- Оптимизация SQLite для продуктивной работы
-- ============================================

-- 1. Включить WAL режим (Write-Ahead Logging)
-- Улучшает производительность при конкурентном доступе
PRAGMA journal_mode=WAL;

-- 2. Настройки производительности
PRAGMA synchronous=NORMAL;  -- Баланс между безопасностью и скоростью
PRAGMA cache_size=-64000;   -- 64MB кэш (по умолчанию 2MB)
PRAGMA temp_store=MEMORY;    -- Временные таблицы в памяти
PRAGMA mmap_size=268435456;  -- 256MB memory-mapped I/O

-- 3. Индексы для таблицы uploads
-- batch_id используется в WHERE (очень часто)
CREATE INDEX IF NOT EXISTS idx_uploads_batch_id ON uploads(batch_id);

-- enterprise_id используется в WHERE и JOIN
CREATE INDEX IF NOT EXISTS idx_uploads_enterprise_id ON uploads(enterprise_id);

-- created_at используется в ORDER BY
CREATE INDEX IF NOT EXISTS idx_uploads_created_at ON uploads(created_at DESC);

-- Составной индекс для поиска дубликатов
CREATE INDEX IF NOT EXISTS idx_uploads_enterprise_filename_size ON uploads(enterprise_id, filename, file_size);

-- status для фильтрации
CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(status);

-- 4. Индексы для таблицы parsed_data
-- upload_id используется в JOIN и WHERE
CREATE INDEX IF NOT EXISTS idx_parsed_data_upload_id ON parsed_data(upload_id);

-- updated_at для сортировки
CREATE INDEX IF NOT EXISTS idx_parsed_data_updated_at ON parsed_data(updated_at DESC);

-- 5. Индексы для таблицы enterprises
-- name используется в WHERE (уже есть UNIQUE, но индекс нужен для COLLATE NOCASE)
CREATE INDEX IF NOT EXISTS idx_enterprises_name ON enterprises(name COLLATE NOCASE);

-- id уже PRIMARY KEY, но можно добавить для JOIN оптимизации
-- (не нужно, PRIMARY KEY уже индекс)

-- 6. Индексы для таблицы aggregated_data
-- Составной индекс для частого запроса: enterprise_id + resource_type + period
CREATE INDEX IF NOT EXISTS idx_aggregated_data_enterprise_resource_period 
    ON aggregated_data(enterprise_id, resource_type, period);

-- enterprise_id для фильтрации
CREATE INDEX IF NOT EXISTS idx_aggregated_data_enterprise_id ON aggregated_data(enterprise_id);

-- period для сортировки
CREATE INDEX IF NOT EXISTS idx_aggregated_data_period ON aggregated_data(period);

-- batch_id для связи с uploads
CREATE INDEX IF NOT EXISTS idx_aggregated_data_batch_id ON aggregated_data(batch_id);

-- 7. Индексы для таблицы node_consumption
-- Составной индекс для уникального поиска
CREATE INDEX IF NOT EXISTS idx_node_consumption_enterprise_node_period_type 
    ON node_consumption(enterprise_id, node_name, period, data_type);

-- enterprise_id для фильтрации
CREATE INDEX IF NOT EXISTS idx_node_consumption_enterprise_id ON node_consumption(enterprise_id);

-- period для сортировки
CREATE INDEX IF NOT EXISTS idx_node_consumption_period ON node_consumption(period);

-- 8. Индексы для таблицы normative_documents
-- file_hash для поиска дубликатов
CREATE INDEX IF NOT EXISTS idx_normative_documents_file_hash ON normative_documents(file_hash);

-- uploaded_at для сортировки
CREATE INDEX IF NOT EXISTS idx_normative_documents_uploaded_at ON normative_documents(uploaded_at DESC);

-- processing_status для фильтрации
CREATE INDEX IF NOT EXISTS idx_normative_documents_status ON normative_documents(processing_status);

-- 9. Индексы для таблицы normative_rules
-- document_id для JOIN
CREATE INDEX IF NOT EXISTS idx_normative_rules_document_id ON normative_rules(document_id);

-- rule_type для фильтрации
CREATE INDEX IF NOT EXISTS idx_normative_rules_rule_type ON normative_rules(rule_type);

-- Составной индекс для сортировки
CREATE INDEX IF NOT EXISTS idx_normative_rules_type_confidence_created 
    ON normative_rules(rule_type, extraction_confidence DESC, created_at DESC);

-- 10. Индексы для таблицы normative_references
-- rule_id для JOIN
CREATE INDEX IF NOT EXISTS idx_normative_references_rule_id ON normative_references(rule_id);

-- field_name для поиска
CREATE INDEX IF NOT EXISTS idx_normative_references_field_name ON normative_references(field_name);

-- Составной индекс для поиска по полю и листу
CREATE INDEX IF NOT EXISTS idx_normative_references_field_sheet 
    ON normative_references(field_name, sheet_name);

-- 11. Индексы для таблицы normative_violations
-- enterprise_id для фильтрации
CREATE INDEX IF NOT EXISTS idx_normative_violations_enterprise_id ON normative_violations(enterprise_id);

-- batch_id для фильтрации
CREATE INDEX IF NOT EXISTS idx_normative_violations_batch_id ON normative_violations(batch_id);

-- status для фильтрации
CREATE INDEX IF NOT EXISTS idx_normative_violations_status ON normative_violations(status);

-- created_at для сортировки
CREATE INDEX IF NOT EXISTS idx_normative_violations_created_at ON normative_violations(created_at DESC);

-- 12. Индексы для таблицы uploads_storage
-- upload_id уже PRIMARY KEY
-- file_hash для поиска дубликатов
CREATE INDEX IF NOT EXISTS idx_uploads_storage_file_hash ON uploads_storage(file_hash);

-- ============================================
-- Проверка индексов
-- ============================================
-- Выполнить после создания индексов:
-- SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%';

