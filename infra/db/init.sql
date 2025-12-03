-- EAIP Database Initialization Script
-- Создание базовых таблиц для всех сервисов

-- ============================================
-- 1. INGEST SERVICE - Результаты парсинга файлов
-- ============================================

CREATE TABLE IF NOT EXISTS ingest_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id VARCHAR(255) UNIQUE NOT NULL,
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT,
    file_path TEXT,
    status VARCHAR(50) DEFAULT 'processing',
    ai_used BOOLEAN DEFAULT FALSE,
    ai_provider VARCHAR(50),
    ocr_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ingest_batches_batch_id ON ingest_batches(batch_id);
CREATE INDEX IF NOT EXISTS idx_ingest_batches_status ON ingest_batches(status);
CREATE INDEX IF NOT EXISTS idx_ingest_batches_created_at ON ingest_batches(created_at);

CREATE TABLE IF NOT EXISTS ingest_parsing_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id VARCHAR(255) NOT NULL REFERENCES ingest_batches(batch_id) ON DELETE CASCADE,
    parsed BOOLEAN DEFAULT FALSE,
    total_characters INTEGER DEFAULT 0,
    total_pages INTEGER DEFAULT 0,
    total_tables INTEGER DEFAULT 0,
    extracted_text TEXT,
    structured_data JSONB,
    metadata JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_parsing_results_batch_id ON ingest_parsing_results(batch_id);
CREATE INDEX IF NOT EXISTS idx_parsing_results_parsed ON ingest_parsing_results(parsed);

-- ============================================
-- 2. VALIDATE SERVICE - Результаты валидации
-- ============================================

CREATE TABLE IF NOT EXISTS validate_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id VARCHAR(255) NOT NULL,
    passed BOOLEAN DEFAULT FALSE,
    issues JSONB DEFAULT '[]'::jsonb,
    validation_rules JSONB,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_validate_results_batch_id ON validate_results(batch_id);
CREATE INDEX IF NOT EXISTS idx_validate_results_passed ON validate_results(passed);

-- ============================================
-- 3. ANALYTICS SERVICE - Аналитические данные
-- ============================================

CREATE TABLE IF NOT EXISTS analytics_forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id VARCHAR(255),
    meter_id VARCHAR(255),
    forecast_data JSONB NOT NULL,
    horizon INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analytics_forecasts_batch_id ON analytics_forecasts(batch_id);
CREATE INDEX IF NOT EXISTS idx_analytics_forecasts_meter_id ON analytics_forecasts(meter_id);

CREATE TABLE IF NOT EXISTS analytics_data_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id VARCHAR(255),
    meter_id VARCHAR(255),
    timestamp TIMESTAMP NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analytics_data_points_batch_id ON analytics_data_points(batch_id);
CREATE INDEX IF NOT EXISTS idx_analytics_data_points_timestamp ON analytics_data_points(timestamp);

-- ============================================
-- 4. GATEWAY-AUTH SERVICE - Пользователи и аутентификация
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- ============================================
-- 5. REPORTS SERVICE - Сгенерированные отчеты
-- ============================================

CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_id VARCHAR(255) NOT NULL,
    report_type VARCHAR(100) NOT NULL,
    file_path TEXT,
    file_size BIGINT,
    status VARCHAR(50) DEFAULT 'generating',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reports_audit_id ON reports(audit_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);

-- ============================================
-- 6. MANAGEMENT SERVICE - Управление данными
-- ============================================

CREATE TABLE IF NOT EXISTS audit_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_id VARCHAR(255) UNIQUE NOT NULL,
    batch_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'draft',
    data JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_records_audit_id ON audit_records(audit_id);
CREATE INDEX IF NOT EXISTS idx_audit_records_status ON audit_records(status);

-- ============================================
-- 7. RECOMMEND SERVICE - Рекомендации
-- ============================================

CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_id VARCHAR(255) NOT NULL,
    recommendation_type VARCHAR(100) NOT NULL,
    priority VARCHAR(50) DEFAULT 'medium',
    content TEXT NOT NULL,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_recommendations_audit_id ON recommendations(audit_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_priority ON recommendations(priority);

-- ============================================
-- 8. Системные таблицы
-- ============================================

CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(100) NOT NULL,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_system_logs_service ON system_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);

-- ============================================
-- Функции для автоматического обновления updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры для автоматического обновления updated_at
CREATE TRIGGER update_ingest_batches_updated_at BEFORE UPDATE ON ingest_batches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ingest_parsing_results_updated_at BEFORE UPDATE ON ingest_parsing_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audit_records_updated_at BEFORE UPDATE ON audit_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Инициализация завершена
-- ============================================

