"""
Сохранение полных распознанных данных для файла акт выполненых работ май.PDF
"""
import sys
from pathlib import Path
import json
import tempfile
import os

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pdf2image import convert_from_path
from eaip_full_skeleton.services.ingest.utils.gemini_vision_ocr import extract_with_gemini_vision

# Проблемный файл
TEST_FILE = Path(r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX\акт выполненых работ май.PDF")

def save_full_data():
    """Сохраняет полные распознанные данные"""
    print("=" * 80)
    print("СОХРАНЕНИЕ ПОЛНЫХ РАСПОЗНАННЫХ ДАННЫХ")
    print("=" * 80)
    print(f"Файл: {TEST_FILE.name}")
    print()
    
    # Конвертируем PDF в изображение
    print("📄 Конвертация PDF в изображение...")
    images = convert_from_path(str(TEST_FILE), dpi=200)
    if not images:
        print("❌ Ошибка: не удалось конвертировать PDF")
        return
    
    image = images[0]
    
    # Сохраняем временное изображение
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        image.save(tmp.name, 'PNG')
        temp_image_path = tmp.name
    
    try:
        # Обработка с улучшениями
        print("🔍 Распознавание с улучшениями (ШАГИ 1-2)...")
        result = extract_with_gemini_vision(temp_image_path, page_num=1, skip_adaptive_retry=False)
        
        # Формируем полные данные
        output = {
            "file_path": str(TEST_FILE),
            "file_name": TEST_FILE.name,
            "file_size_kb": TEST_FILE.stat().st_size / 1024,
            "recognition_result": {
                "confidence": result.get('confidence', 0),
                "tables_count": result.get('tables_count', 0),
                "text": result.get('text', ''),
                "tables": result.get('tables', []),
                "parse_level": result.get('parse_level', 'N/A'),
                "adaptive_retry_used": result.get('adaptive_retry_used', False),
                "low_confidence": result.get('low_confidence', False)
            }
        }
        
        # Сохраняем
        out_file = project_root / "reports" / "ocr" / "recognized_data_akt_may.json"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Полные данные сохранены: {out_file}")
        print(f"\n📊 СТАТИСТИКА:")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Таблиц: {result.get('tables_count', 0)}")
        print(f"  Символов: {len(result.get('text', ''))}")
        
        tables = result.get('tables', [])
        if tables:
            table = tables[0]
            print(f"  Строк в таблице: {len(table.get('rows', []))}")
            print(f"  Столбцов в таблице: {len(table.get('headers', []))}")
        
    finally:
        # Удаляем временный файл
        try:
            os.unlink(temp_image_path)
        except Exception:
            pass

if __name__ == "__main__":
    save_full_data()

