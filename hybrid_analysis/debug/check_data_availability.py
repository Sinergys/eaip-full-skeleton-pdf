"""
Скрипт для проверки доступности данных в агрегированных файлах
Показывает какие ресурсы загружены, какие отсутствуют, какие данные доступны
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class DataAvailabilityChecker:
    """Проверка доступности данных в агрегированных файлах."""
    
    REQUIRED_RESOURCES = ["electricity", "gas", "water", "fuel", "coal", "heat"]
    
    def __init__(self, data_path: Path):
        """
        Инициализация проверки.
        
        Args:
            data_path: Путь к файлу с агрегированными данными
        """
        self.data_path = data_path
        self.data = {}
        
    def load_data(self) -> None:
        """Загрузка данных."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Файл данных не найден: {self.data_path}")
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
    
    def check_structure(self) -> Dict[str, Any]:
        """Проверка структуры данных."""
        structure = {
            "file_format": "unknown",
            "has_resources_key": "resources" in self.data,
            "has_file_based_structure": any(".xlsx" in str(k) for k in self.data.keys()) if isinstance(self.data, dict) else False,
            "top_level_keys": list(self.data.keys()) if isinstance(self.data, dict) else [],
        }
        
        # Определяем формат
        if structure["has_resources_key"]:
            structure["file_format"] = "resource_based"
        elif structure["has_file_based_structure"]:
            structure["file_format"] = "file_based"
        else:
            structure["file_format"] = "unknown"
        
        return structure
    
    def extract_resources(self) -> Dict[str, Any]:
        """Извлечение ресурсов из данных (поддержка разных форматов)."""
        resources = {}
        
        # Формат 1: {"resources": {"electricity": {...}, ...}}
        if "resources" in self.data:
            resources = self.data["resources"]
        
        # Формат 2: {"gaz.xlsx": {"resources": {"gas": {...}}}, ...}
        elif isinstance(self.data, dict) and any(".xlsx" in str(k) for k in self.data.keys()):
            # Объединяем ресурсы из всех файлов
            for file_key, file_data in self.data.items():
                if isinstance(file_data, dict) and "resources" in file_data:
                    for resource_type, resource_data in file_data["resources"].items():
                        if resource_type not in resources:
                            resources[resource_type] = {}
                        # Объединяем данные по кварталам
                        if isinstance(resource_data, dict):
                            for quarter, quarter_data in resource_data.items():
                                if quarter not in resources[resource_type]:
                                    resources[resource_type][quarter] = quarter_data
                                else:
                                    # Объединяем данные квартала (если нужно)
                                    existing = resources[resource_type][quarter]
                                    if isinstance(existing, dict) and isinstance(quarter_data, dict):
                                        existing.update(quarter_data)
        
        # Формат 3: Прямой формат {"electricity": {...}, ...}
        elif all(key in self.data for key in ["electricity", "gas"]) or any(r in self.data for r in self.REQUIRED_RESOURCES):
            resources = {k: v for k, v in self.data.items() if k in self.REQUIRED_RESOURCES}
        
        return resources
    
    def check_resources_availability(self, required_resources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Проверка доступности ресурсов."""
        if required_resources is None:
            required_resources = self.REQUIRED_RESOURCES
        
        resources = self.extract_resources()
        
        availability = {
            "available_resources": [],
            "missing_resources": [],
            "resources_details": {}
        }
        
        for resource_type in required_resources:
            if resource_type in resources:
                resource_data = resources[resource_type]
                
                # Анализ данных ресурса
                quarters = list(resource_data.keys()) if isinstance(resource_data, dict) else []
                has_data = len(quarters) > 0
                
                if has_data:
                    availability["available_resources"].append(resource_type)
                    
                    # Детали по кварталам
                    quarter_details = {}
                    for quarter in quarters:
                        quarter_data = resource_data[quarter]
                        if isinstance(quarter_data, dict):
                            quarter_totals = quarter_data.get("quarter_totals", {})
                            has_totals = len(quarter_totals) > 0
                            quarter_details[quarter] = {
                                "has_quarter_totals": has_totals,
                                "totals_keys": list(quarter_totals.keys()) if has_totals else [],
                                "has_monthly_data": "months" in quarter_data,
                                "month_count": len(quarter_data.get("months", []))
                            }
                    
                    availability["resources_details"][resource_type] = {
                        "quarters_count": len(quarters),
                        "quarters": quarters,
                        "quarter_details": quarter_details
                    }
                else:
                    availability["missing_resources"].append(resource_type)
                    availability["resources_details"][resource_type] = {
                        "status": "empty",
                        "message": "Ресурс присутствует, но не содержит данных"
                    }
            else:
                availability["missing_resources"].append(resource_type)
                availability["resources_details"][resource_type] = {
                    "status": "not_found",
                    "message": "Ресурс отсутствует в данных"
                }
        
        return availability
    
    def check_quarters_coverage(self) -> Dict[str, Any]:
        """Проверка покрытия кварталов."""
        resources = self.extract_resources()
        
        all_quarters = set()
        quarters_by_resource = {}
        
        for resource_type, resource_data in resources.items():
            if isinstance(resource_data, dict):
                quarters = [q for q in resource_data.keys() if "-Q" in str(q) or "Q" in str(q)]
                quarters_by_resource[resource_type] = sorted(quarters)
                all_quarters.update(quarters)
        
        # Определяем годы
        years = set()
        for quarter in all_quarters:
            if "-Q" in str(quarter):
                year = str(quarter).split("-Q")[0]
                years.add(year)
        
        return {
            "all_quarters": sorted(list(all_quarters)),
            "all_years": sorted(list(years)),
            "quarters_by_resource": quarters_by_resource,
            "expected_quarters_per_year": 4,
            "total_expected_quarters": len(years) * 4 if years else 0
        }
    
    def check_data_completeness(self) -> Dict[str, Any]:
        """Проверка полноты данных."""
        resources = self.extract_resources()
        
        completeness = {
            "resource_completeness": {},
            "quarter_completeness": {},
            "overall_score": 0.0
        }
        
        total_score = 0.0
        resource_count = 0
        
        for resource_type, resource_data in resources.items():
            if not isinstance(resource_data, dict):
                continue
            
            quarters = [q for q in resource_data.keys() if isinstance(resource_data[q], dict)]
            quarter_scores = []
            
            for quarter in quarters:
                quarter_data = resource_data[quarter]
                quarter_totals = quarter_data.get("quarter_totals", {})
                
                # Проверяем наличие ключевых полей
                has_volume = any("volume" in str(k).lower() for k in quarter_totals.keys())
                has_cost = any("cost" in str(k).lower() or "sum" in str(k).lower() for k in quarter_totals.keys())
                
                score = 0.5 if has_volume else 0.0
                score += 0.3 if has_cost else 0.0
                score += 0.2 if len(quarter_totals) > 2 else 0.1
                
                quarter_scores.append(score)
                completeness["quarter_completeness"][f"{resource_type}_{quarter}"] = {
                    "score": round(score, 2),
                    "has_volume": has_volume,
                    "has_cost": has_cost,
                    "fields_count": len(quarter_totals)
                }
            
            avg_score = sum(quarter_scores) / len(quarter_scores) if quarter_scores else 0.0
            completeness["resource_completeness"][resource_type] = {
                "score": round(avg_score, 2),
                "quarters_count": len(quarters),
                "avg_quarter_score": round(avg_score, 2)
            }
            
            total_score += avg_score
            resource_count += 1
        
        completeness["overall_score"] = round(total_score / resource_count, 2) if resource_count > 0 else 0.0
        
        return completeness
    
    def generate_report(self, required_resources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Генерация полного отчета."""
        self.load_data()
        
        structure = self.check_structure()
        availability = self.check_resources_availability(required_resources)
        quarters_coverage = self.check_quarters_coverage()
        completeness = self.check_data_completeness()
        
        report = {
            "data_file": str(self.data_path),
            "file_size_kb": round(self.data_path.stat().st_size / 1024, 2),
            "structure": structure,
            "availability": availability,
            "quarters_coverage": quarters_coverage,
            "completeness": completeness,
            "summary": {
                "available_resources_count": len(availability["available_resources"]),
                "missing_resources_count": len(availability["missing_resources"]),
                "required_resources_count": len(required_resources) if required_resources else len(self.REQUIRED_RESOURCES),
                "coverage_percentage": round(
                    len(availability["available_resources"]) / 
                    (len(required_resources) if required_resources else len(self.REQUIRED_RESOURCES)) * 100, 
                    2
                ) if (required_resources or self.REQUIRED_RESOURCES) else 0.0,
                "overall_completeness_score": completeness["overall_score"]
            }
        }
        
        return report


def print_report(report: Dict[str, Any]) -> None:
    """Вывод отчета в консоль."""
    print("=" * 80)
    print("📊 ОТЧЕТ О ДОСТУПНОСТИ ДАННЫХ")
    print("=" * 80)
    print(f"Файл: {report['data_file']}")
    print(f"Размер: {report['file_size_kb']} KB")
    print()
    
    # Структура
    print("📋 СТРУКТУРА ДАННЫХ:")
    print("-" * 80)
    structure = report["structure"]
    print(f"  Формат: {structure['file_format']}")
    print(f"  Ключ 'resources': {'✅' if structure['has_resources_key'] else '❌'}")
    print(f"  Файловая структура: {'✅' if structure['has_file_based_structure'] else '❌'}")
    if structure["top_level_keys"]:
        print(f"  Ключи верхнего уровня: {', '.join(structure['top_level_keys'][:5])}")
        if len(structure["top_level_keys"]) > 5:
            print(f"    ... и еще {len(structure['top_level_keys']) - 5}")
    print()
    
    # Доступность ресурсов
    print("🔍 ДОСТУПНОСТЬ РЕСУРСОВ:")
    print("-" * 80)
    availability = report["availability"]
    print(f"  ✅ Доступно: {len(availability['available_resources'])}")
    for resource in availability["available_resources"]:
        details = availability["resources_details"][resource]
        print(f"     - {resource}: {details.get('quarters_count', 0)} кварталов")
    
    print(f"\n  ❌ Отсутствует: {len(availability['missing_resources'])}")
    for resource in availability["missing_resources"]:
        details = availability["resources_details"][resource]
        print(f"     - {resource}: {details.get('message', 'не найден')}")
    print()
    
    # Покрытие кварталов
    print("📅 ПОКРЫТИЕ КВАРТАЛОВ:")
    print("-" * 80)
    quarters_coverage = report["quarters_coverage"]
    print(f"  Всего кварталов: {len(quarters_coverage['all_quarters'])}")
    print(f"  Годы: {', '.join(quarters_coverage['all_years'])}")
    for resource, quarters in quarters_coverage["quarters_by_resource"].items():
        print(f"  {resource}: {len(quarters)} кварталов")
        if len(quarters) <= 4:
            print(f"    {', '.join(quarters)}")
    print()
    
    # Полнота данных
    print("📊 ПОЛНОТА ДАННЫХ:")
    print("-" * 80)
    completeness = report["completeness"]
    print(f"  Общий балл полноты: {completeness['overall_score']}/1.0")
    for resource, details in completeness["resource_completeness"].items():
        print(f"  {resource}: {details['score']}/1.0 ({details['quarters_count']} кварталов)")
    print()
    
    # Сводка
    print("📋 СВОДКА:")
    print("-" * 80)
    summary = report["summary"]
    print(f"  Ресурсов доступно: {summary['available_resources_count']}/{summary['required_resources_count']}")
    print(f"  Покрытие: {summary['coverage_percentage']}%")
    print(f"  Полнота данных: {summary['overall_completeness_score']}/1.0")
    
    if summary["coverage_percentage"] < 50:
        print("\n  ⚠️  ВНИМАНИЕ: Покрытие ресурсов менее 50%!")
    if summary["overall_completeness_score"] < 0.5:
        print("  ⚠️  ВНИМАНИЕ: Полнота данных низкая!")
    
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Проверка доступности данных в агрегированных файлах")
    parser.add_argument("--data", required=True, help="Путь к файлу с агрегированными данными")
    parser.add_argument("--required-resources", help="Список требуемых ресурсов через запятую (например: electricity,gas,water)")
    parser.add_argument("--output", help="Путь для сохранения отчета JSON")
    
    args = parser.parse_args()
    
    data_path = Path(args.data)
    output_path = Path(args.output) if args.output else None
    
    required_resources = None
    if args.required_resources:
        required_resources = [r.strip() for r in args.required_resources.split(",")]
    
    checker = DataAvailabilityChecker(data_path)
    report = checker.generate_report(required_resources)
    
    print_report(report)
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Отчет сохранен в: {output_path}")

