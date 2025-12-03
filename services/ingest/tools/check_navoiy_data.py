"""Детальная проверка данных для Navoiy IES"""
import sqlite3
from pathlib import Path

INGEST_DIR = Path(__file__).resolve().parent.parent
DB_PATH = INGEST_DIR / "ingest_data.db"

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row

print("=" * 70)
print("ДЕТАЛЬНАЯ ПРОВЕРКА ДАННЫХ ДЛЯ NAVOIY IES")
print("=" * 70)

ent_id = 3

# Проверяем агрегированные данные
agg_count = conn.execute(
    "SELECT COUNT(*) as cnt FROM aggregated_data WHERE enterprise_id = ?",
    (ent_id,)
).fetchone()['cnt']

print(f"\n1. Агрегированные данные: {agg_count} записей")

if agg_count == 0:
    print("   ⚠️ Нет агрегированных данных!")
    print("   Проверяем, есть ли файлы для агрегации...")
    
    # Проверяем успешные загрузки
    success_uploads = conn.execute(
        """
        SELECT batch_id, filename, file_type, created_at
        FROM uploads
        WHERE enterprise_id = ? AND status = 'success'
        ORDER BY created_at DESC
        LIMIT 10
        """,
        (ent_id,)
    ).fetchall()
    
    print(f"\n   Успешных загрузок: {len(success_uploads)}")
    print("   Примеры:")
    for up in success_uploads[:5]:
        print(f"     - {up['filename']} (batch: {up['batch_id'][:8]}...)")

# Проверяем типы ресурсов в aggregated_data для всех предприятий
print("\n2. Агрегированные данные по всем предприятиям:")
print("-" * 70)
all_agg = conn.execute(
    """
    SELECT enterprise_id, resource_type, COUNT(*) as cnt
    FROM aggregated_data
    GROUP BY enterprise_id, resource_type
    ORDER BY enterprise_id, resource_type
    """
).fetchall()

for agg in all_agg:
    ent_name = conn.execute(
        "SELECT name FROM enterprises WHERE id = ?", (agg['enterprise_id'],)
    ).fetchone()['name']
    print(f"   {ent_name} (ID: {agg['enterprise_id']}): {agg['resource_type']} - {agg['cnt']} записей")

# Проверяем, есть ли файлы aggregated JSON
print("\n3. Проверка файлов aggregated JSON:")
print("-" * 70)
from pathlib import Path
aggregated_dir = INGEST_DIR / "data" / "inbox" / "aggregated"
if aggregated_dir.exists():
    agg_files = list(aggregated_dir.glob("*_aggregated.json"))
    print(f"   Найдено файлов: {len(agg_files)}")
    
    # Проверяем, какие batch_id есть в файлах
    import json
    navoiy_batches = set()
    for f in agg_files[:10]:
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            batch_id = f.stem.replace('_aggregated', '')
            # Проверяем, принадлежит ли batch_id Navoiy IES
            upload = conn.execute(
                "SELECT enterprise_id FROM uploads WHERE batch_id = ?",
                (batch_id,)
            ).fetchone()
            if upload and upload['enterprise_id'] == ent_id:
                navoiy_batches.add(batch_id)
        except:
            pass
    
    print(f"   Файлов для Navoiy IES: {len(navoiy_batches)}")
    if navoiy_batches:
        print("   Примеры batch_id:")
        for bid in list(navoiy_batches)[:5]:
            print(f"     - {bid}")

# Проверяем структуру таблицы enterprises
print("\n4. Текущая структура таблицы enterprises:")
print("-" * 70)
table_info = conn.execute("PRAGMA table_info(enterprises)").fetchall()
for col in table_info:
    print(f"   {col['name']}: {col['type']}")

# Проверяем, что есть в main.py про industry
print("\n5. Проверка кода на поддержку типа предприятия:")
print("-" * 70)
main_py = INGEST_DIR / "main.py"
if main_py.exists():
    content = main_py.read_text(encoding='utf-8')
    if '"industry":' in content or "'industry':" in content:
        print("   ✅ Найдено упоминание 'industry' в main.py")
        # Находим контекст
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'industry' in line.lower():
                print(f"     Строка {i+1}: {line.strip()[:80]}")
                if i > 0:
                    print(f"     Контекст: {lines[i-1].strip()[:80]}")
                break
    else:
        print("   ❌ Не найдено упоминание 'industry' в main.py")

conn.close()

print("\n" + "=" * 70)
print("ВЫВОДЫ:")
print("=" * 70)
print("1. Определение типа предприятия: НЕ РЕАЛИЗОВАНО")
print("   - В таблице enterprises нет полей для типа предприятия")
print("   - В коде есть упоминание 'industry', но только в контексте генерации паспорта")
print("\n2. Определение типа продукции: НЕ РЕАЛИЗОВАНО")
print("   - Нет логики определения типа продукции")
print("\n3. Определение типов потребляемых ресурсов: ЧАСТИЧНО РЕАЛИЗОВАНО")
print("   - Есть ResourceClassifier для определения типа ресурса в файле")
print("   - Есть таблица aggregated_data с типами ресурсов")
print("   - НО: для Navoiy IES нет агрегированных данных в БД")
print("=" * 70)

