"""
Сравнительное тестирование методов извлечения таблиц из PDF
Тестирует Camelot, pdfplumber, Tabula на реальных файлах
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Добавляем путь к сервисам
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "eaip_full_skeleton" / "services" / "ingest"))

from utils.table_detector import (
    extract_tables_with_camelot,
    extract_tables_with_pdfplumber,
    extract_tables_with_tabula,
    check_dependencies
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def analyze_table_quality(table: Dict[str, Any]) -> Dict[str, Any]:
    """Анализ качества извлеченной таблицы"""
    rows = table.get("rows", [])
    if not rows:
        return {
            "empty": True,
            "structure_score": 0,
            "data_completeness": 0
        }
    
    # Оценка структуры (проверка на одинаковое количество колонок)
    col_counts = [len(row) for row in rows]
    max_cols = max(col_counts) if col_counts else 0
    min_cols = min(col_counts) if col_counts else 0
    structure_score = 100 if max_cols == min_cols else max(0, 100 - (max_cols - min_cols) * 10)
    
    # Оценка заполненности данных (процент непустых ячеек)
    total_cells = sum(len(row) for row in rows)
    filled_cells = sum(1 for row in rows for cell in row if cell and str(cell).strip())
    data_completeness = (filled_cells / total_cells * 100) if total_cells > 0 else 0
    
    # Проверка на наличие формул/чисел
    numeric_cells = 0
    for row in rows:
        for cell in row:
            if cell:
                cell_str = str(cell).strip()
                # Проверка на число (с учетом запятых и точек)
                try:
                    float(cell_str.replace(',', '.').replace(' ', ''))
                    numeric_cells += 1
                except:
                    pass
    
    numeric_ratio = (numeric_cells / total_cells * 100) if total_cells > 0 else 0
    
    return {
        "empty": False,
        "row_count": len(rows),
        "col_count": max_cols,
        "structure_score": structure_score,
        "data_completeness": data_completeness,
        "numeric_ratio": numeric_ratio,
        "accuracy": table.get("accuracy", None)
    }

def test_method_on_pdf(pdf_path: Path, method: str) -> Dict[str, Any]:
    """Тестирование одного метода на PDF файле"""
    print(f"\n{'='*80}")
    print(f"Тестирование метода: {method}")
    print(f"Файл: {pdf_path.name}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        if method == "camelot":
            tables = extract_tables_with_camelot(str(pdf_path))
        elif method == "pdfplumber":
            tables = extract_tables_with_pdfplumber(str(pdf_path))
        elif method == "tabula":
            tables = extract_tables_with_tabula(str(pdf_path))
        else:
            return {"error": f"Неизвестный метод: {method}"}
        
        elapsed_time = time.time() - start_time
        
        # Анализ результатов
        results = {
            "method": method,
            "file": pdf_path.name,
            "file_size_mb": pdf_path.stat().st_size / (1024 * 1024),
            "elapsed_time": elapsed_time,
            "tables_found": len(tables),
            "tables": []
        }
        
        for table in tables:
            quality = analyze_table_quality(table)
            table_result = {
                "page": table.get("page"),
                "table_index": table.get("table_index"),
                "method": table.get("method"),
                "row_count": quality["row_count"],
                "col_count": quality["col_count"],
                "structure_score": quality["structure_score"],
                "data_completeness": quality["data_completeness"],
                "numeric_ratio": quality["numeric_ratio"],
                "accuracy": quality.get("accuracy")
            }
            results["tables"].append(table_result)
        
        # Общая оценка
        if results["tables"]:
            avg_structure = sum(t["structure_score"] for t in results["tables"]) / len(results["tables"])
            avg_completeness = sum(t["data_completeness"] for t in results["tables"]) / len(results["tables"])
            results["avg_structure_score"] = avg_structure
            results["avg_data_completeness"] = avg_completeness
            results["overall_score"] = (avg_structure + avg_completeness) / 2
        else:
            results["avg_structure_score"] = 0
            results["avg_data_completeness"] = 0
            results["overall_score"] = 0
        
        print(f"✅ Найдено таблиц: {results['tables_found']}")
        print(f"⏱ Время: {elapsed_time:.2f} сек")
        if results["tables"]:
            print(f"📊 Средняя оценка структуры: {results['avg_structure_score']:.1f}%")
            print(f"📊 Средняя заполненность: {results['avg_data_completeness']:.1f}%")
            print(f"⭐ Общая оценка: {results['overall_score']:.1f}%")
        
        return results
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ Ошибка: {e}")
        return {
            "method": method,
            "file": pdf_path.name,
            "error": str(e),
            "elapsed_time": elapsed_time,
            "tables_found": 0
        }

def compare_methods(pdf_path: Path) -> Dict[str, Any]:
    """Сравнение всех методов на одном файле"""
    print(f"\n{'#'*80}")
    print("СРАВНИТЕЛЬНЫЙ ТЕСТ МЕТОДОВ ИЗВЛЕЧЕНИЯ ТАБЛИЦ")
    print(f"{'#'*80}")
    print(f"Файл: {pdf_path}")
    print(f"Размер: {pdf_path.stat().st_size / (1024 * 1024):.2f} MB")
    
    deps = check_dependencies()
    print(f"\nДоступные методы: {', '.join(deps['available_methods'])}")
    
    results = {
        "file": str(pdf_path),
        "file_name": pdf_path.name,
        "file_size_mb": pdf_path.stat().st_size / (1024 * 1024),
        "test_date": datetime.now().isoformat(),
        "methods": {}
    }
    
    # Тестируем каждый доступный метод
    for method in ["camelot", "pdfplumber", "tabula"]:
        if method in deps["available_methods"]:
            method_result = test_method_on_pdf(pdf_path, method)
            results["methods"][method] = method_result
        else:
            print(f"\n⚠ Метод {method} недоступен (зависимости не установлены)")
            results["methods"][method] = {"error": "Метод недоступен"}
    
    # Определяем лучший метод
    best_method = None
    best_score = 0
    
    for method, result in results["methods"].items():
        if "overall_score" in result and result["overall_score"] > best_score:
            best_score = result["overall_score"]
            best_method = method
    
    results["best_method"] = best_method
    results["best_score"] = best_score
    
    print(f"\n{'='*80}")
    print(f"🏆 ЛУЧШИЙ МЕТОД: {best_method} (оценка: {best_score:.1f}%)")
    print(f"{'='*80}")
    
    return results

def main():
    """Основная функция"""
    # Ищем тестовые PDF файлы
    test_dirs = [
        PROJECT_ROOT / "eaip_full_skeleton" / "infra" / "data" / "inbox",
        PROJECT_ROOT / "data" / "source_files",
    ]
    
    pdf_files = []
    for test_dir in test_dirs:
        if test_dir.exists():
            pdf_files.extend(list(test_dir.glob("*.pdf")))
    
    if not pdf_files:
        print("❌ Тестовые PDF файлы не найдены!")
        print("   Искал в:")
        for test_dir in test_dirs:
            print(f"   - {test_dir}")
        return
    
    print(f"✅ Найдено {len(pdf_files)} PDF файлов для тестирования")
    
    # Тестируем каждый файл
    all_results = []
    for pdf_file in pdf_files[:3]:  # Ограничиваем 3 файлами для начала
        result = compare_methods(pdf_file)
        all_results.append(result)
    
    # Сохраняем результаты
    output_file = PROJECT_ROOT / "data" / "aggregated" / "table_extraction_comparison.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: {output_file}")
    
    # Сводная таблица
    print(f"\n{'='*80}")
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print(f"{'='*80}")
    print(f"{'Файл':<40} {'Camelot':<15} {'pdfplumber':<15} {'Tabula':<15} {'Лучший':<10}")
    print("-" * 95)
    
    for result in all_results:
        file_name = result["file_name"][:38]
        camelot_score = result["methods"].get("camelot", {}).get("overall_score") or 0
        pdfplumber_score = result["methods"].get("pdfplumber", {}).get("overall_score") or 0
        tabula_score = result["methods"].get("tabula", {}).get("overall_score") or 0
        best = result.get("best_method") or "N/A"
        
        print(f"{file_name:<40} {camelot_score:>6.1f}%      {pdfplumber_score:>6.1f}%      {tabula_score:>6.1f}%      {best:<10}")

if __name__ == "__main__":
    main()

