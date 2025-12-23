"""
Тест улучшения светлых изображений на проблемном файле
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

def test_light_image_enhancement():
    """Тестирует улучшение светлых изображений"""
    print("=" * 80)
    print("ТЕСТ: Улучшение светлых изображений")
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
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        image.save(tmp.name, 'PNG')
        temp_image_path = tmp.name
    
    try:
        # Тест 1: Обработка БЕЗ улучшения (для сравнения)
        print("\n🔍 Тест 1: Обработка БЕЗ улучшения...")
        start_time = time.time()
        result_before = extract_with_gemini_vision(temp_image_path, page_num=1, skip_adaptive_retry=True)
        time_before = time.time() - start_time
        
        print(f"  Confidence: {result_before.get('confidence', 0):.2f}")
        print(f"  Таблиц: {result_before.get('tables_count', 0)}")
        print(f"  Символов: {len(result_before.get('text', ''))}")
        print(f"  Время: {time_before:.1f} сек")
        
        # Тест 2: Обработка С улучшением (адаптивная обработка включена)
        print("\n✨ Тест 2: Обработка С улучшением светлых изображений...")
        start_time = time.time()
        result_after = extract_with_gemini_vision(temp_image_path, page_num=1, skip_adaptive_retry=False)
        time_after = time.time() - start_time
        
        print(f"  Confidence: {result_after.get('confidence', 0):.2f}")
        print(f"  Таблиц: {result_after.get('tables_count', 0)}")
        print(f"  Символов: {len(result_after.get('text', ''))}")
        print(f"  Время: {time_after:.1f} сек")
        print(f"  Адаптивная обработка использована: {result_after.get('adaptive_retry_used', False)}")
        if result_after.get('adaptive_retry_used'):
            print(f"  Улучшение confidence: {result_after.get('confidence_improvement', 0):.2f}")
        
        # Сравнение
        print("\n" + "=" * 80)
        print("СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
        print("=" * 80)
        
        confidence_before = result_before.get('confidence', 0)
        confidence_after = result_after.get('confidence', 0)
        confidence_improvement = confidence_after - confidence_before
        
        tables_before = result_before.get('tables_count', 0)
        tables_after = result_after.get('tables_count', 0)
        tables_improvement = tables_after - tables_before
        
        print(f"Confidence: {confidence_before:.2f} → {confidence_after:.2f} ({confidence_improvement:+.2f})")
        print(f"Таблиц: {tables_before} → {tables_after} ({tables_improvement:+d})")
        print(f"Время: {time_before:.1f} сек → {time_after:.1f} сек ({time_after - time_before:+.1f} сек)")
        
        # Сохраняем результаты
        results = {
            "file": str(TEST_FILE),
            "before": {
                "confidence": confidence_before,
                "tables_count": tables_before,
                "characters": len(result_before.get('text', '')),
                "time_sec": time_before
            },
            "after": {
                "confidence": confidence_after,
                "tables_count": tables_after,
                "characters": len(result_after.get('text', '')),
                "time_sec": time_after,
                "adaptive_retry_used": result_after.get('adaptive_retry_used', False),
                "confidence_improvement": confidence_improvement
            },
            "improvement": {
                "confidence_delta": confidence_improvement,
                "confidence_percent": (confidence_improvement / confidence_before * 100) if confidence_before > 0 else 0,
                "tables_delta": tables_improvement,
                "time_delta": time_after - time_before
            }
        }
        
        results_file = project_root / "reports" / "ocr" / "step1_light_enhancement_test.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены: {results_file}")
        
        # Вывод
        print("\n" + "=" * 80)
        if confidence_improvement > 0:
            print(f"✅ УЛУЧШЕНИЕ: Confidence увеличен на {confidence_improvement:.2f} ({confidence_improvement/confidence_before*100:.1f}%)")
        else:
            print(f"⚠️  Confidence не улучшился")
        
        if tables_improvement > 0:
            print(f"✅ УЛУЧШЕНИЕ: Таблиц найдено на {tables_improvement} больше")
        else:
            print(f"⚠️  Таблицы не извлечены (требуется улучшение парсера JSON)")
        
        print("=" * 80)
        
    finally:
        # Удаляем временный файл
        import os
        try:
            os.unlink(temp_image_path)
        except Exception:
            pass

if __name__ == "__main__":
    test_light_image_enhancement()

