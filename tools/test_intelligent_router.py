"""
Скрипт для проверки работы Intelligent Router после загрузки файлов.

Использование:
1. Загрузите файл через веб-интерфейс (http://localhost:8001)
2. Запустите этот скрипт с batch_id загруженного файла
3. Или запустите без параметров для проверки последних загрузок
"""

import sys
import json
from pathlib import Path

# Добавляем путь к проекту
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database


def check_routing_map(batch_id: str = None):
    """Проверяет routing_map для загруженных файлов"""
    
    database.init_db()
    
    if batch_id:
        # Проверяем конкретный batch_id
        record = database.get_upload_by_batch(batch_id)
        if not record:
            print(f"❌ Файл с batch_id={batch_id} не найден")
            return
        
        records = [record]
    else:
        # Проверяем последние 5 загрузок
        print("🔍 Проверяю последние загрузки...\n")
        with database.get_connection() as conn:
            conn.row_factory = database.sqlite3.Row
            cursor = conn.execute("""
                SELECT batch_id, filename, file_type, status, parsing_summary
                FROM uploads
                ORDER BY created_at DESC
                LIMIT 5
            """)
            records = [dict(row) for row in cursor.fetchall()]
    
    if not records:
        print("❌ Нет загруженных файлов")
        return
    
    print("=" * 80)
    print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА INTELLIGENT ROUTER")
    print("=" * 80)
    
    for record in records:
        batch_id = record["batch_id"]
        filename = record["filename"]
        file_type = record.get("file_type", "unknown")
        status = record.get("status", "unknown")
        
        print(f"\n📁 Файл: {filename}")
        print(f"   Batch ID: {batch_id}")
        print(f"   Тип: {file_type}")
        print(f"   Статус: {status}")
        
        # Извлекаем routing_map из parsing_summary
        parsing_summary = record.get("parsing_summary")
        if parsing_summary:
            if isinstance(parsing_summary, str):
                try:
                    parsing_summary = json.loads(parsing_summary)
                except:
                    parsing_summary = None
        
        if parsing_summary and "routing_map" in parsing_summary:
            routing_map = parsing_summary["routing_map"]
            
            print("\n   🧠 АНАЛИЗ INTELLIGENT ROUTER:")
            print(f"      📄 Тип документа: {routing_map.get('document_type', 'unknown')}")
            print(f"      ⚡ Тип ресурса: {routing_map.get('resource_type', 'unknown')}")
            print(f"      📊 Тип данных: {routing_map.get('data_type', 'unknown')}")
            print(f"      📅 Период: {routing_map.get('period', 'unknown')}")
            print(f"      🎯 Уверенность: {routing_map.get('confidence', 0.0):.2%}")
            
            print(f"\n   🚀 МАРШРУТИЗАЦИЯ:")
            print(f"      🔧 Primary Module: {routing_map.get('primary_module', 'unknown')}")
            target_tables = routing_map.get('target_tables', [])
            if target_tables:
                print(f"      📋 Target Tables: {', '.join(target_tables)}")
            else:
                print(f"      📋 Target Tables: не указаны")
        else:
            print("\n   ⚠️  Routing map не найден в parsing_summary")
            print("      Возможно, файл был загружен до интеграции Intelligent Router")
        
        print("-" * 80)
    
    print("\n✅ Проверка завершена")


if __name__ == "__main__":
    batch_id = sys.argv[1] if len(sys.argv) > 1 else None
    check_routing_map(batch_id)

