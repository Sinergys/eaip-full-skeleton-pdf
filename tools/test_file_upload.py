"""
Тестовый скрипт для загрузки файла и отслеживания работы Intelligent Router.

Использование:
    python tools/test_file_upload.py "путь/к/файлу.jpg" "Navoiy IES"
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Добавляем путь к проекту
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database
from utils.intelligent_router import IntelligentRouter
from file_parser import parse_file
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def upload_and_track_file(file_path: str, enterprise_name: str = "Navoiy IES"):
    """Загружает файл и отслеживает весь процесс обработки"""
    
    print("=" * 80)
    print("🚀 ТЕСТОВАЯ ЗАГРУЗКА ФАЙЛА С ОТСЛЕЖИВАНИЕМ")
    print("=" * 80)
    
    # Проверяем файл
    if not os.path.exists(file_path):
        print(f"\n❌ Файл не найден: {file_path}")
        return False
    
    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    print(f"\n📁 Файл: {filename}")
    print(f"   Путь: {file_path}")
    print(f"   Размер: {file_size / 1024:.1f} KB")
    
    # Инициализируем БД
    database.init_db()
    
    # Получаем или создаем предприятие
    enterprise = database.get_or_create_enterprise(enterprise_name)
    print(f"\n🏢 Предприятие: {enterprise['name']} (ID: {enterprise['id']})")
    
    # Генерируем batch_id
    from uuid import uuid4
    batch_id = str(uuid4())
    print(f"\n🆔 Batch ID: {batch_id}")
    
    # Копируем файл в INBOX_DIR
    INBOX_DIR = os.getenv("INBOX_DIR", "/data/inbox")
    if not os.path.exists(INBOX_DIR):
        # Пробуем создать или использовать альтернативный путь
        INBOX_DIR = os.path.join(os.getcwd(), "data", "inbox")
        os.makedirs(INBOX_DIR, exist_ok=True)
    
    print(f"\n📂 INBOX_DIR: {INBOX_DIR}")
    
    dst = os.path.join(INBOX_DIR, f"{batch_id}__{filename}")
    
    try:
        import shutil
        shutil.copy2(file_path, dst)
        print(f"   ✅ Файл скопирован в: {dst}")
    except Exception as e:
        print(f"   ❌ Ошибка копирования: {e}")
        return False
    
    # Шаг 1: Парсинг файла
    print(f"\n{'=' * 80}")
    print("📄 ШАГ 1: ПАРСИНГ ФАЙЛА")
    print(f"{'=' * 80}")
    
    try:
        parsing_result = parse_file(dst, batch_id=batch_id)
        
        if parsing_result and parsing_result.get("parsed"):
            print("   ✅ Файл успешно распарсен")
            print(f"   Тип файла: {parsing_result.get('file_type', 'unknown')}")
            
            # Показываем структуру данных
            data = parsing_result.get("data", {})
            if isinstance(data, dict):
                if "text" in data:
                    text_len = len(data.get("text", ""))
                    print(f"   Извлечено текста: {text_len} символов")
                if "ocr_used" in data:
                    print(f"   OCR использован: {data.get('ocr_used', False)}")
        else:
            print("   ⚠️  Файл не был распарсен полностью")
            parsing_result = parsing_result or {}
    except Exception as e:
        print(f"   ❌ Ошибка при парсинге: {e}")
        import traceback
        traceback.print_exc()
        parsing_result = {}
    
    # Шаг 2: Intelligent Router анализ
    print(f"\n{'=' * 80}")
    print("🧠 ШАГ 2: INTELLIGENT ROUTER - АНАЛИЗ")
    print(f"{'=' * 80}")
    
    try:
        router = IntelligentRouter()
        
        # Подготавливаем raw_json для router
        file_type_label = "Изображение (JPG)" if filename.lower().endswith(('.jpg', '.jpeg')) else "Unknown"
        raw_json_for_routing = {
            "file_type": file_type_label.lower(),
            "parsing": parsing_result if parsing_result.get("parsed") else None,
        }
        
        print(f"\n   📊 Быстрый анализ...")
        routing_map = router.analyze_file(
            file_path=dst,
            filename=filename,
            raw_json=raw_json_for_routing if parsing_result.get("parsed") else None,
            fast_mode=True
        )
        
        analysis = routing_map.get("analysis", {})
        confidence = analysis.get("confidence", 0.0)
        
        print(f"   Уверенность: {confidence:.2%}")
        print(f"   Тип документа: {analysis.get('document_type', 'unknown')}")
        print(f"   Тип ресурса: {analysis.get('resource_type', 'unknown')}")
        print(f"   Тип данных: {analysis.get('data_type', 'unknown')}")
        
        # Глубокий анализ если нужно
        if confidence < 0.7:
            print(f"\n   ⚠️  Низкая уверенность, выполняю глубокий анализ...")
            routing_map = router.analyze_file(
                file_path=dst,
                filename=filename,
                raw_json=raw_json_for_routing if parsing_result.get("parsed") else None,
                fast_mode=False
            )
            analysis = routing_map.get("analysis", {})
            confidence = analysis.get("confidence", 0.0)
            print(f"   Уверенность после глубокого анализа: {confidence:.2%}")
        
        # Финальные результаты
        print(f"\n   📊 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        print(f"      📄 Тип документа: {analysis.get('document_type', 'unknown')}")
        print(f"      ⚡ Тип ресурса: {analysis.get('resource_type', 'unknown')}")
        print(f"      📊 Тип данных: {analysis.get('data_type', 'unknown')}")
        print(f"      📅 Период: {analysis.get('period', 'unknown')}")
        print(f"      🎯 Уверенность: {confidence:.2%}")
        
        routing = routing_map.get("routing", {})
        print(f"\n   🚀 МАРШРУТИЗАЦИЯ:")
        print(f"      🔧 Primary Module: {routing.get('primary_module', 'unknown')}")
        target_tables = routing.get('target_tables', [])
        if target_tables:
            print(f"      📋 Target Tables: {', '.join(target_tables)}")
        
    except Exception as e:
        print(f"   ❌ Ошибка при анализе Intelligent Router: {e}")
        import traceback
        traceback.print_exc()
        routing_map = None
    
    # Шаг 3: Сохранение в БД
    print(f"\n{'=' * 80}")
    print("💾 ШАГ 3: СОХРАНЕНИЕ В БД")
    print(f"{'=' * 80}")
    
    try:
        # Определяем статус
        status = "success" if parsing_result.get("parsed") else "partial"
        
        # Создаем parsing_summary
        parsing_summary = {
            "file_type": file_type_label,
            "parsed": parsing_result.get("parsed", False),
        }
        
        # Добавляем routing_map
        if routing_map:
            parsing_summary["routing_map"] = {
                "document_type": analysis.get("document_type"),
                "resource_type": analysis.get("resource_type"),
                "data_type": analysis.get("data_type"),
                "period": analysis.get("period"),
                "confidence": confidence,
                "primary_module": routing.get("primary_module"),
                "target_tables": routing.get("target_tables", []),
            }
        
        # Сохраняем в uploads
        database.create_upload(
            batch_id=batch_id,
            enterprise_id=enterprise["id"],
            filename=filename,
            file_type=file_type_label,
            file_size=file_size,
            status=status,
            parsing_summary=parsing_summary,
            file_hash="",  # Можно вычислить, но для теста не обязательно
            file_mtime=os.path.getmtime(dst),
        )
        print(f"   ✅ Запись создана в таблице uploads")
        
        # Сохраняем raw_json в parsed_data
        if parsing_result:
            from datetime import datetime
            editable_text = json.dumps(parsing_result, ensure_ascii=False, indent=2)
            database.save_parsed_content(
                batch_id=batch_id,
                raw_json=parsing_result,
                editable_text=editable_text
            )
            print(f"   ✅ Данные парсинга сохранены в parsed_data")
        
        print(f"\n{'=' * 80}")
        print(f"✅ ФАЙЛ УСПЕШНО ЗАГРУЖЕН И ОБРАБОТАН")
        print(f"{'=' * 80}")
        print(f"\n📋 ИТОГОВАЯ ИНФОРМАЦИЯ:")
        print(f"   Batch ID: {batch_id}")
        print(f"   Файл: {filename}")
        print(f"   Предприятие: {enterprise_name}")
        print(f"   Тип документа: {analysis.get('document_type', 'unknown')}")
        print(f"   Тип ресурса: {analysis.get('resource_type', 'unknown')}")
        print(f"   Уверенность: {confidence:.2%}")
        
        # Проверяем, что файл действительно в БД
        print(f"\n🔍 ПРОВЕРКА В БД:")
        check_record = database.get_upload_by_batch(batch_id)
        if check_record:
            print(f"   ✅ Файл найден в БД")
            print(f"   Статус: {check_record.get('status', 'unknown')}")
            check_summary = check_record.get("parsing_summary")
            if check_summary:
                if isinstance(check_summary, str):
                    check_summary = json.loads(check_summary)
                if "routing_map" in check_summary:
                    print(f"   ✅ routing_map сохранен в БД")
                    rm = check_summary["routing_map"]
                    print(f"      document_type: {rm.get('document_type')}")
                    print(f"      resource_type: {rm.get('resource_type')}")
                    print(f"      confidence: {rm.get('confidence', 0):.2%}")
        else:
            print(f"   ❌ Файл НЕ найден в БД!")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка при сохранении в БД: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python tools/test_file_upload.py <путь_к_файлу> [предприятие]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    enterprise_name = sys.argv[2] if len(sys.argv) > 2 else "Navoiy IES"
    
    success = upload_and_track_file(file_path, enterprise_name)
    sys.exit(0 if success else 1)

