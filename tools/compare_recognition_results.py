"""
ШАГ 3: Сравнение автоматического и ручного распознавания
Сравнивает результаты автоматического OCR с ручным распознаванием
"""
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_automatic_results() -> Dict[str, Any]:
    """Загружает результаты автоматического распознавания"""
    auto_file = project_root / "reports" / "ocr" / "recognized_data_akt_may.json"
    
    if not auto_file.exists():
        raise FileNotFoundError(f"Файл автоматических результатов не найден: {auto_file}")
    
    with open(auto_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_manual_results(file_path: str) -> Dict[str, Any]:
    """Загружает результаты ручного распознавания из JSON файла"""
    manual_file = Path(file_path)
    
    if not manual_file.exists():
        raise FileNotFoundError(f"Файл ручных результатов не найден: {manual_file}")
    
    with open(manual_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_tables(auto_table: Dict, manual_table: Dict, table_num: int = 1) -> Dict[str, Any]:
    """Сравнивает две таблицы и выявляет расхождения"""
    comparison = {
        "table_number": table_num,
        "auto_rows": len(auto_table.get('rows', [])),
        "manual_rows": len(manual_table.get('rows', [])),
        "auto_cols": len(auto_table.get('headers', [])),
        "manual_cols": len(manual_table.get('headers', [])),
        "row_count_match": False,
        "col_count_match": False,
        "header_matches": [],
        "row_differences": [],
        "missing_rows": [],
        "extra_rows": [],
        "cell_differences": []
    }
    
    # Сравнение количества строк и столбцов
    comparison["row_count_match"] = comparison["auto_rows"] == comparison["manual_rows"]
    comparison["col_count_match"] = comparison["auto_cols"] == comparison["manual_cols"]
    
    # Сравнение заголовков
    auto_headers = auto_table.get('headers', [])
    manual_headers = manual_table.get('headers', [])
    
    max_headers = max(len(auto_headers), len(manual_headers))
    for i in range(max_headers):
        auto_h = auto_headers[i] if i < len(auto_headers) else ""
        manual_h = manual_headers[i] if i < len(manual_headers) else ""
        
        similarity = SequenceMatcher(None, str(auto_h).lower(), str(manual_h).lower()).ratio()
        comparison["header_matches"].append({
            "column": i,
            "auto": auto_h,
            "manual": manual_h,
            "match": auto_h == manual_h,
            "similarity": similarity
        })
    
    # Сравнение строк данных
    auto_rows = auto_table.get('rows', [])
    manual_rows = manual_table.get('rows', [])
    
    # Сравниваем построчно (пропускаем заголовок, если он есть)
    auto_data_rows = auto_rows[1:] if len(auto_rows) > 0 and auto_rows[0][0] in ['№', 'N', 'No'] else auto_rows
    manual_data_rows = manual_rows[1:] if len(manual_rows) > 0 and manual_rows[0][0] in ['№', 'N', 'No'] else manual_rows
    
    max_rows = max(len(auto_data_rows), len(manual_data_rows))
    
    for row_idx in range(max_rows):
        auto_row = auto_data_rows[row_idx] if row_idx < len(auto_data_rows) else []
        manual_row = manual_data_rows[row_idx] if row_idx < len(manual_data_rows) else []
        
        if row_idx >= len(auto_data_rows):
            comparison["missing_rows"].append({
                "row": row_idx + 1,
                "data": manual_row
            })
        elif row_idx >= len(manual_data_rows):
            comparison["extra_rows"].append({
                "row": row_idx + 1,
                "data": auto_row
            })
        else:
            # Сравниваем ячейки в строке
            max_cols = max(len(auto_row), len(manual_row))
            row_diff = {
                "row": row_idx + 1,
                "cell_differences": []
            }
            
            for col_idx in range(max_cols):
                auto_cell = auto_row[col_idx] if col_idx < len(auto_row) else ""
                manual_cell = manual_row[col_idx] if col_idx < len(manual_row) else ""
                
                # Нормализация для сравнения (убираем пробелы, приводим к нижнему регистру)
                auto_normalized = str(auto_cell).strip().lower()
                manual_normalized = str(manual_cell).strip().lower()
                
                if auto_normalized != manual_normalized:
                    similarity = SequenceMatcher(None, auto_normalized, manual_normalized).ratio()
                    row_diff["cell_differences"].append({
                        "column": col_idx,
                        "auto": auto_cell,
                        "manual": manual_cell,
                        "similarity": similarity,
                        "match": False
                    })
            
            if row_diff["cell_differences"]:
                comparison["row_differences"].append(row_diff)
    
    return comparison

def compare_text(auto_text: str, manual_text: str) -> Dict[str, Any]:
    """Сравнивает текстовые данные"""
    auto_normalized = auto_text.strip().lower()
    manual_normalized = manual_text.strip().lower()
    
    similarity = SequenceMatcher(None, auto_normalized, manual_normalized).ratio()
    
    return {
        "auto_length": len(auto_text),
        "manual_length": len(manual_text),
        "similarity": similarity,
        "match": auto_normalized == manual_normalized
    }

def generate_comparison_report(auto_data: Dict, manual_data: Dict, manual_name: str = "Ручное распознавание") -> Dict[str, Any]:
    """Генерирует полный отчет сравнения"""
    report = {
        "file_name": auto_data.get("file_name", "Unknown"),
        "file_path": auto_data.get("file_path", "Unknown"),
        "comparison_date": None,
        "automatic_results": {
            "confidence": auto_data.get("recognition_result", {}).get("confidence", 0),
            "tables_count": auto_data.get("recognition_result", {}).get("tables_count", 0),
            "text_length": len(auto_data.get("recognition_result", {}).get("text", "")),
            "adaptive_retry_used": auto_data.get("recognition_result", {}).get("adaptive_retry_used", False)
        },
        "manual_results": {
            "source": manual_name,
            "tables_count": len(manual_data.get("tables", [])),
            "text_length": len(manual_data.get("text", "")) if "text" in manual_data else 0
        },
        "table_comparisons": [],
        "text_comparison": None,
        "summary": {
            "total_differences": 0,
            "critical_differences": [],
            "warnings": [],
            "recommendations": []
        }
    }
    
    # Сравнение таблиц
    auto_tables = auto_data.get("recognition_result", {}).get("tables", [])
    manual_tables = manual_data.get("tables", [])
    
    if auto_tables and manual_tables:
        for i, (auto_table, manual_table) in enumerate(zip(auto_tables, manual_tables), 1):
            comparison = compare_tables(auto_table, manual_table, i)
            report["table_comparisons"].append(comparison)
            
            # Подсчет различий
            if not comparison["row_count_match"]:
                report["summary"]["critical_differences"].append(
                    f"Таблица {i}: Несоответствие количества строк ({comparison['auto_rows']} vs {comparison['manual_rows']})"
                )
            
            if not comparison["col_count_match"]:
                report["summary"]["critical_differences"].append(
                    f"Таблица {i}: Несоответствие количества столбцов ({comparison['auto_cols']} vs {comparison['manual_cols']})"
                )
            
            report["summary"]["total_differences"] += len(comparison["row_differences"])
            report["summary"]["total_differences"] += len(comparison["missing_rows"])
            report["summary"]["total_differences"] += len(comparison["extra_rows"])
    
    # Сравнение текста
    auto_text = auto_data.get("recognition_result", {}).get("text", "")
    manual_text = manual_data.get("text", "")
    
    if auto_text and manual_text:
        report["text_comparison"] = compare_text(auto_text, manual_text)
        
        if report["text_comparison"]["similarity"] < 0.9:
            report["summary"]["warnings"].append(
                f"Низкое сходство текста: {report['text_comparison']['similarity']:.2%}"
            )
    
    # Генерация рекомендаций
    if report["summary"]["total_differences"] > 0:
        report["summary"]["recommendations"].append(
            "Обнаружены расхождения в данных. Требуется ручная проверка критических различий."
        )
    
    if report["automatic_results"]["confidence"] < 0.8:
        report["summary"]["recommendations"].append(
            f"Низкий confidence автоматического распознавания ({report['automatic_results']['confidence']:.2%}). "
            "Рекомендуется улучшить предобработку изображений."
        )
    
    return report

def save_comparison_report(report: Dict, output_file: Path):
    """Сохраняет отчет сравнения в JSON и Markdown"""
    # JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Markdown
    md_file = output_file.with_suffix('.md')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# ОТЧЕТ СРАВНЕНИЯ: Автоматическое vs Ручное распознавание\n\n")
        f.write(f"**Файл:** {report['file_name']}\n\n")
        f.write(f"**Дата сравнения:** {report.get('comparison_date', 'N/A')}\n\n")
        f.write("---\n\n")
        
        f.write("## 📊 СВОДКА\n\n")
        f.write(f"- **Confidence автоматического:** {report['automatic_results']['confidence']:.2%}\n")
        f.write(f"- **Таблиц (авто/ручное):** {report['automatic_results']['tables_count']} / {report['manual_results']['tables_count']}\n")
        f.write(f"- **Всего различий:** {report['summary']['total_differences']}\n\n")
        
        if report['summary']['critical_differences']:
            f.write("## ⚠️ КРИТИЧЕСКИЕ РАЗЛИЧИЯ\n\n")
            for diff in report['summary']['critical_differences']:
                f.write(f"- {diff}\n")
            f.write("\n")
        
        if report['table_comparisons']:
            f.write("## 📋 СРАВНЕНИЕ ТАБЛИЦ\n\n")
            for comp in report['table_comparisons']:
                f.write(f"### Таблица {comp['table_number']}\n\n")
                f.write(f"- **Строк (авто/ручное):** {comp['auto_rows']} / {comp['manual_rows']}\n")
                f.write(f"- **Столбцов (авто/ручное):** {comp['auto_cols']} / {comp['manual_cols']}\n")
                f.write(f"- **Различий в строках:** {len(comp['row_differences'])}\n")
                f.write(f"- **Пропущенных строк:** {len(comp['missing_rows'])}\n")
                f.write(f"- **Лишних строк:** {len(comp['extra_rows'])}\n\n")
                
                if comp['row_differences']:
                    f.write("#### Различия в данных:\n\n")
                    for row_diff in comp['row_differences'][:10]:  # Первые 10 различий
                        f.write(f"**Строка {row_diff['row']}:**\n")
                        for cell_diff in row_diff['cell_differences'][:5]:  # Первые 5 ячеек
                            f.write(f"- Столбец {cell_diff['column']}: `{cell_diff['auto']}` → `{cell_diff['manual']}` (сходство: {cell_diff['similarity']:.2%})\n")
                        f.write("\n")
        
        if report['summary']['recommendations']:
            f.write("## 💡 РЕКОМЕНДАЦИИ\n\n")
            for rec in report['summary']['recommendations']:
                f.write(f"- {rec}\n")
            f.write("\n")
    
    return md_file

def main():
    """Основная функция для сравнения результатов"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Сравнение автоматического и ручного распознавания')
    parser.add_argument('--manual1', type=str, help='Путь к первому файлу с ручными результатами')
    parser.add_argument('--manual2', type=str, help='Путь ко второму файлу с ручными результатами')
    parser.add_argument('--manual', type=str, help='Путь к файлу с ручными результатами (один файл)')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("ШАГ 3: СРАВНЕНИЕ АВТОМАТИЧЕСКОГО И РУЧНОГО РАСПОЗНАВАНИЯ")
    print("=" * 80)
    print()
    
    # Загружаем автоматические результаты
    print("📥 Загрузка автоматических результатов...")
    try:
        auto_data = load_automatic_results()
        print(f"✅ Загружено: {auto_data.get('file_name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Ошибка загрузки автоматических результатов: {e}")
        return
    
    # Определяем файлы для сравнения
    manual_files = []
    if args.manual1:
        manual_files.append(("Вариант 1", args.manual1))
    if args.manual2:
        manual_files.append(("Вариант 2", args.manual2))
    if args.manual:
        manual_files.append(("Ручное распознавание", args.manual))
    
    if not manual_files:
        print()
        print("⚠️  Ручные результаты не указаны.")
        print()
        print("📋 ИСПОЛЬЗОВАНИЕ:")
        print("   python tools/compare_recognition_results.py --manual1 <путь1> --manual2 <путь2>")
        print("   или")
        print("   python tools/compare_recognition_results.py --manual <путь>")
        print()
        print("📝 Создаю шаблон для ручного ввода данных...")
        
        # Создаем шаблон
        template = {
            "tables": [
                {
                    "rows": [
                        ["№", "Идентификационный код", "Наименование", "Единица измерения", "Количество", "Цена", "Стоимость", "НДС", "Сумма", "Стоимость с НДС"],
                        ["1", "11302001010000000", "НЕКСИЯ 3 S05300 ТАА", "Услуга (раз)", "1.00", "0.00", "0.00", "12%", "0.00", "0.00"],
                        ["2", "08708001374000000", "Свеча 1 контакт", "шт.", "4.00", "37.500.00", "150.000.00", "12%", "18.000.00", "168.000.00"]
                    ],
                    "headers": ["№", "Идентификационный код", "Наименование", "Единица измерения", "Количество", "Цена", "Стоимость", "НДС", "Сумма", "Стоимость с НДС"]
                }
            ],
            "text": "Полный текст документа..."
        }
        
        template_file = project_root / "reports" / "ocr" / "manual_recognition_template.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Шаблон создан: {template_file}")
        print()
        print("📌 ИНСТРУКЦИЯ:")
        print("   1. Заполните шаблон своими данными")
        print("   2. Сохраните как manual_recognition_variant1.json и variant2.json")
        print("   3. Запустите: python tools/compare_recognition_results.py --manual1 <путь1> --manual2 <путь2>")
        return
    
    # Обрабатываем каждый файл
    all_reports = []
    for manual_name, manual_file_path in manual_files:
        print()
        print(f"📥 Загрузка ручных результатов: {manual_name}")
        print(f"   Файл: {manual_file_path}")
        
        try:
            manual_data = load_manual_results(manual_file_path)
            print("✅ Ручные результаты загружены")
            
            # Сравниваем
            print("🔍 Сравнение результатов...")
            report = generate_comparison_report(auto_data, manual_data, manual_name)
            all_reports.append((manual_name, report))
            
        except Exception as e:
            print(f"❌ Ошибка загрузки ручных результатов: {e}")
            continue
    
    if not all_reports:
        print("❌ Не удалось загрузить ни один файл с ручными результатами")
        return
    
    # Сохраняем отчеты
    print()
    print("=" * 80)
    print("✅ ОТЧЕТЫ СОЗДАНЫ")
    print("=" * 80)
    
    for manual_name, report in all_reports:
        safe_name = manual_name.replace(" ", "_").lower()
        output_file = project_root / "reports" / "ocr" / f"step3_comparison_{safe_name}.json"
        md_file = save_comparison_report(report, output_file)
        
        print()
        print(f"📊 {manual_name}:")
        print(f"  📄 JSON: {output_file}")
        print(f"  📄 Markdown: {md_file}")
        print(f"  - Всего различий: {report['summary']['total_differences']}")
        print(f"  - Критических различий: {len(report['summary']['critical_differences'])}")
        print(f"  - Предупреждений: {len(report['summary']['warnings'])}")
    
    # Создаем сводный отчет, если несколько файлов
    if len(all_reports) > 1:
        summary_file = project_root / "reports" / "ocr" / "step3_comparison_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# СВОДНЫЙ ОТЧЕТ: СРАВНЕНИЕ АВТОМАТИЧЕСКОГО И РУЧНОГО РАСПОЗНАВАНИЯ\n\n")
            f.write(f"**Файл:** {auto_data.get('file_name', 'Unknown')}\n\n")
            f.write("---\n\n")
            
            for manual_name, report in all_reports:
                f.write(f"## {manual_name}\n\n")
                f.write(f"- **Всего различий:** {report['summary']['total_differences']}\n")
                f.write(f"- **Критических различий:** {len(report['summary']['critical_differences'])}\n")
                f.write(f"- **Таблиц (авто/ручное):** {report['automatic_results']['tables_count']} / {report['manual_results']['tables_count']}\n")
                f.write(f"- **Confidence:** {report['automatic_results']['confidence']:.2%}\n\n")
                
                if report['summary']['critical_differences']:
                    f.write("### Критические различия:\n\n")
                    for diff in report['summary']['critical_differences'][:5]:
                        f.write(f"- {diff}\n")
                    f.write("\n")
        
        print()
        print(f"📋 Сводный отчет: {summary_file}")
    print()

if __name__ == "__main__":
    main()

