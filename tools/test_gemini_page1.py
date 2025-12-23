"""Тест Gemini Vision OCR на странице 1"""
import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from gemini_vision_ocr import extract_with_gemini_vision
from pdf2image import convert_from_path

PDF_FILE = r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\CamScanner 17-04-2025 15.17.pdf"
OUTPUT_FILE = Path(__file__).parent / "gemini_test_page1.json"

print("=" * 80)
print("БЛОК 3: ТЕСТ GEMINI VISION OCR НА СТРАНИЦЕ 1")
print("=" * 80)
print()

# Шаг 1: Конвертация страницы 1 в изображение
print("ШАГ 1: Конвертация страницы 1 в изображение...")
try:
    poppler_paths = [
        r"C:\poppler\Library\bin",
        r"C:\poppler\bin",
    ]
    poppler_path = None
    for path in poppler_paths:
        if Path(path).exists() and (Path(path) / "pdftoppm.exe").exists():
            poppler_path = path
            break
    
    if poppler_path:
        import os
        current_path = os.environ.get("PATH", "")
        if poppler_path not in current_path:
            os.environ["PATH"] = poppler_path + os.pathsep + current_path
    
    images = convert_from_path(PDF_FILE, dpi=300, first_page=1, last_page=1, poppler_path=poppler_path)
    
    if not images:
        print("❌ Не удалось извлечь страницу")
        sys.exit(1)
    
    image = images[0]
    image_path = Path(__file__).parent / "page1_temp.png"
    image.save(image_path)
    print(f"✅ Страница 1 извлечена: {image.size[0]}x{image.size[1]} пикселей")
    print(f"   Сохранено: {image_path}")
    print()
except Exception as e:
    print(f"❌ Ошибка конвертации: {e}")
    sys.exit(1)

# Шаг 2: Вызов Gemini Vision OCR
print("ШАГ 2: Вызов extract_with_gemini_vision()...")
start_time = time.time()

try:
    result = extract_with_gemini_vision(str(image_path))
    elapsed_time = time.time() - start_time
    
    print(f"✅ OCR завершен за {elapsed_time:.2f} секунд")
    print()
except Exception as e:
    print(f"❌ Ошибка OCR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Шаг 3: Сохранение результата
print("ШАГ 3: Сохранение результата...")
try:
    output_data = {
        "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source_file": PDF_FILE,
        "page": 1,
        "processing_time_sec": round(elapsed_time, 2),
        "result": result
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ Результат сохранен: {OUTPUT_FILE}")
    print()
except Exception as e:
    print(f"❌ Ошибка сохранения: {e}")
    sys.exit(1)

# Отчет
print("=" * 80)
print("РЕЗУЛЬТАТЫ ТЕСТА")
print("=" * 80)
print(f"Успешно: {'Да' if not result.get('error') else 'Нет'}")
print(f"Символов распознано: {len(result.get('text', ''))}")
print(f"Таблиц найдено: {len(result.get('tables', []))}")
print(f"Время обработки: {elapsed_time:.2f} сек")
print()

if result.get('error'):
    print(f"⚠️  Ошибка: {result.get('error')}")
else:
    print("✅ Тест пройден успешно!")

# Удаляем временный файл
try:
    image_path.unlink()
except:
    pass

