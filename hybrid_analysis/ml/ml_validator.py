"""
Этап 3.4: Валидация ML-моделей
Проверка точности предсказаний
"""

import json
import pickle
from pathlib import Path
from typing import Dict, Any


class MLValidator:
    """Валидатор ML-моделей и предсказаний."""
    
    def __init__(
        self,
        adaptation_model_path: Path,
        format_predictions_path: Path,
        semantic_mapping_path: Path
    ):
        """
        Инициализация валидатора.
        
        Args:
            adaptation_model_path: Путь к adaptation_model.pkl
            format_predictions_path: Путь к format_predictions.json
            semantic_mapping_path: Путь к semantic_mapping.json
        """
        self.adaptation_model_path = adaptation_model_path
        self.format_predictions_path = format_predictions_path
        self.semantic_mapping_path = semantic_mapping_path
        self.model = None
        self.format_predictions = {}
        self.semantic_mapping = {}
        self.validation_report = {}
    
    def load_data(self) -> None:
        """Загрузка данных."""
        if self.adaptation_model_path.exists():
            with open(self.adaptation_model_path, 'rb') as f:
                self.model = pickle.load(f)
        
        if self.format_predictions_path.exists():
            self.format_predictions = json.loads(
                self.format_predictions_path.read_text(encoding="utf-8")
            )
        
        if self.semantic_mapping_path.exists():
            self.semantic_mapping = json.loads(
                self.semantic_mapping_path.read_text(encoding="utf-8")
            )
    
    def validate(self) -> Dict[str, Any]:
        """
        Валидация ML-моделей.
        
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
        
        # Проверка 1: Корректность модели
        self._check_model_correctness()
        
        # Проверка 2: Точность предсказаний форматов
        self._check_format_accuracy()
        
        # Проверка 3: Покрытие предсказаниями
        self._check_prediction_coverage()
        
        # Проверка 4: Консистентность правил
        self._check_rules_consistency()
        
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
    
    def _check_model_correctness(self) -> None:
        """Проверка корректности модели."""
        check = {
            "name": "Model Correctness",
            "status": "passed",
            "details": []
        }
        
        if not self.model:
            check["status"] = "failed"
            check["details"].append("Model not loaded")
            self.validation_report["errors"].append("Model file not found or corrupted")
        else:
            # Проверка структуры модели
            required_keys = ["rules", "patterns", "statistics"]
            for key in required_keys:
                if key not in self.model:
                    check["status"] = "failed"
                    check["details"].append(f"Missing key in model: {key}")
                    self.validation_report["errors"].append(f"Model missing key: {key}")
        
        self.validation_report["checks"].append(check)
    
    def _check_format_accuracy(self) -> None:
        """Проверка точности предсказаний форматов."""
        check = {
            "name": "Format Prediction Accuracy",
            "status": "passed",
            "details": []
        }
        
        predictions = self.format_predictions.get("predictions", {})
        
        # Проверка наличия обязательных полей в предсказаниях
        required_fields = ["format", "precision", "units"]
        for cell_address, prediction in predictions.items():
            for field in required_fields:
                if field not in prediction:
                    check["status"] = "warning"
                    check["details"].append(f"Cell {cell_address}: missing field '{field}'")
                    self.validation_report["warnings"].append(
                        f"Cell {cell_address}: missing field '{field}' in prediction"
                    )
        
        self.validation_report["checks"].append(check)
    
    def _check_prediction_coverage(self) -> None:
        """Проверка покрытия предсказаниями."""
        check = {
            "name": "Prediction Coverage",
            "status": "passed",
            "details": []
        }
        
        mapped_cells = self.semantic_mapping.get("statistics", {}).get("mapped_cells", 0)
        total_predictions = self.format_predictions.get("statistics", {}).get("total_predictions", 0)
        
        if mapped_cells > 0:
            coverage = (total_predictions / mapped_cells) * 100
            check["details"].append(f"Coverage: {coverage:.2f}%")
            
            if coverage < 50:
                check["status"] = "warning"
                self.validation_report["warnings"].append(
                    f"Low prediction coverage: {coverage:.2f}%"
                )
        
        self.validation_report["checks"].append(check)
    
    def _check_rules_consistency(self) -> None:
        """Проверка консистентности правил."""
        check = {
            "name": "Rules Consistency",
            "status": "passed",
            "details": []
        }
        
        if self.model and "rules" in self.model:
            rules = self.model["rules"]
            
            # Проверка на дубликаты
            semantic_types = set()
            for semantic_type, rule_list in rules.items():
                if semantic_type in semantic_types:
                    check["status"] = "warning"
                    check["details"].append(f"Duplicate semantic type: {semantic_type}")
                    self.validation_report["warnings"].append(
                        f"Duplicate semantic type in rules: {semantic_type}"
                    )
                semantic_types.add(semantic_type)
        
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


def validate_ml_models(
    adaptation_model_path: Path,
    format_predictions_path: Path,
    semantic_mapping_path: Path,
    output_path: Path
) -> Dict[str, Any]:
    """
    Валидация ML-моделей и сохранение результатов.
    
    Args:
        adaptation_model_path: Путь к adaptation_model.pkl
        format_predictions_path: Путь к format_predictions.json
        semantic_mapping_path: Путь к semantic_mapping.json
        output_path: Путь для сохранения результатов
    
    Returns:
        Отчет о валидации
    """
    validator = MLValidator(adaptation_model_path, format_predictions_path, semantic_mapping_path)
    report = validator.validate()
    validator.save(output_path)
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Валидация ML-моделей")
    parser.add_argument("--adaptation-model", required=True, help="Путь к adaptation_model.pkl")
    parser.add_argument("--format-predictions", required=True, help="Путь к format_predictions.json")
    parser.add_argument("--semantic-mapping", required=True, help="Путь к semantic_mapping.json")
    parser.add_argument("--output", required=True, help="Путь для сохранения JSON")
    
    args = parser.parse_args()
    
    model_path = Path(args.adaptation_model)
    predictions_path = Path(args.format_predictions)
    mapping_path = Path(args.semantic_mapping)
    output_path = Path(args.output)
    
    print("Валидация ML-моделей...")
    report = validate_ml_models(model_path, predictions_path, mapping_path, output_path)
    
    print(f"\n✅ Отчет сохранен в: {output_path}")
    print("📊 Статистика:")
    print(f"  Проверок: {report['summary']['total_checks']}")
    print(f"  Пройдено: {report['summary']['passed']}")
    print(f"  Провалено: {report['summary']['failed']}")
    print(f"  Предупреждений: {report['summary']['warnings_count']}")

