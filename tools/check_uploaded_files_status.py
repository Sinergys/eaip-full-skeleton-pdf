"""
Проверка статуса обработки загруженных файлов.

Показывает:
- Общее количество загруженных файлов
- Статус обработки (success, partial, error, pending)
- Наличие routing_map
- Статистику по типам файлов
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database
import json
from collections import defaultdict


def check_uploaded_files():
    """Проверяет статус всех загруженных файлов"""
    
    database.init_db()
    
    print("=" * 80)
    print("📊 ПРОВЕРКА СТАТУСА ОБРАБОТКИ ФАЙЛОВ")
    print("=" * 80)
    
    with database.get_connection() as conn:
        conn.row_factory = database.sqlite3.Row
        
        # Общая статистика
        cursor = conn.execute("SELECT COUNT(*) as total FROM uploads")
        total_files = cursor.fetchone()["total"]
        
        print(f"\n📁 Всего файлов в БД: {total_files}")
        
        # Статистика по статусам
        cursor = conn.execute("""
            SELECT status, COUNT(*) as count 
            FROM uploads 
            GROUP BY status
        """)
        status_stats = {row["status"]: row["count"] for row in cursor.fetchall()}
        
        print(f"\n📊 Статистика по статусам:")
        for status, count in sorted(status_stats.items()):
            percentage = (count / total_files * 100) if total_files > 0 else 0
            print(f"   {status}: {count} ({percentage:.1f}%)")
        
        # Статистика по routing_map
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN parsing_summary LIKE '%routing_map%' THEN 1 ELSE 0 END) as with_routing_map
            FROM uploads
        """)
        routing_stats = cursor.fetchone()
        with_routing = routing_stats["with_routing_map"]
        without_routing = total_files - with_routing
        
        print(f"\n🧠 Intelligent Router:")
        print(f"   С routing_map: {with_routing} ({with_routing/total_files*100:.1f}%)" if total_files > 0 else "   С routing_map: 0")
        print(f"   Без routing_map: {without_routing} ({without_routing/total_files*100:.1f}%)" if total_files > 0 else "   Без routing_map: 0")
        
        # Статистика по типам файлов
        cursor = conn.execute("""
            SELECT file_type, COUNT(*) as count 
            FROM uploads 
            GROUP BY file_type
            ORDER BY count DESC
        """)
        file_types = {row["file_type"]: row["count"] for row in cursor.fetchall()}
        
        print(f"\n📄 Статистика по типам файлов:")
        for file_type, count in file_types.items():
            percentage = (count / total_files * 100) if total_files > 0 else 0
            print(f"   {file_type}: {count} ({percentage:.1f}%)")
        
        # Файлы с ошибками
        cursor = conn.execute("""
            SELECT batch_id, filename, status, file_type
            FROM uploads
            WHERE status = 'error'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        error_files = [dict(row) for row in cursor.fetchall()]
        
        if error_files:
            print(f"\n❌ Файлы с ошибками (показано до 10):")
            for file_info in error_files:
                print(f"   - {file_info['filename']} (batch_id: {file_info['batch_id']})")
        
        # Файлы без routing_map
        cursor = conn.execute("""
            SELECT batch_id, filename, status, file_type
            FROM uploads
            WHERE parsing_summary NOT LIKE '%routing_map%' OR parsing_summary IS NULL
            ORDER BY created_at DESC
            LIMIT 10
        """)
        no_routing_files = [dict(row) for row in cursor.fetchall()]
        
        if no_routing_files:
            print(f"\n⚠️  Файлы без routing_map (показано до 10):")
            for file_info in no_routing_files:
                print(f"   - {file_info['filename']} (status: {file_info['status']})")
        
        # Анализ routing_map
        cursor = conn.execute("""
            SELECT parsing_summary
            FROM uploads
            WHERE parsing_summary LIKE '%routing_map%'
        """)
        
        routing_analysis = {
            "document_types": defaultdict(int),
            "resource_types": defaultdict(int),
            "confidence_levels": {"high": 0, "medium": 0, "low": 0}
        }
        
        for row in cursor.fetchall():
            try:
                summary = json.loads(row["parsing_summary"]) if isinstance(row["parsing_summary"], str) else row["parsing_summary"]
                if "routing_map" in summary:
                    rm = summary["routing_map"]
                    routing_analysis["document_types"][rm.get("document_type", "unknown")] += 1
                    routing_analysis["resource_types"][rm.get("resource_type", "unknown")] += 1
                    conf = rm.get("confidence", 0.0)
                    if conf >= 0.7:
                        routing_analysis["confidence_levels"]["high"] += 1
                    elif conf >= 0.4:
                        routing_analysis["confidence_levels"]["medium"] += 1
                    else:
                        routing_analysis["confidence_levels"]["low"] += 1
            except:
                pass
        
        if routing_analysis["document_types"]:
            print(f"\n📊 Анализ routing_map:")
            print(f"   Типы документов:")
            for doc_type, count in sorted(routing_analysis["document_types"].items(), key=lambda x: -x[1]):
                print(f"      {doc_type}: {count}")
            
            print(f"   Типы ресурсов:")
            for res_type, count in sorted(routing_analysis["resource_types"].items(), key=lambda x: -x[1]):
                print(f"      {res_type}: {count}")
            
            print(f"   Уровни уверенности:")
            print(f"      Высокая (≥70%): {routing_analysis['confidence_levels']['high']}")
            print(f"      Средняя (40-70%): {routing_analysis['confidence_levels']['medium']}")
            print(f"      Низкая (<40%): {routing_analysis['confidence_levels']['low']}")
        
        # Проверка parsed_data
        cursor = conn.execute("SELECT COUNT(*) as count FROM parsed_data")
        parsed_count = cursor.fetchone()["count"]
        
        print(f"\n💾 Данные парсинга:")
        print(f"   Записей в parsed_data: {parsed_count}")
        print(f"   Файлов с данными парсинга: {parsed_count} из {total_files} ({parsed_count/total_files*100:.1f}%)" if total_files > 0 else "   Файлов с данными парсинга: 0")
        
        print(f"\n{'=' * 80}")
        print("✅ Проверка завершена")
        print(f"{'=' * 80}")


if __name__ == "__main__":
    check_uploaded_files()

