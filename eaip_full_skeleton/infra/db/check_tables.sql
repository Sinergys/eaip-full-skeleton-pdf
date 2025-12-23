-- Скрипт для проверки создания таблиц
-- Использование: docker compose exec postgres psql -U eaip_user -d eaip_db -f /docker-entrypoint-initdb.d/check_tables.sql

-- Проверка таблиц ingest
SELECT 'ingest_batches' as table_name, COUNT(*) as row_count FROM ingest_batches
UNION ALL
SELECT 'ingest_parsing_results', COUNT(*) FROM ingest_parsing_results;

-- Проверка таблиц validate
SELECT 'validate_results' as table_name, COUNT(*) as row_count FROM validate_results;

-- Проверка таблиц analytics
SELECT 'analytics_forecasts' as table_name, COUNT(*) as row_count FROM analytics_forecasts
UNION ALL
SELECT 'analytics_data_points', COUNT(*) FROM analytics_data_points;

-- Проверка таблиц gateway-auth
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'user_sessions', COUNT(*) FROM user_sessions;

-- Проверка таблиц reports
SELECT 'reports' as table_name, COUNT(*) as row_count FROM reports;

-- Проверка таблиц management
SELECT 'audit_records' as table_name, COUNT(*) as row_count FROM audit_records;

-- Проверка таблиц recommend
SELECT 'recommendations' as table_name, COUNT(*) as row_count FROM recommendations;

-- Проверка системных таблиц
SELECT 'system_logs' as table_name, COUNT(*) as row_count FROM system_logs;

-- Список всех таблиц
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;

