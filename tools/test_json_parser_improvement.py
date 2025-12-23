"""
Тест улучшения парсера JSON для больших таблиц
Файл: акт выполненых работ май.PDF
"""
import sys
from pathlib import Path
import time
import json

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pdf2image import convert_from_path
from eaip_full_skeleton.services.ingest.utils.gemini_vision_ocr import extract_with_gemini_vision

# Проблемный файл
TEST_FILE = Path(r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\акт выполненых работ май.PDF")

def test_json_parser_improvement():
    """Тестирует улучшение парсера JSON для больших таблиц"""
    print("=" * 80)
    print("ТЕСТ: Улучшение парсера JSON для больших таблиц")
    print("=" * 80)
    print(f"Файл: {TEST_FILE.name}")
    print("Ожидаемая таблица: 10 столбцов, 33 строки данных")
    print()
    
    # Конвертируем PDF в изображение
    print("📄 Конвертация PDF в изображение...")
    images = convert_from_path(str(TEST_FILE), dpi=200)
    if not images:
        print("❌ Ошибка: не удалось конвертировать PDF")
        return
    
    image = images[0]
    
    # Сохраняем временное изображение
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        image.save(tmp.name, 'PNG')
        temp_image_path = tmp.name
    
    try:
        # Тест: Обработка с улучшенным парсером
        print("\n🔍 Тест: Обработка с улучшенным парсером JSON...")
        start_time = time.time()
        result = extract_with_gemini_vision(temp_image_path, page_num=1, skip_adaptive_retry=False)
        time_elapsed = time.time() - start_time
        
        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Таблиц найдено: {result.get('tables_count', 0)}")
        print(f"  Символов: {len(result.get('text', ''))}")
        print(f"  Время: {time_elapsed:.1f} сек")
        print(f"  Уровень парсинга: {result.get('parse_level', 'N/A')}")
        
        # Анализ таблиц
        tables = result.get('tables', [])
        if tables:
            print(f"\n📋 АНАЛИЗ ТАБЛИЦ:")
            for i, table in enumerate(tables, 1):
                rows = table.get('rows', [])
                headers = table.get('headers', [])
                row_count = len(rows)
                col_count = len(headers) if headers else (len(rows[0]) if rows else 0)
                
                print(f"\n  Таблица {i}:")
                print(f"    Строк: {row_count} (ожидается: 33)")
                print(f"    Столбцов: {col_count} (ожидается: 10)")
                print(f"    Заголовков: {len(headers)}")
                
                if headers:
                    print(f"    Заголовки: {headers[:5]}..." if len(headers) > 5 else f"    Заголовки: {headers}")
                
                if rows:
                    print(f"    Первая строка: {rows[0][:3]}..." if len(rows[0]) > 3 else f"    Первая строка: {rows[0]}")
                    print(f"    Последняя строка: {rows[-1][:3]}..." if len(rows[-1]) > 3 else f"    Последняя строка: {rows[-1]}")
                
                # Проверка полноты
                if row_count == 33 and col_count == 10:
                    print(f"    ✅ Таблица извлечена полностью!")
                elif row_count >= 30 and col_count >= 8:
                    print(f"    ⚠️  Таблица извлечена частично ({row_count}/{33} строк, {col_count}/10 столбцов)")
                else:
                    print(f"    ❌ Таблица извлечена неполно ({row_count}/{33} строк, {col_count}/10 столбцов)")
        else:
            print(f"\n❌ Таблицы не найдены")
        
        # Сохраняем результаты
        results = {
            "file": str(TEST_FILE),
            "result": {
                "confidence": result.get('confidence', 0),
                "tables_count": result.get('tables_count', 0),
                "characters": len(result.get('text', '')),
                "time_sec": time_elapsed,
                "parse_level": result.get('parse_level', 'N/A'),
                "adaptive_retry_used": result.get('adaptive_retry_used', False)
            },
            "tables": []
        }
        
        for i, table in enumerate(tables, 1):
            table_info = {
                "table_number": i,
                "row_count": len(table.get('rows', [])),
                "col_count": len(table.get('headers', [])) if table.get('headers') else (len(table.get('rows', [])[0]) if table.get('rows') else 0),
                "headers_count": len(table.get('headers', [])),
                "headers": table.get('headers', [])[:5],  # Первые 5 заголовков
                "first_row": table.get('rows', [])[0][:5] if table.get('rows') else [],
                "last_row": table.get('rows', [])[-1][:5] if table.get('rows') else []
            }
            results["tables"].append(table_info)
        
        results_file = project_root / "reports" / "ocr" / "step2_json_parser_test.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены: {results_file}")
        
        # Вывод
        print("\n" + "=" * 80)
        if tables:
            table = tables[0]
            row_count = len(table.get('rows', []))
            col_count = len(table.get('headers', [])) if table.get('headers') else (len(table.get('rows', [])[0]) if table.get('rows') else 0)
            
            if row_count == 33 and col_count == 10:
                print("✅ УСПЕХ: Таблица 10×33 извлечена полностью!")
            elif row_count >= 30 and col_count >= 8:
                print(f"⚠️  ЧАСТИЧНЫЙ УСПЕХ: Таблица извлечена частично ({row_count}/33 строк, {col_count}/10 столбцов)")
            else:
                print(f"❌ НЕУДАЧА: Таблица извлечена неполно ({row_count}/33 строк, {col_count}/10 столбцов)")
        else:
            print("❌ НЕУДАЧА: Таблицы не найдены")
        print("=" * 80)
        
    finally:
        # Удаляем временный файл
        import os
        try:
            os.unlink(temp_image_path)
        except Exception:
            pass

if __name__ == "__main__":
    test_json_parser_improvement()

