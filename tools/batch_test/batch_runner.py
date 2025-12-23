"""
Батч-тестирование OCR на 5 файлах (ШАГ 4)
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from pdf2image import convert_from_path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from gemini_vision_ocr import extract_with_gemini_vision

# Конфигурация
INPUT_DIR = Path(r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX")
OUTPUT_DIR = Path(__file__).parent / "results"
LOG_DIR = Path(__file__).parent.parent.parent / "reports" / "ocr"
BATCH_SIZE = 5  # Максимум 5 файлов
PAUSE_BETWEEN_BATCHES = 10  # Пауза между батчами (секунды)

# Создаём директории
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_pdf_files(directory, limit=5):
    """Получает список PDF файлов (максимум limit)"""
    pdf_files = list(directory.glob("*.pdf"))
    return pdf_files[:limit]

def process_file(pdf_path, file_index, total_files):
    """Обрабатывает один PDF файл"""
    print(f"\n[{file_index}/{total_files}] Обработка: {pdf_path.name}")
    start_time = time.time()
    
    file_result = {
        "file": str(pdf_path),
        "file_name": pdf_path.name,
        "pages": [],
        "total_characters": 0,
        "total_tables": 0,
        "total_time_sec": 0,
        "errors": [],
        "low_confidence_count": 0,
        "gemini_retries_count": 0
    }
    
    try:
        # Извлекаем страницы
        images = convert_from_path(str(pdf_path), dpi=300, poppler_path=None)
        print(f"  Извлечено страниц: {len(images)}")
        
        # Обрабатываем каждую страницу
        for page_num, img in enumerate(images, 1):
            print(f"  Страница {page_num}/{len(images)}...", end=" ", flush=True)
            page_start = time.time()
            
            # Сохраняем временное изображение
            temp_path = OUTPUT_DIR / f"{pdf_path.stem}_page{page_num}_temp.png"
            img.save(temp_path)
            
            try:
                # Вызываем OCR
                result = extract_with_gemini_vision(str(temp_path), page_num=page_num)
                
                # Собираем метрики
                page_time = time.time() - page_start
                characters = len(result.get('text', ''))
                tables_count = len(result.get('tables', []))
                has_low_confidence = 'validation_flag' in result and any('low_confidence' in f for f in result.get('validation_flag', []))
                
                if has_low_confidence:
                    file_result['low_confidence_count'] += 1
                
                file_result['pages'].append({
                    "page": page_num,
                    "characters": characters,
                    "tables_count": tables_count,
                    "time_sec": round(page_time, 2),
                    "confidence": result.get('confidence', 0.0),
                    "has_validation_flag": 'validation_flag' in result,
                    "validation_flags": result.get('validation_flag', [])
                })
                
                file_result['total_characters'] += characters
                file_result['total_tables'] += tables_count
                
                print(f"✅ {characters} символов, {tables_count} таблиц, {page_time:.1f}с")
                
                # Удаляем временный файл
                temp_path.unlink()
                
            except Exception as e:
                page_time = time.time() - page_start
                error_msg = str(e)
                file_result['errors'].append({
                    "page": page_num,
                    "error": error_msg,
                    "time_sec": round(page_time, 2)
                })
                print(f"❌ Ошибка: {error_msg[:50]}")
        
        file_result['total_time_sec'] = round(time.time() - start_time, 2)
        print(f"  ✅ Файл обработан: {file_result['total_time_sec']}с, "
              f"{file_result['total_characters']} символов, "
              f"{file_result['total_tables']} таблиц")
        
    except Exception as e:
        file_result['errors'].append({
            "file": str(pdf_path),
            "error": str(e)
        })
        print(f"  ❌ Критическая ошибка: {e}")
    
    return file_result

def main():
    """Основная функция батч-тестирования"""
    print("=" * 80)
    print("БАТЧ-ТЕСТИРОВАНИЕ OCR (ШАГ 4)")
    print("=" * 80)
    print(f"Входная директория: {INPUT_DIR}")
    print(f"Максимум файлов: {BATCH_SIZE}")
    print()
    
    # Получаем список файлов
    pdf_files = get_pdf_files(INPUT_DIR, limit=BATCH_SIZE)
    
    if not pdf_files:
        print("❌ PDF файлы не найдены!")
        return
    
    print(f"Найдено файлов для обработки: {len(pdf_files)}")
    for i, f in enumerate(pdf_files, 1):
        print(f"  {i}. {f.name}")
    print()
    
    # Обрабатываем файлы
    batch_start_time = time.time()
    results = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        file_result = process_file(pdf_file, i, len(pdf_files))
        results.append(file_result)
        
        # Пауза между файлами (кроме последнего)
        if i < len(pdf_files):
            print(f"\nПауза {PAUSE_BETWEEN_BATCHES} сек перед следующим файлом...")
            time.sleep(PAUSE_BETWEEN_BATCHES)
    
    batch_total_time = time.time() - batch_start_time
    
    # Собираем статистику
    total_files = len(results)
    total_pages = sum(len(r['pages']) for r in results)
    total_characters = sum(r['total_characters'] for r in results)
    total_tables = sum(r['total_tables'] for r in results)
    total_errors = sum(len(r['errors']) for r in results)
    total_low_confidence = sum(r['low_confidence_count'] for r in results)
    
    # Вычисляем средние значения
    avg_time_per_page = batch_total_time / total_pages if total_pages > 0 else 0
    error_rate = (total_errors / total_pages * 100) if total_pages > 0 else 0
    low_confidence_rate = (total_low_confidence / total_pages * 100) if total_pages > 0 else 0
    
    # Формируем итоговый отчёт
    report = {
        "test_date": datetime.now().isoformat(),
        "input_directory": str(INPUT_DIR),
        "total_files": total_files,
        "total_pages": total_pages,
        "statistics": {
            "total_time_sec": round(batch_total_time, 2),
            "avg_time_per_page_sec": round(avg_time_per_page, 2),
            "total_characters": total_characters,
            "total_tables": total_tables,
            "total_errors": total_errors,
            "error_rate_percent": round(error_rate, 2),
            "total_low_confidence": total_low_confidence,
            "low_confidence_rate_percent": round(low_confidence_rate, 2)
        },
        "files": results
    }
    
    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"batch_{timestamp}.json"
    log_file = LOG_DIR / "batch_run.log"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Логируем в batch_run.log
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()}|files={total_files}|pages={total_pages}|"
                f"time={batch_total_time:.2f}s|errors={total_errors}|"
                f"low_conf={total_low_confidence}|avg_time={avg_time_per_page:.2f}s\n")
    
    # Выводим итоги
    print()
    print("=" * 80)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 80)
    print(f"Файлов обработано: {total_files}")
    print(f"Страниц обработано: {total_pages}")
    print(f"Общее время: {batch_total_time:.2f} сек ({batch_total_time/60:.1f} мин)")
    print(f"Среднее время на страницу: {avg_time_per_page:.2f} сек")
    print(f"Всего символов: {total_characters:,}")
    print(f"Всего таблиц: {total_tables}")
    print(f"Ошибок: {total_errors} ({error_rate:.1f}%)")
    print(f"Страниц с low_confidence: {total_low_confidence} ({low_confidence_rate:.1f}%)")
    print()
    print(f"✅ Результаты сохранены: {output_file}")
    print(f"✅ Лог сохранён: {log_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
