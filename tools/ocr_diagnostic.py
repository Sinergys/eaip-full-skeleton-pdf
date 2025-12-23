"""
СРОЧНАЯ ДИАГНОСТИКА OCR
Проверка доступных языков и простой тест без предобработки
"""
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    import os
    HAS_OCR = True
    
    # Автоматическое определение пути к Tesseract
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Tesseract-OCR\tesseract.exe",
    ]
    
    current_cmd = pytesseract.pytesseract.tesseract_cmd
    if not current_cmd or current_cmd == "tesseract" or not os.path.exists(current_cmd):
        for tesseract_path in tesseract_paths:
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                print(f"✅ Автоматически найден Tesseract: {tesseract_path}")
                break
        else:
            print("⚠️  Tesseract не найден в стандартных путях")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    HAS_OCR = False
    sys.exit(1)

print("=" * 80)
print("ДИАГНОСТИКА OCR")
print("=" * 80)

# ШАГ 1: Проверка языков Tesseract
print("\nШАГ 1: Проверка доступных языков Tesseract")
print("-" * 80)

tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
print(f"Путь к Tesseract: {tesseract_cmd}")

try:
    result = subprocess.run(
        [tesseract_cmd, '--list-langs'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore',
        timeout=10
    )
    
    if result.returncode == 0:
        langs = result.stdout.strip().split('\n')
        # Первая строка обычно "List of available languages"
        if len(langs) > 1:
            available_langs = [lang.strip() for lang in langs[1:] if lang.strip()]
        else:
            available_langs = [lang.strip() for lang in langs if lang.strip()]
        
        print(f"✅ Найдено языков: {len(available_langs)}")
        print("Доступные языки:")
        for lang in available_langs:
            print(f"  - {lang}")
        
        # Проверяем нужные языки
        has_rus = 'rus' in available_langs or 'rus' in [l.lower() for l in available_langs]
        has_eng = 'eng' in available_langs or 'eng' in [l.lower() for l in available_langs]
        has_uzb = 'uzb' in available_langs or 'uzb_cyrl' in available_langs or any('uzb' in l.lower() for l in available_langs)
        
        print(f"\nПроверка нужных языков:")
        print(f"  rus: {'✅' if has_rus else '❌'}")
        print(f"  eng: {'✅' if has_eng else '❌'}")
        print(f"  uzb/uzb_cyrl: {'✅' if has_uzb else '❌'}")
        
        if not has_rus or not has_eng:
            print("\n⚠️  ВНИМАНИЕ: Отсутствуют необходимые языки!")
    else:
        print(f"❌ Ошибка выполнения: {result.stderr}")
        available_langs = []
except Exception as e:
    print(f"❌ Ошибка при проверке языков: {e}")
    available_langs = []

# ШАГ 2: Простой тест на 1 странице БЕЗ предобработки
print("\n" + "=" * 80)
print("ШАГ 2: Простой тест OCR на странице 1 (БЕЗ предобработки)")
print("-" * 80)

PDF_FILE = r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\CamScanner 17-04-2025 15.17.pdf"

if not Path(PDF_FILE).exists():
    print(f"❌ Файл не найден: {PDF_FILE}")
    sys.exit(1)

try:
    print("Извлечение страницы 1 из PDF...")
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
    print(f"✅ Страница извлечена: {image.size[0]}x{image.size[1]} пикселей")
    
    # Сохраняем оригинальное изображение
    test_dir = Path(__file__).parent.parent / "tests" / "ocr_diagnostic"
    test_dir.mkdir(parents=True, exist_ok=True)
    original_path = test_dir / "page1_original.png"
    image.save(original_path)
    print(f"✅ Сохранено: {original_path}")
    
    # Тест OCR БЕЗ предобработки - только rus+eng
    print("\nТест OCR (rus+eng, БЕЗ предобработки)...")
    
    try:
        text = pytesseract.image_to_string(image, lang='rus+eng', config='--psm 6 --oem 3')
        char_count = len(text.strip())
        
        print(f"✅ OCR выполнен успешно")
        print(f"   Символов извлечено: {char_count}")
        
        if char_count > 0:
            print(f"   Первые 200 символов:")
            print("   " + "-" * 76)
            preview = text[:200].replace('\n', '\\n')
            for line in [preview[i:i+76] for i in range(0, len(preview), 76)]:
                print(f"   {line}")
            print("   " + "-" * 76)
            
            # Сохраняем результат
            result_path = test_dir / "page1_ocr_result.txt"
            with open(result_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\n✅ Результат сохранен: {result_path}")
        else:
            print("⚠️  Текст извлечен, но пустой (0 символов)")
            
    except Exception as e:
        print(f"❌ Ошибка OCR: {e}")
        char_count = 0
    
    # Тест с разными PSM режимами
    print("\nТест с разными PSM режимами:")
    psm_results = {}
    for psm in [1, 6, 11]:
        try:
            config = f'--psm {psm} --oem 3'
            text_psm = pytesseract.image_to_string(image, lang='rus+eng', config=config)
            chars = len(text_psm.strip())
            psm_results[psm] = chars
            print(f"  PSM {psm}: {chars} символов")
        except Exception as e:
            psm_results[psm] = 0
            print(f"  PSM {psm}: ❌ Ошибка - {e}")
    
    best_psm = max(psm_results.items(), key=lambda x: x[1])
    print(f"\n✅ Лучший PSM режим: {best_psm[0]} ({best_psm[1]} символов)")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    char_count = 0

print("\n" + "=" * 80)
print("ДИАГНОСТИКА ЗАВЕРШЕНА")
print("=" * 80)

if char_count > 0:
    print("\n✅ OCR РАБОТАЕТ! Можно запускать полный тест.")
else:
    print("\n⚠️  OCR не извлекает текст. Требуется дополнительная диагностика.")

