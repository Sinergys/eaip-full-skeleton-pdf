#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обходной путь: Экспорт SQLite в SQL, затем импорт в PostgreSQL
Избегает проблем с psycopg2 на Windows
"""
import sqlite3
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SQLITE_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"


def export_sqlite_to_sql():
    """Экспортирует SQLite в SQL формат"""
    logger.info("Экспорт SQLite в SQL...")
    
    if not SQLITE_PATH.exists():
        raise FileNotFoundError(f"SQLite база не найдена: {SQLITE_PATH}")
    
    output_sql = Path(__file__).parent / "sqlite_export.sql"
    
    # Используем sqlite3 для экспорта
    cmd = [
        "sqlite3",
        str(SQLITE_PATH),
        ".dump"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            with open(output_sql, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            logger.info(f"✅ Экспорт завершен: {output_sql}")
            return output_sql
        else:
            logger.error(f"Ошибка экспорта: {result.stderr}")
            return None
            
    except FileNotFoundError:
        logger.error("sqlite3 не найден в PATH. Используйте другой метод.")
        return None


if __name__ == "__main__":
    logger.info("Экспорт SQLite в SQL (обходной путь)...")
    sql_file = export_sqlite_to_sql()
    if sql_file:
        logger.info("✅ Готово! SQL файл создан.")
        logger.info("Следующий шаг: Адаптировать SQL для PostgreSQL и импортировать")

