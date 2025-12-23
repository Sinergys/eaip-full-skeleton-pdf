"""
ПОЛНАЯ ПЕРЕПРОВЕРКА OCR С МАКСИМАЛЬНЫМ УЛУЧШЕНИЕМ КАЧЕСТВА

Функции:
- Автоповорот всех страниц (0°/90°/180°/270°)
- Улучшение контраста, резкости, удаление шумов
- OCR с максимальными настройками (rus+eng+uzb_cyrl, PSM 1/6/11)
- Поиск таблиц на всех страницах
- Прогресс-бар с этапами
- Сохранение всех промежуточных результатов
"""
import sys
import os
import time
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

# Добавляем путь к сервису ingest
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image, ImageEnhance, ImageFilter
    import numpy as np
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
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    HAS_OCR = False

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    print("⚠️  OpenCV не установлен. Некоторые функции улучшения недоступны.")

# Файл для обработки
PDF_FILE = r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\CamScanner 17-04-2025 15.17.pdf"

# Создаем папку для теста с timestamp
TEST_DIR = Path(__file__).parent.parent / "tests" / f"ocr_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
TEST_DIR.mkdir(parents=True, exist_ok=True)

# Подпапки
ORIGINAL_DIR = TEST_DIR / "original"
PROCESSED_DIR = TEST_DIR / "processed"
RESULTS_DIR = TEST_DIR / "results"
for d in [ORIGINAL_DIR, PROCESSED_DIR, RESULTS_DIR]:
    d.mkdir(exist_ok=True)

print("=" * 80)
print("ПОЛНАЯ ПЕРЕПРОВЕРКА OCR С МАКСИМАЛЬНЫМ УЛУЧШЕНИЕМ")
print("=" * 80)
print(f"Файл: {PDF_FILE}")
print(f"Папка теста: {TEST_DIR}")
print()


class ProgressBar:
    """Прогресс-бар для отображения этапов обработки"""
    
    def __init__(self, total_steps: int, description: str = ""):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()
        self.step_times = []
        
    def update(self, step: int, message: str = ""):
        """Обновить прогресс"""
        self.current_step = step
        elapsed = time.time() - self.start_time
        percent = int((step / self.total_steps) * 100)
        bar_length = 50
        filled = int(bar_length * step / self.total_steps)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        step_time = elapsed - sum(self.step_times)
        self.step_times.append(step_time)
        avg_time = elapsed / step if step > 0 else 0
        
        print(f"\r[{bar}] {percent}% | {self.description} | {message} | "
              f"Время: {elapsed:.1f}с (этап: {step_time:.1f}с, среднее: {avg_time:.1f}с)", end="", flush=True)
        
    def finish(self, message: str = ""):
        """Завершить прогресс-бар"""
        total_time = time.time() - self.start_time
        print(f"\r{'█' * 50} 100% | {self.description} | {message} | "
              f"Всего времени: {total_time:.1f}с{' ' * 20}")
        return total_time


def detect_rotation_angle(image: Image.Image) -> int:
    """
    Определяет угол поворота изображения (0°, 90°, 180°, 270°)
    Использует Tesseract OSd (Orientation and Script Detection)
    """
    try:
        # Пробуем определить ориентацию через Tesseract
        osd = pytesseract.image_to_osd(image)
        angle = int(re.search(r'Rotate: (\d+)', osd).group(1))
        return angle
    except:
        # Если не удалось, пробуем все углы и выбираем лучший
        best_angle = 0
        best_confidence = 0
        
        for angle in [0, 90, 180, 270]:
            rotated = image.rotate(-angle, expand=True)
            try:
                # Пробуем OCR с минимальными настройками для проверки
                text = pytesseract.image_to_string(rotated, lang='rus+eng', config='--psm 1')
                # Простая эвристика: больше символов = лучше ориентация
                confidence = len(text.strip())
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_angle = angle
            except:
                continue
                
        return best_angle
    return 0


def auto_rotate_image(image: Image.Image) -> Tuple[Image.Image, int]:
    """
    Автоматически поворачивает изображение до правильной ориентации
    
    Returns:
        (повернутое изображение, угол поворота)
    """
    angle = detect_rotation_angle(image)
    if angle != 0:
        rotated = image.rotate(-angle, expand=True)
        return rotated, angle
    return image, 0


def enhance_image_advanced(image: Image.Image) -> Image.Image:
    """
    МИНИМАЛЬНАЯ предобработка изображения для OCR:
    - Легкое улучшение контраста
    - Легкое увеличение резкости
    """
    # Конвертируем в RGB если нужно
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # МИНИМАЛЬНАЯ обработка - только легкие улучшения
    # Увеличиваем контраст (минимально)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)  # Только +20%
    
    # Увеличиваем резкость (минимально)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.1)  # Только +10%
    
    return image


def ocr_with_psm_modes(image: Image.Image, languages: str = "rus+eng") -> Dict[str, Any]:
    """
    Применяет OCR с разными PSM режимами и выбирает лучший результат
    
    PSM режимы:
    1 = Автоматическое определение ориентации и скрипта
    6 = Предполагается единый блок текста
    11 = Разреженный текст
    """
    results = {}
    psm_modes = [1, 6, 11]
    
    # Пробуем разные комбинации языков (fallback если uzb_cyrl не установлен)
    lang_combinations = [languages, "rus+eng", "rus", "eng"]
    
    for psm in psm_modes:
        best_result = None
        best_error = None
        
        for lang_combo in lang_combinations:
            try:
                config = f'--psm {psm} --oem 3'
                text = pytesseract.image_to_string(image, lang=lang_combo, config=config)
                
                if text.strip():  # Если получили текст, используем этот результат
                    try:
                        data = pytesseract.image_to_data(image, lang=lang_combo, config=config, output_type=pytesseract.Output.DICT)
                        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    except:
                        avg_confidence = 50  # Значение по умолчанию
                    
                    best_result = {
                        'text': text,
                        'char_count': len(text),
                        'avg_confidence': avg_confidence,
                        'word_count': len(text.split()),
                        'languages_used': lang_combo
                    }
                    break  # Используем первый успешный результат
            except Exception as e:
                if not best_error:
                    best_error = str(e)
                continue
        
        if best_result:
            results[psm] = best_result
        else:
            results[psm] = {
                'text': '',
                'char_count': 0,
                'avg_confidence': 0,
                'error': best_error or 'Не удалось распознать текст'
            }
    
    # Выбираем лучший результат (по количеству символов и уверенности)
    best_psm = max(psm_modes, key=lambda p: results[p]['char_count'] * (results[p]['avg_confidence'] / 100))
    
    return {
        'best_psm': best_psm,
        'results': results,
        'best_text': results[best_psm]['text'],
        'best_confidence': results[best_psm]['avg_confidence']
    }


def extract_tables_from_page_text(text: str, page_num: int) -> List[Dict[str, Any]]:
    """Извлекает таблицы из текста страницы"""
    from utils.ocr_table_extractor import extract_tables_from_ocr_text
    
    tables = extract_tables_from_ocr_text(text, page_num=page_num)
    return tables


def process_pdf_full_recheck(pdf_path: str) -> Dict[str, Any]:
    """Полная перепроверка OCR с максимальным улучшением"""
    
    if not HAS_OCR:
        return {"error": "OCR библиотеки не установлены"}
    
    results = {
        "pdf_path": pdf_path,
        "test_dir": str(TEST_DIR),
        "start_time": datetime.now().isoformat(),
        "pages": [],
        "tables": [],
        "statistics": {}
    }
    
    # Этап 1: Извлечение страниц из PDF
    progress = ProgressBar(5, "Этап 1/5: Извлечение страниц")
    progress.update(0, "Конвертация PDF в изображения...")
    
    try:
        poppler_paths = [
            r"C:\poppler\Library\bin",
            r"C:\poppler\bin",
        ]
        poppler_path = None
        for path in poppler_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "pdftoppm.exe")):
                poppler_path = path
                break
        
        if poppler_path:
            current_path = os.environ.get("PATH", "")
            if poppler_path not in current_path:
                os.environ["PATH"] = poppler_path + os.pathsep + current_path
        
        images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
        progress.update(1, f"Извлечено {len(images)} страниц")
    except Exception as e:
        progress.finish(f"Ошибка: {e}")
        return {"error": f"Ошибка конвертации PDF: {e}"}
    
    progress.finish("Страницы извлечены")
    
    # Сохраняем оригинальные изображения
    for i, img in enumerate(images, 1):
        img.save(ORIGINAL_DIR / f"page_{i:02d}_original.png")
    
    # Этап 2: Предобработка (поворот + улучшение)
    progress = ProgressBar(len(images), "Этап 2/5: Предобработка изображений")
    
    processed_images = []
    rotation_angles = []
    
    for i, image in enumerate(images, 1):
        progress.update(i, f"Страница {i}/{len(images)}")
        
        # Сохраняем оригинал
        original_path = ORIGINAL_DIR / f"page_{i:02d}_original.png"
        image.save(original_path)
        
        # Автоповорот
        rotated_image, angle = auto_rotate_image(image)
        rotation_angles.append(angle)
        
        # Сохраняем повернутое изображение
        rotated_path = PROCESSED_DIR / f"page_{i:02d}_rotated_{angle}deg.png"
        rotated_image.save(rotated_path)
        
        # Улучшение изображения
        enhanced_image = enhance_image_advanced(rotated_image)
        
        # Сохраняем улучшенное изображение
        enhanced_path = PROCESSED_DIR / f"page_{i:02d}_enhanced.png"
        enhanced_image.save(enhanced_path)
        
        processed_images.append({
            'original': image,
            'rotated': rotated_image,
            'enhanced': enhanced_image,
            'rotation_angle': angle,
            'paths': {
                'original': str(original_path),
                'rotated': str(rotated_path),
                'enhanced': str(enhanced_path)
            }
        })
    
    progress.finish("Предобработка завершена")
    
    # Этап 3: OCR с максимальными настройками
    progress = ProgressBar(len(processed_images), "Этап 3/5: OCR распознавание")
    
    ocr_results = []
    total_chars = 0
    
    for i, proc_data in enumerate(processed_images, 1):
        progress.update(i, f"Страница {i}/{len(processed_images)}")
        
        # Пробуем OCR на разных версиях изображения (fallback)
        page_text = ""
        ocr_result = None
        image_used = "enhanced"
        
        # 1. Пробуем улучшенное изображение
        try:
            ocr_result = ocr_with_psm_modes(proc_data['enhanced'], languages="rus+eng")
            page_text = ocr_result['best_text']
        except Exception as e:
            print(f"\n⚠️  Ошибка OCR на улучшенном изображении страницы {i}: {e}")
        
        # 2. Если не получилось, пробуем повернутое
        if not page_text.strip():
            try:
                ocr_result = ocr_with_psm_modes(proc_data['rotated'], languages="rus+eng")
                page_text = ocr_result['best_text']
                image_used = "rotated"
            except Exception as e:
                print(f"\n⚠️  Ошибка OCR на повернутом изображении страницы {i}: {e}")
        
        # 3. Если все еще не получилось, пробуем оригинал
        if not page_text.strip():
            try:
                ocr_result = ocr_with_psm_modes(proc_data['original'], languages="rus+eng")
                page_text = ocr_result['best_text']
                image_used = "original"
            except Exception as e:
                print(f"\n⚠️  Ошибка OCR на оригинальном изображении страницы {i}: {e}")
                # Создаем пустой результат
                ocr_result = {
                    'best_psm': 1,
                    'best_text': '',
                    'best_confidence': 0,
                    'results': {}
                }
        
        if not ocr_result:
            ocr_result = {
                'best_psm': 1,
                'best_text': '',
                'best_confidence': 0,
                'results': {}
            }
        
        total_chars += len(page_text)
        
        ocr_results.append({
            'page': i,
            'text': page_text,
            'char_count': len(page_text),
            'best_psm': ocr_result.get('best_psm', 1),
            'confidence': ocr_result.get('best_confidence', 0),
            'all_psm_results': ocr_result.get('results', {}),
            'image_used': image_used
        })
        
        # Сохраняем OCR текст
        text_path = RESULTS_DIR / f"page_{i:02d}_ocr_text.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"--- Страница {i} ---\n")
            f.write(f"PSM режим: {ocr_result['best_psm']}\n")
            f.write(f"Уверенность: {ocr_result['best_confidence']:.2f}%\n")
            f.write(f"Символов: {len(page_text)}\n")
            f.write("\n" + "="*60 + "\n\n")
            f.write(page_text)
    
    progress.finish(f"OCR завершен: {total_chars} символов")
    
    # Этап 4: Поиск таблиц
    progress = ProgressBar(len(ocr_results), "Этап 4/5: Поиск таблиц")
    
    all_tables = []
    
    for i, ocr_data in enumerate(ocr_results, 1):
        progress.update(i, f"Страница {i}/{len(ocr_results)}")
        
        page_text = ocr_data['text']
        tables = extract_tables_from_page_text(page_text, page_num=i)
        
        if tables:
            all_tables.extend(tables)
            ocr_data['tables_found'] = len(tables)
        else:
            ocr_data['tables_found'] = 0
    
    progress.finish(f"Найдено таблиц: {len(all_tables)}")
    
    # Этап 5: Сохранение результатов
    progress = ProgressBar(1, "Этап 5/5: Сохранение результатов")
    progress.update(1, "Формирование отчета...")
    
    # Сохраняем полный OCR текст
    full_text = "\n\n".join([f"--- Страница {r['page']} ---\n{r['text']}" for r in ocr_results])
    with open(RESULTS_DIR / "full_ocr_text.txt", 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    # Сохраняем таблицы
    if all_tables:
        with open(RESULTS_DIR / "tables.json", 'w', encoding='utf-8') as f:
            json.dump(all_tables, f, ensure_ascii=False, indent=2, default=str)
    
    # Формируем результаты
    results['pages'] = []
    for i, (proc_data, ocr_data) in enumerate(zip(processed_images, ocr_results), 1):
        results['pages'].append({
            'page_number': i,
            'rotation_angle': proc_data['rotation_angle'],
            'char_count': ocr_data['char_count'],
            'confidence': ocr_data['confidence'],
            'best_psm': ocr_data['best_psm'],
            'tables_found': ocr_data.get('tables_found', 0),
            'paths': proc_data['paths']
        })
    
    results['tables'] = all_tables
    results['statistics'] = {
        'total_pages': len(images),
        'total_characters': total_chars,
        'total_tables': len(all_tables),
        'avg_confidence': sum(r['confidence'] for r in ocr_results) / len(ocr_results) if ocr_results else 0,
        'rotation_angles': rotation_angles,
        'tables_by_page': {i+1: ocr_results[i].get('tables_found', 0) for i in range(len(ocr_results))}
    }
    
    results['end_time'] = datetime.now().isoformat()
    
    # Сохраняем полный отчет
    with open(RESULTS_DIR / "full_report.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    progress.finish("Результаты сохранены")
    
    return results


def generate_text_report(results: Dict[str, Any]) -> str:
    """Генерирует текстовый отчет"""
    report = []
    report.append("=" * 80)
    report.append("ОТЧЕТ ПОЛНОЙ ПЕРЕПРОВЕРКИ OCR")
    report.append("=" * 80)
    report.append(f"Файл: {results.get('pdf_path', 'N/A')}")
    report.append(f"Папка теста: {results.get('test_dir', 'N/A')}")
    report.append(f"Время начала: {results.get('start_time', 'N/A')}")
    report.append(f"Время окончания: {results.get('end_time', 'N/A')}")
    report.append("")
    
    stats = results.get('statistics', {})
    report.append("СТАТИСТИКА:")
    report.append(f"  Всего страниц: {stats.get('total_pages', 0)}")
    report.append(f"  Всего символов: {stats.get('total_characters', 0)}")
    report.append(f"  Всего таблиц: {stats.get('total_tables', 0)}")
    report.append(f"  Средняя уверенность OCR: {stats.get('avg_confidence', 0):.2f}%")
    report.append("")
    
    report.append("ПОВОРОТЫ СТРАНИЦ:")
    angles = stats.get('rotation_angles', [])
    for i, angle in enumerate(angles, 1):
        report.append(f"  Страница {i}: {angle}°")
    report.append("")
    
    report.append("ТАБЛИЦЫ ПО СТРАНИЦАМ:")
    tables_by_page = stats.get('tables_by_page', {})
    for page, count in tables_by_page.items():
        report.append(f"  Страница {page}: {count} таблиц")
    report.append("")
    
    report.append("ДЕТАЛИ ПО СТРАНИЦАМ:")
    for page_data in results.get('pages', []):
        report.append(f"  Страница {page_data['page_number']}:")
        report.append(f"    Поворот: {page_data['rotation_angle']}°")
        report.append(f"    Символов: {page_data['char_count']}")
        report.append(f"    Уверенность: {page_data['confidence']:.2f}%")
        report.append(f"    Лучший PSM: {page_data['best_psm']}")
        report.append(f"    Таблиц: {page_data['tables_found']}")
    report.append("")
    
    report.append("СОХРАНЕННЫЕ ФАЙЛЫ:")
    report.append(f"  Оригинальные изображения: {ORIGINAL_DIR}")
    report.append(f"  Обработанные изображения: {PROCESSED_DIR}")
    report.append(f"  Результаты OCR: {RESULTS_DIR}")
    report.append("")
    
    if results.get('error'):
        report.append(f"ОШИБКИ: {results['error']}")
    
    report.append("=" * 80)
    
    return "\n".join(report)


if __name__ == "__main__":
    print()
    print("Начинаю полную перепроверку OCR...")
    print()
    
    results = process_pdf_full_recheck(PDF_FILE)
    
    # Генерируем и сохраняем отчет
    report = generate_text_report(results)
    
    report_path = TEST_DIR / "REPORT.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print()
    print("=" * 80)
    print("ОТЧЕТ:")
    print("=" * 80)
    print(report)
    print()
    print(f"Полный отчет сохранен: {report_path}")
    print(f"Все файлы сохранены в: {TEST_DIR}")
    print()
    print("ОЖИДАЮ ДАЛЬНЕЙШИХ КОМАНД.")

