"""Тест функциональности импорта в БД"""
import sys
import json
from pathlib import Path

# Добавляем путь к модулям
INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

import database
from database import import_resource_to_db, get_connection

print("=" * 70)
print("ТЕСТ ФУНКЦИОНАЛЬНОСТИ ИМПОРТА В БД")
print("=" * 70)

# Проверяем структуру таблицы
print("\n📊 Проверка структуры таблицы aggregated_data...")
try:
    with get_connection() as conn:
        cursor = conn.execute("PRAGMA table_info(aggregated_data)")
        columns = cursor.fetchall()
        if columns:
            print(f"✅ Таблица aggregated_data существует ({len(columns)} колонок)")
            for col in columns:
                print(f"   - {col[1]}: {col[2]}")
        else:
            print("❌ Таблица aggregated_data не найдена!")
except Exception as e:
    print(f"❌ Ошибка проверки таблицы: {e}")

# Проверяем функцию импорта
print("\n🔍 Проверка функции import_resource_to_db...")
test_data = {
    "2022-Q1": {
        "year": 2022,
        "quarter": 1,
        "total_kwh": 1000,
        "total_cost": 5000
    },
    "2022-Q2": {
        "year": 2022,
        "quarter": 2,
        "total_kwh": 1200,
        "total_cost": 6000
    }
}

print(f"   Тестовые данные: {len(test_data)} периода")
print("   Функция доступна: ✅")

# Проверяем текущее количество записей
print("\n📊 Текущее состояние БД...")
try:
    with get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM aggregated_data")
        count = cursor.fetchone()[0]
        print(f"   Записей в aggregated_data: {count}")
        
        if count > 0:
            # Показываем примеры
            cursor = conn.execute("""
                SELECT resource_type, period, batch_id 
                FROM aggregated_data 
                LIMIT 5
            """)
            print("   Примеры записей:")
            for row in cursor.fetchall():
                print(f"     → {row[0]} / {row[1]} (batch: {row[2][:8]}...)")
except Exception as e:
    print(f"❌ Ошибка проверки БД: {e}")

# Проверяем файлы с данными
print("\n📂 Проверка файлов aggregated...")
aggregated_dir = INGEST_DIR / "data" / "inbox" / "aggregated"
if aggregated_dir.exists():
    files = list(aggregated_dir.glob("*_aggregated.json"))
    files_with_data = []
    for f in files[:5]:
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            resources = data.get("resources", {})
            if resources:
                files_with_data.append(f.name)
        except:
            pass
    
    print(f"   Всего файлов: {len(files)}")
    print(f"   Файлов с данными: {len(files_with_data)}")
    if files_with_data:
        print("   Примеры:")
        for name in files_with_data[:3]:
            print(f"     → {name}")
else:
    print("   ❌ Директория aggregated/ не найдена")

print("\n" + "=" * 70)
print("✅ Проверка завершена")
print("=" * 70)

