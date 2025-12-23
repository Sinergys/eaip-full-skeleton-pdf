"""
Проверка проекта "Навои ТЭС" и результатов Intelligent Router.

Скрипт показывает:
- Все загруженные файлы для предприятия "Навои ТЭС"
- Результаты анализа Intelligent Router для каждого файла
- Статистику по типам документов и ресурсов
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

# Добавляем путь к проекту
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database


def check_navoi_project():
    """Проверяет все файлы проекта Навои ТЭС"""
    
    database.init_db()
    
    print("=" * 80)
    print("🔍 ПРОВЕРКА ПРОЕКТА 'НАВОИ ТЭС'")
    print("=" * 80)
    
    # Ищем предприятие "Навои ТЭС"
    with database.get_connection() as conn:
        conn.row_factory = database.sqlite3.Row
        cursor = conn.execute("""
            SELECT id, name FROM enterprises 
            WHERE name LIKE '%Навои%' OR name LIKE '%NAVOI%' OR name LIKE '%навои%'
        """)
        enterprises = [dict(row) for row in cursor.fetchall()]
    
    if not enterprises:
        print("\n❌ Предприятие 'Навои ТЭС' не найдено в БД")
        print("\n💡 Создайте предприятие через веб-интерфейс или загрузите файл с указанием названия 'Навои ТЭС'")
        return
    
    print(f"\n✅ Найдено предприятий: {len(enterprises)}")
    for ent in enterprises:
        print(f"   - ID: {ent['id']}, Название: {ent['name']}")
    
    # Статистика
    stats = {
        "total_files": 0,
        "with_routing_map": 0,
        "document_types": defaultdict(int),
        "resource_types": defaultdict(int),
        "confidence_levels": {"high": 0, "medium": 0, "low": 0}
    }
    
    # Проверяем файлы для каждого предприятия
    for enterprise in enterprises:
        enterprise_id = enterprise["id"]
        enterprise_name = enterprise["name"]
        
        print(f"\n{'=' * 80}")
        print(f"📁 ПРЕДПРИЯТИЕ: {enterprise_name} (ID: {enterprise_id})")
        print(f"{'=' * 80}")
        
        with database.get_connection() as conn:
            conn.row_factory = database.sqlite3.Row
            cursor = conn.execute("""
                SELECT batch_id, filename, file_type, status, created_at, parsing_summary
                FROM uploads
                WHERE enterprise_id = ?
                ORDER BY created_at DESC
            """, (enterprise_id,))
            files = [dict(row) for row in cursor.fetchall()]
        
        if not files:
            print(f"\n   ⚠️  Нет загруженных файлов для этого предприятия")
            continue
        
        print(f"\n   📊 Всего файлов: {len(files)}")
        stats["total_files"] += len(files)
        
        for file_record in files:
            batch_id = file_record["batch_id"]
            filename = file_record["filename"]
            file_type = file_record.get("file_type", "unknown")
            status = file_record.get("status", "unknown")
            created_at = file_record.get("created_at", "")
            
            print(f"\n   📄 Файл: {filename}")
            print(f"      Batch ID: {batch_id}")
            print(f"      Тип: {file_type}")
            print(f"      Статус: {status}")
            print(f"      Загружен: {created_at}")
            
            # Извлекаем routing_map
            parsing_summary = file_record.get("parsing_summary")
            routing_map = None
            
            if parsing_summary:
                if isinstance(parsing_summary, str):
                    try:
                        parsing_summary = json.loads(parsing_summary)
                    except:
                        parsing_summary = None
                
                if parsing_summary and "routing_map" in parsing_summary:
                    routing_map = parsing_summary["routing_map"]
                    stats["with_routing_map"] += 1
            
            if routing_map:
                print(f"\n      🧠 INTELLIGENT ROUTER:")
                
                doc_type = routing_map.get("document_type", "unknown")
                resource_type = routing_map.get("resource_type", "unknown")
                data_type = routing_map.get("data_type", "unknown")
                period = routing_map.get("period", "unknown")
                confidence = routing_map.get("confidence", 0.0)
                
                print(f"         📄 Тип документа: {doc_type}")
                print(f"         ⚡ Тип ресурса: {resource_type}")
                print(f"         📊 Тип данных: {data_type}")
                print(f"         📅 Период: {period}")
                print(f"         🎯 Уверенность: {confidence:.2%}")
                
                # Статистика
                stats["document_types"][doc_type] += 1
                stats["resource_types"][resource_type] += 1
                
                if confidence >= 0.7:
                    stats["confidence_levels"]["high"] += 1
                elif confidence >= 0.4:
                    stats["confidence_levels"]["medium"] += 1
                else:
                    stats["confidence_levels"]["low"] += 1
                
                primary_module = routing_map.get("primary_module", "unknown")
                target_tables = routing_map.get("target_tables", [])
                print(f"\n      🚀 МАРШРУТИЗАЦИЯ:")
                print(f"         🔧 Primary Module: {primary_module}")
                if target_tables:
                    print(f"         📋 Target Tables: {', '.join(target_tables)}")
            else:
                print(f"\n      ⚠️  Routing map не найден")
                print(f"         (Файл загружен до интеграции Intelligent Router или произошла ошибка)")
    
    # Итоговая статистика
    print(f"\n{'=' * 80}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print(f"{'=' * 80}")
    print(f"\n📁 Всего файлов: {stats['total_files']}")
    print(f"✅ С routing map: {stats['with_routing_map']}")
    print(f"⚠️  Без routing map: {stats['total_files'] - stats['with_routing_map']}")
    
    if stats["document_types"]:
        print(f"\n📄 Типы документов:")
        for doc_type, count in sorted(stats["document_types"].items(), key=lambda x: -x[1]):
            print(f"   - {doc_type}: {count}")
    
    if stats["resource_types"]:
        print(f"\n⚡ Типы ресурсов:")
        for resource_type, count in sorted(stats["resource_types"].items(), key=lambda x: -x[1]):
            print(f"   - {resource_type}: {count}")
    
    if stats["with_routing_map"] > 0:
        print(f"\n🎯 Уровни уверенности:")
        print(f"   - Высокая (≥70%): {stats['confidence_levels']['high']}")
        print(f"   - Средняя (40-70%): {stats['confidence_levels']['medium']}")
        print(f"   - Низкая (<40%): {stats['confidence_levels']['low']}")
    
    print(f"\n{'=' * 80}")
    print("✅ Проверка завершена")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    check_navoi_project()

