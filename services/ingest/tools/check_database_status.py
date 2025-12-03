"""Проверка статуса базы данных - что уже загружено"""
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime

INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

DB_PATH = INGEST_DIR / "ingest_data.db"

print("=" * 70)
print("ПРОВЕРКА СТАТУСА БАЗЫ ДАННЫХ")
print(f"База данных: {DB_PATH}")
print(f"Существует: {DB_PATH.exists()}")
print("=" * 70)

if not DB_PATH.exists():
    print("\n❌ База данных не найдена!")
    sys.exit(1)

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row

# Получаем список всех таблиц
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()

print(f"\n📊 НАЙДЕНО ТАБЛИЦ: {len(tables)}")
print("-" * 70)

for table_row in tables:
    table_name = table_row[0]
    count = conn.execute(f"SELECT COUNT(*) as cnt FROM {table_name}").fetchone()[0]
    print(f"  {table_name}: {count} записей")

print("\n" + "=" * 70)
print("ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ПО ТАБЛИЦАМ")
print("=" * 70)

# 1. Предприятия
print("\n1. ПРЕДПРИЯТИЯ (enterprises):")
print("-" * 70)
enterprises = conn.execute(
    "SELECT id, name, created_at FROM enterprises ORDER BY name"
).fetchall()
if enterprises:
    for ent in enterprises:
        print(f"   ID: {ent['id']}, Название: {ent['name']}, Создано: {ent['created_at']}")
else:
    print("   Нет записей")

# 2. Загрузки
print("\n2. ЗАГРУЗКИ (uploads):")
print("-" * 70)
uploads = conn.execute(
    """
    SELECT u.id, u.batch_id, u.enterprise_id, u.filename, u.file_type, 
           u.status, u.created_at, e.name as enterprise_name
    FROM uploads u
    LEFT JOIN enterprises e ON u.enterprise_id = e.id
    ORDER BY u.created_at DESC
    LIMIT 10
    """
).fetchall()
if uploads:
    print(f"   Всего загрузок: {conn.execute('SELECT COUNT(*) FROM uploads').fetchone()[0]}")
    print(f"   Последние 10 загрузок:")
    for up in uploads:
        print(f"   - Batch: {up['batch_id'][:8]}..., Файл: {up['filename']}, "
              f"Тип: {up['file_type']}, Статус: {up['status']}, "
              f"Предприятие: {up['enterprise_name']}")
else:
    print("   Нет записей")

# 3. Распарсенные данные
print("\n3. РАСПАРСЕННЫЕ ДАННЫЕ (parsed_data):")
print("-" * 70)
parsed_count = conn.execute("SELECT COUNT(*) FROM parsed_data").fetchone()[0]
print(f"   Всего записей: {parsed_count}")

# 4. Агрегированные данные
print("\n4. АГРЕГИРОВАННЫЕ ДАННЫЕ (aggregated_data):")
print("-" * 70)
agg_data = conn.execute(
    """
    SELECT resource_type, period, COUNT(*) as cnt,
           MIN(created_at) as first_created, MAX(created_at) as last_created
    FROM aggregated_data
    GROUP BY resource_type, period
    ORDER BY resource_type, period
    """
).fetchall()

if agg_data:
    total = conn.execute("SELECT COUNT(*) FROM aggregated_data").fetchone()[0]
    print(f"   Всего записей: {total}")
    print(f"   По типам ресурсов:")
    
    # Группируем по типам ресурсов
    by_resource = {}
    for row in agg_data:
        resource = row['resource_type']
        if resource not in by_resource:
            by_resource[resource] = []
        by_resource[resource].append(row)
    
    for resource, periods in by_resource.items():
        total_periods = len(periods)
        total_records = sum(p['cnt'] for p in periods)
        print(f"     {resource}: {total_records} записей, {total_periods} периодов")
        for p in periods[:3]:  # Показываем первые 3 периода
            print(f"       - {p['period']}: {p['cnt']} записей")
        if len(periods) > 3:
            print(f"       ... и еще {len(periods) - 3} периодов")
else:
    print("   Нет записей")

# 5. Потребление по узлам учёта
print("\n5. ПОТРЕБЛЕНИЕ ПО УЗЛАМ УЧЁТА (node_consumption):")
print("-" * 70)
nodes_data = conn.execute(
    """
    SELECT node_name, period, COUNT(*) as cnt,
           SUM(active_energy_kwh) as total_active,
           SUM(reactive_energy_kvarh) as total_reactive
    FROM node_consumption
    GROUP BY node_name, period
    ORDER BY node_name, period
    LIMIT 20
    """
).fetchall()

if nodes_data:
    total = conn.execute("SELECT COUNT(*) FROM node_consumption").fetchone()[0]
    print(f"   Всего записей: {total}")
    print(f"   Примеры (первые 20):")
    for node in nodes_data:
        node_name = node['node_name'] or 'N/A'
        period = node['period'] or 'N/A'
        total_active = node['total_active'] or 0.0
        total_reactive = node['total_reactive'] or 0.0
        print(f"     - Узел: {node_name}, Период: {period}, "
              f"Активная: {total_active:.2f} кВт·ч, "
              f"Реактивная: {total_reactive:.2f} кВАр·ч")
else:
    print("   Нет записей")

# 6. Статистика по статусам загрузок
print("\n6. СТАТИСТИКА ПО СТАТУСАМ ЗАГРУЗОК:")
print("-" * 70)
status_stats = conn.execute(
    """
    SELECT status, COUNT(*) as cnt
    FROM uploads
    GROUP BY status
    ORDER BY cnt DESC
    """
).fetchall()
for stat in status_stats:
    print(f"   {stat['status']}: {stat['cnt']} файлов")

# 7. Статистика по типам файлов
print("\n7. СТАТИСТИКА ПО ТИПАМ ФАЙЛОВ:")
print("-" * 70)
file_type_stats = conn.execute(
    """
    SELECT file_type, COUNT(*) as cnt
    FROM uploads
    WHERE file_type IS NOT NULL
    GROUP BY file_type
    ORDER BY cnt DESC
    """
).fetchall()
for ft in file_type_stats:
    print(f"   {ft['file_type']}: {ft['cnt']} файлов")

# 8. Проверка связности данных
print("\n8. ПРОВЕРКА СВЯЗНОСТИ ДАННЫХ:")
print("-" * 70)

# Загрузки без распарсенных данных
uploads_without_parsed = conn.execute(
    """
    SELECT COUNT(*) as cnt
    FROM uploads u
    LEFT JOIN parsed_data pd ON u.id = pd.upload_id
    WHERE pd.upload_id IS NULL
    """
).fetchone()[0]
print(f"   Загрузок без распарсенных данных: {uploads_without_parsed}")

# Загрузки без агрегированных данных
uploads_without_agg = conn.execute(
    """
    SELECT COUNT(DISTINCT u.batch_id) as cnt
    FROM uploads u
    LEFT JOIN aggregated_data ad ON u.batch_id = ad.batch_id
    WHERE ad.batch_id IS NULL AND u.status = 'completed'
    """
).fetchone()[0]
print(f"   Завершенных загрузок без агрегированных данных: {uploads_without_agg}")

# Узлы учёта без данных потребления
nodes_without_consumption = conn.execute(
    """
    SELECT COUNT(DISTINCT u.batch_id) as cnt
    FROM uploads u
    WHERE u.filename LIKE '%schetch%' OR u.filename LIKE '%узл%'
    AND NOT EXISTS (
        SELECT 1 FROM node_consumption nc WHERE nc.batch_id = u.batch_id
    )
    """
).fetchone()[0]
print(f"   Файлов узлов учёта без данных потребления: {nodes_without_consumption}")

conn.close()

print("\n" + "=" * 70)
print("ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 70)

