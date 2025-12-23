"""Полный тест Gemini Vision OCR на всех 4 страницах"""
import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from gemini_vision_ocr import extract_with_gemini_vision
from pdf2image import convert_from_path

PDF_FILE = r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\CamScanner 17-04-2025 15.17.pdf"
OUTPUT_FILE = Path(__file__).parent / "gemini_full_test_4pages.json"

print("=" * 80)
print("ПОЛНЫЙ ТЕСТ GEMINI VISION OCR НА 4 СТРАНИЦАХ")
print("=" * 80)
print()

# Извлечение всех страниц
print("ШАГ 1: Извлечение всех страниц...")
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

images = convert_from_path(PDF_FILE, dpi=300, poppler_path=poppler_path)
print(f"✅ Извлечено {len(images)} страниц")
print()

# Обработка каждой страницы
print("ШАГ 2: Обработка страниц через Gemini Vision...")
results = []
total_chars = 0
total_tables = 0
total_time = 0
errors = []

for i, image in enumerate(images, 1):
    print(f"Страница {i}/{len(images)}...", end=" ", flush=True)
    
    # Сохраняем временное изображение
    temp_path = Path(__file__).parent / f"page{i}_temp.png"
    image.save(temp_path)
    
    # Обработка через Gemini
    start_time = time.time()
    try:
        result = extract_with_gemini_vision(str(temp_path))
        elapsed = time.time() - start_time
        total_time += elapsed
        
        page_text = result.get('text', '')
        page_tables = result.get('tables', [])
        
        chars = len(page_text)
        tables_count = len(page_tables)
        
        total_chars += chars
        total_tables += tables_count
        
        results.append({
            'page': i,
            'characters': chars,
            'tables_count': tables_count,
            'time_sec': round(elapsed, 2),
            'text_preview': page_text[:200] if page_text else '',
            'tables': page_tables,
            'error': result.get('error'),
            'confidence': result.get('confidence', 0.0)
        })
        
        print(f"✅ {chars} символов, {tables_count} таблиц, {elapsed:.1f}с")
        
    except Exception as e:
        elapsed = time.time() - start_time
        total_time += elapsed
        errors.append(f"Страница {i}: {str(e)}")
        results.append({
            'page': i,
            'characters': 0,
            'tables_count': 0,
            'time_sec': round(elapsed, 2),
            'error': str(e)
        })
        print(f"❌ Ошибка: {e}")
    
    # Удаляем временный файл
    try:
        temp_path.unlink()
    except:
        pass

print()

# Агрегация результатов
print("ШАГ 3: Агрегация результатов...")
output_data = {
    "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
    "source_file": PDF_FILE,
    "total_pages": len(images),
    "pages_processed": len([r for r in results if not r.get('error')]),
    "statistics": {
        "total_characters": total_chars,
        "total_tables": total_tables,
        "total_time_sec": round(total_time, 2),
        "avg_time_per_page": round(total_time / len(images), 2),
        "avg_characters_per_page": round(total_chars / len(images), 0) if images else 0
    },
    "pages": results,
    "errors": errors
}

# Сохранение
print("ШАГ 4: Сохранение результатов...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)

print(f"✅ Результаты сохранены: {OUTPUT_FILE}")
print()

# Отчет
print("=" * 80)
print("ИТОГОВЫЙ ОТЧЕТ")
print("=" * 80)
print(f"Страниц обработано: {output_data['pages_processed']}/{output_data['total_pages']}")
print(f"Символов: {total_chars}")
print(f"Таблиц: {total_tables}")
print(f"Время: {total_time:.2f} сек (среднее: {output_data['statistics']['avg_time_per_page']:.2f} сек/страница)")
if errors:
    print(f"Проблемы: {len(errors)}")
    for err in errors:
        print(f"  - {err}")
else:
    print("Проблемы: Нет")
print("=" * 80)
