#!/usr/bin/env python3
"""
Скрипт для создания индексов в SQLite БД
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("eaip_full_skeleton/services/ingest/ingest_data.db")

if not DB_PATH.exists():
    print(f"❌ БД не найдена: {DB_PATH}")
    sys.exit(1)

# SQL команды для создания индексов
INDEXES = [
    # uploads
    "CREATE INDEX IF NOT EXISTS idx_uploads_batch_id ON uploads(batch_id)",
    "CREATE INDEX IF NOT EXISTS idx_uploads_enterprise_id ON uploads(enterprise_id)",
    "CREATE INDEX IF NOT EXISTS idx_uploads_created_at ON uploads(created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_uploads_enterprise_filename_size ON uploads(enterprise_id, filename, file_size)",
    "CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(status)",
    
    # parsed_data
    "CREATE INDEX IF NOT EXISTS idx_parsed_data_upload_id ON parsed_data(upload_id)",
    "CREATE INDEX IF NOT EXISTS idx_parsed_data_updated_at ON parsed_data(updated_at DESC)",
    
    # enterprises
    "CREATE INDEX IF NOT EXISTS idx_enterprises_name ON enterprises(name COLLATE NOCASE)",
    
    # aggregated_data
    "CREATE INDEX IF NOT EXISTS idx_aggregated_data_enterprise_resource_period ON aggregated_data(enterprise_id, resource_type, period)",
    "CREATE INDEX IF NOT EXISTS idx_aggregated_data_enterprise_id ON aggregated_data(enterprise_id)",
    "CREATE INDEX IF NOT EXISTS idx_aggregated_data_period ON aggregated_data(period)",
    "CREATE INDEX IF NOT EXISTS idx_aggregated_data_batch_id ON aggregated_data(batch_id)",
    
    # node_consumption
    "CREATE INDEX IF NOT EXISTS idx_node_consumption_enterprise_node_period_type ON node_consumption(enterprise_id, node_name, period, data_type)",
    "CREATE INDEX IF NOT EXISTS idx_node_consumption_enterprise_id ON node_consumption(enterprise_id)",
    "CREATE INDEX IF NOT EXISTS idx_node_consumption_period ON node_consumption(period)",
    
    # normative_documents
    "CREATE INDEX IF NOT EXISTS idx_normative_documents_file_hash ON normative_documents(file_hash)",
    "CREATE INDEX IF NOT EXISTS idx_normative_documents_uploaded_at ON normative_documents(uploaded_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_normative_documents_status ON normative_documents(processing_status)",
    
    # normative_rules
    "CREATE INDEX IF NOT EXISTS idx_normative_rules_document_id ON normative_rules(document_id)",
    "CREATE INDEX IF NOT EXISTS idx_normative_rules_rule_type ON normative_rules(rule_type)",
    "CREATE INDEX IF NOT EXISTS idx_normative_rules_type_confidence_created ON normative_rules(rule_type, extraction_confidence DESC, created_at DESC)",
    
    # normative_references
    "CREATE INDEX IF NOT EXISTS idx_normative_references_rule_id ON normative_references(rule_id)",
    "CREATE INDEX IF NOT EXISTS idx_normative_references_field_name ON normative_references(field_name)",
    "CREATE INDEX IF NOT EXISTS idx_normative_references_field_sheet ON normative_references(field_name, sheet_name)",
    
    # normative_violations
    "CREATE INDEX IF NOT EXISTS idx_normative_violations_enterprise_id ON normative_violations(enterprise_id)",
    "CREATE INDEX IF NOT EXISTS idx_normative_violations_batch_id ON normative_violations(batch_id)",
    "CREATE INDEX IF NOT EXISTS idx_normative_violations_status ON normative_violations(status)",
    "CREATE INDEX IF NOT EXISTS idx_normative_violations_created_at ON normative_violations(created_at DESC)",
    
    # uploads_storage
    "CREATE INDEX IF NOT EXISTS idx_uploads_storage_file_hash ON uploads_storage(file_hash)",
]

def main():
    print("📊 Создание индексов...")
    print(f"   БД: {DB_PATH}")
    
    conn = sqlite3.connect(str(DB_PATH))
    created = 0
    errors = 0
    
    for index_sql in INDEXES:
        try:
            conn.execute(index_sql)
            index_name = index_sql.split("idx_")[1].split(" ")[0] if "idx_" in index_sql else "unknown"
            print(f"   ✅ {index_name}")
            created += 1
        except Exception as e:
            errors += 1
            print(f"   ⚠️ Ошибка: {str(e)[:60]}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Создано индексов: {created}")
    if errors > 0:
        print(f"⚠️ Ошибок: {errors}")
    
    # Проверка
    conn = sqlite3.connect(str(DB_PATH))
    indexes = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
    ).fetchall()
    conn.close()
    
    print(f"📋 Всего индексов idx_*: {len(indexes)}")
    return 0 if errors == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

