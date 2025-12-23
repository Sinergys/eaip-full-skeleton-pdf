"""
Этап 4.4: Валидация совместимости
Проверка возможности конвертации между шаблонами
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class CompatibilityValidator:
    """Класс для валидации совместимости шаблонов."""
    
    def __init__(self, structural_comparison_path: Path,
                 semantic_comparison_path: Optional[Path] = None,
                 adapter_path: Optional[Path] = None):
        """
        Инициализация валидатора.
        
        Args:
            structural_comparison_path: Путь к результатам структурного сравнения
            semantic_comparison_path: Путь к результатам семантического сравнения (опционально)
            adapter_path: Путь к адаптерам (опционально)
        """
        self.structural_comparison_path = structural_comparison_path
        self.semantic_comparison_path = semantic_comparison_path
        self.adapter_path = adapter_path
        self.structural_comparison = {}
        self.semantic_comparison = {}
        self.adapters = {}
        self.validation_report = {}
    
    def load_data(self) -> None:
        """Загрузка данных для валидации."""
        if self.structural_comparison_path.exists():
            self.structural_comparison = json.loads(
                self.structural_comparison_path.read_text(encoding="utf-8")
            )
        
        if self.semantic_comparison_path and self.semantic_comparison_path.exists():
            self.semantic_comparison = json.loads(
                self.semantic_comparison_path.read_text(encoding="utf-8")
            )
        
        if self.adapter_path and self.adapter_path.exists():
            self.adapters = json.loads(
                self.adapter_path.read_text(encoding="utf-8")
            )
    
    def validate(self) -> Dict[str, Any]:
        """
        Валидация совместимости.
        
        Returns:
            Словарь с отчетом о валидации
        """
        self.validation_report = {
            "validation_date": datetime.now().isoformat(),
            "source_template": self.structural_comparison.get("template1", {}).get("name", ""),
            "target_template": self.structural_comparison.get("template2", {}).get("name", ""),
            "overall_compatibility": {
                "status": "unknown",
                "score": 0.0,
                "confidence": 0.0
            },
            "structural_compatibility": {},
            "semantic_compatibility": {},
            "adapter_validation": {},
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "conversion_feasibility": {}
        }
        
        # Валидация структурной совместимости
        structural_validation = self._validate_structural_compatibility()
        self.validation_report["structural_compatibility"] = structural_validation
        
        # Валидация семантической совместимости
        if self.semantic_comparison:
            semantic_validation = self._validate_semantic_compatibility()
            self.validation_report["semantic_compatibility"] = semantic_validation
        
        # Валидация адаптеров
        if self.adapters:
            adapter_validation = self._validate_adapters()
            self.validation_report["adapter_validation"] = adapter_validation
        
        # Расчет общей совместимости
        self._calculate_overall_compatibility()
        
        # Оценка возможности конвертации
        self._assess_conversion_feasibility()
        
        return self.validation_report
    
    def _validate_structural_compatibility(self) -> Dict[str, Any]:
        """Валидация структурной совместимости."""
        validation = {
            "status": "unknown",
            "score": 0.0,
            "issues": [],
            "warnings": [],
            "details": {}
        }
        
        similarity_metrics = self.structural_comparison.get("similarity_metrics", {})
        overall_similarity = similarity_metrics.get("overall_similarity", 0.0)
        
        validation["score"] = overall_similarity
        
        # Оценка статуса
        if overall_similarity >= 0.8:
            validation["status"] = "high"
        elif overall_similarity >= 0.5:
            validation["status"] = "medium"
        else:
            validation["status"] = "low"
        
        # Анализ различий
        differences = self.structural_comparison.get("structural_differences", {})
        sheet_count_diff = differences.get("sheet_count_diff", 0)
        
        if abs(sheet_count_diff) > 2:
            validation["warnings"].append(
                f"Значительная разница в количестве листов: {sheet_count_diff}"
            )
        
        # Анализ листов
        sheet_comparison = self.structural_comparison.get("sheet_comparison", [])
        common_sheets = [s for s in sheet_comparison if s.get("status") == "common"]
        unique_sheets_1 = [s for s in sheet_comparison if s.get("status") == "unique_to_template1"]
        unique_sheets_2 = [s for s in sheet_comparison if s.get("status") == "unique_to_template2"]
        
        if len(unique_sheets_1) > 0:
            validation["warnings"].append(
                f"В source template есть {len(unique_sheets_1)} уникальных листов, которые будут пропущены"
            )
        
        if len(unique_sheets_2) > 0:
            validation["warnings"].append(
                f"В target template есть {len(unique_sheets_2)} уникальных листов, которые будут созданы пустыми"
            )
        
        validation["details"] = {
            "common_sheets_count": len(common_sheets),
            "unique_sheets_source": len(unique_sheets_1),
            "unique_sheets_target": len(unique_sheets_2),
            "sheet_name_similarity": similarity_metrics.get("sheet_name_similarity", 0.0),
            "structural_similarity": similarity_metrics.get("structural_similarity", 0.0)
        }
        
        return validation
    
    def _validate_semantic_compatibility(self) -> Dict[str, Any]:
        """Валидация семантической совместимости."""
        validation = {
            "status": "unknown",
            "score": 0.0,
            "issues": [],
            "details": {}
        }
        
        if not self.semantic_comparison:
            return validation
        
        common_concepts = self.semantic_comparison.get("common_concepts", [])
        unique_to_1 = self.semantic_comparison.get("unique_to_template1", [])
        unique_to_2 = self.semantic_comparison.get("unique_to_template2", [])
        
        total_concepts = len(common_concepts) + len(unique_to_1) + len(unique_to_2)
        
        if total_concepts > 0:
            score = len(common_concepts) / total_concepts
            validation["score"] = score
            
            # Оценка статуса
            if score >= 0.7:
                validation["status"] = "high"
            elif score >= 0.5:
                validation["status"] = "medium"
            else:
                validation["status"] = "low"
            
            if len(unique_to_1) > 0:
                validation["issues"].append(
                    f"В source template есть {len(unique_to_1)} уникальных концептов без эквивалентов"
                )
        
        validation["details"] = {
            "common_concepts_count": len(common_concepts),
            "unique_concepts_source": len(unique_to_1),
            "unique_concepts_target": len(unique_to_2),
            "total_concepts": total_concepts
        }
        
        return validation
    
    def _validate_adapters(self) -> Dict[str, Any]:
        """Валидация адаптеров."""
        validation = {
            "status": "unknown",
            "score": 0.0,
            "issues": [],
            "warnings": [],
            "details": {}
        }
        
        if not self.adapters:
            return validation
        
        confidence = self.adapters.get("metadata", {}).get("confidence", 0.0)
        validation["score"] = confidence
        
        # Оценка статуса
        if confidence >= 0.7:
            validation["status"] = "high"
        elif confidence >= 0.5:
            validation["status"] = "medium"
        else:
            validation["status"] = "low"
        
        # Анализ адаптеров
        adapters = self.adapters.get("adapters", {})
        skip_count = sum(1 for a in adapters.values() if a.get("type") == "skip")
        create_count = sum(1 for a in adapters.values() if a.get("type") == "create")
        
        if skip_count > 0:
            validation["issues"].append(
                f"{skip_count} листов будут пропущены при конвертации"
            )
        
        if create_count > 0:
            validation["warnings"].append(
                f"{create_count} листов будут созданы пустыми"
            )
        
        validation["details"] = {
            "total_adapters": len(adapters),
            "skip_count": skip_count,
            "create_count": create_count,
            "map_count": len(adapters) - skip_count - create_count
        }
        
        return validation
    
    def _calculate_overall_compatibility(self) -> None:
        """Расчет общей совместимости."""
        structural_score = self.validation_report["structural_compatibility"].get("score", 0.0)
        semantic_score = self.validation_report.get("semantic_compatibility", {}).get("score", 0.0)
        adapter_score = self.validation_report.get("adapter_validation", {}).get("score", 0.0)
        
        # Взвешенное среднее
        if semantic_score > 0 and adapter_score > 0:
            overall_score = (structural_score * 0.3 + semantic_score * 0.4 + adapter_score * 0.3)
        elif semantic_score > 0:
            overall_score = (structural_score * 0.5 + semantic_score * 0.5)
        else:
            overall_score = structural_score
        
        self.validation_report["overall_compatibility"]["score"] = overall_score
        self.validation_report["overall_compatibility"]["confidence"] = overall_score
        
        # Оценка статуса
        if overall_score >= 0.8:
            status = "high"
        elif overall_score >= 0.5:
            status = "medium"
        else:
            status = "low"
        
        self.validation_report["overall_compatibility"]["status"] = status
    
    def _assess_conversion_feasibility(self) -> None:
        """Оценка возможности конвертации."""
        feasibility = self.structural_comparison.get("conversion_feasibility", {})
        overall_score = self.validation_report["overall_compatibility"]["score"]
        
        self.validation_report["conversion_feasibility"] = {
            "is_feasible": overall_score >= 0.5,
            "confidence": overall_score,
            "recommended_approach": self._recommend_approach(overall_score),
            "challenges": feasibility.get("challenges", []),
            "recommendations": feasibility.get("recommendations", [])
        }
        
        # Добавление рекомендаций на основе валидации
        if overall_score < 0.5:
            self.validation_report["conversion_feasibility"]["recommendations"].append(
                "Низкая совместимость - требуется ручная проверка и корректировка"
            )
        elif overall_score < 0.8:
            self.validation_report["conversion_feasibility"]["recommendations"].append(
                "Умеренная совместимость - рекомендуется тестирование конвертации на тестовых данных"
            )
        else:
            self.validation_report["conversion_feasibility"]["recommendations"].append(
                "Высокая совместимость - конвертация может быть выполнена автоматически"
            )
    
    def _recommend_approach(self, score: float) -> str:
        """Рекомендация подхода к конвертации."""
        if score >= 0.8:
            return "automatic"
        elif score >= 0.5:
            return "semi_automatic"
        else:
            return "manual"
    
    def save(self, output_path: Path) -> None:
        """Сохранение отчета о валидации."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.validation_report, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


def validate_compatibility(structural_comparison_path: Path,
                          output_path: Path,
                          semantic_comparison_path: Optional[Path] = None,
                          adapter_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Валидация совместимости шаблонов.
    
    Args:
        structural_comparison_path: Путь к результатам структурного сравнения
        output_path: Путь для сохранения отчета
        semantic_comparison_path: Путь к результатам семантического сравнения (опционально)
        adapter_path: Путь к адаптерам (опционально)
    
    Returns:
        Словарь с отчетом о валидации
    """
    validator = CompatibilityValidator(structural_comparison_path, semantic_comparison_path, adapter_path)
    validator.load_data()
    report = validator.validate()
    validator.save(output_path)
    
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Валидация совместимости шаблонов")
    parser.add_argument("--structural", required=True, help="Путь к структурному сравнению")
    parser.add_argument("--output", required=True, help="Путь для сохранения JSON")
    parser.add_argument("--semantic", help="Путь к семантическому сравнению")
    parser.add_argument("--adapter", help="Путь к адаптерам")
    
    args = parser.parse_args()
    
    structural_path = Path(args.structural)
    output_path = Path(args.output)
    semantic_path = Path(args.semantic) if args.semantic else None
    adapter_path = Path(args.adapter) if args.adapter else None
    
    if not structural_path.exists():
        raise FileNotFoundError(f"Файл не найден: {structural_path}")
    
    print("Валидация совместимости:")
    print(f"  Structural comparison: {structural_path}")
    if semantic_path:
        print(f"  Semantic comparison: {semantic_path}")
    if adapter_path:
        print(f"  Adapters: {adapter_path}")
    
    report = validate_compatibility(structural_path, output_path, semantic_path, adapter_path)
    
    print(f"\n✅ Отчет сохранен в: {output_path}")
    print("\n📊 Результаты валидации:")
    print(f"  Общая совместимость: {report['overall_compatibility']['status']} ({report['overall_compatibility']['score']:.2%})")
    print(f"  Конвертация возможна: {report['conversion_feasibility']['is_feasible']}")
    print(f"  Рекомендуемый подход: {report['conversion_feasibility']['recommended_approach']}")
    print(f"  Проблем: {len(report['issues'])}")
    print(f"  Предупреждений: {len(report['warnings'])}")

