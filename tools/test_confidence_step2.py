"""
Тест проверки confidence thresholds на 4 страницах (ШАГ 2)
"""
import sys
from pathlib import Path
from pdf2image import convert_from_path
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from gemini_vision_ocr import extract_with_gemini_vision

PDF_FILE = r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\CamScanner 17-04-2025 15.17.pdf"

print("=" * 80)
print("ТЕСТ CONFIDENCE THRESHOLDS НА 4 СТРАНИЦАХ (ШАГ 2)")
print("=" * 80)
print()

# Извлекаем страницы
print("ШАГ 1: Извлечение страниц...")
images = convert_from_path(PDF_FILE, dpi=300, poppler_path=None)
print(f"✅ Извлечено {len(images)} страниц")
print()

# Обрабатываем каждую страницу
results = []
low_confidence_count = 0

for i, img in enumerate(images, 1):
    print(f"Обработка страницы {i}/{len(images)}...")
    
    # Сохраняем временное изображение
    temp_path = Path(__file__).parent / f"page{i}_temp.png"
    img.save(temp_path)
    
    try:
        # Вызываем OCR
        result = extract_with_gemini_vision(str(temp_path), page_num=i)
        
        # Проверяем наличие validation_flag
        has_low_confidence = 'validation_flag' in result and 'low_confidence' in result.get('validation_flag', [])
        
        if has_low_confidence:
            low_confidence_count += 1
        
        results.append({
            "page": i,
            "confidence": result.get('confidence', 0.0),
            "has_validation_flag": 'validation_flag' in result,
            "validation_flags": result.get('validation_flag', []),
            "characters": len(result.get('text', '')),
            "tables_count": len(result.get('tables', []))
        })
        
        print(f"  ✅ Страница {i}: confidence={result.get('confidence', 0.0):.2f}, "
              f"символов={len(result.get('text', ''))}, "
              f"таблиц={len(result.get('tables', []))}, "
              f"validation_flag={'low_confidence' if has_low_confidence else 'none'}")
        
        # Удаляем временный файл
        temp_path.unlink()
        
    except Exception as e:
        print(f"  ❌ Ошибка на странице {i}: {e}")
        results.append({
            "page": i,
            "error": str(e)
        })

print()
print("=" * 80)
print("РЕЗУЛЬТАТЫ")
print("=" * 80)
print(f"Всего страниц: {len(results)}")
print(f"Страниц с low_confidence: {low_confidence_count}")
print()

# Сохраняем результаты
output_path = Path(__file__).parent / "step2_confidence_test.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({
        "test_date": "2025-11-29",
        "source_file": PDF_FILE,
        "total_pages": len(results),
        "low_confidence_count": low_confidence_count,
        "results": results
    }, f, ensure_ascii=False, indent=2)

print(f"✅ Результаты сохранены: {output_path}")

# Проверяем лог low_confidence
log_path = Path(__file__).parent.parent / "reports" / "ocr" / "low_confidence.log"
if log_path.exists():
    log_lines = log_path.read_text(encoding='utf-8').strip().split('\n')
    log_count = len([l for l in log_lines if l.strip()])
    print(f"✅ Записей в low_confidence.log: {log_count}")
else:
    print("⚠️  Файл low_confidence.log не найден")

print()
print("=" * 80)

