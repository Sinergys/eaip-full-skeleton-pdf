"""Отладка связи между таблицами."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row

# Проверяем batch_id в node_consumption
print("=" * 80)
print("BATCH_ID В NODE_CONSUMPTION:")
print("=" * 80)
cursor = conn.execute("SELECT DISTINCT batch_id FROM node_consumption LIMIT 10")
batch_ids = cursor.fetchall()
for b in batch_ids:
    print(f"  {b['batch_id']}")

# Проверяем batch_id в uploads для файлов "Реализация"
print("\n" + "=" * 80)
print("BATCH_ID В UPLOADS (ФАЙЛЫ 'РЕАЛИЗАЦИЯ'):")
print("=" * 80)
cursor2 = conn.execute(
    "SELECT batch_id, filename FROM uploads WHERE filename LIKE '%Реализация%' OR filename LIKE '%реализация%' LIMIT 10"
)
uploads = cursor2.fetchall()
for u in uploads:
    print(f"  {u['batch_id']}: {u['filename']}")

# Проверяем совпадения
print("\n" + "=" * 80)
print("ПРОВЕРКА СОВПАДЕНИЙ:")
print("=" * 80)
nc_batch_ids = {b['batch_id'] for b in batch_ids}
upload_batch_ids = {u['batch_id'] for u in uploads}
matches = nc_batch_ids & upload_batch_ids
print(f"  Совпадающих batch_id: {len(matches)}")
if matches:
    for match in list(matches)[:5]:
        print(f"    {match}")

# Прямое обновление всех записей из этих batch_id
if matches:
    print("\n" + "=" * 80)
    print("ОБНОВЛЕНИЕ ЗАПИСЕЙ:")
    print("=" * 80)
    placeholders = ','.join('?' * len(matches))
    updated = conn.execute(
        f"UPDATE node_consumption SET data_type = 'realization' WHERE batch_id IN ({placeholders})",
        list(matches)
    )
    conn.commit()
    print(f"  ✅ Обновлено {updated.rowcount} записей")

conn.close()

