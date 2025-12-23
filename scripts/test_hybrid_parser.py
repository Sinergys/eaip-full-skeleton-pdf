"""
Тестирование гибридного парсера таблиц
Сравнивает результаты старого и нового подходов
"""

import json
import time
from pathlib import Path
from datetime import datetime

# Добавляем путь к сервисам
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

from utils.table_detector import (
    detect_pdf_type,
    hybrid_table_extraction,
    extract_tables_from_pdf
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_pdf_type_detection():
    """Тестирование определения типа PDF"""
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ОПРЕДЕЛЕНИЯ ТИПА PDF")
    print("=" * 80)
    
    # Ищем тестовые PDF файлы
    test_dirs = [
        PROJECT_ROOT / "eaip_full_skeleton" / "infra" / "data" / "inbox",
    ]
    
    pdf_files = []
    for test_dir in test_dirs:
        if test_dir.exists():
            pdf_files.extend(list(test_dir.glob("*.pdf")))
    
    if not pdf_files:
        print("❌ Тестовые PDF файлы не найдены!")
        return
    
    print(f"\n✅ Найдено {len(pdf_files)} PDF файлов для тестирования\n")
    
    results = []
    for pdf_file in pdf_files[:3]:  # Ограничиваем 3 файлами
        print(f"📄 Файл: {pdf_file.name}")
        pdf_type = detect_pdf_type(str(pdf_file))
        print(f"   Тип: {pdf_type}")
        print()
        
        results.append({
            "file": str(pdf_file),
            "file_name": pdf_file.name,
            "file_size_mb": pdf_file.stat().st_size / (1024 * 1024),
            "detected_type": pdf_type
        })
    
    # Сохраняем результаты
    output_file = PROJECT_ROOT / "data" / "aggregated" / "pdf_type_detection.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Результаты сохранены в: {output_file}")
    return results

def test_hybrid_vs_old():
    """Сравнение гибридного парсера со старым подходом"""
    print("\n" + "=" * 80)
    print("СРАВНЕНИЕ ГИБРИДНОГО ПАРСЕРА СО СТАРЫМ ПОДХОДОМ")
    print("=" * 80)
    
    # Ищем тестовые PDF файлы
    test_dirs = [
        PROJECT_ROOT / "eaip_full_skeleton" / "infra" / "data" / "inbox",
    ]
    
    pdf_files = []
    for test_dir in test_dirs:
        if test_dir.exists():
            pdf_files.extend(list(test_dir.glob("*.pdf")))
    
    if not pdf_files:
        print("❌ Тестовые PDF файлы не найдены!")
        return
    
    print(f"\n✅ Найдено {len(pdf_files)} PDF файлов для тестирования\n")
    
    all_results = []
    
    for pdf_file in pdf_files[:3]:  # Ограничиваем 3 файлами
        print(f"\n{'='*80}")
        print(f"Тестирование: {pdf_file.name}")
        print(f"{'='*80}")
        
        # Определяем тип
        pdf_type = detect_pdf_type(str(pdf_file))
        print(f"Тип PDF: {pdf_type}")
        
        result = {
            "file": str(pdf_file),
            "file_name": pdf_file.name,
            "file_size_mb": pdf_file.stat().st_size / (1024 * 1024),
            "detected_type": pdf_type,
            "test_date": datetime.now().isoformat()
        }
        
        # Старый подход
        print("\n📊 Старый подход (extract_tables_from_pdf)...")
        start_time = time.time()
        try:
            old_tables = extract_tables_from_pdf(str(pdf_file))
            old_time = time.time() - start_time
            result["old_approach"] = {
                "tables_found": len(old_tables),
                "processing_time": old_time,
                "tables": [{"rows": len(t.get("rows", [])), "cols": t.get("col_count", 0)} for t in old_tables]
            }
            print(f"   ✅ Найдено таблиц: {len(old_tables)}")
            print(f"   ⏱ Время: {old_time:.2f} сек")
        except Exception as e:
            result["old_approach"] = {"error": str(e)}
            print(f"   ❌ Ошибка: {e}")
        
        # Новый подход (гибридный)
        print("\n🚀 Гибридный подход (hybrid_table_extraction)...")
        start_time = time.time()
        try:
            hybrid_tables = hybrid_table_extraction(str(pdf_file))
            hybrid_time = time.time() - start_time
            result["hybrid_approach"] = {
                "tables_found": len(hybrid_tables),
                "processing_time": hybrid_time,
                "tables": [{"rows": len(t.get("rows", [])), "cols": t.get("col_count", 0)} for t in hybrid_tables]
            }
            print(f"   ✅ Найдено таблиц: {len(hybrid_tables)}")
            print(f"   ⏱ Время: {hybrid_time:.2f} сек")
            
            # Сравнение
            improvement = len(hybrid_tables) - len(old_tables) if "old_approach" in result and "tables_found" in result["old_approach"] else 0
            if improvement > 0:
                print(f"   📈 Улучшение: +{improvement} таблиц")
            elif improvement < 0:
                print(f"   📉 Ухудшение: {improvement} таблиц")
            else:
                print("   ➡️  Без изменений")
                
        except Exception as e:
            result["hybrid_approach"] = {"error": str(e)}
            print(f"   ❌ Ошибка: {e}")
        
        all_results.append(result)
    
    # Сохраняем результаты
    output_file = PROJECT_ROOT / "data" / "aggregated" / "hybrid_parser_comparison.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: {output_file}")
    
    # Сводная статистика
    print(f"\n{'='*80}")
    print("СВОДНАЯ СТАТИСТИКА")
    print(f"{'='*80}")
    
    old_total = sum(r.get("old_approach", {}).get("tables_found", 0) for r in all_results)
    hybrid_total = sum(r.get("hybrid_approach", {}).get("tables_found", 0) for r in all_results)
    
    print(f"Старый подход: {old_total} таблиц всего")
    print(f"Гибридный подход: {hybrid_total} таблиц всего")
    print(f"Улучшение: {hybrid_total - old_total:+d} таблиц")
    
    return all_results

def main():
    """Основная функция"""
    # Тест 1: Определение типа PDF
    test_pdf_type_detection()
    
    # Тест 2: Сравнение подходов
    test_hybrid_vs_old()

if __name__ == "__main__":
    main()

