"""
Тестовый скрипт для проверки загрузки PDF скана и распознавания через OCR
"""
import requests
import sys
import os

# URL сервиса ingest
INGEST_URL = "http://localhost:8001"

def test_health():
    """Проверка доступности сервиса"""
    try:
        response = requests.get(f"{INGEST_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Сервис ingest доступен")
            print(f"   Ответ: {response.json()}")
            return True
        else:
            print(f"❌ Сервис вернул код {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к сервису ingest")
        print("   Убедитесь, что сервис запущен: docker compose up -d ingest")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке сервиса: {e}")
        return False

def upload_pdf(pdf_path: str):
    """Загрузка PDF файла и проверка OCR"""
    if not os.path.exists(pdf_path):
        print(f"❌ Файл не найден: {pdf_path}")
        return None
    
    print(f"\n📄 Загружаю файл: {pdf_path}")
    print(f"   Размер: {os.path.getsize(pdf_path) / 1024:.2f} КБ")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            response = requests.post(
                f"{INGEST_URL}/web/upload",
                files=files,
                timeout=300  # OCR может занять время для больших файлов (5 минут)
            )
        
        if response.status_code == 200:
            print("✅ Файл успешно загружен")
            return response.json()
        else:
            print(f"❌ Ошибка загрузки: {response.status_code}")
            print(f"   Ответ: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при загрузке файла: {e}")
        return None

def check_parsing_results(batch_id: str):
    """Проверка результатов парсинга"""
    print(f"\n🔍 Проверяю результаты парсинга для batch_id: {batch_id}")
    
    try:
        # Получаем полные результаты
        response = requests.get(f"{INGEST_URL}/ingest/parse/{batch_id}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("✅ Результаты парсинга получены")
            
            # Проверяем структуру данных
            parsing = data.get("parsing", {})
            parsed_data = parsing.get("data", {})
            
            print("\n📊 Статистика:")
            print(f"   Тип файла: {parsing.get('file_type', 'unknown')}")
            print(f"   Распознано: {'✅ Да' if parsing.get('parsed') else '❌ Нет'}")
            
            if parsing.get('file_type') == 'pdf':
                pdf_data = parsed_data
                pages = pdf_data.get("metadata", {}).get("num_pages", 0)
                chars = pdf_data.get("total_characters", 0)
                tables = pdf_data.get("total_tables", 0)
                ocr_used = pdf_data.get("ocr_used", False)
                
                print(f"   Страниц: {pages}")
                print(f"   Символов: {chars}")
                print(f"   Таблиц: {tables}")
                print(f"   OCR использован: {'✅ Да' if ocr_used else '❌ Нет'}")
                
                if ocr_used:
                    print("\n🎉 OCR успешно применен!")
                    text_preview = pdf_data.get("text", "")[:200]
                    if text_preview:
                        print("\n📝 Превью текста (первые 200 символов):")
                        print(f"   {text_preview}...")
                else:
                    text_preview = pdf_data.get("text", "")[:200]
                    if text_preview:
                        print("\n📝 Превью текста (первые 200 символов):")
                        print(f"   {text_preview}...")
                    else:
                        print("\n⚠️ Текст не извлечен. Возможно, документ требует OCR.")
                        print(f"   Среднее символов на страницу: {chars / pages if pages > 0 else 0:.0f}")
            
            return data
        else:
            print(f"❌ Ошибка получения результатов: {response.status_code}")
            print(f"   Ответ: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при проверке результатов: {e}")
        return None

def get_summary(batch_id: str):
    """Получение краткой сводки"""
    try:
        response = requests.get(f"{INGEST_URL}/ingest/parse/{batch_id}/summary", timeout=10)
        if response.status_code == 200:
            summary = response.json()
            print("\n📋 Краткая сводка:")
            print(f"   Файл: {summary.get('filename', 'unknown')}")
            print(f"   Статус: {summary.get('status', 'unknown')}")
            if summary.get('file_type') == 'pdf':
                print(f"   Страниц: {summary.get('pages', 0)}")
                print(f"   Символов: {summary.get('total_characters', 0)}")
            return summary
        else:
            print(f"⚠️ Не удалось получить сводку: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Ошибка получения сводки: {e}")
        return None

def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("🧪 ТЕСТ ЗАГРУЗКИ PDF И РАСПОЗНАВАНИЯ OCR")
    print("=" * 60)
    
    # Проверка доступности сервиса
    if not test_health():
        sys.exit(1)
    
    # Поиск тестового PDF файла
    test_files = [
        "infra/passport_demo1.pdf",
        "infra/passport_demo1_full.pdf",
        "infra/data/inbox/passport_demo1.pdf"
    ]
    
    # Ищем первый доступный файл
    pdf_path = None
    for path in test_files:
        if os.path.exists(path):
            pdf_path = path
            break
    
    # Если файл передан как аргумент
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    if not pdf_path or not os.path.exists(pdf_path):
        print("\n❌ Тестовый PDF файл не найден")
        print("   Использование: python test_pdf_ocr.py [путь_к_pdf_файлу]")
        print("\n   Искал файлы:")
        for path in test_files:
            print(f"   - {path}")
        sys.exit(1)
    
    # Загружаем файл
    upload_result = upload_pdf(pdf_path)
    if not upload_result:
        sys.exit(1)
    
    batch_id = upload_result.get("batch_id")
    if not batch_id:
        print("❌ Batch ID не получен из ответа")
        print(f"   Ответ: {upload_result}")
        sys.exit(1)
    
    print(f"\n✅ Batch ID: {batch_id}")
    
    # Проверяем результаты парсинга
    results = check_parsing_results(batch_id)
    
    # Получаем сводку
    get_summary(batch_id)
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)
    print(f"\n🌐 Веб-интерфейс: {INGEST_URL}/web/upload")
    print(f"📚 API документация: {INGEST_URL}/docs")
    
    if results:
        print("\n💡 Для просмотра полных результатов:")
        print(f"   curl {INGEST_URL}/ingest/parse/{batch_id}")

if __name__ == "__main__":
    main()

