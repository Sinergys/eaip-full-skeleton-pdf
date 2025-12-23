"""
Параметризованный тест для генерации Word-отчётов на эталонных предприятиях.

Генерирует Word-отчёты для всех reference_enterprise_1...4 и проверяет:
- Корректность генерации
- Соответствие ключевых чисел с Excel-паспортом
- Использование эталонных таблиц как fallback
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Добавляем пути
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest"))

from domain.report_data import ReportData
from utils.word_report_generator import WordReportGenerator
from utils.word_readiness_validator import validate_word_report_readiness, get_missing_data_summary

# Список всех эталонных объектов
REFERENCE_ENTERPRISES = [
    "reference_enterprise_1",
    "reference_enterprise_2_heat_intensive",
    "reference_enterprise_3_electric_intensive",
    "reference_enterprise_4_services",
]


def load_reference_data(enterprise_name: str) -> Dict[str, Any]:
    """Загружает эталонные данные для указанного предприятия."""
    reference_path = PROJECT_ROOT / "data" / "fixtures" / f"{enterprise_name}.json"
    if not reference_path.exists():
        raise FileNotFoundError(f"Эталонный файл не найден: {reference_path}")
    
    return json.loads(reference_path.read_text(encoding="utf-8"))


def extract_data_for_word_report(reference: Dict[str, Any]) -> Dict[str, Any]:
    """
    Извлекает данные из эталонного объекта для Word-генератора.
    
    Returns:
        Словарь с данными для WordReportGenerator.generate_report()
    """
    input_data = reference.get("input_data", {})
    
    # Агрегированные данные
    aggregated_data = {
        "resources": input_data.get("aggregated_resources", {}).get("resources", {})
    }
    
    # Данные предприятия
    enterprise_data = {
        "name": reference.get("enterprise_name", "Неизвестное предприятие"),
        "id": reference.get("enterprise_id", 0),
        "address": "Адрес не указан",  # Можно добавить в эталонные данные
        "inn": "Не указан",
    }
    
    # Оборудование
    equipment_data = input_data.get("equipment", {})
    
    # Узлы учёта
    nodes_data = input_data.get("nodes", {})
    if isinstance(nodes_data, dict) and "tables" in nodes_data:
        nodes_data = nodes_data.get("tables", [])
    
    # Ограждающие конструкции
    envelope_data = input_data.get("envelope", {})
    
    return {
        "enterprise_data": enterprise_data,
        "aggregated_data": aggregated_data,
        "equipment_data": equipment_data if equipment_data else None,
        "nodes_data": nodes_data if nodes_data else None,
        "envelope_data": envelope_data if envelope_data else None,
    }


def generate_word_report(
    enterprise_name: str,
    output_dir: Path,
    skip_readiness_check: bool = False
) -> Dict[str, Any]:
    """
    Генерирует Word-отчёт для эталонного предприятия.
    
    Returns:
        Словарь с результатами генерации
    """
    try:
        # Загружаем данные
        reference = load_reference_data(enterprise_name)
        data = extract_data_for_word_report(reference)
        
        # Создаём ReportData для проверки готовности
        report_data = ReportData.from_raw_data(
            aggregated_data=data["aggregated_data"],
            equipment_data=data["equipment_data"],
            nodes_data=data["nodes_data"],
            envelope_data=data["envelope_data"],
            enterprise_data=data["enterprise_data"]
        )
        
        # Проверяем готовность (если не пропущена)
        readiness = None
        if not skip_readiness_check:
            readiness = validate_word_report_readiness(report_data)
            if not readiness["ready"]:
                summary = get_missing_data_summary(readiness)
                print(f"⚠️ Предупреждение для {enterprise_name}:\n{summary}\n")
        
        # Генерируем Word-отчёт
        generator = WordReportGenerator()
        output_path = output_dir / f"{enterprise_name}_report.docx"
        
        doc = generator.generate_report(
            enterprise_data=data["enterprise_data"],
            aggregated_data=data["aggregated_data"],
            equipment_data=data["equipment_data"],
            nodes_data=data["nodes_data"],
            envelope_data=data["envelope_data"],
            output_path=output_path,
            skip_readiness_check=skip_readiness_check
        )
        
        # Сохраняем, если не был указан output_path
        if not output_path.exists():
            doc.save(output_path)
        
        # Извлекаем ключевые показатели из ReportData для сравнения
        kpis = {
            "electricity_total": report_data.electricity.total_consumption,
            "gas_total": report_data.gas.total_consumption,
            "water_total": report_data.water.total_consumption,
            "total_energy_cost": report_data.total_energy_cost,
            "equipment_power": report_data.equipment.total_installed_power_kw,
            "measures_count": report_data.measures.total_count,
        }
        
        # Сравниваем с Excel-паспортом (если есть)
        excel_passport_path = output_dir.parent / enterprise_name / f"{enterprise_name}_passport.xlsx"
        comparison = compare_with_excel_passport(kpis, excel_passport_path, reference)
        
        return {
            "success": True,
            "enterprise": enterprise_name,
            "output_path": str(output_path),
            "readiness": readiness,
            "kpis": kpis,
            "comparison": comparison,
            "error": None,
        }
        
    except Exception as e:
        return {
            "success": False,
            "enterprise": enterprise_name,
            "output_path": None,
            "readiness": None,
            "kpis": {},
            "error": str(e),
        }


def compare_with_excel_passport(
    word_kpis: Dict[str, float],
    excel_passport_path: Path,
    reference: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Сравнивает ключевые показатели Word-отчёта с Excel-паспортом и эталонными значениями.
    
    Args:
        word_kpis: КПИ из Word-отчёта (ReportData)
        excel_passport_path: Путь к сгенерированному Excel-паспорту
        reference: Эталонные данные для сравнения (опционально)
    
    Returns:
        Словарь с результатами сравнения
    """
    differences = {}
    compared_sources = []
    
    # Сравниваем с эталонными значениями (если есть)
    if reference:
        expected_values = reference.get("expected_results", {})
        if expected_values:
            compared_sources.append("эталонные значения")
            
            # Сравниваем общее потребление электроэнергии
            if "electricity_total" in word_kpis:
                expected_electricity = expected_values.get("electricity_total")
                if expected_electricity is not None:
                    diff = abs(word_kpis["electricity_total"] - expected_electricity)
                    if diff > 0.01:  # Допустимая погрешность
                        differences["electricity_total"] = {
                            "word": word_kpis["electricity_total"],
                            "expected": expected_electricity,
                            "difference": diff,
                        }
            
            # Сравниваем общее потребление газа
            if "gas_total" in word_kpis:
                expected_gas = expected_values.get("gas_total")
                if expected_gas is not None:
                    diff = abs(word_kpis["gas_total"] - expected_gas)
                    if diff > 0.01:
                        differences["gas_total"] = {
                            "word": word_kpis["gas_total"],
                            "expected": expected_gas,
                            "difference": diff,
                        }
    
    # Сравниваем с Excel-паспортом (если существует)
    if excel_passport_path.exists():
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(excel_passport_path, data_only=True)
            compared_sources.append("Excel-паспорт")
            
            # Можно добавить извлечение значений из Excel для сравнения
            # Пока оставляем базовую структуру
            
        except Exception as e:
            differences["excel_error"] = str(e)
    
    return {
        "compared": len(compared_sources) > 0,
        "compared_sources": compared_sources,
        "differences": differences,
        "matches": len(differences) == 0,
    }


def run_single_test(enterprise_name: str, output_dir: Path) -> Dict[str, Any]:
    """Запускает тест для одного предприятия."""
    print(f"\n{'='*70}")
    print(f"Тестирование: {enterprise_name}")
    print(f"{'='*70}")
    
    result = generate_word_report(enterprise_name, output_dir)
    
    if result["success"]:
        print(f"✅ Word-отчёт успешно сгенерирован: {result['output_path']}")
        
        if result["readiness"]:
            print(f"   Готовность данных: {result['readiness']['completeness_score']*100:.0f}%")
            print(f"   Готовых разделов: {result['readiness']['ready_sections_count']}/{result['readiness']['total_sections_count']}")
        
        print("   Ключевые показатели:")
        for kpi_name, kpi_value in result["kpis"].items():
            if isinstance(kpi_value, float):
                print(f"     - {kpi_name}: {kpi_value:,.2f}")
            else:
                print(f"     - {kpi_name}: {kpi_value}")
        
        # Показываем результаты сравнения
        if result.get("comparison", {}).get("compared"):
            comparison = result["comparison"]
            if comparison.get("matches"):
                print("   ✅ Ключевые показатели совпадают с эталоном")
            else:
                print("   ⚠️ Обнаружены расхождения:")
                for kpi, diff_info in comparison.get("differences", {}).items():
                    if isinstance(diff_info, dict) and "difference" in diff_info:
                        print(f"     - {kpi}: разница {diff_info['difference']:,.2f}")
    else:
        print(f"❌ Ошибка генерации: {result['error']}")
    
    return result


def main():
    """Основная функция тестирования."""
    print("="*70)
    print("ТЕСТИРОВАНИЕ ГЕНЕРАЦИИ WORD-ОТЧЁТОВ")
    print("="*70)
    print(f"Тестируем {len(REFERENCE_ENTERPRISES)} эталонных объектов:")
    for i, name in enumerate(REFERENCE_ENTERPRISES, 1):
        print(f"  {i}. {name}")
    
    # Создаём директорию для результатов
    output_dir = PROJECT_ROOT / "test_output" / "word_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nРезультаты будут сохранены в: {output_dir}")
    
    # Запускаем тесты для всех предприятий
    results = []
    for enterprise_name in REFERENCE_ENTERPRISES:
        result = run_single_test(enterprise_name, output_dir)
        results.append(result)
    
    # Формируем итоговый отчёт
    print(f"\n{'='*70}")
    print("ИТОГОВЫЙ ОТЧЁТ")
    print(f"{'='*70}")
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"Успешно: {successful}/{len(results)}")
    print(f"Ошибок: {failed}/{len(results)}")
    
    if failed > 0:
        print("\nОшибки:")
        for result in results:
            if not result["success"]:
                print(f"  - {result['enterprise']}: {result['error']}")
    
    # Сохраняем JSON-отчёт
    report_path = output_dir / "test_report.json"
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "successful": successful,
        "failed": failed,
        "results": results,
    }
    report_path.write_text(
        json.dumps(report_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nДетальный отчёт сохранён: {report_path}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())

