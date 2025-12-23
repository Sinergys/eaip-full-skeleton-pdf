"""Проверка данных узлов учёта в БД"""
import sys
import sqlite3
import json
from pathlib import Path

INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

print("=" * 70)
print("ПРОВЕРКА ДАННЫХ УЗЛОВ УЧЁТА В БД")
print("=" * 70)

# Проверяем таблицу node_consumption
db_path = INGEST_DIR / "ingest_data.db"
conn = sqlite3.connect(str(db_path))

# Проверяем количество записей
cursor = conn.execute("SELECT COUNT(*) as cnt FROM node_consumption")
row = cursor.fetchone()
total_records = row[0] if row else 0
print(f"\n1. Записей в таблице node_consumption: {total_records}")

if total_records > 0:
    # Показываем примеры
    cursor = conn.execute(
        "SELECT node_name, period, active_energy_kwh, reactive_energy_kvarh, batch_id "
        "FROM node_consumption LIMIT 10"
    )
    rows = cursor.fetchall()
    print(f"\n2. Примеры записей:")
    for r in rows:
        print(f"   - Узел: {r[0]}, Период: {r[1]}, Активная: {r[2]}, Реактивная: {r[3]}, Batch: {r[4]}")

# Проверяем файлы nodes.json
aggregated_dir = INGEST_DIR / "data" / "inbox" / "aggregated"
nodes_files = list(aggregated_dir.glob("*nodes.json"))
print(f"\n3. Файлов nodes.json найдено: {len(nodes_files)}")

if nodes_files:
    f = nodes_files[0]
    data = json.loads(f.read_text(encoding="utf-8"))
    print(f"\n4. Структура файла {f.name}:")
    print(f"   Ключи: {list(data.keys())}")
    print(f"   Количество узлов: {len(data.get('nodes', []))}")
    if data.get('nodes'):
        node = data['nodes'][0]
        print(f"   Пример узла:")
        print(f"     - name: {node.get('name')}")
        print(f"     - active_energy_p: {node.get('active_energy_p')}")
        print(f"     - reactive_energy_q: {node.get('reactive_energy_q')}")

conn.close()

print("\n" + "=" * 70)
print("ВЫВОД:")
if total_records == 0:
    print("⚠️ В БД нет записей узлов учёта")
    print("   Это может быть потому что:")
    print("   1. Файлы узлов учёта не были обработаны после исправления")
    print("   2. Или период установлен как 'unknown' и записи не создаются")
    print("   3. Или данные узлов не содержат периодов (это нормально)")
else:
    print(f"✅ В БД есть {total_records} записей узлов учёта")
print("=" * 70)

