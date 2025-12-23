#!/usr/bin/env python3
"""
Проверка оптимизации SQLite
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("eaip_full_skeleton/services/ingest/ingest_data.db")

conn = sqlite3.connect(str(DB_PATH))

print("📊 Проверка оптимизации SQLite:")
print("")

# 1. WAL режим
wal = conn.execute("PRAGMA journal_mode").fetchone()[0]
print(f"1. WAL режим: {wal} {'✅' if wal == 'wal' else '❌'}")

# 2. Настройки производительности
print("")
print("2. Настройки производительности:")
cache = conn.execute("PRAGMA cache_size").fetchone()[0]
print(f"   cache_size: {cache} ({'64MB ✅' if cache == -64000 else 'не настроено'})")

sync = conn.execute("PRAGMA synchronous").fetchone()[0]
sync_map = {0: "OFF", 1: "NORMAL", 2: "FULL"}
print(f"   synchronous: {sync_map.get(sync, sync)} ({'✅' if sync == 1 else ''})")

temp = conn.execute("PRAGMA temp_store").fetchone()[0]
temp_map = {0: "DEFAULT", 1: "FILE", 2: "MEMORY"}
print(f"   temp_store: {temp_map.get(temp, temp)} ({'✅' if temp == 2 else ''})")

mmap = conn.execute("PRAGMA mmap_size").fetchone()[0]
mmap_mb = mmap / (1024 * 1024) if mmap else 0
print(f"   mmap_size: {mmap_mb:.0f}MB ({'✅' if mmap_mb >= 256 else ''})")

# 3. Индексы
print("")
print("3. Индексы:")
indexes = conn.execute(
    "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
).fetchone()[0]
print(f"   Создано индексов: {indexes} {'✅' if indexes >= 29 else '⚠️'}")

# Список всех индексов
if indexes > 0:
    index_list = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name"
    ).fetchall()
    print(f"   Индексы: {', '.join([idx[0] for idx in index_list[:5]])}...")

conn.close()

print("")
print("✅ Оптимизация SQLite завершена!")

