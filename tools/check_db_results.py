"""Проверка результатов в БД."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row

# Проверяем количество записей
cursor = conn.execute('SELECT COUNT(*) as count FROM node_consumption WHERE data_type = ?', ('realization',))
row = cursor.fetchone()
print(f"✅ Записей с типом 'realization': {row['count']}")

# Показываем примеры
cursor2 = conn.execute(
    'SELECT node_name, period, active_energy_kwh, reactive_energy_kvarh, cost_sum, data_type, batch_id FROM node_consumption WHERE data_type = ? LIMIT 10',
    ('realization',)
)
rows = cursor2.fetchall()

print(f"\n📋 Примеры записей (первые 10):")
for i, r in enumerate(rows, 1):
    print(f"   {i}. {r['node_name']}: активная={r['active_energy_kwh']}, период={r['period']}, batch_id={r['batch_id'][:16]}...")

# Статистика по файлам
cursor3 = conn.execute(
    """
    SELECT u.filename, COUNT(*) as count
    FROM node_consumption nc
    JOIN uploads u ON nc.batch_id = u.batch_id
    WHERE nc.data_type = 'realization'
    GROUP BY u.filename
    ORDER BY count DESC
    """
)
rows3 = cursor3.fetchall()

print(f"\n📊 Статистика по файлам:")
for r in rows3:
    print(f"   - {r['filename']}: {r['count']} записей")

conn.close()

