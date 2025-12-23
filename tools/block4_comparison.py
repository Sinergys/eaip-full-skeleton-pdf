"""БЛОК 4: Сравнение Gemini vs Tesseract на странице 1"""
import sys
import time
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest"))
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from gemini_vision_ocr import extract_with_gemini_vision
from file_parser import apply_ocr_to_pdf
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

PDF_FILE = r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\CamScanner 17-04-2025 15.17.pdf"
OUTPUT_FILE = Path(__file__).parent / "block4_comparison_result.json"

print("=" * 80)
print("БЛОК 4: СРАВНЕНИЕ GEMINI VS TESSERACT")
print("=" * 80)
print()

# Извлечение страницы 1
print("Извлечение страницы 1...")
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
image = images[0]
image_path = Path(__file__).parent / "page1_comparison_temp.png"
image.save(image_path)
print(f"✅ Страница 1 извлечена: {image.size[0]}x{image.size[1]} пикселей")
print()

# Тест 1: Tesseract OCR
print("=" * 80)
print("ТЕСТ 1: TESSERACT OCR")
print("=" * 80)

start_time = time.time()

# Автоопределение поворота через OSD
try:
    osd = pytesseract.image_to_osd(image)
    angle_match = re.search(r'(?<=Rotate: )\d+', osd)
    if angle_match:
        angle = int(angle_match.group(0))
        if angle != 0:
            image = image.rotate(-angle, expand=True)
            print(f"   Поворот применен: {angle}°")
except:
    pass

# Предобработка
from file_parser import preprocess_image_for_ocr
enhanced_image = preprocess_image_for_ocr(image)

# OCR
tesseract_text = pytesseract.image_to_string(enhanced_image, lang='rus+eng', config='--psm 6 --oem 3')
tesseract_time = time.time() - start_time

# Поиск таблиц
from ocr_table_extractor import extract_tables_from_ocr_text
tesseract_tables = extract_tables_from_ocr_text(tesseract_text, page_num=1)

print(f"Время обработки: {tesseract_time:.2f} сек")
print(f"Символов распознано: {len(tesseract_text)}")
print(f"Таблиц найдено: {len(tesseract_tables)}")
print()

# Тест 2: Gemini Vision OCR
print("=" * 80)
print("ТЕСТ 2: GEMINI VISION OCR")
print("=" * 80)

start_time = time.time()
gemini_result = extract_with_gemini_vision(str(image_path))
gemini_time = time.time() - start_time

gemini_text = gemini_result.get('text', '')
gemini_tables = gemini_result.get('tables', [])

print(f"Время обработки: {gemini_time:.2f} сек")
print(f"Символов распознано: {len(gemini_text)}")
print(f"Таблиц найдено: {len(gemini_tables)}")
print()

# Сравнение качества текста
print("=" * 80)
print("СРАВНЕНИЕ КАЧЕСТВА ТЕКСТА")
print("=" * 80)

# Простые метрики
tesseract_readable = len([c for c in tesseract_text if c.isalnum() or c.isspace()])
gemini_readable = len([c for c in gemini_text if c.isalnum() or c.isspace()])

print(f"Tesseract:")
print(f"  Всего символов: {len(tesseract_text)}")
print(f"  Читаемых символов: {tesseract_readable} ({tesseract_readable/len(tesseract_text)*100:.1f}%)")
print(f"  Первые 200 символов:")
print(f"    {tesseract_text[:200].replace(chr(10), ' ')}")
print()

print(f"Gemini:")
print(f"  Всего символов: {len(gemini_text)}")
print(f"  Читаемых символов: {gemini_readable} ({gemini_readable/len(gemini_text)*100:.1f}%)")
print(f"  Первые 200 символов:")
print(f"    {gemini_text[:200].replace(chr(10), ' ')}")
print()

# Сравнение таблиц
print("=" * 80)
print("СРАВНЕНИЕ ТАБЛИЦ")
print("=" * 80)

print(f"Tesseract: найдено {len(tesseract_tables)} таблиц")
if tesseract_tables:
    t = tesseract_tables[0]
    print(f"  Строк: {t.get('row_count', 0)}, Колонок: {t.get('col_count', 0)}")
    print(f"  Метод: {t.get('method', 'unknown')}")

print(f"Gemini: найдено {len(gemini_tables)} таблиц")
if gemini_tables:
    t = gemini_tables[0]
    rows = t.get('rows', [])
    print(f"  Строк: {len(rows)}, Колонок: {len(rows[0]) if rows else 0}")
    print(f"  Есть заголовки: {'headers' in t}")

print()

# Итоговое сравнение
print("=" * 80)
print("ИТОГОВОЕ СРАВНЕНИЕ")
print("=" * 80)

comparison = {
    "tesseract": {
        "time_sec": round(tesseract_time, 2),
        "characters": len(tesseract_text),
        "readable_chars": tesseract_readable,
        "readable_percent": round(tesseract_readable/len(tesseract_text)*100, 1) if tesseract_text else 0,
        "tables_count": len(tesseract_tables),
        "tables": tesseract_tables
    },
    "gemini": {
        "time_sec": round(gemini_time, 2),
        "characters": len(gemini_text),
        "readable_chars": gemini_readable,
        "readable_percent": round(gemini_readable/len(gemini_text)*100, 1) if gemini_text else 0,
        "tables_count": len(gemini_tables),
        "tables": gemini_tables
    }
}

# Определение победителя
winner = "Равны"
if len(gemini_text) > len(tesseract_text) * 1.2:
    winner = "Gemini"
elif len(tesseract_text) > len(gemini_text) * 1.2:
    winner = "Tesseract"
elif gemini_readable > tesseract_readable * 1.2:
    winner = "Gemini"
elif tesseract_readable > gemini_readable * 1.2:
    winner = "Tesseract"
elif len(gemini_tables) > len(tesseract_tables):
    winner = "Gemini"
elif len(tesseract_tables) > len(gemini_tables):
    winner = "Tesseract"

print(f"Победитель: {winner}")
print()
print(f"Время: Gemini {gemini_time:.2f}с vs Tesseract {tesseract_time:.2f}с")
print(f"Символов: Gemini {len(gemini_text)} vs Tesseract {len(tesseract_text)}")
print(f"Читаемость: Gemini {comparison['gemini']['readable_percent']:.1f}% vs Tesseract {comparison['tesseract']['readable_percent']:.1f}%")
print(f"Таблицы: Gemini {len(gemini_tables)} vs Tesseract {len(tesseract_tables)}")
print()

# Сохранение результатов
comparison["winner"] = winner
comparison["test_date"] = time.strftime("%Y-%m-%d %H:%M:%S")
comparison["source_file"] = PDF_FILE
comparison["page"] = 1

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(comparison, f, ensure_ascii=False, indent=2, default=str)

print(f"✅ Результаты сохранены: {OUTPUT_FILE}")

# Удаляем временный файл
try:
    image_path.unlink()
except:
    pass

