"""
ШАГ 4: Анализ различий между автоматическим и ручным распознаванием
Выявление паттернов ошибок и рекомендации по улучшению
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_comparison_report() -> Dict[str, Any]:
    """Загружает отчет сравнения"""
    report_file = project_root / "reports" / "ocr" / "step3_comparison_ручное_распознавание.json"
    
    if not report_file.exists():
        raise FileNotFoundError(f"Отчет сравнения не найден: {report_file}")
    
    with open(report_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_cell_differences(report: Dict) -> Dict[str, Any]:
    """Анализирует различия в ячейках и выявляет паттерны"""
    analysis = {
        "total_differences": 0,
        "by_column": defaultdict(int),
        "by_similarity": defaultdict(int),
        "error_patterns": [],
        "common_errors": [],
        "numeric_errors": [],
        "text_errors": []
    }
    
    for table_comp in report.get("table_comparisons", []):
        for row_diff in table_comp.get("row_differences", []):
            for cell_diff in row_diff.get("cell_differences", []):
                analysis["total_differences"] += 1
                
                col = cell_diff.get("column", 0)
                similarity = cell_diff.get("similarity", 0)
                auto_val = str(cell_diff.get("auto", ""))
                manual_val = str(cell_diff.get("manual", ""))
                
                # Группировка по столбцам
                analysis["by_column"][col] += 1
                
                # Группировка по сходству
                if similarity < 0.3:
                    analysis["by_similarity"]["low"] += 1
                elif similarity < 0.7:
                    analysis["by_similarity"]["medium"] += 1
                else:
                    analysis["by_similarity"]["high"] += 1
                
                # Анализ типов ошибок
                if auto_val.replace('.', '').replace(',', '').isdigit() or manual_val.replace('.', '').replace(',', '').isdigit():
                    analysis["numeric_errors"].append({
                        "column": col,
                        "auto": auto_val,
                        "manual": manual_val,
                        "similarity": similarity
                    })
                else:
                    analysis["text_errors"].append({
                        "column": col,
                        "auto": auto_val,
                        "manual": manual_val,
                        "similarity": similarity
                    })
                
                # Выявление паттернов
                if similarity < 0.5:
                    analysis["error_patterns"].append({
                        "type": "low_similarity",
                        "column": col,
                        "auto": auto_val[:50],
                        "manual": manual_val[:50]
                    })
    
    return analysis

def analyze_structure_issues(report: Dict) -> Dict[str, Any]:
    """Анализирует структурные проблемы"""
    issues = {
        "row_count_mismatch": False,
        "col_count_mismatch": False,
        "header_mismatches": [],
        "missing_rows": 0,
        "extra_rows": 0
    }
    
    for table_comp in report.get("table_comparisons", []):
        if not table_comp.get("row_count_match"):
            issues["row_count_mismatch"] = True
            issues["missing_rows"] += len(table_comp.get("missing_rows", []))
            issues["extra_rows"] += len(table_comp.get("extra_rows", []))
        
        if not table_comp.get("col_count_match"):
            issues["col_count_mismatch"] = True
        
        # Анализ заголовков
        for header_match in table_comp.get("header_matches", []):
            if not header_match.get("match"):
                issues["header_mismatches"].append({
                    "column": header_match.get("column"),
                    "auto": header_match.get("auto"),
                    "manual": header_match.get("manual"),
                    "similarity": header_match.get("similarity", 0)
                })
    
    return issues

def generate_recommendations(analysis: Dict, structure_issues: Dict, report: Dict) -> List[str]:
    """Генерирует рекомендации на основе анализа"""
    recommendations = []
    
    # Анализ confidence
    confidence = report.get("automatic_results", {}).get("confidence", 0)
    if confidence >= 0.95:
        recommendations.append("✅ Confidence 95% - отличный результат, превышает цель (80%+)")
    elif confidence >= 0.80:
        recommendations.append("⚠️ Confidence 80-95% - хороший результат, но можно улучшить")
    else:
        recommendations.append("❌ Confidence <80% - требуется улучшение предобработки")
    
    # Анализ структурных проблем
    if structure_issues["row_count_mismatch"]:
        recommendations.append("⚠️ Несоответствие количества строк - проверить логику определения конца таблицы")
    
    if structure_issues["col_count_mismatch"]:
        recommendations.append("❌ Несоответствие количества столбцов - критическая проблема")
    
    if structure_issues["header_mismatches"]:
        low_sim_headers = [h for h in structure_issues["header_mismatches"] if h["similarity"] < 0.7]
        if low_sim_headers:
            recommendations.append(f"⚠️ {len(low_sim_headers)} заголовков имеют низкое сходство - проверить распознавание заголовков")
    
    # Анализ ошибок по столбцам
    if analysis["by_column"]:
        max_errors_col = max(analysis["by_column"].items(), key=lambda x: x[1])
        recommendations.append(f"📊 Столбец {max_errors_col[0]} имеет больше всего ошибок ({max_errors_col[1]}) - приоритет для улучшения")
    
    # Анализ типов ошибок
    if len(analysis["numeric_errors"]) > len(analysis["text_errors"]):
        recommendations.append("🔢 Больше ошибок в числовых значениях - улучшить распознавание чисел")
    else:
        recommendations.append("📝 Больше ошибок в текстовых значениях - улучшить распознавание текста")
    
    # Анализ сходства
    low_sim_count = analysis["by_similarity"].get("low", 0)
    if low_sim_count > analysis["total_differences"] * 0.3:
        recommendations.append(f"⚠️ {low_sim_count} различий с низким сходством (<30%) - требуется детальный анализ")
    
    return recommendations

def generate_report(analysis: Dict, structure_issues: Dict, recommendations: List[str], report: Dict) -> Dict[str, Any]:
    """Генерирует полный отчет анализа"""
    return {
        "file_name": report.get("file_name", "Unknown"),
        "analysis_date": None,
        "summary": {
            "total_differences": analysis["total_differences"],
            "confidence": report.get("automatic_results", {}).get("confidence", 0),
            "structure_issues": {
                "row_mismatch": structure_issues["row_count_mismatch"],
                "col_mismatch": structure_issues["col_count_mismatch"],
                "missing_rows": structure_issues["missing_rows"],
                "extra_rows": structure_issues["extra_rows"]
            }
        },
        "analysis": {
            "differences_by_column": dict(analysis["by_column"]),
            "differences_by_similarity": dict(analysis["by_similarity"]),
            "numeric_errors_count": len(analysis["numeric_errors"]),
            "text_errors_count": len(analysis["text_errors"]),
            "error_patterns_count": len(analysis["error_patterns"])
        },
        "structure_issues": structure_issues,
        "recommendations": recommendations,
        "detailed_analysis": {
            "top_error_columns": sorted(analysis["by_column"].items(), key=lambda x: x[1], reverse=True)[:5],
            "sample_numeric_errors": analysis["numeric_errors"][:5],
            "sample_text_errors": analysis["text_errors"][:5],
            "sample_error_patterns": analysis["error_patterns"][:10]
        }
    }

def save_report(analysis_report: Dict, output_file: Path):
    """Сохраняет отчет в JSON и Markdown"""
    # JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, ensure_ascii=False, indent=2)
    
    # Markdown
    md_file = output_file.with_suffix('.md')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# ШАГ 4: АНАЛИЗ РАЗЛИЧИЙ И РЕКОМЕНДАЦИИ\n\n")
        f.write(f"**Файл:** {analysis_report['file_name']}\n\n")
        f.write("---\n\n")
        
        f.write("## 📊 СВОДКА\n\n")
        f.write(f"- **Confidence:** {analysis_report['summary']['confidence']:.2%}\n")
        f.write(f"- **Всего различий:** {analysis_report['summary']['total_differences']}\n")
        f.write(f"- **Пропущенных строк:** {analysis_report['summary']['structure_issues']['missing_rows']}\n")
        f.write(f"- **Лишних строк:** {analysis_report['summary']['structure_issues']['extra_rows']}\n\n")
        
        f.write("## 📈 АНАЛИЗ РАЗЛИЧИЙ\n\n")
        f.write("### По столбцам:\n\n")
        for col, count in analysis_report['detailed_analysis']['top_error_columns']:
            f.write(f"- **Столбец {col}:** {count} различий\n")
        f.write("\n")
        
        f.write("### По типу:\n\n")
        f.write(f"- **Числовые ошибки:** {analysis_report['analysis']['numeric_errors_count']}\n")
        f.write(f"- **Текстовые ошибки:** {analysis_report['analysis']['text_errors_count']}\n")
        f.write("\n")
        
        f.write("### По сходству:\n\n")
        sim_data = analysis_report['analysis']['differences_by_similarity']
        f.write(f"- **Низкое (<30%):** {sim_data.get('low', 0)}\n")
        f.write(f"- **Среднее (30-70%):** {sim_data.get('medium', 0)}\n")
        f.write(f"- **Высокое (>70%):** {sim_data.get('high', 0)}\n")
        f.write("\n")
        
        f.write("## 💡 РЕКОМЕНДАЦИИ\n\n")
        for i, rec in enumerate(analysis_report['recommendations'], 1):
            f.write(f"{i}. {rec}\n")
        f.write("\n")
        
        if analysis_report['detailed_analysis']['sample_numeric_errors']:
            f.write("## 🔢 ПРИМЕРЫ ЧИСЛОВЫХ ОШИБОК\n\n")
            for error in analysis_report['detailed_analysis']['sample_numeric_errors']:
                f.write(f"- Столбец {error['column']}: `{error['auto']}` → `{error['manual']}` (сходство: {error['similarity']:.2%})\n")
            f.write("\n")
        
        if analysis_report['detailed_analysis']['sample_text_errors']:
            f.write("## 📝 ПРИМЕРЫ ТЕКСТОВЫХ ОШИБОК\n\n")
            for error in analysis_report['detailed_analysis']['sample_text_errors']:
                f.write(f"- Столбец {error['column']}: `{error['auto'][:50]}` → `{error['manual'][:50]}` (сходство: {error['similarity']:.2%})\n")
            f.write("\n")
    
    return md_file

def main():
    """Основная функция"""
    print("=" * 80)
    print("ШАГ 4: АНАЛИЗ РАЗЛИЧИЙ И РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ")
    print("=" * 80)
    print()
    
    # Загружаем отчет сравнения
    print("📥 Загрузка отчета сравнения...")
    try:
        report = load_comparison_report()
        print("✅ Отчет загружен")
    except Exception as e:
        print(f"❌ Ошибка загрузки отчета: {e}")
        return
    
    # Анализируем различия
    print()
    print("🔍 Анализ различий...")
    analysis = analyze_cell_differences(report)
    structure_issues = analyze_structure_issues(report)
    
    # Генерируем рекомендации
    print("💡 Генерация рекомендаций...")
    recommendations = generate_recommendations(analysis, structure_issues, report)
    
    # Создаем отчет
    print("📊 Создание отчета...")
    analysis_report = generate_report(analysis, structure_issues, recommendations, report)
    
    # Сохраняем
    output_file = project_root / "reports" / "ocr" / "step4_analysis_report.json"
    md_file = save_report(analysis_report, output_file)
    
    print()
    print("=" * 80)
    print("✅ АНАЛИЗ ЗАВЕРШЕН")
    print("=" * 80)
    print()
    print(f"📄 JSON: {output_file}")
    print(f"📄 Markdown: {md_file}")
    print()
    print("📊 КЛЮЧЕВЫЕ РЕЗУЛЬТАТЫ:")
    print(f"  - Всего различий: {analysis_report['summary']['total_differences']}")
    print(f"  - Confidence: {analysis_report['summary']['confidence']:.2%}")
    print(f"  - Числовых ошибок: {analysis_report['analysis']['numeric_errors_count']}")
    print(f"  - Текстовых ошибок: {analysis_report['analysis']['text_errors_count']}")
    print(f"  - Рекомендаций: {len(recommendations)}")
    print()

if __name__ == "__main__":
    main()

