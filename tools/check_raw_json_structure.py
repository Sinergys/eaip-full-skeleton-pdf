"""Проверка структуры raw_json в БД для файлов 'Реализация'."""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row

cursor = conn.execute(
    """
    SELECT u.batch_id, u.filename, pd.raw_json
    FROM uploads u
    JOIN parsed_data pd ON u.id = pd.upload_id
    WHERE u.filename LIKE '%Реализация 2022%'
    ORDER BY u.created_at DESC
    LIMIT 1
    """
)

row = cursor.fetchone()
conn.close()

if row:
    print(f"Файл: {row['filename']}")
    print(f"batch_id: {row['batch_id']}")
    print("\n" + "="*80)
    print("СТРУКТУРА raw_json:")
    print("="*80)
    
    try:
        raw_json = json.loads(row['raw_json'])
        
        print(f"\nКлючи верхнего уровня: {list(raw_json.keys())}")
        
        # Проверяем различные возможные структуры
        if 'data' in raw_json:
            print(f"\n✅ Найден ключ 'data'")
            data = raw_json['data']
            print(f"   Ключи в 'data': {list(data.keys())}")
            
            if 'sheets' in data:
                print(f"   ✅ Найдены 'sheets': {len(data['sheets'])} листов")
                for i, sheet in enumerate(data['sheets'][:3], 1):
                    print(f"      Лист {i}: {sheet.get('name', 'Без имени')}, строк: {len(sheet.get('rows', []))}")
            else:
                print(f"   ❌ 'sheets' не найдены в 'data'")
        
        if 'parsing' in raw_json:
            print(f"\n✅ Найден ключ 'parsing'")
            parsing = raw_json['parsing']
            print(f"   Ключи в 'parsing': {list(parsing.keys())}")
            
            if 'data' in parsing:
                print(f"   ✅ Найден 'data' в 'parsing'")
                data = parsing['data']
                print(f"      Ключи в 'parsing.data': {list(data.keys())}")
                
                if 'sheets' in data:
                    print(f"      ✅ Найдены 'sheets': {len(data['sheets'])} листов")
                    for i, sheet in enumerate(data['sheets'][:3], 1):
                        print(f"         Лист {i}: {sheet.get('name', 'Без имени')}, строк: {len(sheet.get('rows', []))}")
        
        # Показываем полную структуру (первые уровни)
        print(f"\n" + "="*80)
        print("ПОЛНАЯ СТРУКТУРА (первые 2 уровня):")
        print("="*80)
        print(json.dumps({k: (type(v).__name__ if not isinstance(v, (dict, list)) else f"{type(v).__name__}({len(v) if isinstance(v, (dict, list)) else 'N/A'})") for k, v in raw_json.items()}, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        print(f"Первые 500 символов raw_json:")
        print(row['raw_json'][:500])
else:
    print("❌ Файл не найден")

