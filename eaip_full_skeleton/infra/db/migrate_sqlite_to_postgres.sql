-- ============================================
-- Миграция SQLite -> PostgreSQL для ingest сервиса
-- ============================================
-- Этот скрипт создает таблицы PostgreSQL на основе структуры SQLite

-- ============================================
-- 1. ENTERPRISES - Предприятия
-- ============================================

CREATE TABLE IF NOT EXISTS enterprises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    industry TEXT,
    enterprise_type TEXT,
    product_type TEXT
);

CREATE INDEX IF NOT EXISTS idx_enterprises_name ON enterprises(name);

-- ============================================
-- 2. UPLOADS - Загрузки файлов
-- ============================================

CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(255) NOT NULL UNIQUE,
    enterprise_id INTEGER NOT NULL REFERENCES enterprises(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    status VARCHAR(50) NOT NULL,
    parsing_summary TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_uploads_batch_id ON uploads(batch_id);
CREATE INDEX IF NOT EXISTS idx_uploads_enterprise_id ON uploads(enterprise_id);
CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(status);

-- ============================================
-- 3. PARSED_DATA - Распарсенные данные
-- ============================================

CREATE TABLE IF NOT EXISTS parsed_data (
    upload_id INTEGER PRIMARY KEY REFERENCES uploads(id) ON DELETE CASCADE,
    raw_json JSONB,  -- JSONB вместо TEXT для лучшей производительности
    editable_text TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_parsed_data_raw_json ON parsed_data USING GIN(raw_json);

-- ============================================
-- 4. UPLOADS_STORAGE - Хранилище метаданных файлов
-- ============================================

CREATE TABLE IF NOT EXISTS uploads_storage (
    upload_id INTEGER PRIMARY KEY REFERENCES uploads(id) ON DELETE CASCADE,
    file_hash VARCHAR(64),
    file_mtime DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_uploads_storage_file_hash ON uploads_storage(file_hash);

-- ============================================
-- 5. NORMATIVE_DOCUMENTS - Нормативные документы
-- ============================================

CREATE TABLE IF NOT EXISTS normative_documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    file_path TEXT NOT NULL,
    file_hash VARCHAR(64),
    file_size BIGINT,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ai_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'pending',
    full_text TEXT,
    parsed_data_json JSONB
);

CREATE INDEX IF NOT EXISTS idx_normative_documents_file_hash ON normative_documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_normative_documents_type ON normative_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_normative_documents_status ON normative_documents(processing_status);

-- ============================================
-- 6. NORMATIVE_RULES - Правила из нормативных документов
-- ============================================

CREATE TABLE IF NOT EXISTS normative_rules (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES normative_documents(id) ON DELETE CASCADE,
    rule_type VARCHAR(100) NOT NULL,
    description TEXT,
    formula TEXT,
    parameters TEXT,
    numeric_value DOUBLE PRECISION,
    unit VARCHAR(50),
    ai_extracted BOOLEAN DEFAULT FALSE,
    extraction_confidence DOUBLE PRECISION,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_normative_rules_document_id ON normative_rules(document_id);
CREATE INDEX IF NOT EXISTS idx_normative_rules_type ON normative_rules(rule_type);

-- ============================================
-- 7. NORMATIVE_REFERENCES - Связи правил с полями
-- ============================================

CREATE TABLE IF NOT EXISTS normative_references (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER NOT NULL REFERENCES normative_rules(id) ON DELETE CASCADE,
    field_name VARCHAR(255) NOT NULL,
    sheet_name VARCHAR(255),
    cell_reference VARCHAR(50),
    passport_field_path TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_normative_references_rule_id ON normative_references(rule_id);
CREATE INDEX IF NOT EXISTS idx_normative_references_field_name ON normative_references(field_name);

-- ============================================
-- 8. NORMATIVE_VIOLATIONS - Нарушения нормативов
-- ============================================

CREATE TABLE IF NOT EXISTS normative_violations (
    id SERIAL PRIMARY KEY,
    enterprise_id INTEGER REFERENCES enterprises(id) ON DELETE SET NULL,
    batch_id VARCHAR(255),
    field_name VARCHAR(255) NOT NULL,
    sheet_name VARCHAR(255),
    actual_value DOUBLE PRECISION NOT NULL,
    normative_value DOUBLE PRECISION,
    deviation_percent DOUBLE PRECISION,
    status VARCHAR(50) NOT NULL,
    message TEXT,
    rule_id INTEGER REFERENCES normative_rules(id) ON DELETE SET NULL,
    cell_reference VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_normative_violations_enterprise_id ON normative_violations(enterprise_id);
CREATE INDEX IF NOT EXISTS idx_normative_violations_batch_id ON normative_violations(batch_id);
CREATE INDEX IF NOT EXISTS idx_normative_violations_status ON normative_violations(status);

-- ============================================
-- 9. AGGREGATED_DATA - Агрегированные данные энергоресурсов
-- ============================================

CREATE TABLE IF NOT EXISTS aggregated_data (
    id SERIAL PRIMARY KEY,
    enterprise_id INTEGER NOT NULL REFERENCES enterprises(id) ON DELETE CASCADE,
    batch_id VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    period VARCHAR(50) NOT NULL,
    data_json JSONB NOT NULL,  -- JSONB для лучшей производительности
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(enterprise_id, resource_type, period)
);

CREATE INDEX IF NOT EXISTS idx_aggregated_data_enterprise_id ON aggregated_data(enterprise_id);
CREATE INDEX IF NOT EXISTS idx_aggregated_data_batch_id ON aggregated_data(batch_id);
CREATE INDEX IF NOT EXISTS idx_aggregated_data_resource_type ON aggregated_data(resource_type);
CREATE INDEX IF NOT EXISTS idx_aggregated_data_period ON aggregated_data(period);
CREATE INDEX IF NOT EXISTS idx_aggregated_data_json ON aggregated_data USING GIN(data_json);

-- ============================================
-- 10. NODE_CONSUMPTION - Потребление по узлам учёта
-- ============================================

CREATE TABLE IF NOT EXISTS node_consumption (
    id SERIAL PRIMARY KEY,
    enterprise_id INTEGER NOT NULL REFERENCES enterprises(id) ON DELETE CASCADE,
    batch_id VARCHAR(255) NOT NULL,
    node_name VARCHAR(255) NOT NULL,
    period VARCHAR(50) NOT NULL,
    active_energy_kwh DOUBLE PRECISION,
    reactive_energy_kvarh DOUBLE PRECISION,
    cost_sum DOUBLE PRECISION,
    data_type VARCHAR(50) DEFAULT 'consumption',
    data_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(enterprise_id, node_name, period, data_type)
);

CREATE INDEX IF NOT EXISTS idx_node_consumption_enterprise_id ON node_consumption(enterprise_id);
CREATE INDEX IF NOT EXISTS idx_node_consumption_batch_id ON node_consumption(batch_id);
CREATE INDEX IF NOT EXISTS idx_node_consumption_period ON node_consumption(period);

-- ============================================
-- Триггеры для автоматического обновления updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_aggregated_data_updated_at BEFORE UPDATE ON aggregated_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_node_consumption_updated_at BEFORE UPDATE ON node_consumption
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Комментарии к таблицам
-- ============================================

COMMENT ON TABLE enterprises IS 'Предприятия';
COMMENT ON TABLE uploads IS 'Загрузки файлов';
COMMENT ON TABLE parsed_data IS 'Распарсенные данные файлов';
COMMENT ON TABLE normative_documents IS 'Нормативные документы';
COMMENT ON TABLE normative_rules IS 'Правила из нормативных документов';
COMMENT ON TABLE aggregated_data IS 'Агрегированные данные энергоресурсов';
COMMENT ON TABLE node_consumption IS 'Потребление электроэнергии по узлам учёта';

