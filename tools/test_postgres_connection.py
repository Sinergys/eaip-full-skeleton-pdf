#!/usr/bin/env python3
"""Простой тест подключения к PostgreSQL"""
import psycopg2
import sys

# Исправление кодировки
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='eaip_db',
        user='eaip_user',
        password='eaip_password'
    )
    print("✓ Подключение к PostgreSQL успешно")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✓ Версия PostgreSQL: {version[:50]}...")
    
    cursor.execute("SELECT COUNT(*) FROM enterprises;")
    count = cursor.fetchone()[0]
    print(f"✓ Предприятий в БД: {count}")
    
    conn.close()
    print("✓ Тест завершен успешно")
except Exception as e:
    print(f"✗ Ошибка: {e}")
    sys.exit(1)

