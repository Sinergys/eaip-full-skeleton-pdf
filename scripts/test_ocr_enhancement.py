"""
Тестирование улучшений OCR на сканированных документах
Сравнивает точность OCR до и после применения image_enhancement
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Добавляем путь к сервисам
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

try:
    from utils.image_enhancement import (
        enhance_image_for_ocr,
        detect_skew_angle,
        deskew_image
    )
    HAS_ENHANCEMENT = True
except ImportError as e:
    print(f"⚠ Модуль image_enhancement недоступен: {e}")
    HAS_ENHANCEMENT = False

try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    print("⚠ pytesseract или PIL не установлены")
    HAS_OCR = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def extract_text_with_ocr(image_path: Path, enhanced: bool = False) -> Tuple[str, float]:
    """Извлечение текста через OCR"""
    if not HAS_OCR:
        return "", 0.0
    
    start_time = time.time()
    
    try:
        img = Image.open(image_path)
        
        if enhanced and HAS_ENHANCEMENT:
            # Применяем улучшения
            img = enhance_image_for_ocr(img)
        
        # OCR
        text = pytesseract.image_to_string(img, lang='rus+eng')
        elapsed_time = time.time() - start_time
        
        return text, elapsed_time
        
    except Exception as e:
        print(f"❌ Ошибка OCR: {e}")
        return "", 0.0

def calculate_ocr_accuracy(original_text: str, recognized_text: str) -> Dict[str, float]:
    """Расчет точности OCR (упрощенный метод)"""
    if not original_text or not recognized_text:
        return {
            "character_accuracy": 0.0,
            "word_accuracy": 0.0,
            "line_accuracy": 0.0
        }
    
    # Точность по символам (простой метод - сравнение длины)
    # В реальности нужен более сложный алгоритм (Levenshtein distance)
    orig_chars = len(original_text.replace(' ', '').replace('\n', ''))
    recog_chars = len(recognized_text.replace(' ', '').replace('\n', ''))
    char_accuracy = min(100.0, (recog_chars / orig_chars * 100) if orig_chars > 0 else 0.0)
    
    # Точность по словам
    orig_words = set(original_text.lower().split())
    recog_words = set(recognized_text.lower().split())
    if orig_words:
        matched_words = len(orig_words & recog_words)
        word_accuracy = (matched_words / len(orig_words)) * 100
    else:
        word_accuracy = 0.0
    
    # Точность по строкам
    orig_lines = original_text.split('\n')
    recog_lines = recognized_text.split('\n')
    if orig_lines:
        matched_lines = sum(1 for ol in orig_lines if any(ol.lower() in rl.lower() for rl in recog_lines))
        line_accuracy = (matched_lines / len(orig_lines)) * 100
    else:
        line_accuracy = 0.0
    
    return {
        "character_accuracy": char_accuracy,
        "word_accuracy": word_accuracy,
        "line_accuracy": line_accuracy,
        "average_accuracy": (char_accuracy + word_accuracy + line_accuracy) / 3
    }

def test_ocr_on_image(image_path: Path, reference_text: str = None) -> Dict[str, Any]:
    """Тестирование OCR на изображении"""
    print(f"\n{'='*80}")
    print(f"Тестирование OCR: {image_path.name}")
    print(f"{'='*80}")
    
    results = {
        "file": str(image_path),
        "file_name": image_path.name,
        "file_size_mb": image_path.stat().st_size / (1024 * 1024),
        "test_date": datetime.now().isoformat()
    }
    
    # OCR без улучшений
    print("📄 OCR без улучшений...")
    text_original, time_original = extract_text_with_ocr(image_path, enhanced=False)
    results["original"] = {
        "text_length": len(text_original),
        "processing_time": time_original,
        "text_preview": text_original[:200] + "..." if len(text_original) > 200 else text_original
    }
    
    # OCR с улучшениями
    if HAS_ENHANCEMENT:
        print("✨ OCR с улучшениями...")
        text_enhanced, time_enhanced = extract_text_with_ocr(image_path, enhanced=True)
        results["enhanced"] = {
            "text_length": len(text_enhanced),
            "processing_time": time_enhanced,
            "text_preview": text_enhanced[:200] + "..." if len(text_enhanced) > 200 else text_enhanced
        }
        
        # Сравнение
        improvement = len(text_enhanced) - len(text_original)
        improvement_pct = (improvement / len(text_original) * 100) if len(text_original) > 0 else 0
        
        results["comparison"] = {
            "text_length_improvement": improvement,
            "text_length_improvement_pct": improvement_pct,
            "time_increase": time_enhanced - time_original,
            "time_increase_pct": ((time_enhanced - time_original) / time_original * 100) if time_original > 0 else 0
        }
        
        print(f"✅ Улучшение длины текста: {improvement_pct:+.1f}%")
        print(f"⏱ Увеличение времени: {time_enhanced - time_original:.2f} сек")
        
        # Если есть эталонный текст, рассчитываем точность
        if reference_text:
            accuracy_original = calculate_ocr_accuracy(reference_text, text_original)
            accuracy_enhanced = calculate_ocr_accuracy(reference_text, text_enhanced)
            
            results["original"]["accuracy"] = accuracy_original
            results["enhanced"]["accuracy"] = accuracy_enhanced
            
            accuracy_improvement = accuracy_enhanced["average_accuracy"] - accuracy_original["average_accuracy"]
            results["comparison"]["accuracy_improvement"] = accuracy_improvement
            
            print(f"📊 Точность без улучшений: {accuracy_original['average_accuracy']:.1f}%")
            print(f"📊 Точность с улучшениями: {accuracy_enhanced['average_accuracy']:.1f}%")
            print(f"📈 Улучшение точности: {accuracy_improvement:+.1f}%")
    else:
        print("⚠ Модуль улучшений недоступен")
    
    return results

def convert_pdf_to_images(pdf_path: Path, output_dir: Path) -> List[Path]:
    """Конвертация PDF в изображения для OCR тестирования"""
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(str(pdf_path), dpi=300)
        image_paths = []
        
        for i, img in enumerate(images):
            img_path = output_dir / f"{pdf_path.stem}_page_{i+1}.png"
            img.save(img_path, "PNG")
            image_paths.append(img_path)
        
        return image_paths
    except ImportError:
        print("⚠ pdf2image не установлен, пропускаю конвертацию PDF")
        return []
    except Exception as e:
        print(f"❌ Ошибка конвертации PDF: {e}")
        return []

def main():
    """Основная функция"""
    if not HAS_OCR:
        print("❌ OCR недоступен (pytesseract не установлен)")
        return
    
    # Ищем тестовые изображения и PDF
    test_dirs = [
        PROJECT_ROOT / "eaip_full_skeleton" / "infra" / "data" / "inbox",
        PROJECT_ROOT / "data" / "source_files",
    ]
    
    image_files = []
    pdf_files = []
    
    for test_dir in test_dirs:
        if test_dir.exists():
            image_files.extend(list(test_dir.glob("*.png")))
            image_files.extend(list(test_dir.glob("*.jpg")))
            image_files.extend(list(test_dir.glob("*.jpeg")))
            pdf_files.extend(list(test_dir.glob("*.pdf")))
    
    # Конвертируем PDF в изображения
    if pdf_files:
        temp_images_dir = PROJECT_ROOT / "data" / "temp_images"
        temp_images_dir.mkdir(parents=True, exist_ok=True)
        
        for pdf_file in pdf_files[:2]:  # Ограничиваем 2 файлами
            print(f"🔄 Конвертация PDF в изображения: {pdf_file.name}")
            converted = convert_pdf_to_images(pdf_file, temp_images_dir)
            image_files.extend(converted)
    
    if not image_files:
        print("❌ Тестовые изображения не найдены!")
        return
    
    print(f"✅ Найдено {len(image_files)} изображений для тестирования")
    
    # Тестируем каждое изображение
    all_results = []
    for image_file in image_files[:5]:  # Ограничиваем 5 изображениями
        result = test_ocr_on_image(image_file)
        all_results.append(result)
    
    # Сохраняем результаты
    output_file = PROJECT_ROOT / "data" / "aggregated" / "ocr_enhancement_comparison.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: {output_file}")
    
    # Сводная статистика
    if all_results and HAS_ENHANCEMENT:
        print(f"\n{'='*80}")
        print("СВОДНАЯ СТАТИСТИКА")
        print(f"{'='*80}")
        
        improvements = [r["comparison"]["text_length_improvement_pct"] for r in all_results if "comparison" in r]
        if improvements:
            avg_improvement = sum(improvements) / len(improvements)
            print(f"📈 Среднее улучшение длины текста: {avg_improvement:+.1f}%")
        
        time_increases = [r["comparison"]["time_increase"] for r in all_results if "comparison" in r]
        if time_increases:
            avg_time_increase = sum(time_increases) / len(time_increases)
            print(f"⏱ Среднее увеличение времени: {avg_time_increase:.2f} сек")

if __name__ == "__main__":
    main()

