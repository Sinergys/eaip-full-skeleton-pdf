import sqlite3
import json

conn = sqlite3.connect('C:/eaip/eaip_full_skeleton/services/ingest/ingest_data.db')

# Получаем последнюю загрузку
cursor = conn.execute('SELECT batch_id, filename FROM uploads ORDER BY created_at DESC LIMIT 1')
row = cursor.fetchone()

if not row:
    print("❌ Нет данных в БД")
    exit()

batch_id, filename = row
print(f"batch_id: {batch_id[:16]}...")
print(f"filename: {filename}")

# Получаем upload_id
cursor2 = conn.execute('SELECT id FROM uploads WHERE batch_id=?', (batch_id,))
upload_id = cursor2.fetchone()[0]
print(f"upload_id: {upload_id}")

# Получаем raw_json
cursor3 = conn.execute('SELECT raw_json FROM parsed_data WHERE upload_id=?', (upload_id,))
raw = cursor3.fetchone()

if not raw:
    print("❌ Нет parsed_data для этого файла")
    exit()

parsed = json.loads(raw[0])
print("\n✅ Структура данных:")
print(f"  Ключи верхнего уровня: {list(parsed.keys())}")

if 'sheets' in parsed:
    print(f"  Количество листов: {len(parsed['sheets'])}")
    if parsed['sheets']:
        sheet = parsed['sheets'][0]
        print(f"  Первый лист: {sheet.get('name', 'Без имени')}")
        print(f"  Строк в первом листе: {len(sheet.get('rows', []))}")
else:
    print("  ⚠️ Нет ключа 'sheets'")
    print(f"  Все ключи: {parsed.keys()}")

