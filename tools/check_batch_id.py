"""Проверка batch_id в БД"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database

database.init_db()
batch_id = "64dfa04c-daea-4407-bb1b-2b61e3ba4403"

record = database.get_upload_by_batch(batch_id)
if record:
    print(f"✅ Найден: {record['filename']}")
else:
    print(f"❌ Не найден")
    # Ищем похожие
    with database.get_connection() as conn:
        conn.row_factory = database.sqlite3.Row
        cursor = conn.execute("SELECT batch_id, filename FROM uploads WHERE filename LIKE '%т-3%' OR filename LIKE '%jpg%' LIMIT 10")
        rows = cursor.fetchall()
        if rows:
            print("\nПохожие файлы:")
            for row in rows:
                print(f"  {row['batch_id']}: {row['filename']}")
        else:
            print("\nФайлы не найдены")

