"""Проверка существования таблицы node_consumption."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='node_consumption'"
)
table = cursor.fetchone()

if table:
    print(f"✅ Таблица 'node_consumption' существует")
    
    # Проверяем структуру
    cursor2 = conn.execute("PRAGMA table_info(node_consumption)")
    columns = cursor2.fetchall()
    print(f"\n📋 Структура таблицы:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # Проверяем количество записей
    cursor3 = conn.execute("SELECT COUNT(*) as count FROM node_consumption")
    count = cursor3.fetchone()[0]
    print(f"\n📊 Всего записей: {count}")
    
    # Проверяем по типам
    cursor4 = conn.execute("SELECT data_type, COUNT(*) as count FROM node_consumption GROUP BY data_type")
    types = cursor4.fetchall()
    print(f"\n📊 По типам данных:")
    for t in types:
        print(f"   - {t[0] or 'NULL'}: {t[1]} записей")
else:
    print(f"❌ Таблица 'node_consumption' не существует")

conn.close()

