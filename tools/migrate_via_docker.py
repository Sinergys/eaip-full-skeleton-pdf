#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Альтернативный способ миграции через Docker exec (обход проблемы кодировки Windows)
Использование: python tools/migrate_via_docker.py
"""
import sqlite3
import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SQLITE_DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"


def export_sqlite_to_json():
    """Экспортирует данные из SQLite в JSON"""
    logger.info("Экспорт данных из SQLite...")
    
    if not SQLITE_DB_PATH.exists():
        raise FileNotFoundError(f"SQLite база не найдена: {SQLITE_DB_PATH}")
    
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    
    data = {}
    
    # Экспорт enterprises
    cursor = conn.execute("SELECT * FROM enterprises")
    data['enterprises'] = [dict(row) for row in cursor.fetchall()]
    logger.info(f"  Экспортировано {len(data['enterprises'])} предприятий")
    
    # Экспорт uploads
    cursor = conn.execute("SELECT * FROM uploads")
    data['uploads'] = [dict(row) for row in cursor.fetchall()]
    logger.info(f"  Экспортировано {len(data['uploads'])} загрузок")
    
    # Экспорт parsed_data
    cursor = conn.execute("SELECT * FROM parsed_data")
    data['parsed_data'] = [dict(row) for row in cursor.fetchall()]
    logger.info(f"  Экспортировано {len(data['parsed_data'])} записей parsed_data")
    
    conn.close()
    
    # Сохраняем в JSON
    json_path = Path(__file__).parent / "sqlite_export.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"✅ Данные экспортированы в {json_path}")
    return json_path


def main():
    """Главная функция"""
    logger.info("=" * 60)
    logger.info("Миграция через Docker (обход проблемы кодировки)")
    logger.info("=" * 60)
    
    try:
        # Шаг 1: Экспорт из SQLite
        json_path = export_sqlite_to_json()
        
        logger.info("")
        logger.info("✅ Экспорт завершен!")
        logger.info("")
        logger.info("Следующий шаг: Импорт в PostgreSQL через Docker")
        logger.info("Или используйте скрипт migrate_sqlite_to_postgres.py")
        logger.info("с исправленным окружением Windows")
        
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
