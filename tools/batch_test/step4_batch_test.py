"""
ШАГ 4: Тестовый батч (5 файлов) с контролем
Цель: проверить стабильность и throughput на реальном наборе
Используются файлы, важные для закрытия по данным
"""
import sys
import os
from pathlib import Path
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from pdf2image import convert_from_path
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Создаем директорию для сохранения тестовых файлов
TEST_FILES_DIR_SAVE = project_root / "tests" / "ocr_test_files"
TEST_FILES_DIR_SAVE.mkdir(parents=True, exist_ok=True)

from eaip_full_skeleton.services.ingest.utils.gemini_vision_ocr import extract_with_gemini_vision

# Настройка логирования
log_dir = project_root / "reports" / "ocr"
log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / "batch_run.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
BATCH_SIZE = 5  # Всего 5 файлов
PAUSE_BETWEEN_FILES = 10  # Пауза 10 сек между файлами
TEST_FILES_DIR = Path(r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX")

# Фильтры по размеру файлов
MIN_FILE_SIZE_MB = 0.05  # Минимальный размер файла (MB) - исключаем очень мелкие файлы
MAX_FILE_SIZE_MB = 5.0   # Максимальный размер файла (MB) - для быстрого теста

# Параллельная обработка
USE_PARALLEL_PROCESSING = True  # Использовать параллельную обработку страниц
MAX_WORKERS = 3  # Количество потоков для параллельной обработки

# Сохранение тестовых файлов
SAVE_TEST_FILES = True  # Сохранять все тестовые файлы (не удалять)

# Параллельная обработка
USE_PARALLEL_PROCESSING = True  # Использовать параллельную обработку страниц
MAX_WORKERS = 3  # Количество потоков для параллельной обработки

# Сохранение тестовых файлов
SAVE_TEST_FILES = True  # Сохранять все тестовые файлы (не удалять)
TEST_FILES_DIR_SAVE = project_root / "tests" / "ocr_test_files"  # Директория для сохранения

# Файлы, важные для закрытия по данным (акты, счета-фактуры) - выбраны мелкие файлы < 0.5 MB
CLOSURE_FILES = [
    "счёт фактура.PDF",                     # Счет-фактура (0.09 MB)
    "Акт выполненных работ-2 (1).PDF",     # Акт для закрытия (0.14 MB)
    "акт выполненых работ май.PDF",         # Акт для закрытия (0.21 MB)
    "ПДВ.pdf",                              # Экологический документ (0.21 MB)
    "акт выполненных работ (1).PDF"         # Акт для закрытия (0.29 MB)
]

def print_progress_bar(current: int, total: int, prefix: str = "", suffix: str = "", length: int = 50):
    """Выводит текстовый прогресс-бар"""
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '░' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)
    if current == total:
        print()  # Новая строка после завершения

def print_ocr_progress(page_num: int, total_pages: int, elapsed: float = 0, status: str = "обработка"):
    """Выводит детальный прогресс для OCR операции"""
    percent = (page_num / float(total_pages)) * 100
    filled = int(50 * page_num // total_pages)
    bar = '█' * filled + '░' * (50 - filled)
    elapsed_str = f"{elapsed:.1f}с" if elapsed > 0 else ""
    print(f'\r  📄 Страница {page_num}/{total_pages} |{bar}| {percent:.1f}% {status} {elapsed_str}', end='', flush=True)

def get_pdf_files() -> List[Path]:
    """
    Выбирает файлы, важные для закрытия по данным Навои ИЭС
    Фильтрует по размеру: MIN_FILE_SIZE_MB <= размер <= MAX_FILE_SIZE_MB
    """
    files = []
    min_size_bytes = MIN_FILE_SIZE_MB * 1024 * 1024
    max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Сначала выбираем приоритетные файлы для закрытия по данным
    for filename in CLOSURE_FILES:
        file_path = TEST_FILES_DIR / filename
        if file_path.exists():
            file_size = file_path.stat().st_size
            # Проверяем размер файла
            if min_size_bytes <= file_size <= max_size_bytes:
                files.append(file_path)
                logger.debug(f"Добавлен файл: {filename} ({file_size / 1024 / 1024:.2f} MB)")
            else:
                logger.warning(f"Файл {filename} пропущен: размер {file_size / 1024 / 1024:.2f} MB не в диапазоне [{MIN_FILE_SIZE_MB}, {MAX_FILE_SIZE_MB}] MB")
        else:
            logger.warning(f"Файл не найден: {filename}")
    
    # Если не все файлы найдены, дополняем подходящими PDF из директории
    if len(files) < BATCH_SIZE:
        logger.info(f"Найдено {len(files)} приоритетных файлов, ищем дополнительные...")
        all_pdfs = sorted(TEST_FILES_DIR.glob("*.pdf"))
        
        for pdf in all_pdfs:
            if pdf in files:
                continue  # Пропускаем уже добавленные
            
            file_size = pdf.stat().st_size
            # Проверяем размер и добавляем подходящие файлы
            if min_size_bytes <= file_size <= max_size_bytes:
                files.append(pdf)
                logger.debug(f"Добавлен дополнительный файл: {pdf.name} ({file_size / 1024 / 1024:.2f} MB)")
                if len(files) >= BATCH_SIZE:
                    break
    
    selected = files[:BATCH_SIZE]
    logger.info(f"Выбрано {len(selected)} файлов для обработки (размер: {MIN_FILE_SIZE_MB}-{MAX_FILE_SIZE_MB} MB)")
    
    return selected

def process_single_page(page_data: tuple, file_path: Path, file_num: int, total_pages: int, lock: threading.Lock) -> Dict[str, Any]:
    """
    Обрабатывает одну страницу PDF через Gemini Vision OCR
    Используется для параллельной обработки
    """
    page_num, image = page_data
    page_start = time.time()
    page_result = {
        "page_number": page_num,
        "characters": 0,
        "tables_count": 0,
        "tables": [],  # Полные данные таблиц
        "text": "",  # Полный текст
        "processing_time_sec": 0,
        "error": None,
        "low_confidence": False,
        "confidence": 0.0
    }
    
    # Создаем уникальное имя файла для сохранения
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = TEST_FILES_DIR_SAVE / f"file_{file_num}_pages"
    save_dir.mkdir(parents=True, exist_ok=True)
    saved_image_path = save_dir / f"page_{page_num}_{timestamp}.png"
    
    try:
        # Сохраняем изображение (не удаляем после использования)
        image.save(str(saved_image_path), 'PNG')
        tmp_path = str(saved_image_path)
        
        # Предобработка изображения
        try:
            from PIL import Image as PILImage
            from eaip_full_skeleton.services.ingest.file_parser import preprocess_image_for_ocr
            enhanced_image = preprocess_image_for_ocr(PILImage.open(tmp_path), dpi=200)
            enhanced_image.save(tmp_path, 'PNG')
            logger.debug(f"Изображение предобработано для страницы {page_num}")
        except Exception as preprocess_error:
            logger.debug(f"Предобработка пропущена: {preprocess_error}")
        
        # Вызываем Gemini Vision OCR
        ocr_start = time.time()
        result = extract_with_gemini_vision(tmp_path, page_num=page_num)
        ocr_elapsed = time.time() - ocr_start
        
        # Извлекаем данные
        text = result.get("text", "")
        tables = result.get("tables", [])
        confidence = result.get("confidence", 0.0)
        
        page_result["characters"] = len(text)
        page_result["tables_count"] = len(tables)
        page_result["tables"] = tables  # Сохраняем полные данные таблиц в структурированном формате
        page_result["text"] = text  # Сохраняем текст для полноты
        page_result["confidence"] = confidence
        
        # Проверяем low_confidence
        if confidence < 0.70:
            page_result["low_confidence"] = True
        
        # Обновляем прогресс-бар (с блокировкой для потокобезопасности)
        with lock:
            status = f"✅ {len(text)} симв., {len(tables)} табл., conf={confidence:.2f}"
            print_ocr_progress(page_num, total_pages, ocr_elapsed, status)
            print()  # Новая строка
        
        logger.info(f"Страница {page_num}: {len(text)} символов, {len(tables)} таблиц, confidence={confidence:.2f}, время={ocr_elapsed:.2f}с")
        if tables:
            logger.debug(f"Таблицы страницы {page_num}: {len(tables)} шт., структура: {[t.get('row_count', 0) if isinstance(t, dict) else 'N/A' for t in tables]}")
        logger.info(f"Изображение страницы {page_num} сохранено: {saved_image_path}")
        
    except Exception as e:
        error_msg = f"Ошибка обработки страницы {page_num}: {e}"
        logger.error(error_msg)
        page_result["error"] = str(e)
        with lock:
            print_ocr_progress(page_num, total_pages, 0, f"❌ Ошибка: {str(e)[:30]}")
            print()  # Новая строка
    
    page_result["processing_time_sec"] = time.time() - page_start
    return page_result

def process_pages_parallel(images: List, file_path: Path, file_num: int, total_pages: int) -> List[Dict[str, Any]]:
    """
    Параллельная обработка страниц PDF
    """
    pages_results = []
    lock = threading.Lock()
    
    # Подготавливаем данные для обработки
    pages_data = [(i+1, img) for i, img in enumerate(images)]
    
    # Параллельная обработка
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Запускаем обработку всех страниц
        futures = {
            executor.submit(process_single_page, page_data, file_path, file_num, total_pages, lock): page_data
            for page_data in pages_data
        }
        
        # Собираем результаты по мере завершения
        for future in as_completed(futures):
            page_data = futures[future]
            page_num = page_data[0]
            try:
                result = future.result()
                pages_results.append(result)
            except Exception as e:
                logger.error(f"Ошибка обработки страницы {page_num}: {e}")
                pages_results.append({
                    "page_number": page_num,
                    "characters": 0,
                    "tables_count": 0,
                    "tables": [],
                    "text": "",
                    "processing_time_sec": 0,
                    "error": str(e),
                    "low_confidence": False,
                    "confidence": 0.0
                })
    
    return pages_results

def process_pdf_file(file_path: Path, file_num: int, total_files: int) -> Dict[str, Any]:
    """Обрабатывает один PDF файл через Gemini Vision OCR"""
    file_result = {
        "file_path": str(file_path),
        "file_name": file_path.name,
        "file_size_kb": file_path.stat().st_size / 1024,
        "pages": [],
        "total_characters": 0,
        "total_tables": 0,
        "total_time_sec": 0,
        "avg_time_per_page_sec": 0,
        "errors": [],
        "low_confidence_count": 0,
        "gemini_retries_count": 0,
        "success": False
    }
    
    start_time = time.time()
    
    try:
        print(f"\n{'='*80}")
        print(f"ФАЙЛ {file_num}/{total_files}: {file_path.name}")
        print(f"{'='*80}")
        logger.info(f"Начинаю обработку файла: {file_path.name}")
        
        # Извлекаем страницы PDF как изображения (необходимо для Gemini Vision API)
        # Для сканированных PDF это быстрая операция, т.к. страницы уже являются изображениями
        try:
            print("📄 Извлечение страниц из PDF...")
            conv_start = time.time()
            
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
            
            # Используем DPI=200 для ускорения (достаточно для OCR)
            images = convert_from_path(str(file_path), dpi=200, poppler_path=poppler_path)
            total_pages = len(images)
            conv_time = time.time() - conv_start
            
            print(f"✅ Извлечено {total_pages} страниц за {conv_time:.1f}с")
            logger.info(f"PDF конвертирован в {total_pages} изображений за {conv_time:.2f}с")
        except Exception as e:
            error_msg = f"Ошибка конвертации PDF: {e}"
            logger.error(error_msg)
            file_result["errors"].append(error_msg)
            return file_result
        
        # Обрабатываем страницы (параллельно или последовательно)
        processing_mode = "параллельно" if USE_PARALLEL_PROCESSING and total_pages > 1 else "последовательно"
        print(f"\n📊 Обработка страниц через Gemini Vision OCR ({processing_mode}):")
        
        if USE_PARALLEL_PROCESSING and total_pages > 1:
            # Параллельная обработка страниц
            pages_results = process_pages_parallel(images, file_path, file_num, total_pages)
            file_result["pages"] = sorted(pages_results, key=lambda x: x["page_number"])
            
            # Агрегируем результаты
            for page_result in pages_results:
                file_result["total_characters"] += page_result.get("characters", 0)
                file_result["total_tables"] += page_result.get("tables_count", 0)  # Используем tables_count вместо tables
                if page_result.get("low_confidence", False):
                    file_result["low_confidence_count"] += 1
                if page_result.get("error"):
                    file_result["errors"].append(page_result["error"])
        else:
            # Последовательная обработка страниц
            for page_num, image in enumerate(images, 1):
                page_start = time.time()
            page_result = {
                "page_number": page_num,
                "characters": 0,
                "tables_count": 0,
                "tables": [],  # Полные данные таблиц
                "text": "",  # Полный текст
                "processing_time_sec": 0,
                "error": None,
                "low_confidence": False,
                "confidence": 0.0
            }
            
            try:
                # Прогресс-бар для страницы
                print_ocr_progress(page_num, total_pages, 0, "🔄 OCR...")
                
                # Сохраняем изображение (не удаляем после использования, если SAVE_TEST_FILES=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_dir = TEST_FILES_DIR_SAVE / f"file_{file_num}_pages"
                save_dir.mkdir(parents=True, exist_ok=True)
                saved_image_path = save_dir / f"page_{page_num}_{timestamp}.png"
                
                image.save(str(saved_image_path), 'PNG')
                tmp_path = str(saved_image_path)
                
                try:
                    # Предобработка изображения для улучшения качества OCR
                    try:
                        from PIL import Image as PILImage
                        from eaip_full_skeleton.services.ingest.file_parser import preprocess_image_for_ocr
                        enhanced_image = preprocess_image_for_ocr(PILImage.open(tmp_path), dpi=200)
                        enhanced_image.save(tmp_path, 'PNG')
                        logger.debug(f"Изображение предобработано для страницы {page_num}")
                    except Exception as preprocess_error:
                        logger.debug(f"Предобработка пропущена: {preprocess_error}")
                    
                    # Вызываем Gemini Vision OCR с отслеживанием времени
                    ocr_start = time.time()
                    result = extract_with_gemini_vision(tmp_path, page_num=page_num)
                    ocr_elapsed = time.time() - ocr_start
                    
                    # Извлекаем данные
                    text = result.get("text", "")
                    tables = result.get("tables", [])
                    confidence = result.get("confidence", 0.0)
                    
                    page_result["characters"] = len(text)
                    page_result["tables_count"] = len(tables)
                    page_result["tables"] = tables  # Сохраняем полные данные таблиц в структурированном формате
                    page_result["text"] = text  # Сохраняем текст для полноты
                    page_result["confidence"] = confidence
                    
                    # Проверяем low_confidence
                    if confidence < 0.70:  # Порог для таблиц
                        page_result["low_confidence"] = True
                        file_result["low_confidence_count"] += 1
                    
                    file_result["total_characters"] += len(text)
                    file_result["total_tables"] += len(tables)
                    
                    # Обновляем прогресс-бар с результатами
                    status = f"✅ {len(text)} симв., {len(tables)} табл., conf={confidence:.2f}"
                    print_ocr_progress(page_num, total_pages, ocr_elapsed, status)
                    print()  # Новая строка
                    
                    logger.info(f"Страница {page_num}: {len(text)} символов, {len(tables)} таблиц, confidence={confidence:.2f}, время={ocr_elapsed:.2f}с")
                    logger.info(f"Изображение страницы {page_num} сохранено: {saved_image_path}")
                    
                except Exception as e:
                    # В случае ошибки тоже сохраняем файл для анализа
                    logger.warning(f"Ошибка обработки, но файл сохранен: {saved_image_path}")
                    raise
                
            except Exception as e:
                error_msg = f"Ошибка обработки страницы {page_num}: {e}"
                logger.error(error_msg)
                page_result["error"] = str(e)
                file_result["errors"].append(error_msg)
                print_ocr_progress(page_num, total_pages, 0, f"❌ Ошибка: {str(e)[:30]}")
                print()  # Новая строка
            
            page_result["processing_time_sec"] = time.time() - page_start
            file_result["pages"].append(page_result)
        
        file_result["total_time_sec"] = time.time() - start_time
        if len(file_result["pages"]) > 0:
            file_result["avg_time_per_page_sec"] = file_result["total_time_sec"] / len(file_result["pages"])
        
        file_result["success"] = len(file_result["errors"]) == 0
        
        print(f"\n✅ Файл обработан: {file_result['total_characters']} символов, "
              f"{file_result['total_tables']} таблиц, {file_result['total_time_sec']:.2f} сек")
        logger.info(f"Файл {file_path.name} обработан: {file_result['total_characters']} символов, "
                   f"{file_result['total_tables']} таблиц, {file_result['total_time_sec']:.2f} сек")
        
    except Exception as e:
        error_msg = f"Критическая ошибка обработки файла {file_path.name}: {e}"
        logger.error(error_msg)
        file_result["errors"].append(error_msg)
        file_result["total_time_sec"] = time.time() - start_time
    
    return file_result

def print_file_report(file_result: Dict[str, Any], file_num: int, total_files: int):
    """Выводит отчет по обработанному файлу"""
    print(f"\n{'='*80}")
    print(f"📋 ОТЧЕТ ПО ФАЙЛУ {file_num}/{total_files}")
    print(f"{'='*80}")
    print(f"Файл: {file_result['file_name']}")
    print(f"Размер: {file_result['file_size_kb']:.2f} KB")
    print(f"Страниц: {len(file_result['pages'])}")
    print(f"Символов: {file_result['total_characters']}")
    print(f"Таблиц: {file_result['total_tables']}")
    print(f"Время обработки: {file_result['total_time_sec']:.2f} сек")
    print(f"Среднее время на страницу: {file_result['avg_time_per_page_sec']:.2f} сек")
    print(f"Low confidence страниц: {file_result['low_confidence_count']}")
    print(f"Ошибок: {len(file_result['errors'])}")
    print(f"Статус: {'✅ Успешно' if file_result['success'] else '❌ Ошибки'}")
    
    if file_result['errors']:
        print(f"\n⚠️ Ошибки:")
        for i, error in enumerate(file_result['errors'], 1):
            print(f"  {i}. {error}")
    
    print(f"{'='*80}\n")

def run_batch_test():
    """Запускает батч-тест на 5 файлах"""
    logger.info("=" * 80)
    logger.info("ШАГ 4: Тестовый батч (5 файлов) с контролем")
    logger.info("=" * 80)
    
    # Выбираем 5 PDF файлов
    pdf_files = get_pdf_files()
    
    if len(pdf_files) == 0:
        logger.error(f"PDF файлы не найдены в {TEST_FILES_DIR}")
        return
    
    print(f"\n📁 Выбрано {len(pdf_files)} файлов для обработки:")
    for i, f in enumerate(pdf_files, 1):
        print(f"  {i}. {f.name}")
    
    logger.info(f"Выбрано {len(pdf_files)} файлов для обработки:")
    for i, f in enumerate(pdf_files, 1):
        logger.info(f"  {i}. {f.name}")
    
    # Результаты батча
    batch_results = {
        "batch_start_time": datetime.now().isoformat(),
        "batch_size": len(pdf_files),
        "files": [],
        "summary": {
            "total_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "total_characters": 0,
            "total_tables": 0,
            "total_time_sec": 0,
            "avg_time_per_page_sec": 0,
            "total_errors": 0,
            "low_confidence_percentage": 0.0,
            "low_confidence_count": 0,
            "gemini_retries_count": 0
        }
    }
    
    batch_start = time.time()
    
    # Обрабатываем каждый файл
    for i, pdf_file in enumerate(pdf_files, 1):
        file_result = process_pdf_file(pdf_file, i, len(pdf_files))
        batch_results["files"].append(file_result)
        
        # Выводим отчет по файлу
        print_file_report(file_result, i, len(pdf_files))
        
        # Сохраняем промежуточные результаты
        intermediate_file = log_dir / f"step4_batch_intermediate_{i}.json"
        with open(intermediate_file, 'w', encoding='utf-8') as f:
            json.dump({
                "file_num": i,
                "total_files": len(pdf_files),
                "file_result": file_result,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # Обновляем summary
        batch_results["summary"]["total_files"] += 1
        if file_result["success"]:
            batch_results["summary"]["successful_files"] += 1
        else:
            batch_results["summary"]["failed_files"] += 1
        
        batch_results["summary"]["total_characters"] += file_result["total_characters"]
        batch_results["summary"]["total_tables"] += file_result["total_tables"]
        batch_results["summary"]["total_errors"] += len(file_result["errors"])
        batch_results["summary"]["low_confidence_count"] = batch_results["summary"].get("low_confidence_count", 0) + file_result["low_confidence_count"]
        
        # Пауза между файлами (кроме последнего)
        if i < len(pdf_files):
            print(f"\n⏸️  Пауза {PAUSE_BETWEEN_FILES} сек перед следующим файлом...\n")
            time.sleep(PAUSE_BETWEEN_FILES)
        else:
            print(f"\n✅ Все файлы обработаны!")
    
    batch_results["batch_end_time"] = datetime.now().isoformat()
    batch_results["summary"]["total_time_sec"] = time.time() - batch_start
    
    # Вычисляем средние метрики
    total_pages = sum(len(f["pages"]) for f in batch_results["files"])
    if total_pages > 0:
        batch_results["summary"]["avg_time_per_page_sec"] = batch_results["summary"]["total_time_sec"] / total_pages
    
    total_pages_with_data = sum(1 for f in batch_results["files"] for p in f["pages"] if p.get("characters", 0) > 0)
    if total_pages_with_data > 0:
        batch_results["summary"]["low_confidence_percentage"] = (
            batch_results["summary"]["low_confidence_count"] / total_pages_with_data * 100
        )
    
    # Сохраняем финальные результаты
    results_file = log_dir / "step4_batch_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(batch_results, f, ensure_ascii=False, indent=2)
    
    # Выводим итоговый отчет
    print(f"\n{'='*80}")
    print(f"📊 ИТОГОВЫЙ ОТЧЕТ БАТЧ-ТЕСТА")
    print(f"{'='*80}")
    print(f"Файлов обработано: {batch_results['summary']['total_files']}")
    print(f"Успешно: {batch_results['summary']['successful_files']}")
    print(f"Ошибок: {batch_results['summary']['failed_files']}")
    print(f"Всего символов: {batch_results['summary']['total_characters']}")
    print(f"Всего таблиц: {batch_results['summary']['total_tables']}")
    print(f"Общее время: {batch_results['summary']['total_time_sec']:.2f} сек")
    print(f"Среднее время на страницу: {batch_results['summary']['avg_time_per_page_sec']:.2f} сек")
    print(f"Low confidence: {batch_results['summary']['low_confidence_percentage']:.1f}%")
    print(f"Результаты сохранены: {results_file}")
    print(f"{'='*80}\n")
    
    logger.info("\n" + "=" * 80)
    logger.info("БАТЧ-ТЕСТ ЗАВЕРШЕН")
    logger.info("=" * 80)
    logger.info(f"Файлов обработано: {batch_results['summary']['total_files']}")
    logger.info(f"Успешно: {batch_results['summary']['successful_files']}")
    logger.info(f"Ошибок: {batch_results['summary']['failed_files']}")
    logger.info(f"Всего символов: {batch_results['summary']['total_characters']}")
    logger.info(f"Всего таблиц: {batch_results['summary']['total_tables']}")
    logger.info(f"Общее время: {batch_results['summary']['total_time_sec']:.2f} сек")
    logger.info(f"Среднее время на страницу: {batch_results['summary']['avg_time_per_page_sec']:.2f} сек")
    logger.info(f"Low confidence: {batch_results['summary']['low_confidence_percentage']:.1f}%")
    logger.info(f"Результаты сохранены: {results_file}")
    
    return batch_results

if __name__ == "__main__":
    run_batch_test()
