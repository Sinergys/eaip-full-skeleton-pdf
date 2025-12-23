"""
ШАГ 7: Расширенное тестирование улучшений на других файлах
Проверяет эффективность всех улучшений (ШАГИ 1-6) на реальных документах
"""
import sys
from pathlib import Path
import json
from pdf2image import convert_from_path
import tempfile
import os
from datetime import datetime
from typing import List, Dict, Any

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eaip_full_skeleton.services.ingest.utils.gemini_vision_ocr import extract_with_gemini_vision

def get_test_files(directory: Path, max_files: int = 5) -> List[Path]:
    """
    Выбирает тестовые файлы для проверки улучшений
    
    Критерии:
    - PDF файлы
    - Небольшой размер (< 1 MB)
    - Релевантные для данных Навои
    """
    files = []
    
    if not directory.exists():
        print(f"⚠️  Директория не найдена: {directory}")
        return files
    
    # Ищем PDF файлы
    for file_path in directory.glob("*.PDF"):
        if file_path.stat().st_size < 1024 * 1024:  # < 1 MB
            files.append(file_path)
            if len(files) >= max_files:
                break
    
    # Если не нашли, пробуем .pdf
    if len(files) < max_files:
        for file_path in directory.glob("*.pdf"):
            if file_path.stat().st_size < 1024 * 1024:
                if file_path not in files:
                    files.append(file_path)
                    if len(files) >= max_files:
                        break
    
    return files

def process_file(file_path: Path) -> Dict[str, Any]:
    """Обрабатывает один файл с улучшениями ШАГОВ 1-6"""
    result = {
        "file_path": str(file_path),
        "file_name": file_path.name,
        "file_size_kb": file_path.stat().st_size / 1024,
        "pages": [],
        "total_characters": 0,
        "total_tables": 0,
        "total_pages": 0,
        "processing_time_sec": 0,
        "errors": [],
        "improvements_applied": {
            "light_image_enhancement": True,  # ШАГ 1
            "json_parser_improvement": True,  # ШАГ 2
            "number_postprocessing": False,
            "id_code_postprocessing": False
        }
    }
    
    start_time = datetime.now()
    
    try:
        # Конвертируем PDF в изображения
        images = convert_from_path(str(file_path), dpi=200)
        
        if not images:
            result["errors"].append("Не удалось конвертировать PDF в изображения")
            return result
        
        result["total_pages"] = len(images)
        
        # Обрабатываем каждую страницу
        for page_num, image in enumerate(images, 1):
            page_start = datetime.now()
            
            # Сохраняем временное изображение
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                image.save(tmp.name, 'PNG')
                temp_image_path = tmp.name
            
            try:
                # Обработка с улучшениями ШАГОВ 1-6
                page_result = extract_with_gemini_vision(
                    temp_image_path, 
                    page_num=page_num, 
                    skip_adaptive_retry=False
                )
                
                page_time = (datetime.now() - page_start).total_seconds()
                
                # Проверяем, какие улучшения были применены
                if page_result.get('numbers_postprocessed'):
                    result["improvements_applied"]["number_postprocessing"] = True
                if page_result.get('id_codes_postprocessed'):
                    result["improvements_applied"]["id_code_postprocessing"] = True
                
                page_data = {
                    "page_number": page_num,
                    "characters": len(page_result.get('text', '')),
                    "tables_count": page_result.get('tables_count', 0),
                    "confidence": page_result.get('confidence', 0),
                    "processing_time_sec": page_time,
                    "error": page_result.get('error'),
                    "low_confidence": page_result.get('low_confidence', False),
                    "adaptive_retry_used": page_result.get('adaptive_retry_used', False),
                    "numbers_postprocessed": page_result.get('numbers_postprocessed', False),
                    "id_codes_postprocessed": page_result.get('id_codes_postprocessed', False),
                    "parse_level": page_result.get('parse_level', 'N/A')
                }
                
                result["pages"].append(page_data)
                result["total_characters"] += page_data["characters"]
                result["total_tables"] += page_data["tables_count"]
                
            except Exception as e:
                result["errors"].append(f"Страница {page_num}: {str(e)}")
            finally:
                try:
                    os.unlink(temp_image_path)
                except Exception:
                    pass
        
        result["processing_time_sec"] = (datetime.now() - start_time).total_seconds()
        
    except Exception as e:
        result["errors"].append(f"Общая ошибка: {str(e)}")
    
    return result

def main():
    """Основная функция"""
    print("=" * 80)
    print("ШАГ 7: РАСШИРЕННОЕ ТЕСТИРОВАНИЕ УЛУЧШЕНИЙ")
    print("=" * 80)
    print()
    
    # Директория с файлами
    inbox_dir = Path(r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX")
    
    # Выбираем тестовые файлы
    print("📁 Поиск тестовых файлов...")
    test_files = get_test_files(inbox_dir, max_files=5)
    
    if not test_files:
        print("❌ Не найдено подходящих файлов для тестирования")
        return
    
    print(f"✅ Найдено {len(test_files)} файлов для тестирования:")
    for i, f in enumerate(test_files, 1):
        print(f"  {i}. {f.name} ({f.stat().st_size/1024:.1f} KB)")
    print()
    
    # Обрабатываем файлы
    results = []
    for i, file_path in enumerate(test_files, 1):
        print(f"📄 Обработка файла {i}/{len(test_files)}: {file_path.name}")
        result = process_file(file_path)
        results.append(result)
        
        # Показываем краткую статистику
        print(f"  ✅ Страниц: {result['total_pages']}, Символов: {result['total_characters']}, "
              f"Таблиц: {result['total_tables']}, Время: {result['processing_time_sec']:.1f}с")
        print(f"  📊 Confidence: {sum(p.get('confidence', 0) for p in result['pages'])/len(result['pages']) if result['pages'] else 0:.2f}")
        print(f"  🔧 Улучшения: Числа={result['improvements_applied']['number_postprocessing']}, "
              f"ID коды={result['improvements_applied']['id_code_postprocessing']}")
        if result['errors']:
            print(f"  ⚠️  Ошибок: {len(result['errors'])}")
        print()
    
    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = project_root / "reports" / "ocr" / f"step7_batch_test_results_{timestamp}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    summary = {
        "test_date": timestamp,
        "total_files": len(results),
        "total_pages": sum(r['total_pages'] for r in results),
        "total_characters": sum(r['total_characters'] for r in results),
        "total_tables": sum(r['total_tables'] for r in results),
        "total_processing_time_sec": sum(r['processing_time_sec'] for r in results),
        "total_errors": sum(len(r['errors']) for r in results),
        "files_with_errors": sum(1 for r in results if r['errors']),
        "improvements_applied": {
            "number_postprocessing": sum(1 for r in results if r['improvements_applied']['number_postprocessing']),
            "id_code_postprocessing": sum(1 for r in results if r['improvements_applied']['id_code_postprocessing'])
        },
        "files": results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # Создаем Markdown отчет
    md_file = output_file.with_suffix('.md')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# ШАГ 7: РАСШИРЕННОЕ ТЕСТИРОВАНИЕ УЛУЧШЕНИЙ\n\n")
        f.write(f"**Дата:** {timestamp}\n\n")
        f.write("---\n\n")
        
        f.write("## 📊 СВОДКА\n\n")
        f.write(f"- **Файлов протестировано:** {summary['total_files']}\n")
        f.write(f"- **Всего страниц:** {summary['total_pages']}\n")
        f.write(f"- **Всего символов:** {summary['total_characters']:,}\n")
        f.write(f"- **Всего таблиц:** {summary['total_tables']}\n")
        f.write(f"- **Общее время обработки:** {summary['total_processing_time_sec']:.1f} сек\n")
        f.write(f"- **Среднее время на файл:** {summary['total_processing_time_sec']/summary['total_files']:.1f} сек\n")
        f.write(f"- **Среднее время на страницу:** {summary['total_processing_time_sec']/summary['total_pages']:.1f} сек\n")
        f.write(f"- **Файлов с ошибками:** {summary['files_with_errors']}\n")
        f.write(f"- **Всего ошибок:** {summary['total_errors']}\n\n")
        
        f.write("## 🔧 ПРИМЕНЕННЫЕ УЛУЧШЕНИЯ\n\n")
        f.write(f"- **Постобработка чисел:** {summary['improvements_applied']['number_postprocessing']}/{summary['total_files']} файлов\n")
        f.write(f"- **Постобработка ID кодов:** {summary['improvements_applied']['id_code_postprocessing']}/{summary['total_files']} файлов\n\n")
        
        f.write("## 📋 РЕЗУЛЬТАТЫ ПО ФАЙЛАМ\n\n")
        for i, file_result in enumerate(results, 1):
            f.write(f"### Файл {i}: {file_result['file_name']}\n\n")
            f.write(f"- **Размер:** {file_result['file_size_kb']:.1f} KB\n")
            f.write(f"- **Страниц:** {file_result['total_pages']}\n")
            f.write(f"- **Символов:** {file_result['total_characters']:,}\n")
            f.write(f"- **Таблиц:** {file_result['total_tables']}\n")
            f.write(f"- **Время обработки:** {file_result['processing_time_sec']:.1f} сек\n")
            
            if file_result['pages']:
                avg_confidence = sum(p.get('confidence', 0) for p in file_result['pages']) / len(file_result['pages'])
                f.write(f"- **Средний confidence:** {avg_confidence:.2%}\n")
            
            if file_result['errors']:
                f.write(f"- **Ошибки:** {len(file_result['errors'])}\n")
                for error in file_result['errors']:
                    f.write(f"  - {error}\n")
            
            f.write("\n")
    
    print("=" * 80)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 80)
    print()
    print(f"📄 JSON: {output_file}")
    print(f"📄 Markdown: {md_file}")
    print()
    print("📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"  - Файлов: {summary['total_files']}")
    print(f"  - Страниц: {summary['total_pages']}")
    print(f"  - Символов: {summary['total_characters']:,}")
    print(f"  - Таблиц: {summary['total_tables']}")
    print(f"  - Время: {summary['total_processing_time_sec']:.1f} сек")
    print(f"  - Ошибок: {summary['total_errors']}")
    print()

if __name__ == "__main__":
    main()

