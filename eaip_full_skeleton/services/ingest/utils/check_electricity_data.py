"""
Диагностический скрипт для проверки структуры данных электроэнергии
"""

import sqlite3
import json
import sys
from pathlib import Path

# Добавляем путь к модулям
ingest_path = Path(__file__).resolve().parent.parent
if str(ingest_path) not in sys.path:
    sys.path.insert(0, str(ingest_path))


def check_electricity_file():
    """Проверяет структуру данных файла с электроэнергией"""
    conn = sqlite3.connect("ingest_data.db")
    cursor = conn.execute("""
        SELECT u.batch_id, u.filename, pd.raw_json 
        FROM uploads u
        LEFT JOIN parsed_data pd ON pd.upload_id = u.id
        WHERE u.filename LIKE '%electroenergiya%' 
        ORDER BY u.created_at DESC 
        LIMIT 1
    """)
    row = cursor.fetchone()

    if not row:
        print("❌ Файл с электроэнергией не найден")
        return

    batch_id, filename, raw_json_str = row
    print(f"📄 Файл: {filename}")
    print(f"📦 Batch ID: {batch_id[:8]}...")
    print()

    try:
        data = json.loads(raw_json_str)
    except Exception as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return

    parsing = data.get("parsing", {})
    data_section = parsing.get("data", {})
    sheets = data_section.get("sheets", [])

    print(f"📊 Количество листов: {len(sheets)}")
    print()

    # Ищем лист ЭЛЕКТР
    electr_sheet = None
    for sheet in sheets:
        sheet_name = sheet.get("name", "")
        rows = sheet.get("rows", [])
        print(f"  Лист: '{sheet_name}', строк: {len(rows)}")
        if sheet_name == "ЭЛЕКТР":
            electr_sheet = sheet

    if not electr_sheet:
        print("\n❌ Лист 'ЭЛЕКТР' не найден!")
        return

    print(f"\n✅ Лист 'ЭЛЕКТР' найден: {len(electr_sheet.get('rows', []))} строк")
    print("\n📋 Первые 10 строк:")
    rows = electr_sheet.get("rows", [])
    for idx, row in enumerate(rows[:10]):
        print(f"  Строка {idx}:")
        print(f"    Длина: {len(row)}")
        if row:
            print(f"    Первая ячейка: {repr(row[0])} (тип: {type(row[0]).__name__})")
            if len(row) > 1:
                print(
                    f"    Вторая ячейка: {repr(row[1])} (тип: {type(row[1]).__name__})"
                )
            if len(row) > 2:
                print(
                    f"    Третья ячейка: {repr(row[2])} (тип: {type(row[2]).__name__})"
                )
            print(f"    Все ячейки: {row[:10]}")
        else:
            print("    (пустая строка)")
        print()

    # Проверяем, есть ли годы
    print("🔍 Поиск годов в данных:")
    years_found = []
    for idx, row in enumerate(rows):
        if row and len(row) > 0:
            first_cell = row[0]
            if isinstance(first_cell, int) and first_cell in (2022, 2023, 2024):
                years_found.append((idx, first_cell))
            elif isinstance(first_cell, str) and first_cell.strip() in (
                "2022",
                "2023",
                "2024",
            ):
                years_found.append((idx, int(first_cell.strip())))

    if years_found:
        print(f"  ✅ Найдено {len(years_found)} упоминаний годов:")
        for row_idx, year in years_found[:5]:
            print(f"    Строка {row_idx}: {year}")
    else:
        print("  ❌ Годы не найдены!")

    # Проверяем, есть ли месяцы
    print("\n🔍 Поиск месяцев в данных:")
    months_found = []
    month_aliases = {
        "январь": 1,
        "февраль": 2,
        "март": 3,
        "апрель": 4,
        "май": 5,
        "июнь": 6,
        "июль": 7,
        "август": 8,
        "сентябрь": 9,
        "октябрь": 10,
        "ноябрь": 11,
        "декабрь": 12,
    }

    for idx, row in enumerate(rows):
        if row and len(row) > 0:
            first_cell = row[0]
            if isinstance(first_cell, str):
                month_lower = first_cell.lower().strip()
                if month_lower in month_aliases:
                    months_found.append((idx, first_cell, month_aliases[month_lower]))

    if months_found:
        print(f"  ✅ Найдено {len(months_found)} упоминаний месяцев:")
        for row_idx, month_name, month_num in months_found[:10]:
            print(f"    Строка {row_idx}: '{month_name}' (месяц {month_num})")
    else:
        print("  ❌ Месяцы не найдены!")

    conn.close()


if __name__ == "__main__":
    check_electricity_file()
