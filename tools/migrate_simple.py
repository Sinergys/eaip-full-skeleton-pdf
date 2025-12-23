#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт миграции - обход проблемы кодировки через чистые параметры
"""
import sqlite3
import psycopg2
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Жестко заданные параметры (ASCII только)
PG_HOST = "localhost"
PG_PORT = 5432
PG_DB = "eaip_db"
PG_USER = "eaip_user"
PG_PASSWORD = "eaip_password"

SQLITE_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"


def connect_pg():
    """Подключение к PostgreSQL - минималистичный вариант"""
    # Используем connection string с явными ASCII значениями
    dsn = f"host={PG_HOST} port={PG_PORT} dbname={PG_DB} user={PG_USER} password={PG_PASSWORD}"
    return psycopg2.connect(dsn, connect_timeout=5)


def test_connection():
    """Тест подключения"""
    try:
        conn = connect_pg()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        logger.info(f"✓ Подключение успешно: {version[:50]}...")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка подключения: {e}")
        return False


if __name__ == "__main__":
    logger.info("Тест подключения к PostgreSQL...")
    if test_connection():
        logger.info("✅ Подключение работает! Можно запускать миграцию.")
    else:
        logger.error("❌ Подключение не работает. Проверьте настройки.")

