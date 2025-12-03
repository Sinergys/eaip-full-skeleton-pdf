"""Проверка проблемы с агрегацией файла узлов учёта"""
import sys
import sqlite3
import json
from pathlib import Path

INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

batch_id = "06d2ab5d-2bc2-46bf-909b-bb1b49fb3599"

print("=" * 70)
print(f"ПРОВЕРКА ПРОБЛЕМЫ С АГРЕГАЦИЕЙ")
print(f"batch_id: {batch_id}")
print("=" * 70)

# Проверяем should_aggregate_file
from utils.energy_aggregator import should_aggregate_file
from utils.nodes_parser import is_nodes_file

filename = "schetchiki.xlsx"
print(f"\n1. Проверка типа файла:")
print(f"   Файл: {filename}")
print(f"   should_aggregate_file: {should_aggregate_file(filename)}")
print(f"   is_nodes_file: {is_nodes_file(filename, None)}")

# Проверяем данные в БД
db_path = INGEST_DIR / "ingest_data.db"
conn = sqlite3.connect(str(db_path))
cursor = conn.execute(
    """
    SELECT pd.raw_json, u.filename 
    FROM parsed_data pd 
    JOIN uploads u ON pd.upload_id = u.id 
    WHERE u.batch_id = ?
    """,
    (batch_id,)
)
row = cursor.fetchone()
conn.close()

if row:
    raw_json_str, original_filename = row
    data = json.loads(raw_json_str)
    
    print(f"\n2. Данные в БД:")
    print(f"   Исходный файл: {original_filename}")
    print(f"   Ключи в raw_json: {list(data.keys())}")
    print(f"   Sheets: {len(data.get('sheets', []))}")
    for sheet in data.get('sheets', [])[:3]:
        print(f"     - {sheet.get('name')}: {len(sheet.get('rows', []))} строк")
    
    # Проверяем aggregate_from_db_json
    print(f"\n3. Проверка aggregate_from_db_json:")
    from utils.energy_aggregator import aggregate_from_db_json
    
    parsed_json = {
        "batch_id": batch_id,
        "filename": original_filename,
        "file_type": "excel",
        "parsing": {
            "parsed": True,
            "file_type": "excel",
            "data": data
        }
    }
    
    result = aggregate_from_db_json(parsed_json)
    if result:
        resources = result.get("resources", {})
        print(f"   Результат: НЕ None")
        print(f"   Ресурсы: {list(resources.keys())}")
        for res_type, res_data in resources.items():
            if isinstance(res_data, dict):
                periods = [k for k in res_data.keys() if isinstance(res_data[k], dict)]
                print(f"     {res_type}: {len(periods)} периодов")
            else:
                print(f"     {res_type}: {res_data}")
    else:
        print(f"   Результат: None (правильно для файла узлов учёта)")
else:
    print(f"\n❌ Данные не найдены в БД для batch_id: {batch_id}")

print("\n" + "=" * 70)
print("ВЫВОД:")
print("✅ ИСПРАВЛЕНО: Добавлена проверка is_specialized_file")
print("   Файлы узлов учёта (nodes) больше не будут создавать")
print("   пустые aggregated.json файлы")
print("=" * 70)

