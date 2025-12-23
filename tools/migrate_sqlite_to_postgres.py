#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт миграции данных из SQLite в PostgreSQL
Использование: python tools/migrate_sqlite_to_postgres.py
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

# Исправление кодировки для Windows
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Конфигурация
SQLITE_DB_PATH = Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"

# PostgreSQL подключение (из переменных окружения или docker-compose)
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "database": os.getenv("POSTGRES_DB", "eaip_db"),
    "user": os.getenv("POSTGRES_USER", "eaip_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "eaip_password"),
}


def connect_sqlite():
    """Подключение к SQLite"""
    if not SQLITE_DB_PATH.exists():
        raise FileNotFoundError(f"SQLite база не найдена: {SQLITE_DB_PATH}")
    
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def connect_postgres():
    """Подключение к PostgreSQL с исправлением кодировки"""
    try:
        # Используем переменные окружения напрямую (ASCII только)
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        database = os.getenv("POSTGRES_DB", "eaip_db")
        user = os.getenv("POSTGRES_USER", "eaip_user")
        password = os.getenv("POSTGRES_PASSWORD", "eaip_password")
        
        # Подключение с явным указанием кодировки
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        # Устанавливаем UTF-8 для подключения
        conn.set_client_encoding('UTF8')
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к PostgreSQL: {e}")
        logger.info("Проверьте настройки подключения")
        raise


def migrate_enterprises(sqlite_conn, pg_conn):
    """Миграция таблицы enterprises"""
    logger.info("Миграция enterprises...")
    
    # Получаем данные из SQLite
    sqlite_cursor = sqlite_conn.execute(
        "SELECT id, name, created_at, industry, enterprise_type, product_type FROM enterprises"
    )
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        logger.info("  Таблица enterprises пуста")
        return {}
    
    # Маппинг старых ID на новые
    id_mapping = {}
    
    # Вставляем данные в PostgreSQL
    pg_cursor = pg_conn.cursor()
    
    for row in rows:
        old_id = row["id"]
        name = row["name"]
        created_at = row["created_at"]
        industry = row["industry"]
        enterprise_type = row["enterprise_type"]
        product_type = row["product_type"]
        
        # Проверяем, существует ли уже запись
        pg_cursor.execute(
            "SELECT id FROM enterprises WHERE name = %s",
            (name,)
        )
        existing = pg_cursor.fetchone()
        
        if existing:
            new_id = existing[0]
            logger.debug(f"  Предприятие '{name}' уже существует (ID: {new_id})")
        else:
            # Вставляем новую запись
            pg_cursor.execute(
                """
                INSERT INTO enterprises (name, created_at, industry, enterprise_type, product_type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (name, created_at, industry, enterprise_type, product_type)
            )
            new_id = pg_cursor.fetchone()[0]
            logger.debug(f"  Создано предприятие '{name}' (ID: {old_id} -> {new_id})")
        
        id_mapping[old_id] = new_id
    
    pg_conn.commit()
    logger.info(f"  Мигрировано {len(id_mapping)} предприятий")
    return id_mapping


def migrate_uploads(sqlite_conn, pg_conn, enterprise_id_mapping: Dict[int, int]):
    """Миграция таблицы uploads"""
    logger.info("Миграция uploads...")
    
    sqlite_cursor = sqlite_conn.execute(
        "SELECT id, batch_id, enterprise_id, filename, file_type, file_size, status, parsing_summary, created_at FROM uploads"
    )
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        logger.info("  Таблица uploads пуста")
        return {}
    
    id_mapping = {}
    pg_cursor = pg_conn.cursor()
    
    for row in rows:
        old_id = row["id"]
        batch_id = row["batch_id"]
        old_enterprise_id = row["enterprise_id"]
        filename = row["filename"]
        file_type = row["file_type"]
        file_size = row["file_size"]
        status = row["status"]
        parsing_summary = row["parsing_summary"]
        created_at = row["created_at"]
        
        # Получаем новый ID предприятия
        new_enterprise_id = enterprise_id_mapping.get(old_enterprise_id)
        if not new_enterprise_id:
            logger.warning(f"  Пропускаю upload {batch_id}: предприятие {old_enterprise_id} не найдено")
            continue
        
        # Проверяем существование
        pg_cursor.execute(
            "SELECT id FROM uploads WHERE batch_id = %s",
            (batch_id,)
        )
        existing = pg_cursor.fetchone()
        
        if existing:
            new_id = existing[0]
        else:
            pg_cursor.execute(
                """
                INSERT INTO uploads (batch_id, enterprise_id, filename, file_type, file_size, status, parsing_summary, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (batch_id, new_enterprise_id, filename, file_type, file_size, status, parsing_summary, created_at)
            )
            new_id = pg_cursor.fetchone()[0]
        
        id_mapping[old_id] = new_id
    
    pg_conn.commit()
    logger.info(f"  Мигрировано {len(id_mapping)} загрузок")
    return id_mapping


def migrate_parsed_data(sqlite_conn, pg_conn, upload_id_mapping: Dict[int, int]):
    """Миграция таблицы parsed_data"""
    logger.info("Миграция parsed_data...")
    
    sqlite_cursor = sqlite_conn.execute(
        "SELECT upload_id, raw_json, editable_text, updated_at FROM parsed_data"
    )
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        logger.info("  Таблица parsed_data пуста")
        return
    
    pg_cursor = pg_conn.cursor()
    migrated = 0
    
    for row in rows:
        old_upload_id = row["upload_id"]
        new_upload_id = upload_id_mapping.get(old_upload_id)
        
        if not new_upload_id:
            logger.warning(f"  Пропускаю parsed_data для upload_id {old_upload_id}")
            continue
        
        raw_json_str = row["raw_json"]
        editable_text = row["editable_text"]
        updated_at = row["updated_at"]
        
        # Парсим JSON
        raw_json = None
        if raw_json_str:
            try:
                raw_json = json.loads(raw_json_str)
            except json.JSONDecodeError:
                logger.warning(f"  Ошибка парсинга JSON для upload_id {new_upload_id}")
        
        # Вставляем или обновляем
        pg_cursor.execute(
            """
            INSERT INTO parsed_data (upload_id, raw_json, editable_text, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (upload_id) DO UPDATE
            SET raw_json = EXCLUDED.raw_json,
                editable_text = EXCLUDED.editable_text,
                updated_at = EXCLUDED.updated_at
            """,
            (new_upload_id, json.dumps(raw_json) if raw_json else None, editable_text, updated_at)
        )
        migrated += 1
    
    pg_conn.commit()
    logger.info(f"  Мигрировано {migrated} записей parsed_data")


def migrate_normative_documents(sqlite_conn, pg_conn):
    """Миграция нормативных документов"""
    logger.info("Миграция normative_documents...")
    
    sqlite_cursor = sqlite_conn.execute(
        """SELECT id, title, document_type, file_path, file_hash, file_size, 
                  uploaded_at, ai_processed, processing_status, full_text, parsed_data_json 
           FROM normative_documents"""
    )
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        logger.info("  Таблица normative_documents пуста")
        return {}
    
    id_mapping = {}
    pg_cursor = pg_conn.cursor()
    
    for row in rows:
        old_id = row["id"]
        title = row["title"]
        document_type = row["document_type"]
        file_path = row["file_path"]
        file_hash = row["file_hash"]
        file_size = row["file_size"]
        uploaded_at = row["uploaded_at"]
        ai_processed = row["ai_processed"]
        processing_status = row["processing_status"]
        full_text = row["full_text"]
        parsed_data_json_str = row["parsed_data_json"]
        
        # Парсим parsed_data_json
        parsed_data_json = None
        if parsed_data_json_str:
            try:
                parsed_data_json = json.loads(parsed_data_json_str)
            except json.JSONDecodeError:
                pass
        
        # Проверяем по hash
        if file_hash:
            pg_cursor.execute(
                "SELECT id FROM normative_documents WHERE file_hash = %s",
                (file_hash,)
            )
            existing = pg_cursor.fetchone()
            
            if existing:
                new_id = existing[0]
                id_mapping[old_id] = new_id
                continue
        
        # Создаем новую запись
        pg_cursor.execute(
            """
            INSERT INTO normative_documents 
            (title, document_type, file_path, file_hash, file_size, uploaded_at, 
             ai_processed, processing_status, full_text, parsed_data_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (title, document_type, file_path, file_hash, file_size, uploaded_at,
             ai_processed, processing_status, full_text,
             json.dumps(parsed_data_json) if parsed_data_json else None)
        )
        new_id = pg_cursor.fetchone()[0]
        id_mapping[old_id] = new_id
    
    pg_conn.commit()
    logger.info(f"  Мигрировано {len(id_mapping)} нормативных документов")
    return id_mapping


def migrate_aggregated_data(sqlite_conn, pg_conn, enterprise_id_mapping: Dict[int, int]):
    """Миграция агрегированных данных"""
    logger.info("Миграция aggregated_data...")
    
    sqlite_cursor = sqlite_conn.execute(
        "SELECT enterprise_id, batch_id, resource_type, period, data_json, created_at, updated_at FROM aggregated_data"
    )
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        logger.info("  Таблица aggregated_data пуста")
        return
    
    pg_cursor = pg_conn.cursor()
    migrated = 0
    
    for row in rows:
        old_enterprise_id = row["enterprise_id"]
        new_enterprise_id = enterprise_id_mapping.get(old_enterprise_id)
        
        if not new_enterprise_id:
            logger.warning(f"  Пропускаю aggregated_data: предприятие {old_enterprise_id} не найдено")
            continue
        
        batch_id = row["batch_id"]
        resource_type = row["resource_type"]
        period = row["period"]
        data_json_str = row["data_json"]
        created_at = row["created_at"]
        updated_at = row["updated_at"]
        
        # Парсим JSON
        try:
            data_json = json.loads(data_json_str) if data_json_str else {}
        except json.JSONDecodeError:
            logger.warning(f"  Ошибка парсинга JSON для aggregated_data")
            continue
        
        # Вставляем с ON CONFLICT
        pg_cursor.execute(
            """
            INSERT INTO aggregated_data 
            (enterprise_id, batch_id, resource_type, period, data_json, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (enterprise_id, resource_type, period) DO UPDATE
            SET batch_id = EXCLUDED.batch_id,
                data_json = EXCLUDED.data_json,
                updated_at = EXCLUDED.updated_at
            """,
            (new_enterprise_id, batch_id, resource_type, period,
             json.dumps(data_json), created_at, updated_at)
        )
        migrated += 1
    
    pg_conn.commit()
    logger.info(f"  Мигрировано {migrated} записей aggregated_data")


def main():
    """Главная функция миграции"""
    logger.info("=" * 60)
    logger.info("Начало миграции SQLite -> PostgreSQL")
    logger.info("=" * 60)
    
    sqlite_conn = None
    pg_conn = None
    
    try:
        # Подключения
        logger.info("Подключение к базам данных...")
        sqlite_conn = connect_sqlite()
        logger.info(f"  ✓ SQLite: {SQLITE_DB_PATH}")
        
        pg_conn = connect_postgres()
        logger.info(f"  ✓ PostgreSQL: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}")
        
        # Миграция в правильном порядке (с учетом foreign keys)
        enterprise_id_mapping = migrate_enterprises(sqlite_conn, pg_conn)
        upload_id_mapping = migrate_uploads(sqlite_conn, pg_conn, enterprise_id_mapping)
        migrate_parsed_data(sqlite_conn, pg_conn, upload_id_mapping)
        normative_id_mapping = migrate_normative_documents(sqlite_conn, pg_conn)
        migrate_aggregated_data(sqlite_conn, pg_conn, enterprise_id_mapping)
        
        # TODO: Добавить миграцию остальных таблиц:
        # - uploads_storage
        # - normative_rules
        # - normative_references
        # - normative_violations
        # - node_consumption
        
        logger.info("=" * 60)
        logger.info("✓ Миграция завершена успешно!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Ошибка миграции: {e}", exc_info=True)
        if pg_conn:
            pg_conn.rollback()
        raise
    
    finally:
        if sqlite_conn:
            sqlite_conn.close()
        if pg_conn:
            pg_conn.close()


if __name__ == "__main__":
    main()

