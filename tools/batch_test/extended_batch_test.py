"""
РАСШИРЕННЫЙ БАТЧ-ТЕСТ: 10-15 небольших файлов для данных Навои
Цель: проверить стабильность и качество на реальном наборе
Используются файлы, важные для закрытия по данным (акты, счета-фактуры, экологические документы)
"""
import sys
import os
from pathlib import Path
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
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

log_file = log_dir / "extended_batch_run.log"
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
TEST_FILES_DIR = Path(r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX")
MAX_FILE_SIZE_KB = 500  # Максимальный размер файла (KB) - только небольшие файлы
MIN_FILE_SIZE_KB = 50   # Минимальный размер файла (KB)

# Параллельная обработка
USE_PARALLEL_PROCESSING = True
MAX_WORKERS = 3

# Сохранение тестовых файлов
SAVE_TEST_FILES = True

# Приоритетные файлы для закрытия данных (акты, счета-фактуры, экологические документы)
PRIORITY_KEYWORDS = [
    "акт", "счёт", "счет", "фактура", "ПДВ", "ПДС", 
    "dalolatnomasi", "defekt", "nosozlik", "rasm"
]

def print_progress_bar(current: int, total: int, prefix: str = "", suffix: str = "", length: int = 50):
    """Выводит текстовый прогресс-бар"""
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '░' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)
    if current == total:
        print()  # Новая строка после завершения

def print_file_progress(file_num: int, total_files: int, filename: str, status: str = ""):
    """Выводит прогресс обработки файлов"""
    percent = (file_num / float(total_files)) * 100
    filled = int(50 * file_num // total_files)
    bar = '█' * filled + '░' * (50 - filled)
    print(f'\r📁 Файл {file_num}/{total_files} |{bar}| {percent:.1f}% - {filename[:50]} {status}', end='', flush=True)

def print_page_progress(page_num: int, total_pages: int, elapsed: float = 0, status: str = "обработка"):
    """Выводит детальный прогресс для OCR операции"""
    percent = (page_num / float(total_pages)) * 100
    filled = int(50 * page_num // total_pages)
    bar = '█' * filled + '░' * (50 - filled)
    elapsed_str = f"{elapsed:.1f}с" if elapsed > 0 else ""
    print(f'\r  📄 Страница {page_num}/{total_pages} |{bar}| {percent:.1f}% {status} {elapsed_str}', end='', flush=True)

def get_priority_score(filename: str) -> int:
    """Вычисляет приоритет файла на основе ключевых слов"""
    filename_lower = filename.lower()
    score = 0
    for keyword in PRIORITY_KEYWORDS:
        if keyword.lower() in filename_lower:
            score += 1
    return score

def select_test_files(max_files: int = 15) -> List[Path]:
    """
    Выбирает файлы для теста:
    1. Небольшие файлы (< 500KB)
    2. Приоритетные для закрытия данных
    3. Разнообразные типы документов
    """
    all_files = []
    
    if not TEST_FILES_DIR.exists():
        logger.error(f"Директория не найдена: {TEST_FILES_DIR}")
        return []
    
    for file_path in TEST_FILES_DIR.iterdir():
        if file_path.suffix.lower() != '.pdf':
            continue
        
        file_size_kb = file_path.stat().st_size / 1024
        
        # Фильтр по размеру
        if file_size_kb < MIN_FILE_SIZE_KB or file_size_kb > MAX_FILE_SIZE_KB:
            continue
        
        # Вычисляем приоритет
        priority = get_priority_score(file_path.name)
        
        all_files.append({
            'path': file_path,
            'size_kb': file_size_kb,
            'priority': priority
        })
    
    # Сортируем по приоритету (сначала высокий), затем по размеру (сначала маленькие)
    all_files.sort(key=lambda x: (-x['priority'], x['size_kb']))
    
    # Берем первые max_files файлов
    selected = [f['path'] for f in all_files[:max_files]]
    
    logger.info(f"Выбрано {len(selected)} файлов из {len(all_files)} доступных")
    for i, f in enumerate(selected[:5], 1):
        logger.info(f"  {i}. {f.name} ({f.stat().st_size/1024:.1f} KB, приоритет: {get_priority_score(f.name)})")
    
    return selected

def process_single_page(
    image: Any,
    page_num: int,
    file_name: str,
    save_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """Обрабатывает одну страницу"""
    page_start = time.time()
    
    # Сохраняем изображение во временный файл
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        image.save(tmp.name, 'PNG')
        tmp_path = tmp.name
    
    page_result = {
        "page_number": page_num,
        "characters": 0,
        "tables_count": 0,
        "tables": [],
        "text": "",
        "processing_time_sec": 0,
        "error": None,
        "low_confidence": False,
        "confidence": 0.0,
        "adaptive_retry_used": False
    }
    
    try:
        # Сохраняем изображение, если нужно
        if save_dir and SAVE_TEST_FILES:
            save_path = save_dir / f"{file_name}_page{page_num}.png"
            image.save(save_path, 'PNG')
        
        # Вызываем OCR
        result = extract_with_gemini_vision(tmp_path, page_num=page_num)
        
        # Извлекаем данные из результата
        page_result["characters"] = len(result.get("text", ""))
        page_result["text"] = result.get("text", "")
        page_result["tables_count"] = len(result.get("tables", []))
        page_result["tables"] = result.get("tables", [])
        page_result["confidence"] = result.get("confidence", 0.0)
        page_result["low_confidence"] = result.get("low_confidence", False)
        page_result["adaptive_retry_used"] = result.get("adaptive_retry_used", False)
        
    except Exception as e:
        logger.error(f"Ошибка обработки страницы {page_num} файла {file_name}: {e}")
        page_result["error"] = str(e)
    finally:
        # Удаляем временный файл
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
    
    page_result["processing_time_sec"] = time.time() - page_start
    return page_result

def process_pages_parallel(
    images: List[Any],
    file_name: str,
    save_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Параллельная обработка страниц"""
    results = []
    lock = threading.Lock()
    
    def process_with_progress(page_num: int, image: Any):
        result = process_single_page(image, page_num, file_name, save_dir)
        with lock:
            results.append(result)
            print_page_progress(
                len(results),
                len(images),
                result["processing_time_sec"],
                "✅" if result["error"] is None else "❌"
            )
        return result
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_with_progress, i+1, img): (i+1, img)
            for i, img in enumerate(images)
        }
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Ошибка в потоке: {e}")
    
    # Сортируем результаты по номеру страницы
    results.sort(key=lambda x: x["page_number"])
    return results

def process_file(file_path: Path, file_num: int, total_files: int) -> Dict[str, Any]:
    """Обрабатывает один файл"""
    file_start = time.time()
    file_name = file_path.stem
    
    print_file_progress(file_num, total_files, file_name, "🔄 Начало обработки...")
    
    file_result = {
        "file_path": str(file_path),
        "file_name": file_path.name,
        "file_size_kb": file_path.stat().st_size / 1024,
        "pages": [],
        "total_characters": 0,
        "total_tables": 0,
        "total_pages": 0,
        "processing_time_sec": 0,
        "error": None,
        "low_confidence_pages": 0,
        "adaptive_retry_pages": 0,
        "avg_confidence": 0.0
    }
    
    # Создаем директорию для сохранения изображений этого файла
    if SAVE_TEST_FILES:
        file_save_dir = TEST_FILES_DIR_SAVE / file_name
        file_save_dir.mkdir(parents=True, exist_ok=True)
    else:
        file_save_dir = None
    
    try:
        # Конвертируем PDF в изображения
        print_file_progress(file_num, total_files, file_name, "📄 Конвертация PDF...")
        images = convert_from_path(str(file_path), dpi=200)
        file_result["total_pages"] = len(images)
        
        # Обрабатываем страницы
        print_file_progress(file_num, total_files, file_name, "🔍 OCR обработка...")
        print()  # Новая строка для прогресса страниц
        
        if USE_PARALLEL_PROCESSING and len(images) > 1:
            page_results = process_pages_parallel(images, file_name, file_save_dir)
        else:
            page_results = []
            for page_num, image in enumerate(images, 1):
                result = process_single_page(image, page_num, file_name, file_save_dir)
                page_results.append(result)
                print_page_progress(
                    page_num,
                    len(images),
                    result["processing_time_sec"],
                    "✅" if result["error"] is None else "❌"
                )
        
        print()  # Новая строка после прогресса страниц
        
        # Агрегируем результаты
        file_result["pages"] = page_results
        file_result["total_characters"] = sum(p.get("characters", 0) for p in page_results)
        file_result["total_tables"] = sum(p.get("tables_count", 0) for p in page_results)
        file_result["low_confidence_pages"] = sum(1 for p in page_results if p.get("low_confidence", False))
        file_result["adaptive_retry_pages"] = sum(1 for p in page_results if p.get("adaptive_retry_used", False))
        
        confidences = [p.get("confidence", 0.0) for p in page_results if p.get("confidence", 0.0) > 0]
        if confidences:
            file_result["avg_confidence"] = sum(confidences) / len(confidences)
        
        print_file_progress(file_num, total_files, file_name, f"✅ Завершено ({file_result['total_characters']} символов, {file_result['total_tables']} таблиц)")
        
    except Exception as e:
        logger.error(f"Ошибка обработки файла {file_name}: {e}")
        file_result["error"] = str(e)
        print_file_progress(file_num, total_files, file_name, f"❌ Ошибка: {e}")
    
    file_result["processing_time_sec"] = time.time() - file_start
    print()  # Новая строка после завершения файла
    
    return file_result

def main():
    """Основная функция батч-теста"""
    print("=" * 80)
    print("РАСШИРЕННЫЙ БАТЧ-ТЕСТ OCR МОДУЛЯ")
    print("=" * 80)
    print(f"Директория: {TEST_FILES_DIR}")
    print(f"Максимальный размер файла: {MAX_FILE_SIZE_KB} KB")
    print(f"Параллельная обработка: {'✅' if USE_PARALLEL_PROCESSING else '❌'} (workers: {MAX_WORKERS})")
    print(f"Сохранение файлов: {'✅' if SAVE_TEST_FILES else '❌'}")
    print("=" * 80)
    print()
    
    # Выбираем файлы
    print("🔍 Поиск файлов...")
    test_files = select_test_files(max_files=15)
    
    if not test_files:
        logger.error("Не найдено файлов для теста")
        return
    
    print(f"\n✅ Выбрано {len(test_files)} файлов для теста\n")
    
    # Запускаем обработку
    batch_start = time.time()
    results = []
    errors = []
    
    for file_num, file_path in enumerate(test_files, 1):
        try:
            result = process_file(file_path, file_num, len(test_files))
            results.append(result)
            
            if result.get("error"):
                errors.append({
                    "file": result["file_name"],
                    "error": result["error"]
                })
        except Exception as e:
            logger.error(f"Критическая ошибка при обработке {file_path.name}: {e}")
            errors.append({
                "file": file_path.name,
                "error": str(e)
            })
    
    batch_time = time.time() - batch_start
    
    # Агрегируем статистику
    total_files = len(results)
    successful_files = sum(1 for r in results if r.get("error") is None)
    total_characters = sum(r.get("total_characters", 0) for r in results)
    total_tables = sum(r.get("total_tables", 0) for r in results)
    total_pages = sum(r.get("total_pages", 0) for r in results)
    low_confidence_count = sum(r.get("low_confidence_pages", 0) for r in results)
    adaptive_retry_count = sum(r.get("adaptive_retry_pages", 0) for r in results)
    
    avg_confidence = 0.0
    confidences = []
    for r in results:
        if r.get("avg_confidence", 0) > 0:
            confidences.append(r["avg_confidence"])
    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
    
    avg_time_per_page = batch_time / total_pages if total_pages > 0 else 0
    low_confidence_percent = (low_confidence_count / total_pages * 100) if total_pages > 0 else 0
    
    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = log_dir / f"extended_batch_results_{timestamp}.json"
    
    batch_summary = {
        "batch_start_time": datetime.now().isoformat(),
        "batch_size": len(test_files),
        "files": results,
        "summary": {
            "total_files": total_files,
            "successful_files": successful_files,
            "failed_files": len(errors),
            "total_characters": total_characters,
            "total_tables": total_tables,
            "total_pages": total_pages,
            "total_time_sec": round(batch_time, 2),
            "avg_time_per_page_sec": round(avg_time_per_page, 2),
            "low_confidence_pages": low_confidence_count,
            "low_confidence_percent": round(low_confidence_percent, 2),
            "adaptive_retry_pages": adaptive_retry_count,
            "avg_confidence": round(avg_confidence, 3),
            "errors": errors
        }
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(batch_summary, f, ensure_ascii=False, indent=2)
    
    # Выводим итоговый отчет
    print("\n" + "=" * 80)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 80)
    print(f"📁 Файлов обработано: {successful_files}/{total_files}")
    print(f"📄 Всего страниц: {total_pages}")
    print(f"📝 Всего символов: {total_characters:,}")
    print(f"📊 Всего таблиц: {total_tables}")
    print(f"⏱️  Общее время: {batch_time:.1f} сек ({batch_time/60:.1f} мин)")
    print(f"⏱️  Среднее время на страницу: {avg_time_per_page:.1f} сек")
    print(f"📊 Средний confidence: {avg_confidence:.3f}")
    print(f"⚠️  Low confidence страниц: {low_confidence_count} ({low_confidence_percent:.1f}%)")
    print(f"🔄 Адаптивная обработка использована: {adaptive_retry_count} страниц")
    print(f"❌ Ошибок: {len(errors)}")
    print(f"💾 Результаты сохранены: {results_file}")
    print("=" * 80)
    
    logger.info(f"Батч-тест завершен. Результаты: {results_file}")

if __name__ == "__main__":
    main()

