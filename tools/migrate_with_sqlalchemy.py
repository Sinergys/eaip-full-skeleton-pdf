#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Миграция с использованием SQLAlchemy (обход проблемы psycopg2 на Windows)
Продвинутый подход, используемый в production
"""
import sqlite3
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# PostgreSQL подключение через SQLAlchemy (правильно обрабатывает кодировку)
PG_URL = "postgresql://eaip_user:eaip_password@localhost:5432/eaip_db"

SQLITE_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"


def test_connection():
    """Тест подключения через SQLAlchemy"""
    try:
        engine = create_engine(PG_URL, pool_pre_ping=True, echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"✓ Подключение успешно!")
            logger.info(f"  Версия: {version[:60]}...")
        return engine
    except Exception as e:
        logger.error(f"✗ Ошибка подключения: {e}")
        return None


if __name__ == "__main__":
    logger.info("Тест подключения через SQLAlchemy...")
    engine = test_connection()
    if engine:
        logger.info("✅ SQLAlchemy работает! Можно использовать для миграции.")
    else:
        logger.error("❌ Подключение не работает.")

