"""
Простой скрипт для переобработки одного файла по batch_id.
Использует данные из БД без необходимости парсинга файла.
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database
from utils.intelligent_router import IntelligentRouter


def reprocess_batch_id(batch_id: str):
    """Переобрабатывает файл по batch_id используя данные из БД"""
    
    database.init_db()
    
    print(f"\n{'=' * 80}")
    print(f"🔄 Переобработка файла: batch_id={batch_id}")
    print(f"{'=' * 80}")
    
    # Получаем данные из БД
    upload_record = database.get_upload_by_batch(batch_id)
    if not upload_record:
        print(f"\n❌ Файл с batch_id={batch_id} не найден в БД")
        return False
    
    filename = upload_record["filename"]
    file_type = upload_record.get("file_type", "unknown")
    
    print(f"\n📁 Файл: {filename}")
    print(f"   Тип: {file_type}")
    
    # Получаем raw_json из БД
    raw_json_data = upload_record.get("raw_json")
    if not raw_json_data:
        print(f"\n⚠️  raw_json не найден в БД для этого файла")
        return False
    
    # Подготавливаем структуру для router
    if isinstance(raw_json_data, str):
        try:
            raw_json_data = json.loads(raw_json_data)
        except:
            print(f"\n❌ Ошибка при парсинге raw_json")
            return False
    
    # Структура для router: {"file_type": "...", "parsing": {"data": {...}}}
    raw_json = {
        "file_type": file_type.lower(),
        "parsing": {
            "data": raw_json_data
        }
    }
    
    print(f"\n🧠 Анализ с Intelligent Router...")
    
    try:
        router = IntelligentRouter()
        
        # Анализируем (без файла, только по данным из БД)
        # Создаем временный путь для router (он может не использоваться)
        dummy_path = f"/tmp/{batch_id}__{filename}"
        
        routing_map = router.analyze_file(
            file_path=dummy_path,
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
                file_path=dummy_path,
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
        parsing_summary = upload_record.get("parsing_summary")
        if isinstance(parsing_summary, str):
            try:
                parsing_summary = json.loads(parsing_summary)
            except:
                parsing_summary = {}
        elif not parsing_summary:
            parsing_summary = {}
        
        # Добавляем/обновляем routing_map
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
        print(f"\n{'=' * 80}")
        print(f"✅ Переобработка завершена успешно!")
        print(f"{'=' * 80}\n")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"\n❌ Ошибка при переобработке: {e}")
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python tools/reprocess_single_file.py <batch_id>")
        sys.exit(1)
    
    batch_id = sys.argv[1]
    success = reprocess_batch_id(batch_id)
    sys.exit(0 if success else 1)

