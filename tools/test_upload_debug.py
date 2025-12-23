"""
Диагностика загрузки файла - проверка всех этапов
"""
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

import database
from file_parser import parse_file
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_upload_small_file():
    """Тестирует загрузку маленького файла"""
    
    print("=" * 80)
    print("🔍 ДИАГНОСТИКА ЗАГРУЗКИ ФАЙЛА")
    print("=" * 80)
    
    # 1. Проверка БД
    print("\n1️⃣ Проверка базы данных...")
    try:
        database.init_db()
        print("   ✅ БД инициализирована")
    except Exception as e:
        print(f"   ❌ Ошибка БД: {e}")
        return
    
    # 2. Проверка INBOX_DIR
    print("\n2️⃣ Проверка INBOX_DIR...")
    INBOX_DIR = os.getenv("INBOX_DIR", "/data/inbox")
    if not os.path.exists(INBOX_DIR):
        INBOX_DIR = os.path.join(os.getcwd(), "data", "inbox")
        os.makedirs(INBOX_DIR, exist_ok=True)
    print(f"   ✅ INBOX_DIR: {INBOX_DIR}")
    print(f"   ✅ Существует: {os.path.exists(INBOX_DIR)}")
    print(f"   ✅ Доступен для записи: {os.access(INBOX_DIR, os.W_OK)}")
    
    # 3. Поиск тестового файла
    print("\n3️⃣ Поиск тестового файла...")
    test_paths = [
        r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX",
        INBOX_DIR,
        os.getcwd(),
    ]
    
    test_file = None
    for test_path in test_paths:
        if not os.path.exists(test_path):
            continue
        files = list(Path(test_path).glob("*.xlsx")) + list(Path(test_path).glob("*.docx"))
        if files:
            # Берем самый маленький файл
            test_file = min(files, key=lambda f: f.stat().st_size)
            print(f"   ✅ Найден файл: {test_file}")
            print(f"   📊 Размер: {test_file.stat().st_size / 1024:.2f} KB")
            break
    
    if not test_file:
        print("   ❌ Тестовый файл не найден")
        print("   💡 Создайте маленький Excel или Word файл для теста")
        return
    
    # 4. Тест парсинга
    print("\n4️⃣ Тест парсинга файла...")
    try:
        from uuid import uuid4
        batch_id = str(uuid4())
        
        # Копируем файл в INBOX_DIR
        import shutil
        dst = os.path.join(INBOX_DIR, f"{batch_id}__{test_file.name}")
        shutil.copy2(test_file, dst)
        print(f"   ✅ Файл скопирован: {dst}")
        
        # Парсинг
        print(f"   📄 Начало парсинга...")
        parsing_result = parse_file(dst, batch_id=batch_id)
        
        if parsing_result and parsing_result.get("parsed"):
            print(f"   ✅ Парсинг успешен")
            print(f"   📊 Тип файла: {parsing_result.get('file_type', 'unknown')}")
        else:
            print(f"   ⚠️  Парсинг не завершен полностью")
            print(f"   📊 Результат: {parsing_result}")
        
    except Exception as e:
        print(f"   ❌ Ошибка парсинга: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. Тест сохранения в БД
    print("\n5️⃣ Тест сохранения в БД...")
    try:
        enterprise = database.get_or_create_enterprise("Navoiy IES")
        print(f"   ✅ Предприятие: {enterprise['name']} (ID: {enterprise['id']})")
        
        file_size = os.path.getsize(dst)
        import hashlib
        file_hash = hashlib.sha1()
        with open(dst, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                file_hash.update(chunk)
        file_digest = file_hash.hexdigest()
        
        parsing_summary = {
            "file_type": "Excel" if test_file.suffix == ".xlsx" else "Word",
            "parsed": parsing_result.get("parsed", False) if parsing_result else False,
        }
        
        database.create_upload(
            batch_id=batch_id,
            enterprise_id=enterprise["id"],
            filename=test_file.name,
            file_type="Excel" if test_file.suffix == ".xlsx" else "Word",
            file_size=file_size,
            status="success" if parsing_result and parsing_result.get("parsed") else "partial",
            parsing_summary=parsing_summary,
            file_hash=file_digest,
            file_mtime=os.path.getmtime(dst),
        )
        print(f"   ✅ Запись создана в uploads (batch_id: {batch_id})")
        
        # Проверяем, что запись есть
        check_record = database.get_upload_by_batch(batch_id)
        if check_record:
            print(f"   ✅ Проверка: файл найден в БД")
        else:
            print(f"   ❌ ОШИБКА: файл НЕ найден в БД после сохранения!")
        
    except Exception as e:
        print(f"   ❌ Ошибка сохранения в БД: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 80)
    print(f"\n📋 Результат:")
    print(f"   Файл: {test_file.name}")
    print(f"   Batch ID: {batch_id}")
    print(f"   Статус: {'✅ Успешно' if parsing_result and parsing_result.get('parsed') else '⚠️ Частично'}")
    print(f"\n💡 Если все этапы прошли успешно, проблема может быть в:")
    print(f"   - Веб-сервере (проверьте, что он запущен)")
    print(f"   - CORS настройках")
    print(f"   - JavaScript ошибках в браузере (откройте консоль F12)")

if __name__ == "__main__":
    test_upload_small_file()

