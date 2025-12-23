"""Проверка фактов в БД"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database

database.init_db()

with database.get_connection() as conn:
    cursor = conn.execute("SELECT COUNT(*) as cnt FROM uploads")
    total = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT COUNT(*) as cnt FROM uploads WHERE enterprise_id = (SELECT id FROM enterprises WHERE name = 'Navoiy IES')")
    navoi_count = cursor.fetchone()[0]
    
    cursor = conn.execute("SELECT filename, batch_id, created_at FROM uploads ORDER BY created_at DESC LIMIT 5")
    recent = cursor.fetchall()
    
    print("=" * 80)
    print("📊 ФАКТЫ ИЗ БД:")
    print("=" * 80)
    print(f"Всего файлов в БД: {total}")
    print(f"Файлов для Navoiy IES: {navoi_count}")
    print(f"\nПоследние 5 файлов:")
    for row in recent:
        print(f"  - {row[0]} (batch_id: {row[1]}, создан: {row[2]})")

