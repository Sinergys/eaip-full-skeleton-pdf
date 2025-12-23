"""
Тестовый скрипт для проверки загрузки изображений и распознавания через OCR
"""
import requests
import sys
import os
from pathlib import Path

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
        print("   Убедитесь, что сервис запущен на порту 8001")
        print("   Команда: cd eaip_full_skeleton/services/ingest && python -m uvicorn main:app --reload --port 8001")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке сервиса: {e}")
        return False


def upload_image(image_path: str, enterprise_name: str = "Test Enterprise", resource_type: str = "other"):
    """Загрузка изображения и проверка OCR"""
    if not os.path.exists(image_path):
        print(f"❌ Файл не найден: {image_path}")
        return None
    
    # Определяем MIME тип
    ext = Path(image_path).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png'
    }
    mime_type = mime_types.get(ext, 'image/jpeg')
    
    print(f"\n🖼️  Загружаю изображение: {image_path}")
    print(f"   Размер: {os.path.getsize(image_path) / 1024:.2f} КБ")
    print(f"   Тип: {ext}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, mime_type)}
            data = {
                'enterprise_name': enterprise_name,
                'resource_type': resource_type
            }
            response = requests.post(
                f"{INGEST_URL}/web/upload",
                files=files,
                data=data,
                timeout=120  # OCR может занять время (2 минуты)
            )
        
        if response.status_code == 200:
            print("✅ Изображение успешно загружено")
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
    try:
        response = requests.get(f"{INGEST_URL}/ingest/parse/{batch_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            parsing = data.get("parsing", {})
            
            if parsing.get("parsed"):
                print("\n✅ Файл успешно распознан")
                
                # Проверяем данные OCR
                parsed_data = parsing.get("data", {})
                ocr_used = parsed_data.get("ocr_used", False)
                char_count = parsed_data.get("char_count", 0)
                text = parsed_data.get("text", "")
                
                if ocr_used:
                    print("🔍 OCR: Использовано")
                    print(f"📊 Символов распознано: {char_count}")
                    
                    # Показываем превью текста
                    if text:
                        preview = text[:200].replace('\n', ' ')
                        print("\n📝 Превью текста (первые 200 символов):")
                        print(f"   {preview}...")
                    else:
                        print("⚠️  Текст не извлечен")
                else:
                    print("⚠️  OCR не использовался")
                    if char_count == 0:
                        print("   Возможно, OCR библиотеки не установлены или произошла ошибка")
                
                # Метаданные изображения
                image_size = parsed_data.get("image_size")
                image_mode = parsed_data.get("image_mode")
                if image_size:
                    print("\n🖼️  Метаданные изображения:")
                    print(f"   Размер: {image_size[0]}x{image_size[1]} пикселей")
                    print(f"   Режим: {image_mode}")
                
                return True
            else:
                print("\n❌ Файл не был распознан")
                error = parsing.get("data", {}).get("error") or parsing.get("data", {}).get("message")
                if error:
                    print(f"   Ошибка: {error}")
                return False
        else:
            print(f"❌ Ошибка получения результатов: {response.status_code}")
            print(f"   Ответ: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке результатов: {e}")
        return False


def get_summary(batch_id: str):
    """Получение краткой сводки"""
    try:
        response = requests.get(f"{INGEST_URL}/ingest/parse/{batch_id}/summary", timeout=10)
        if response.status_code == 200:
            summary = response.json()
            print("\n📊 Краткая сводка:")
            print(f"   Batch ID: {summary.get('batch_id')}")
            print(f"   Статус: {summary.get('status')}")
            print(f"   Файл: {summary.get('filename')}")
            print(f"   Тип: {summary.get('file_type')}")
            return summary
        else:
            print(f"⚠️  Не удалось получить сводку: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️  Ошибка получения сводки: {e}")
        return None


def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("🧪 ТЕСТ ЗАГРУЗКИ ИЗОБРАЖЕНИЙ И РАСПОЗНАВАНИЯ OCR")
    print("=" * 60)
    
    # Проверка доступности сервиса
    if not test_health():
        sys.exit(1)
    
    # Если файл передан как аргумент
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("\n❌ Не указан путь к изображению")
        print("   Использование: python test_image_ocr.py [путь_к_изображению]")
        print("\n   Поддерживаемые форматы: .jpg, .jpeg, .png")
        print("\n   Пример:")
        print("   python test_image_ocr.py test_image.jpg")
        sys.exit(1)
    
    if not os.path.exists(image_path):
        print(f"\n❌ Файл не найден: {image_path}")
        sys.exit(1)
    
    # Проверяем расширение
    ext = Path(image_path).suffix.lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        print(f"\n❌ Неподдерживаемый формат: {ext}")
        print("   Поддерживаются: .jpg, .jpeg, .png")
        sys.exit(1)
    
    # Загружаем файл
    upload_result = upload_image(image_path)
    if not upload_result:
        sys.exit(1)
    
    batch_id = upload_result.get("batch_id")
    if not batch_id:
        print("❌ Batch ID не получен из ответа")
        print(f"   Ответ: {upload_result}")
        sys.exit(1)
    
    print(f"\n✅ Batch ID: {batch_id}")
    
    # Проверяем результаты парсинга
    check_parsing_results(batch_id)
    
    # Получаем сводку
    get_summary(batch_id)
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)
    print(f"\n🌐 Веб-интерфейс: {INGEST_URL}/web/upload")
    print(f"📚 API документация: {INGEST_URL}/docs")
    print("\n💡 Совет: Вы также можете загрузить изображение через веб-интерфейс")


if __name__ == "__main__":
    main()

