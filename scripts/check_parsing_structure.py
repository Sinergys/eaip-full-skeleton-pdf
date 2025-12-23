import sqlite3
import json

conn = sqlite3.connect('C:/eaip/eaip_full_skeleton/services/ingest/ingest_data.db')

cursor = conn.execute('SELECT batch_id FROM uploads ORDER BY created_at DESC LIMIT 1')
batch_id = cursor.fetchone()[0]

cursor2 = conn.execute('SELECT id FROM uploads WHERE batch_id=?', (batch_id,))
upload_id = cursor2.fetchone()[0]

cursor3 = conn.execute('SELECT raw_json FROM parsed_data WHERE upload_id=?', (upload_id,))
raw = cursor3.fetchone()[0]

parsed = json.loads(raw)
parsing = parsed.get('parsing', {})

print("=== Структура parsing ===")
print(f"Keys: {list(parsing.keys())}")
print(f"\nparsing.parsed: {parsing.get('parsed')}")
print(f"parsing.file_type: {parsing.get('file_type')}")

data = parsing.get('data', {})
print("\n=== Структура parsing.data ===")
print(f"Keys: {list(data.keys())}")

if 'sheets' in data:
    print(f"\nКоличество sheets: {len(data['sheets'])}")
    if data['sheets']:
        first_sheet = data['sheets'][0]
        print(f"Первый лист: {first_sheet.get('name')}")
        print(f"Строк: {len(first_sheet.get('rows', []))}")
else:
    print("\n⚠️ 'sheets' нет в data")
    print(f"Все ключи data: {list(data.keys())}")

