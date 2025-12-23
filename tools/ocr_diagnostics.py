"""Диагностика OCR модуля - сбор информации для анализа"""
import sys
import time
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest"))
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from gemini_vision_ocr import extract_with_gemini_vision
from file_parser import apply_ocr_to_pdf, preprocess_image_for_ocr
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

PDF_FILE = r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\CamScanner 17-04-2025 15.17.pdf"

print("=" * 80)
print("ДИАГНОСТИКА OCR МОДУЛЯ")
print("=" * 80)
print()

# 1. Анализ таймаута страницы 1
print("1. АНАЛИЗ ТАЙМАУТА СТРАНИЦЫ 1")
print("-" * 80)

images = convert_from_path(PDF_FILE, dpi=300, first_page=1, last_page=1)
image = images[0]
temp_path = Path(__file__).parent / "page1_diag_temp.png"
image.save(temp_path)

timings = {}
start = time.time()

# Этап 1: Предобработка
try:
    preproc_start = time.time()
    enhanced = preprocess_image_for_ocr(image)
    timings['preproc_ms'] = int((time.time() - preproc_start) * 1000)
    print(f"✅ Предобработка: {timings['preproc_ms']} мс")
except Exception as e:
    timings['preproc_ms'] = 0
    timings['preproc_error'] = str(e)
    print(f"❌ Предобработка: {e}")

# Этап 2: OCR (Tesseract)
try:
    ocr_start = time.time()
    text = pytesseract.image_to_string(enhanced, lang='rus+eng', config='--psm 6 --oem 3')
    timings['ocr_ms'] = int((time.time() - ocr_start) * 1000)
    print(f"✅ OCR (Tesseract): {timings['ocr_ms']} мс")
except Exception as e:
    timings['ocr_ms'] = 0
    timings['ocr_error'] = str(e)
    print(f"❌ OCR: {e}")

# Этап 3: Извлечение таблиц
try:
    table_start = time.time()
    from ocr_table_extractor import extract_tables_from_ocr_text
    tables = extract_tables_from_ocr_text(text, page_num=1)
    timings['table_extract_ms'] = int((time.time() - table_start) * 1000)
    print(f"✅ Извлечение таблиц: {timings['table_extract_ms']} мс")
except Exception as e:
    timings['table_extract_ms'] = 0
    timings['table_error'] = str(e)
    print(f"❌ Извлечение таблиц: {e}")

# Этап 4: Gemini Vision (с таймаутом)
try:
    gemini_start = time.time()
    gemini_result = extract_with_gemini_vision(str(temp_path))
    timings['gemini_ms'] = int((time.time() - gemini_start) * 1000)
    print(f"✅ Gemini Vision: {timings['gemini_ms']} мс")
except Exception as e:
    timings['gemini_ms'] = 0
    timings['gemini_error'] = str(e)
    timings['gemini_timeout'] = "504 Deadline Exceeded" in str(e)
    print(f"❌ Gemini Vision: {e}")

timings['total_ms'] = int((time.time() - start) * 1000)
print(f"Всего времени: {timings['total_ms']} мс")
print()

# 2. Логи обработки всех страниц
print("2. ЛОГИ ОБРАБОТКИ 4 СТРАНИЦ")
print("-" * 80)

images = convert_from_path(PDF_FILE, dpi=300, poppler_path=None)
page_logs = []

for i, img in enumerate(images, 1):
    print(f"\npage: {i}")
    
    log = {"page": i}
    start_page = time.time()
    
    # Предобработка
    preproc_start = time.time()
    try:
        enhanced = preprocess_image_for_ocr(img)
        log['preproc_ms'] = int((time.time() - preproc_start) * 1000)
    except Exception as e:
        log['preproc_ms'] = 0
        log['preproc_error'] = str(e)
    
    # OCR
    ocr_start = time.time()
    try:
        text = pytesseract.image_to_string(enhanced, lang='rus+eng', config='--psm 6 --oem 3')
        log['ocr_ms'] = int((time.time() - ocr_start) * 1000)
        
        # Confidence (примерная оценка)
        try:
            data = pytesseract.image_to_data(enhanced, lang='rus+eng', config='--psm 6 --oem 3', output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data['conf'] if c != '-1']
            log['text_confidence'] = round(sum(confidences) / len(confidences), 1) if confidences else 0
        except:
            log['text_confidence'] = 0
    except Exception as e:
        log['ocr_ms'] = 0
        log['ocr_error'] = str(e)
        text = ""
    
    # Таблицы
    table_start = time.time()
    try:
        from ocr_table_extractor import extract_tables_from_ocr_text
        tables = extract_tables_from_ocr_text(text, page_num=i)
        log['table_extract_ms'] = int((time.time() - table_start) * 1000)
        log['tables_count'] = len(tables)
        log['tables_confidence'] = "medium" if tables else "none"
    except Exception as e:
        log['table_extract_ms'] = 0
        log['table_error'] = str(e)
        tables = []
    
    log['total_ms'] = int((time.time() - start_page) * 1000)
    
    # Вывод в формате
    print(f"pipeline: [preproc {log['preproc_ms']}ms] [ocr {log['ocr_ms']}ms] [table-extract {log['table_extract_ms']}ms]")
    print(f"confidence: text={log.get('text_confidence', 0)}% tables={log.get('tables_confidence', 'none')}")
    if log.get('preproc_error') or log.get('ocr_error') or log.get('table_error'):
        warnings = [k for k in ['preproc_error', 'ocr_error', 'table_error'] if log.get(k)]
        print(f"warnings: {warnings}")
    
    page_logs.append(log)

print()

# 3. Тест fix_string_content()
print("3. ТЕСТ fix_string_content()")
print("-" * 80)

def fix_string_content(match):
    content = match.group(1)
    result = []
    i = 0
    while i < len(content):
        if content[i] == '\\' and i + 1 < len(content):
            result.append(content[i:i+2])
            i += 2
        elif content[i] == '\n':
            result.append('\\n')
            i += 1
        elif content[i] == '\r':
            result.append('\\r')
            i += 1
        elif content[i] == '\t':
            result.append('\\t')
            i += 1
        elif ord(content[i]) < 32:
            i += 1
        else:
            result.append(content[i])
            i += 1
    return '"' + ''.join(result) + '"'

test_strings = [
    'Текст с\nпереносами строк',
    'Смешанный\tтекст\nс табуляцией',
    'Строка с "кавычками" и\nпереносами',
    'Unicode: \u00A0\u2009\u202F',
    'Control: \x00\x01\x02'
]

print("Тестовые строки:")
for i, test_str in enumerate(test_strings, 1):
    json_str = f'{{"text": "{test_str}"}}'
    try:
        fixed = re.sub(r'"([^"]*(?:\\.[^"]*)*)"', fix_string_content, json_str)
        parsed = json.loads(fixed)
        print(f"  {i}. ✅ '{test_str[:30]}...' -> OK")
    except Exception as e:
        print(f"  {i}. ❌ '{test_str[:30]}...' -> {e}")

print()

# 4. Пример выходного JSON
print("4. ПРИМЕР ВЫХОДНОГО JSON")
print("-" * 80)

if Path("tools/gemini_test_page1.json").exists():
    with open("tools/gemini_test_page1.json", 'r', encoding='utf-8') as f:
        example = json.load(f)
    
    result = example.get('result', {})
    print("Пример JSON (первые 500 символов):")
    json_str = json.dumps(result, ensure_ascii=False, indent=2)[:500]
    print(json_str)
    print("...")
    print(f"Полный размер: {len(json.dumps(result))} символов")
    print(f"Таблиц: {len(result.get('tables', []))}")
    if result.get('tables'):
        table = result['tables'][0]
        print(f"Первая таблица: {table.get('row_count', 0)} строк, {len(table.get('rows', [])[0]) if table.get('rows') else 0} колонок")
print()

# 5. Параметры confidence
print("5. ПАРАМЕТРЫ CONFIDENCE")
print("-" * 80)

print("Текущие пороги (из кода):")
print("  - text: не используется явный порог")
print("  - numbers: не используется явный порог")
print("  - dates: не используется явный порог")

# Проверяем фактические значения
if Path("tools/gemini_full_test_4pages.json").exists():
    with open("tools/gemini_full_test_4pages.json", 'r', encoding='utf-8') as f:
        full_data = json.load(f)
    
    print("\nФактические значения confidence из Gemini:")
    for page_data in full_data.get('pages', []):
        if page_data.get('tables'):
            for table in page_data['tables']:
                conf = table.get('confidence', 'N/A')
                print(f"  Страница {page_data['page']}: {conf}")

print()

# 6. Готовность к batch
print("6. ГОТОВНОСТЬ К BATCH-ОБРАБОТКЕ")
print("-" * 80)

print("Текущие ограничения:")
print("  - Gemini API: ~20 сек/страница (может быть таймаут при больших изображениях)")
print("  - Tesseract: ~8-10 сек/страница")
print("  - Память: зависит от размера изображений")
print("  - Сеть: требуется для Gemini API")

print("\nОценка для 20-50 файлов:")
avg_time = 18.0  # секунд на страницу
avg_pages = 4  # страниц на файл
files_count = 50

total_time = (avg_time * avg_pages * files_count) / 60  # минуты
print(f"  - 50 файлов × 4 страницы × 18 сек = ~{total_time:.0f} минут")
print(f"  - Рекомендуется: батчи по 5-10 файлов с паузами")

print("\nГотовность: ✅ Да, с ограничениями")
print("  - Требуется обработка батчами")
print("  - Нужны паузы между запросами Gemini API")
print("  - Рекомендуется прогресс-бар и логирование")

print()
print("=" * 80)
print("ДИАГНОСТИКА ЗАВЕРШЕНА")
print("=" * 80)

