"""
Массовая загрузка файлов из папки с полным контролем и отслеживанием.

Использование:
    python tools/batch_upload_from_folder.py "C:/AUDIT/OBJECTS/Navoiy IES/INBOX" "Navoiy IES"
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database
from utils.intelligent_router import IntelligentRouter
from file_parser import parse_file
from database import safe_json_dumps
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def batch_upload_from_folder(folder_path: str, enterprise_name: str = "Navoiy IES", system_mode: str = "debug"):
    """Загружает все Excel и Word файлы из папки с полным контролем"""
    
    print("=" * 80)
    print("🚀 МАССОВАЯ ЗАГРУЗКА ФАЙЛОВ ИЗ ПАПКИ")
    print("=" * 80)
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Папка не найдена: {folder_path}")
        return
    
    # Находим все Excel и Word файлы
    excel_files = list(folder.glob("*.xlsx")) + list(folder.glob("*.xlsm")) + list(folder.glob("*.xls"))
    word_files = list(folder.glob("*.docx"))
    all_files = excel_files + word_files
    
    print(f"\n📁 Папка: {folder_path}")
    print(f"📄 Найдено файлов:")
    print(f"   Excel: {len(excel_files)}")
    print(f"   Word: {len(word_files)}")
    print(f"   Всего: {len(all_files)}")
    
    if not all_files:
        print("❌ Файлы не найдены")
        return
    
    # Инициализируем БД
    database.init_db()
    
    # Получаем или создаем предприятие
    enterprise = database.get_or_create_enterprise(enterprise_name)
    print(f"\n🏢 Предприятие: {enterprise['name']} (ID: {enterprise['id']})")
    
    # Проверяем текущее состояние БД
    with database.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM uploads WHERE enterprise_id = ?", (enterprise["id"],))
        existing_count = cursor.fetchone()[0]
    
    print(f"📊 Файлов в БД для этого предприятия: {existing_count}")
    
    # Статистика
    stats = {
        "total": len(all_files),
        "processed": 0,
        "success": 0,
        "error": 0,
        "skipped": 0,
        "with_routing_map": 0,
        "errors": []
    }
    
    # INBOX_DIR для копирования файлов (используем тот же путь, что и в main.py)
    INBOX_DIR = os.getenv("INBOX_DIR", "/data/inbox")
    if not os.path.exists(INBOX_DIR):
        # Если папка не существует, создаем локальную
        INBOX_DIR = os.path.join(os.getcwd(), "data", "inbox")
    os.makedirs(INBOX_DIR, exist_ok=True)
    
    print(f"\n📂 INBOX_DIR: {INBOX_DIR}")
    print(f"\n{'=' * 80}")
    print("🔄 НАЧАЛО ОБРАБОТКИ")
    print(f"{'=' * 80}\n")
    
    router = IntelligentRouter()
    
    for idx, file_path in enumerate(all_files, 1):
        filename = file_path.name
        print(f"\n[{idx}/{len(all_files)}] 📄 Обработка: {filename}")
        print("-" * 80)
        
        try:
            # Генерируем batch_id
            from uuid import uuid4
            batch_id = str(uuid4())
            
            # Копируем файл в INBOX_DIR
            dst = os.path.join(INBOX_DIR, f"{batch_id}__{filename}")
            import shutil
            shutil.copy2(file_path, dst)
            print(f"   ✅ Файл скопирован: {dst}")
            
            # Парсинг
            print(f"   📄 Парсинг файла...")
            parsing_result = parse_file(dst, batch_id=batch_id)
            
            if not parsing_result or not parsing_result.get("parsed"):
                print(f"   ⚠️  Файл не был распарсен полностью")
                parsing_result = parsing_result or {}
            
            # Intelligent Router анализ
            print(f"   🧠 Анализ Intelligent Router...")
            file_type_label = "Excel" if filename.lower().endswith(('.xlsx', '.xlsm', '.xls')) else "Word"
            raw_json_for_routing = {
                "file_type": file_type_label.lower(),
                "parsing": parsing_result if parsing_result.get("parsed") else None,
            }
            
            routing_map = router.analyze_file(
                file_path=dst,
                filename=filename,
                raw_json=raw_json_for_routing if parsing_result.get("parsed") else None,
                fast_mode=True
            )
            
            confidence = routing_map.get("analysis", {}).get("confidence", 0.0)
            if confidence < 0.7:
                routing_map = router.analyze_file(
                    file_path=dst,
                    filename=filename,
                    raw_json=raw_json_for_routing if parsing_result.get("parsed") else None,
                    fast_mode=False
                )
                confidence = routing_map.get("analysis", {}).get("confidence", 0.0)
            
            analysis = routing_map.get("analysis", {})
            routing = routing_map.get("routing", {})
            
            print(f"   📊 Результаты:")
            print(f"      Тип документа: {analysis.get('document_type', 'unknown')}")
            print(f"      Тип ресурса: {analysis.get('resource_type', 'unknown')}")
            print(f"      Уверенность: {confidence:.2%}")
            
            # Сохранение в БД
            print(f"   💾 Сохранение в БД...")
            status = "success" if parsing_result.get("parsed") else "partial"
            file_size = os.path.getsize(dst)
            
            # Вычисляем hash
            import hashlib
            file_hash = hashlib.sha1()
            with open(dst, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    file_hash.update(chunk)
            file_digest = file_hash.hexdigest()
            
            # Проверяем дубликат
            existing_upload = database.find_duplicate_upload(
                enterprise_id=enterprise["id"],
                filename=filename,
                file_size=file_size,
                file_hash=file_digest,
            )
            
            if existing_upload and system_mode != "debug":
                # В production режиме пропускаем дубликаты
                print(f"   ⏭️  Дубликат найден, пропускаем (hash совпадает)")
                stats["skipped"] += 1
                os.remove(dst)
                continue
            
            if existing_upload and system_mode == "debug":
                # В debug режиме удаляем старую запись
                existing_batch_id = existing_upload["batch_id"]
                database.delete_upload_by_batch_id(existing_batch_id)
                print(f"   🔄 Дубликат найден, удаляем старую запись (debug режим)")
            
            # Создаем parsing_summary
            parsing_summary = {
                "file_type": file_type_label,
                "parsed": parsing_result.get("parsed", False),
            }
            
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
                stats["with_routing_map"] += 1
            
            # Сохраняем в uploads
            database.create_upload(
                batch_id=batch_id,
                enterprise_id=enterprise["id"],
                filename=filename,
                file_type=file_type_label,
                file_size=file_size,
                status=status,
                parsing_summary=parsing_summary,
                file_hash=file_digest,
                file_mtime=os.path.getmtime(dst),
            )
            print(f"   ✅ Запись создана в uploads (batch_id: {batch_id})")
            
            # Сохраняем в parsed_data
            if parsing_result:
                editable_text = safe_json_dumps(parsing_result, ensure_ascii=False, indent=2)
                database.save_parsed_content(
                    batch_id=batch_id,
                    raw_json=parsing_result,
                    editable_text=editable_text
                )
                print(f"   ✅ Данные парсинга сохранены в parsed_data")
            
            stats["processed"] += 1
            stats["success"] += 1
            
            # Проверяем, что файл действительно в БД
            check_record = database.get_upload_by_batch(batch_id)
            if check_record:
                print(f"   ✅ Проверка: файл найден в БД")
            else:
                print(f"   ❌ ОШИБКА: файл НЕ найден в БД после сохранения!")
                stats["errors"].append(f"{filename}: не найден в БД после сохранения")
                stats["error"] += 1
            
        except Exception as e:
            print(f"   ❌ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
            stats["error"] += 1
            stats["errors"].append(f"{filename}: {str(e)}")
            stats["processed"] += 1
    
    # Итоговая статистика
    print(f"\n{'=' * 80}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print(f"{'=' * 80}")
    print(f"\n📁 Всего файлов: {stats['total']}")
    print(f"✅ Успешно обработано: {stats['success']}")
    print(f"❌ Ошибок: {stats['error']}")
    print(f"⏭️  Пропущено (дубликаты): {stats['skipped']}")
    print(f"🧠 С routing_map: {stats['with_routing_map']}")
    
    # Проверяем финальное состояние БД
    with database.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM uploads WHERE enterprise_id = ?", (enterprise["id"],))
        final_count = cursor.fetchone()[0]
    
    print(f"\n📊 Файлов в БД после обработки: {final_count}")
    print(f"📈 Добавлено новых: {final_count - existing_count}")
    
    if stats["errors"]:
        print(f"\n❌ ОШИБКИ:")
        for error in stats["errors"][:10]:  # Показываем первые 10
            print(f"   - {error}")
        if len(stats["errors"]) > 10:
            print(f"   ... и еще {len(stats['errors']) - 10} ошибок")
    
    print(f"\n{'=' * 80}")
    print("✅ Обработка завершена")
    print(f"{'=' * 80}")
    
    return stats


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python tools/batch_upload_from_folder.py <путь_к_папке> [предприятие] [режим]")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    enterprise_name = sys.argv[2] if len(sys.argv) > 2 else "Navoiy IES"
    system_mode = sys.argv[3] if len(sys.argv) > 3 else "debug"
    
    stats = batch_upload_from_folder(folder_path, enterprise_name, system_mode)
    
    if stats["error"] > 0:
        sys.exit(1)


