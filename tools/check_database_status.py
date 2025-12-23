"""Проверка состояния базы данных и импортированных данных"""
import sqlite3
import os
import json
from pathlib import Path

# Путь к БД
db_path = os.path.join('eaip_full_skeleton', 'services', 'ingest', 'ingest_data.db')

results = {
    "db_exists": os.path.exists(db_path),
    "enterprises": 0,
    "uploads": 0,
    "parsed_data": 0,
    "enterprises_list": [],
    "uploads_list": [],
    "parsed_data_summary": []
}

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Проверка enterprises
    rows = conn.execute('SELECT COUNT(*) as cnt FROM enterprises').fetchone()
    results["enterprises"] = rows[0] if rows else 0
    
    if results["enterprises"] > 0:
        enterprises = conn.execute('SELECT id, name, created_at FROM enterprises').fetchall()
        results["enterprises_list"] = [dict(row) for row in enterprises]
    
    # Проверка uploads
    rows = conn.execute('SELECT COUNT(*) as cnt FROM uploads').fetchone()
    results["uploads"] = rows[0] if rows else 0
    
    if results["uploads"] > 0:
        uploads = conn.execute('''
            SELECT u.id, u.batch_id, u.filename, u.file_type, u.file_size, 
                   u.status, u.created_at, e.name as enterprise_name
            FROM uploads u
            JOIN enterprises e ON u.enterprise_id = e.id
            ORDER BY u.created_at DESC
            LIMIT 20
        ''').fetchall()
        results["uploads_list"] = [dict(row) for row in uploads]
    
    # Проверка parsed_data
    rows = conn.execute('SELECT COUNT(*) as cnt FROM parsed_data').fetchone()
    results["parsed_data"] = rows[0] if rows else 0
    
    if results["parsed_data"] > 0:
        parsed = conn.execute('''
            SELECT pd.upload_id, u.filename, u.file_type, 
                   LENGTH(pd.raw_json) as json_size,
                   pd.updated_at
            FROM parsed_data pd
            JOIN uploads u ON pd.upload_id = u.id
            ORDER BY pd.updated_at DESC
            LIMIT 10
        ''').fetchall()
        results["parsed_data_summary"] = [dict(row) for row in parsed]
    
    conn.close()

# Сохраняем результаты
output_file = Path("reports") / "ocr" / "database_status_check.json"
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print(f"✅ Проверка БД завершена. Результаты: {output_file}")
print(f"   Enterprises: {results['enterprises']}")
print(f"   Uploads: {results['uploads']}")
print(f"   Parsed data: {results['parsed_data']}")

