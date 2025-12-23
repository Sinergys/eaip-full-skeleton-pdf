#!/usr/bin/env python3
"""
Скрипт миграции данных из SQLite в PostgreSQL
Исправленная версия с правильной обработкой кодировки для Windows
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Исправление кодировки для Windows перед любыми операциями
if sys.platform == 'win32':
    import io
    import locale
    # Устанавливаем UTF-8 для вывода
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
SQLITE_DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"

# PostgreSQL подключение - используем простые строки ASCII
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "eaip_db",
    "user": "eaip_user",
    "password": "eaip_password",
}

# Переопределяем из переменных окружения, если они есть (как ASCII)
if os.getenv("POSTGRES_HOST"):
    POSTGRES_CONFIG["host"] = os.getenv("POSTGRES_HOST")
if os.getenv("POSTGRES_PORT"):
    POSTGRES_CONFIG["port"] = int(os.getenv("POSTGRES_PORT"))
if os.getenv("POSTGRES_DB"):
    POSTGRES_CONFIG["database"] = os.getenv("POSTGRES_DB")
if os.getenv("POSTGRES_USER"):
    POSTGRES_CONFIG["user"] = os.getenv("POSTGRES_USER")
if os.getenv("POSTGRES_PASSWORD"):
    POSTGRES_CONFIG["password"] = os.getenv("POSTGRES_PASSWORD")


def connect_sqlite():
    """Подключение к SQLite"""
    if not SQLITE_DB_PATH.exists():
        raise FileNotFoundError(f"SQLite база не найдена: {SQLITE_DB_PATH}")
    
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def connect_postgres():
    """Подключение к PostgreSQL с исправленной обработкой кодировки"""
    try:
        # Используем прямые параметры (не строку подключения)
        # Убеждаемся, что все значения - строки ASCII
        conn = psycopg2.connect(
            host=str(POSTGRES_CONFIG['host']),
            port=int(POSTGRES_CONFIG['port']),
            database=str(POSTGRES_CONFIG['database']),
            user=str(POSTGRES_CONFIG['user']),
            password=str(POSTGRES_CONFIG['password']),
            client_encoding='UTF8'
        )
        # Устанавливаем кодировку подключения
        conn.set_client_encoding('UTF8')
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к PostgreSQL: {e}")
        logger.info(f"Параметры: host={POSTGRES_CONFIG['host']}, port={POSTGRES_CONFIG['port']}")
        logger.info("Проверьте, что PostgreSQL запущен: docker compose up -d postgres")
        raise

