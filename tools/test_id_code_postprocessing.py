"""
Тест постобработки идентификационных кодов на проблемном файле
"""
import sys
from pathlib import Path
import json
from pdf2image import convert_from_path
import tempfile
import os

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eaip_full_skeleton.services.ingest.utils.gemini_vision_ocr import extract_with_gemini_vision

def test_id_code_postprocessing():
    """Тестирует постобработку идентификационных кодов на проблемном файле"""
    print("=" * 80)
    print("ШАГ 6: ТЕСТ ПОСТОБРАБОТКИ ИДЕНТИФИКАЦИОННЫХ КОДОВ")
    print("=" * 80)
    print()
    
    # Проблемный файл
    test_file = Path(r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\акт выполненых работ май.PDF")
    
    if not test_file.exists():
        print(f"❌ Файл не найден: {test_file}")
        return
    
    print(f"📄 Тестовый файл: {test_file.name}")
    print()
    
    # Конвертируем PDF в изображение
    print("📄 Конвертация PDF в изображение...")
    images = convert_from_path(str(test_file), dpi=200)
    if not images:
        print("❌ Ошибка: не удалось конвертировать PDF")
        return
    
    image = images[0]
    
    # Сохраняем временное изображение
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        image.save(tmp.name, 'PNG')
        temp_image_path = tmp.name
    
    try:
        # Обработка с постобработкой идентификационных кодов
        print("🔍 Распознавание с постобработкой идентификационных кодов...")
        result = extract_with_gemini_vision(temp_image_path, page_num=1, skip_adaptive_retry=False)
        
        # Сохраняем результаты
        output_file = project_root / "reports" / "ocr" / "step6_id_code_postprocessing_test.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "file_path": str(test_file),
                "file_name": test_file.name,
                "result": result,
                "id_codes_postprocessed": result.get('id_codes_postprocessed', False),
                "numbers_postprocessed": result.get('numbers_postprocessed', False)
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Результаты сохранены: {output_file}")
        print()
        print("📊 СТАТИСТИКА:")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Таблиц: {result.get('tables_count', 0)}")
        print(f"  Постобработка чисел: {'✅ Да' if result.get('numbers_postprocessed') else '❌ Нет'}")
        print(f"  Постобработка ID кодов: {'✅ Да' if result.get('id_codes_postprocessed') else '❌ Нет'}")
        
        # Показываем примеры идентификационных кодов
        if result.get('tables'):
            table = result['tables'][0]
            print()
            print("📋 Примеры идентификационных кодов из таблицы:")
            if table.get('rows'):
                # Показываем первые 5 строк с данными
                for i, row in enumerate(table['rows'][:6], 1):
                    if i == 1:
                        print(f"  Заголовки: {row[:3]}")
                    else:
                        print(f"  Строка {i-1}: ID код = '{row[1][:50] if len(row) > 1 else 'N/A'}'")
        
    finally:
        # Удаляем временный файл
        try:
            os.unlink(temp_image_path)
        except Exception:
            pass

if __name__ == "__main__":
    test_id_code_postprocessing()

