"""Проверка типа предприятия и связанных данных для Navoiy IES"""
import sys
import sqlite3
import json
from pathlib import Path

INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

DB_PATH = INGEST_DIR / "ingest_data.db"

print("=" * 70)
print("ПРОВЕРКА ТИПА ПРЕДПРИЯТИЯ И СВЯЗАННЫХ ДАННЫХ")
print("=" * 70)

if not DB_PATH.exists():
    print("\n❌ База данных не найдена!")
    sys.exit(1)

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row

# 1. Находим предприятие Navoiy IES
print("\n1. ПРЕДПРИЯТИЕ NAVOIY IES:")
print("-" * 70)
enterprise = conn.execute(
    "SELECT * FROM enterprises WHERE name LIKE '%Navoi%'"
).fetchone()

if not enterprise:
    print("   ❌ Предприятие Navoiy IES не найдено!")
    conn.close()
    sys.exit(1)

print(f"   ID: {enterprise['id']}")
print(f"   Название: {enterprise['name']}")
print(f"   Создано: {enterprise['created_at']}")

# 2. Проверяем структуру таблицы enterprises
print("\n2. СТРУКТУРА ТАБЛИЦЫ enterprises:")
print("-" * 70)
table_info = conn.execute("PRAGMA table_info(enterprises)").fetchall()
for col in table_info:
    print(f"   {col['name']}: {col['type']}")

# 3. Проверяем, есть ли поле industry или enterprise_type
print("\n3. ПРОВЕРКА ПОЛЕЙ ДЛЯ ТИПА ПРЕДПРИЯТИЯ:")
print("-" * 70)
has_industry = any(col['name'] in ('industry', 'enterprise_type', 'type') for col in table_info)
if not has_industry:
    print("\n   ⚠️ Поле для типа предприятия (industry/enterprise_type) НЕ НАЙДЕНО!")
    print("   Текущая структура не поддерживает хранение типа предприятия")

# 4. Анализируем загруженные файлы для определения типа предприятия
print("\n4. АНАЛИЗ ЗАГРУЖЕННЫХ ФАЙЛОВ:")
print("-" * 70)
uploads = conn.execute(
    """
    SELECT filename, file_type, status, created_at
    FROM uploads
    WHERE enterprise_id = ?
    ORDER BY created_at DESC
    """,
    (enterprise['id'],)
).fetchall()

print(f"   Всего загрузок: {len(uploads)}")
print(f"   Примеры файлов (первые 10):")
for up in uploads[:10]:
    print(f"     - {up['filename']} ({up['file_type']})")

# Анализируем названия файлов для определения типа предприятия
keywords_industry = {
    'энергетика': ['энерг', 'электро', 'тэс', 'гэс', 'энерго'],
    'химия': ['хими', 'азот', 'навоийазот'],
    'металлургия': ['металл', 'сталь', 'железо'],
    'нефтепереработка': ['нефть', 'нефте', 'нефтепереработ'],
    'машиностроение': ['машин', 'оборудование'],
}

print("\n   Анализ ключевых слов в названиях файлов:")
found_keywords = {}
for up in uploads:
    filename_lower = up['filename'].lower()
    for industry, keywords in keywords_industry.items():
        for keyword in keywords:
            if keyword in filename_lower:
                if industry not in found_keywords:
                    found_keywords[industry] = 0
                found_keywords[industry] += 1
                break

if found_keywords:
    print("   Найдены упоминания отраслей:")
    for industry, count in sorted(found_keywords.items(), key=lambda x: x[1], reverse=True):
        print(f"     {industry}: {count} упоминаний")
else:
    print("   Не найдено явных указаний на отрасль")

# 5. Проверяем типы потребляемых ресурсов
print("\n5. ТИПЫ ПОТРЕБЛЯЕМЫХ РЕСУРСОВ:")
print("-" * 70)
resources = conn.execute(
    """
    SELECT DISTINCT resource_type, COUNT(*) as cnt
    FROM aggregated_data
    WHERE enterprise_id = ?
    GROUP BY resource_type
    ORDER BY cnt DESC
    """,
    (enterprise['id'],)
).fetchall()

if resources:
    print(f"   Найдено типов ресурсов: {len(resources)}")
    for res in resources:
        print(f"     {res['resource_type']}: {res['cnt']} записей")
else:
    print("   Нет агрегированных данных по ресурсам")

# 6. Анализируем данные для определения типа продукции
print("\n6. ПОПЫТКА ОПРЕДЕЛЕНИЯ ТИПА ПРОДУКЦИИ:")
print("-" * 70)
# Проверяем, есть ли данные о производстве
production_data = conn.execute(
    """
    SELECT resource_type, period, data_json
    FROM aggregated_data
    WHERE enterprise_id = ? AND resource_type = 'production'
    LIMIT 5
    """,
    (enterprise['id'],)
).fetchall()

if production_data:
    print("   Найдены данные о производстве:")
    for prod in production_data:
        data = json.loads(prod['data_json']) if prod['data_json'] else {}
        print(f"     Период: {prod['period']}")
        if isinstance(data, dict):
            months = data.get('months', [])
            for month in months[:3]:
                values = month.get('values', {})
                if values:
                    print(f"       {month.get('month', 'N/A')}: {list(values.keys())}")
else:
    # Анализируем названия файлов для определения продукции
    production_keywords = ['производство', 'продукция', 'выпуск', 'изготовление']
    production_found = False
    for up in uploads:
        filename_lower = up['filename'].lower()
        if any(kw in filename_lower for kw in production_keywords):
            production_found = True
            print(f"   Найден файл, возможно связанный с производством: {up['filename']}")
            break
    
    if not production_found:
        print("   Возможные типы продукции:")
        print("     - Электроэнергия (для энергетических предприятий)")
        print("     - Химическая продукция (для химических предприятий)")
        print("   Не найдено явных указаний на тип продукции")

# 7. Проверяем, есть ли в коде логика определения типа предприятия
print("\n7. ПРОВЕРКА КОДА НА ЛОГИКУ ОПРЕДЕЛЕНИЯ ТИПА ПРЕДПРИЯТИЯ:")
print("-" * 70)
code_files = [
    INGEST_DIR / "database.py",
    INGEST_DIR / "main.py",
    INGEST_DIR / "utils" / "resource_classifier.py",
]

found_logic = False
for code_file in code_files:
    if code_file.exists():
        content = code_file.read_text(encoding='utf-8')
        if any(keyword in content.lower() for keyword in ['industry', 'enterprise_type', 'product_type', 'отрасль']):
            print(f"   ✅ Найдены упоминания в {code_file.name}")
            found_logic = True

if not found_logic:
    print("     ❌ Логика определения типа предприятия НЕ НАЙДЕНА в коде")

conn.close()

print("\n" + "=" * 70)
print("ИТОГОВЫЙ ОТЧЕТ:")
print("=" * 70)
print(f"1. Предприятие: {enterprise['name']} (ID: {enterprise['id']})")
print(f"2. Загрузок: {len(uploads)}")
if resources:
    print(f"   Типы: {', '.join([r['resource_type'] for r in resources])}")
print(f"3. Тип предприятия: {'Не определен' if not has_industry else 'Определен'}")
print(f"4. Тип продукции: {'Не определен' if not production_data else 'Частично определен по файлам'}")

print("\n" + "=" * 70)
print("РЕКОМЕНДАЦИИ:")
print("=" * 70)
print("1. Добавить в таблицу enterprises поля:")
print("   - industry (отрасль)")
print("   - enterprise_type (тип предприятия)")
print("   - product_type (тип продукции)")
print("2. Реализовать логику автоматического определения типа предприятия")
print("   на основе анализа загруженных файлов и данных")
print("3. Создать справочник отраслей и типов продукции")
print("=" * 70)
