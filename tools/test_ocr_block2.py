"""
БЛОК 2: OCR РАСПОЗНАВАНИЕ
Тестирование OCR на реальных PDF документах
"""
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Добавляем путь к сервису ingest
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

TEST_FILES = [
    {
        "name": "CamScanner 17-04-2025 15.17.pdf",
        "path": r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\CamScanner 17-04-2025 15.17.pdf",
        "description": "Сканированный документ (CamScanner), 4 страницы"
    },
    {
        "name": "Navoiy IES 06. 2023.PDF",
        "path": r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\Акт баланс 2023\акт реализация НЭС 2023\Navoiy IES 06. 2023.PDF",
        "description": "Акт баланс (реализация НЭС) за июнь 2023, 1 страница"
    }
]

def test_ocr_direct(file_path, file_name):
    """Прямое тестирование OCR через file_parser"""
    print(f"\n{'='*60}")
    print(f"Тестирование OCR: {file_name}")
    print(f"{'='*60}")
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return None
    
    try:
        from file_parser import parse_file
        import PyPDF2
        
        print(f"📂 Файл: {file_path}")
        file_size = os.path.getsize(file_path)
        print(f"📏 Размер: {file_size / 1024:.1f} KB")
        
        # Определяем количество страниц для оценки времени
        try:
            pdf = PyPDF2.PdfReader(file_path)
            page_count = len(pdf.pages)
            print(f"📄 Страниц: {page_count}")
            print(f"⏱️  Оценочное время OCR: ~{page_count * 30} секунд (30 сек/страница)")
        except:
            print(f"📄 Не удалось определить количество страниц")
            page_count = 0
        
        print(f"\n⏳ Начало парсинга (OCR)...")
        print(f"   Оценочное время: ~{page_count * 30} секунд ({page_count} страниц × 30 сек/страница)")
        print(f"   Прогресс:")
        print(f"   [░░░░░░░░░░░░░░░░░░░░] 0%")
        
        start_time = time.time()
        last_progress_time = start_time
        
        # Функция для отображения прогресса
        def show_progress(elapsed, estimated_total):
            if estimated_total > 0:
                percent = min(100, int((elapsed / estimated_total) * 100))
                filled = int(percent / 5)
                bar = "█" * filled + "░" * (20 - filled)
                print(f"\r   [{bar}] {percent}% ({elapsed:.0f}с / ~{estimated_total:.0f}с)", end="", flush=True)
        
        # Запускаем парсинг в отдельном потоке для отслеживания прогресса
        import threading
        parsing_complete = threading.Event()
        parsing_result = [None]
        parsing_error = [None]
        
        def parse_thread():
            try:
                parsing_result[0] = parse_file(file_path, batch_id=None)
            except Exception as e:
                parsing_error[0] = e
            finally:
                parsing_complete.set()
        
        thread = threading.Thread(target=parse_thread, daemon=True)
        thread.start()
        
        # Отслеживаем прогресс
        estimated_time = page_count * 30 if page_count > 0 else 120
        while not parsing_complete.is_set():
            elapsed = time.time() - start_time
            show_progress(elapsed, estimated_time)
            if parsing_complete.wait(timeout=2):
                break
        
        processing_time = time.time() - start_time
        print(f"\r   [████████████████████] 100% ({processing_time:.1f}с)        ")
        
        if parsing_error[0]:
            raise parsing_error[0]
        
        result = parsing_result[0]
        
        print(f"\n✅ Парсинг завершен за {processing_time:.1f}с!")
        
        # Извлечение OCR данных
        data = result.get('data', {})
        
        ocr_info = {
            'file_name': file_name,
            'file_path': file_path,
            'file_size_kb': round(file_size / 1024, 1),
            'processing_time_sec': round(processing_time, 2),
            'parsed': result.get('parsed', False),
            'file_type': result.get('file_type', 'unknown'),
            'ocr_used': data.get('ocr_used', False),
            'ocr_success': data.get('ocr_success', False),
            'ocr_attempted': data.get('ocr_attempted', False),
            'total_characters': data.get('total_characters', 0),
            'total_tables': data.get('total_tables', 0),
            'pages': data.get('metadata', {}).get('num_pages', 0),
            'is_scanned': data.get('is_scanned', False),
            'scanned_confidence': data.get('scanned_confidence', 'unknown'),
            'pdf_type': data.get('pdf_type', 'unknown'),
            'processing_strategy': data.get('processing_strategy', 'unknown'),
        }
        
        # Извлечение текста (первые 500 символов для отчета)
        if data.get('text'):
            ocr_info['text_preview'] = data['text'][:500]
            ocr_info['text_length'] = len(data['text'])
        else:
            ocr_info['text_preview'] = None
            ocr_info['text_length'] = 0
        
        # Информация о таблицах
        tables = data.get('tables', [])
        ocr_info['tables'] = []
        for table in tables[:3]:  # Первые 3 таблицы
            ocr_info['tables'].append({
                'page': table.get('page', 0),
                'method': table.get('method', 'unknown'),
                'row_count': table.get('row_count', 0),
                'col_count': table.get('col_count', 0),
                'confidence': table.get('confidence', 'unknown'),
            })
        
        # Ошибки OCR
        if data.get('ocr_error'):
            ocr_info['ocr_error'] = data.get('ocr_error')
        
        # AI валидация (если есть)
        if data.get('ai_validation'):
            ocr_info['ai_validation'] = {
                'is_valid': data['ai_validation'].get('is_valid', False),
                'confidence': data['ai_validation'].get('confidence', 0.0),
                'issues_count': len(data['ai_validation'].get('issues', [])),
            }
        
        print(f"\n✅ Парсинг завершен за {processing_time:.1f}с")
        print(f"   OCR использован: {ocr_info['ocr_used']}")
        print(f"   OCR успешен: {ocr_info['ocr_success']}")
        print(f"   Распознано символов: {ocr_info['total_characters']}")
        print(f"   Найдено таблиц: {ocr_info['total_tables']}")
        print(f"   Страниц: {ocr_info['pages']}")
        
        return {
            'result': result,
            'ocr_info': ocr_info
        }
        
    except Exception as e:
        print(f"❌ Ошибка при парсинге: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 60)
    print("БЛОК 2: OCR РАСПОЗНАВАНИЕ")
    print("=" * 60)
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    for file_info in TEST_FILES:
        file_path = file_info['path']
        file_name = file_info['name']
        description = file_info['description']
        
        print(f"\n📄 Файл: {file_name}")
        print(f"   Описание: {description}")
        
        test_result = test_ocr_direct(file_path, file_name)
        
        if test_result:
            results.append({
                'file_info': file_info,
                'ocr_info': test_result['ocr_info'],
                'parsing_result': {
                    'parsed': test_result['result'].get('parsed', False),
                    'file_type': test_result['result'].get('file_type'),
                }
            })
    
    # Сохранение результатов
    output_file = Path(__file__).parent / "ocr_test_results_block2.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'block': 'BLOCK_2_OCR_RECOGNITION',
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print("ОТЧЕТ БЛОКА 2")
    print(f"{'='*60}")
    
    for i, result in enumerate(results, 1):
        ocr = result['ocr_info']
        print(f"\n{i}. {ocr['file_name']}")
        print(f"   Статус обработки: {'✅ Успешно' if ocr['parsed'] else '❌ Ошибка'}")
        print(f"   Количество распознанных символов: {ocr['total_characters']}")
        print(f"   Количество найденных таблиц: {ocr['total_tables']}")
        print(f"   Время обработки: {ocr['processing_time_sec']}с")
        print(f"   OCR использован: {ocr['ocr_used']}")
        print(f"   OCR успешен: {ocr['ocr_success']}")
        print(f"   Путь к результатам: БД (parsed_data.raw_json), batch_id не используется (прямой вызов)")
        
        if ocr.get('ocr_error'):
            print(f"   ⚠️  OCR ошибка: {ocr['ocr_error']}")
    
    print(f"\n📁 Результаты сохранены: {output_file}")
    print(f"\nБЛОК 2 ЗАВЕРШЕН. Жду команды для БЛОКА 3.")

if __name__ == "__main__":
    main()

