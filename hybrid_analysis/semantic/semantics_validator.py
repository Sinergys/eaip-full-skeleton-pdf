"""
Этап 2.4: Валидация семантики
Проверка логической целостности семантических данных
"""

import json
from pathlib import Path
from typing import Dict, Any


class SemanticsValidator:
    """Валидатор семантических данных."""
    
    def __init__(self, cell_semantics_path: Path, semantic_mapping_path: Path):
        """
        Инициализация валидатора.
        
        Args:
            cell_semantics_path: Путь к cell_semantics.json
            semantic_mapping_path: Путь к semantic_mapping.json
        """
        self.cell_semantics_path = cell_semantics_path
        self.semantic_mapping_path = semantic_mapping_path
        self.cell_semantics = {}
        self.semantic_mapping = {}
        self.validation_report = {}
    
    def load_data(self) -> None:
        """Загрузка данных."""
        if self.cell_semantics_path.exists():
            self.cell_semantics = json.loads(
                self.cell_semantics_path.read_text(encoding="utf-8")
            )
        
        if self.semantic_mapping_path.exists():
            self.semantic_mapping = json.loads(
                self.semantic_mapping_path.read_text(encoding="utf-8")
            )
    
    def validate(self) -> Dict[str, Any]:
        """
        Валидация семантических данных.
        
        Returns:
            Отчет о валидации
        """
        self.load_data()
        
        self.validation_report = {
            "validation_date": str(Path(__file__).stat().st_mtime),
            "checks": [],
            "errors": [],
            "warnings": [],
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "warnings_count": 0
            }
        }
        
        # Проверка 1: Целостность семантических профилей
        self._check_semantic_profiles_integrity()
        
        # Проверка 2: Корректность маппинга
        self._check_mapping_correctness()
        
        # Проверка 3: Полнота покрытия
        self._check_coverage()
        
        # Проверка 4: Консистентность единиц измерения
        self._check_units_consistency()
        
        # Обновление сводки
        self.validation_report["summary"]["total_checks"] = len(self.validation_report["checks"])
        self.validation_report["summary"]["passed"] = sum(
            1 for check in self.validation_report["checks"] if check["status"] == "passed"
        )
        self.validation_report["summary"]["failed"] = sum(
            1 for check in self.validation_report["checks"] if check["status"] == "failed"
        )
        self.validation_report["summary"]["warnings_count"] = len(self.validation_report["warnings"])
        
        return self.validation_report
    
    def _check_semantic_profiles_integrity(self) -> None:
        """Проверка целостности семантических профилей."""
        check = {
            "name": "Semantic Profiles Integrity",
            "status": "passed",
            "details": []
        }
        
        cells = self.cell_semantics.get("cells", {})
        
        # Проверка обязательных полей
        required_fields = ["address", "semantic_type", "category"]
        for cell_address, cell_data in cells.items():
            for field in required_fields:
                if field not in cell_data:
                    check["status"] = "failed"
                    check["details"].append(f"Cell {cell_address}: missing field '{field}'")
                    self.validation_report["errors"].append(
                        f"Cell {cell_address}: missing required field '{field}'"
                    )
        
        self.validation_report["checks"].append(check)
    
    def _check_mapping_correctness(self) -> None:
        """Проверка корректности маппинга."""
        check = {
            "name": "Mapping Correctness",
            "status": "passed",
            "details": []
        }
        
        mappings = self.semantic_mapping.get("mappings", [])
        
        # Проверка формата путей к данным
        for mapping in mappings:
            data_path = mapping.get("data_path", "")
            if data_path and not data_path.startswith("resources."):
                check["status"] = "failed"
                check["details"].append(f"Invalid data path format: {data_path}")
                self.validation_report["errors"].append(
                    f"Invalid data path format: {data_path}"
                )
        
        self.validation_report["checks"].append(check)
    
    def _check_coverage(self) -> None:
        """Проверка полноты покрытия."""
        check = {
            "name": "Coverage Check",
            "status": "passed",
            "details": []
        }
        
        total_cells = self.semantic_mapping.get("statistics", {}).get("total_cells", 0)
        mapped_cells = self.semantic_mapping.get("statistics", {}).get("mapped_cells", 0)
        
        if total_cells > 0:
            coverage = (mapped_cells / total_cells) * 100
            check["details"].append(f"Coverage: {coverage:.2f}%")
            
            if coverage < 10:
                check["status"] = "failed"
                self.validation_report["errors"].append(
                    f"Low coverage: {coverage:.2f}% (expected > 10%)"
                )
            elif coverage < 50:
                check["status"] = "warning"
                self.validation_report["warnings"].append(
                    f"Low coverage: {coverage:.2f}% (recommended > 50%)"
                )
        
        self.validation_report["checks"].append(check)
    
    def _check_units_consistency(self) -> None:
        """Проверка консистентности единиц измерения."""
        check = {
            "name": "Units Consistency",
            "status": "passed",
            "details": []
        }
        
        cells = self.cell_semantics.get("cells", {})
        
        # Группировка по типам ресурсов
        resource_units = {}
        for cell_address, cell_data in cells.items():
            resource_type = cell_data.get("resource_type")
            units = cell_data.get("units")
            
            if resource_type and units:
                if resource_type not in resource_units:
                    resource_units[resource_type] = set()
                resource_units[resource_type].add(units)
        
        # Проверка консистентности
        for resource_type, units_set in resource_units.items():
            if len(units_set) > 1:
                check["status"] = "warning"
                check["details"].append(
                    f"Resource {resource_type}: multiple units {units_set}"
                )
                self.validation_report["warnings"].append(
                    f"Resource {resource_type} has inconsistent units: {units_set}"
                )
        
        self.validation_report["checks"].append(check)
    
    def save(self, output_path: Path) -> None:
        """
        Сохранение отчета о валидации.
        
        Args:
            output_path: Путь для сохранения JSON
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.validation_report, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


def validate_semantics(
    cell_semantics_path: Path,
    semantic_mapping_path: Path,
    output_path: Path
) -> Dict[str, Any]:
    """
    Валидация семантики и сохранение результатов.
    
    Args:
        cell_semantics_path: Путь к cell_semantics.json
        semantic_mapping_path: Путь к semantic_mapping.json
        output_path: Путь для сохранения результатов
    
    Returns:
        Отчет о валидации
    """
    validator = SemanticsValidator(cell_semantics_path, semantic_mapping_path)
    report = validator.validate()
    validator.save(output_path)
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Валидация семантики")
    parser.add_argument("--cell-semantics", required=True, help="Путь к cell_semantics.json")
    parser.add_argument("--semantic-mapping", required=True, help="Путь к semantic_mapping.json")
    parser.add_argument("--output", required=True, help="Путь для сохранения JSON")
    
    args = parser.parse_args()
    
    semantics_path = Path(args.cell_semantics)
    mapping_path = Path(args.semantic_mapping)
    output_path = Path(args.output)
    
    print("Валидация семантики...")
    report = validate_semantics(semantics_path, mapping_path, output_path)
    
    print(f"\n✅ Отчет сохранен в: {output_path}")
    print("📊 Статистика:")
    print(f"  Проверок: {report['summary']['total_checks']}")
    print(f"  Пройдено: {report['summary']['passed']}")
    print(f"  Провалено: {report['summary']['failed']}")
    print(f"  Предупреждений: {report['summary']['warnings_count']}")

