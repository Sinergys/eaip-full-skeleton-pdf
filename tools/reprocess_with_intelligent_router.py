"""
Скрипт для переобработки загруженных файлов с улучшенным Intelligent Router.

Использование:
    python tools/reprocess_with_intelligent_router.py [batch_id]
    python tools/reprocess_with_intelligent_router.py --all  # все файлы
    python tools/reprocess_with_intelligent_router.py --enterprise "Navoiy IES"  # файлы предприятия
"""

import sys
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# Добавляем путь к проекту
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database
from utils.intelligent_router import IntelligentRouter
from file_parser import parse_file


def reprocess_file(batch_id: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """Переобрабатывает файл с улучшенным Intelligent Router"""
    
    # Получаем информацию о файле из БД
    upload_record = database.get_upload_by_batch(batch_id)
    if not upload_record:
        return {"error": f"Файл с batch_id={batch_id} не найден в БД"}
    
    filename = upload_record["filename"]
    
    # Находим файл на диске
    if not file_path:
        # Ищем файл в INBOX_DIR
        INBOX_DIR = os.getenv("INBOX_DIR", "/data/inbox")
        file_path = os.path.join(INBOX_DIR, f"{batch_id}__{filename}")
        
        if not os.path.exists(file_path):
            # Пробуем найти по имени
            for file in Path(INBOX_DIR).glob(f"*{filename}"):
                file_path = str(file)
                break
            else:
                return {"error": f"Файл {filename} не найден на диске"}
    
    if not os.path.exists(file_path):
        return {"error": f"Файл {file_path} не существует"}
    
    print(f"\n{'=' * 80}")
    print(f"🔄 Переобработка файла: {filename}")
    print(f"   Batch ID: {batch_id}")
    print(f"   Путь: {file_path}")
    print(f"{'=' * 80}")
    
    try:
        # Пытаемся получить raw_json из БД сначала
        print("\n📄 Получение данных из БД...")
        upload_record = database.get_upload_by_batch(batch_id)
        raw_json = None
        
        if upload_record and upload_record.get("raw_json"):
            try:
                raw_json_data = upload_record["raw_json"]
                if isinstance(raw_json_data, str):
                    raw_json_data = json.loads(raw_json_data)
                # Структура для router: {"file_type": "...", "parsing": {"data": {...}}}
                raw_json = {
                    "file_type": Path(filename).suffix.lower().replace(".", ""),
                    "parsing": {"data": raw_json_data} if isinstance(raw_json_data, dict) else raw_json_data
                }
                print("   ✅ Данные получены из БД")
            except Exception as e:
                print(f"   ⚠️  Ошибка при чтении данных из БД: {e}")
                raw_json = None
        
        # Если данных нет в БД, пытаемся распарсить файл
        if not raw_json and os.path.exists(file_path):
            print("   📄 Парсинг файла...")
            try:
                parsing_result = parse_file(file_path, batch_id=batch_id)
                if parsing_result and parsing_result.get("parsed"):
                    raw_json = {
                        "file_type": Path(filename).suffix.lower().replace(".", ""),
                        "parsing": parsing_result
                    }
                    print("   ✅ Файл распарсен")
                else:
                    print("   ⚠️  Файл не был распарсен")
                    raw_json = {"file_type": Path(filename).suffix.lower().replace(".", ""), "parsing": parsing_result or {}}
            except Exception as e:
                print(f"   ⚠️  Ошибка при парсинге: {e}")
                raw_json = {"file_type": Path(filename).suffix.lower().replace(".", ""), "parsing": {}}
        
        if not raw_json:
            return {"error": "Не удалось получить данные для анализа"}
        
        # Анализируем с Intelligent Router
        print("\n🧠 Анализ с Intelligent Router...")
        router = IntelligentRouter()
        
        # Быстрый анализ
        routing_map = router.analyze_file(
            file_path=file_path,
            filename=filename,
            raw_json=raw_json,
            fast_mode=True
        )
        
        confidence = routing_map.get("analysis", {}).get("confidence", 0.0)
        print(f"   Быстрый анализ: confidence = {confidence:.2%}")
        
        # Глубокий анализ если нужно
        if confidence < 0.7:
            print("   ⚠️  Низкая уверенность, выполняю глубокий анализ...")
            routing_map = router.analyze_file(
                file_path=file_path,
                filename=filename,
                raw_json=raw_json,
                fast_mode=False
            )
            confidence = routing_map.get("analysis", {}).get("confidence", 0.0)
            print(f"   Глубокий анализ: confidence = {confidence:.2%}")
        
        # Выводим результаты
        analysis = routing_map.get("analysis", {})
        routing = routing_map.get("routing", {})
        
        print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print(f"   📄 Тип документа: {analysis.get('document_type', 'unknown')}")
        print(f"   ⚡ Тип ресурса: {analysis.get('resource_type', 'unknown')}")
        print(f"   📊 Тип данных: {analysis.get('data_type', 'unknown')}")
        print(f"   📅 Период: {analysis.get('period', 'unknown')}")
        print(f"   🎯 Уверенность: {confidence:.2%}")
        
        print(f"\n🚀 МАРШРУТИЗАЦИЯ:")
        print(f"   🔧 Primary Module: {routing.get('primary_module', 'unknown')}")
        target_tables = routing.get('target_tables', [])
        if target_tables:
            print(f"   📋 Target Tables: {', '.join(target_tables)}")
        
        # Обновляем parsing_summary в БД
        print(f"\n💾 Обновление данных в БД...")
        upload_record = database.get_upload_by_batch(batch_id)
        if upload_record:
            parsing_summary = upload_record.get("parsing_summary")
            if isinstance(parsing_summary, str):
                try:
                    parsing_summary = json.loads(parsing_summary)
                except:
                    parsing_summary = {}
            elif not parsing_summary:
                parsing_summary = {}
            
            # Добавляем routing_map
            parsing_summary["routing_map"] = {
                "document_type": analysis.get("document_type"),
                "resource_type": analysis.get("resource_type"),
                "data_type": analysis.get("data_type"),
                "period": analysis.get("period"),
                "confidence": confidence,
                "primary_module": routing.get("primary_module"),
                "target_tables": routing.get("target_tables", []),
            }
            
            # Обновляем в БД
            with database.get_connection() as conn:
                conn.execute("""
                    UPDATE uploads
                    SET parsing_summary = ?
                    WHERE batch_id = ?
                """, (json.dumps(parsing_summary, ensure_ascii=False), batch_id))
                conn.commit()
            
            print(f"   ✅ Данные обновлены в БД")
        else:
            print(f"   ⚠️  Не удалось обновить данные в БД")
        
        return {
            "success": True,
            "batch_id": batch_id,
            "filename": filename,
            "routing_map": routing_map
        }
        
    except Exception as e:
        import traceback
        print(f"\n❌ Ошибка при переобработке: {e}")
        print(traceback.format_exc())
        return {"error": str(e)}


def reprocess_all_files(enterprise_name: Optional[str] = None) -> None:
    """Переобрабатывает все файлы или файлы предприятия"""
    
    database.init_db()
    
    print("=" * 80)
    print("🔄 МАССОВАЯ ПЕРЕОБРАБОТКА ФАЙЛОВ")
    print("=" * 80)
    
    # Получаем список файлов
    with database.get_connection() as conn:
        conn.row_factory = database.sqlite3.Row
        
        if enterprise_name:
            # Файлы конкретного предприятия
            cursor = conn.execute("""
                SELECT u.batch_id, u.filename, u.file_path, e.name as enterprise_name
                FROM uploads u
                JOIN enterprises e ON u.enterprise_id = e.id
                WHERE e.name LIKE ?
                ORDER BY u.created_at DESC
            """, (f"%{enterprise_name}%",))
        else:
            # Все файлы
            cursor = conn.execute("""
                SELECT u.batch_id, u.filename, u.file_path, e.name as enterprise_name
                FROM uploads u
                JOIN enterprises e ON u.enterprise_id = e.id
                ORDER BY u.created_at DESC
            """)
        
        files = [dict(row) for row in cursor.fetchall()]
    
    if not files:
        print(f"\n❌ Файлы не найдены")
        return
    
    print(f"\n📁 Найдено файлов: {len(files)}")
    if enterprise_name:
        print(f"   Предприятие: {enterprise_name}")
    
    success_count = 0
    error_count = 0
    
    for file_record in files:
        batch_id = file_record["batch_id"]
        filename = file_record["filename"]
        file_path = file_record.get("file_path")
        
        result = reprocess_file(batch_id, file_path)
        
        if result.get("success"):
            success_count += 1
        else:
            error_count += 1
            print(f"   ❌ Ошибка: {result.get('error', 'unknown')}")
    
    print(f"\n{'=' * 80}")
    print(f"✅ Успешно: {success_count}")
    print(f"❌ Ошибок: {error_count}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            reprocess_all_files()
        elif sys.argv[1] == "--enterprise" and len(sys.argv) > 2:
            enterprise_name = sys.argv[2]
            reprocess_all_files(enterprise_name)
        else:
            batch_id = sys.argv[1]
            result = reprocess_file(batch_id)
            if result.get("success"):
                print("\n✅ Переобработка завершена успешно")
            else:
                print(f"\n❌ Ошибка: {result.get('error', 'unknown')}")
                sys.exit(1)
    else:
        print("Использование:")
        print("  python tools/reprocess_with_intelligent_router.py [batch_id]")
        print("  python tools/reprocess_with_intelligent_router.py --all")
        print("  python tools/reprocess_with_intelligent_router.py --enterprise 'Navoiy IES'")

