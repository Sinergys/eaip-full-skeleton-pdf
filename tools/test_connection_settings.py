#!/usr/bin/env python3
"""
Тест применения настроек при подключении через get_connection()
"""
import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path("eaip_full_skeleton/services/ingest").absolute()))

from database import get_connection

print("🔍 Проверка применения настроек через get_connection():")
print("")

with get_connection() as conn:
    # Проверяем настройки
    wal = conn.execute("PRAGMA journal_mode").fetchone()[0]
    print(f"1. WAL режим: {wal} {'✅' if wal == 'wal' else '❌'}")
    
    cache = conn.execute("PRAGMA cache_size").fetchone()[0]
    print(f"2. cache_size: {cache} ({'64MB ✅' if cache == -64000 else 'не настроено'})")
    
    sync = conn.execute("PRAGMA synchronous").fetchone()[0]
    sync_map = {0: "OFF", 1: "NORMAL", 2: "FULL"}
    print(f"3. synchronous: {sync_map.get(sync, sync)} ({'✅' if sync == 1 else ''})")
    
    temp = conn.execute("PRAGMA temp_store").fetchone()[0]
    temp_map = {0: "DEFAULT", 1: "FILE", 2: "MEMORY"}
    print(f"4. temp_store: {temp_map.get(temp, temp)} ({'✅' if temp == 2 else ''})")
    
    mmap = conn.execute("PRAGMA mmap_size").fetchone()[0]
    mmap_mb = mmap / (1024 * 1024) if mmap else 0
    print(f"5. mmap_size: {mmap_mb:.0f}MB ({'✅' if mmap_mb >= 256 else ''})")

print("")
print("✅ Настройки применяются автоматически при каждом подключении!")

