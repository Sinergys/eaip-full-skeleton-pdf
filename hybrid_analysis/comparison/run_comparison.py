"""
Этап 4: Полный цикл сравнительного анализа
Интеграция всех модулей сравнения шаблонов
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from structural_comparison import compare_templates
from semantic_comparison import compare_semantics
from adapter_generator import generate_adapters
from compatibility_validator import validate_compatibility


class TemplateComparisonPipeline:
    """Пайплайн для полного сравнительного анализа шаблонов."""
    
    def __init__(self, template1_path: Path, template2_path: Path,
                 output_dir: Path,
                 template1_structure_path: Optional[Path] = None,
                 template2_structure_path: Optional[Path] = None,
                 template1_semantic_path: Optional[Path] = None,
                 template2_semantic_path: Optional[Path] = None):
        """
        Инициализация пайплайна.
        
        Args:
            template1_path: Путь к первому шаблону (new_energy_passport.xlsx)
            template2_path: Путь ко второму шаблону (template_metin.xlsx)
            output_dir: Директория для сохранения результатов
            template1_structure_path: Путь к JSON структуры первого шаблона (опционально)
            template2_structure_path: Путь к JSON структуры второго шаблона (опционально)
            template1_semantic_path: Путь к семантическому анализу первого шаблона (опционально)
            template2_semantic_path: Путь к семантическому анализу второго шаблона (опционально)
        """
        self.template1_path = template1_path
        self.template2_path = template2_path
        self.output_dir = output_dir
        self.template1_structure_path = template1_structure_path
        self.template2_structure_path = template2_structure_path
        self.template1_semantic_path = template1_semantic_path
        self.template2_semantic_path = template2_semantic_path
        
        # Пути к результатам
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.structural_comparison_path = self.output_dir / "template_structure_comparison.json"
        self.semantic_comparison_path = self.output_dir / "semantic_comparison.json"
        self.adapter_path = self.output_dir / "template_adapters.json"
        self.validation_path = self.output_dir / "compatibility_validation_report.json"
        self.summary_path = self.output_dir / "comparison_summary.json"
        
        self.results = {}
    
    def run(self) -> Dict[str, Any]:
        """
        Запуск полного цикла сравнения.
        
        Returns:
            Словарь с результатами всех этапов
        """
        print("=" * 80)
        print("ЭТАП 4: СРАВНИТЕЛЬНЫЙ АНАЛИЗ ШАБЛОНОВ")
        print("=" * 80)
        
        self.results = {
            "pipeline_start": datetime.now().isoformat(),
            "template1": {
                "path": str(self.template1_path),
                "name": self.template1_path.stem
            },
            "template2": {
                "path": str(self.template2_path),
                "name": self.template2_path.stem
            },
            "stages": {}
        }
        
        # Этап 4.1: Структурное сопоставление
        print("\n📊 Этап 4.1: Структурное сопоставление шаблонов...")
        structural_result = self._run_structural_comparison()
        self.results["stages"]["structural_comparison"] = {
            "status": "completed",
            "output_file": str(self.structural_comparison_path),
            "summary": self._summarize_structural_comparison(structural_result)
        }
        
        # Этап 4.2: Семантическое сопоставление
        print("\n🔍 Этап 4.2: Семантическое сопоставление...")
        semantic_result = self._run_semantic_comparison()
        self.results["stages"]["semantic_comparison"] = {
            "status": "completed" if semantic_result else "skipped",
            "output_file": str(self.semantic_comparison_path) if semantic_result else None,
            "summary": self._summarize_semantic_comparison(semantic_result) if semantic_result else None
        }
        
        # Этап 4.3: Генерация адаптеров
        print("\n🔧 Этап 4.3: Генерация адаптеров...")
        adapter_result = self._run_adapter_generation(semantic_result is not None)
        self.results["stages"]["adapter_generation"] = {
            "status": "completed",
            "output_file": str(self.adapter_path),
            "summary": self._summarize_adapters(adapter_result)
        }
        
        # Этап 4.4: Валидация совместимости
        print("\n✅ Этап 4.4: Валидация совместимости...")
        validation_result = self._run_validation(semantic_result is not None)
        self.results["stages"]["validation"] = {
            "status": "completed",
            "output_file": str(self.validation_path),
            "summary": self._summarize_validation(validation_result)
        }
        
        # Финальная сводка
        self.results["pipeline_end"] = datetime.now().isoformat()
        self.results["overall_summary"] = self._create_overall_summary(validation_result)
        
        # Сохранение сводки
        self._save_summary()
        
        print("\n" + "=" * 80)
        print("✅ СРАВНИТЕЛЬНЫЙ АНАЛИЗ ЗАВЕРШЕН")
        print("=" * 80)
        self._print_summary()
        
        return self.results
    
    def _run_structural_comparison(self) -> Dict[str, Any]:
        """Запуск структурного сравнения."""
        comparison = compare_templates(
            self.template1_path,
            self.template2_path,
            self.structural_comparison_path,
            self.template1_structure_path,
            self.template2_structure_path
        )
        return comparison
    
    def _run_semantic_comparison(self) -> Optional[Dict[str, Any]]:
        """Запуск семантического сравнения."""
        # Для семантического сравнения достаточно только template1_semantic_path
        if not self.template1_semantic_path:
            print("  ⚠️  Пропущено: не указан путь к семантическому анализу template1")
            return None
        
        if not self.template1_semantic_path.exists():
            print(f"  ⚠️  Пропущено: файл не найден: {self.template1_semantic_path}")
            return None
        
        # Для template2 семантический анализ может отсутствовать
        template2_semantic = None
        if self.template2_semantic_path and self.template2_semantic_path.exists():
            template2_semantic = self.template2_semantic_path
        elif self.template2_semantic_path:
            print("  ⚠️  Внимание: семантический анализ для template2 не найден, "
                  "используется только template1")
        
        comparison = compare_semantics(
            self.template1_semantic_path,
            template2_semantic,
            self.semantic_comparison_path
        )
        
        return comparison
    
    def _run_adapter_generation(self, has_semantic: bool) -> Dict[str, Any]:
        """Запуск генерации адаптеров."""
        semantic_path = self.semantic_comparison_path if has_semantic and self.semantic_comparison_path.exists() else None
        
        adapters = generate_adapters(
            self.structural_comparison_path,
            self.adapter_path,
            self.template1_path,
            self.template2_path,
            semantic_path
        )
        return adapters
    
    def _run_validation(self, has_semantic: bool) -> Dict[str, Any]:
        """Запуск валидации совместимости."""
        semantic_path = self.semantic_comparison_path if has_semantic and self.semantic_comparison_path.exists() else None
        
        validation = validate_compatibility(
            self.structural_comparison_path,
            self.validation_path,
            semantic_path,
            self.adapter_path
        )
        return validation
    
    def _summarize_structural_comparison(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Создание сводки структурного сравнения."""
        return {
            "overall_similarity": result.get("similarity_metrics", {}).get("overall_similarity", 0.0),
            "common_sheets": len([s for s in result.get("sheet_comparison", []) if s.get("status") == "common"]),
            "unique_to_template1": len([s for s in result.get("sheet_comparison", []) if s.get("status") == "unique_to_template1"]),
            "unique_to_template2": len([s for s in result.get("sheet_comparison", []) if s.get("status") == "unique_to_template2"]),
            "feasibility_confidence": result.get("conversion_feasibility", {}).get("confidence", 0.0)
        }
    
    def _summarize_semantic_comparison(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создание сводки семантического сравнения."""
        if not result:
            return None
        
        return {
            "common_concepts": len(result.get("common_concepts", [])),
            "unique_to_template1": len(result.get("unique_to_template1", [])),
            "unique_to_template2": len(result.get("unique_to_template2", [])),
            "conversion_rules": len(result.get("conversion_rules", []))
        }
    
    def _summarize_adapters(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Создание сводки адаптеров."""
        adapters = result.get("adapters", {})
        return {
            "total_adapters": len(adapters),
            "confidence": result.get("metadata", {}).get("confidence", 0.0),
            "skip_count": sum(1 for a in adapters.values() if a.get("type") == "skip"),
            "create_count": sum(1 for a in adapters.values() if a.get("type") == "create"),
            "map_count": sum(1 for a in adapters.values() if a.get("type") == "map")
        }
    
    def _summarize_validation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Создание сводки валидации."""
        return {
            "overall_compatibility": result.get("overall_compatibility", {}).get("status", "unknown"),
            "compatibility_score": result.get("overall_compatibility", {}).get("score", 0.0),
            "is_feasible": result.get("conversion_feasibility", {}).get("is_feasible", False),
            "recommended_approach": result.get("conversion_feasibility", {}).get("recommended_approach", "unknown"),
            "issues_count": len(result.get("issues", [])),
            "warnings_count": len(result.get("warnings", []))
        }
    
    def _create_overall_summary(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Создание общей сводки."""
        overall = validation_result.get("overall_compatibility", {})
        feasibility = validation_result.get("conversion_feasibility", {})
        
        return {
            "compatibility_status": overall.get("status", "unknown"),
            "compatibility_score": overall.get("score", 0.0),
            "conversion_feasible": feasibility.get("is_feasible", False),
            "recommended_approach": feasibility.get("recommended_approach", "unknown"),
            "confidence": overall.get("confidence", 0.0)
        }
    
    def _save_summary(self) -> None:
        """Сохранение итоговой сводки."""
        self.summary_path.write_text(
            json.dumps(self.results, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def _print_summary(self) -> None:
        """Вывод сводки в консоль."""
        summary = self.results["overall_summary"]
        
        print("\n📊 ОБЩАЯ СВОДКА:")
        print(f"  Совместимость: {summary['compatibility_status']} ({summary['compatibility_score']:.2%})")
        print(f"  Конвертация возможна: {'✅ Да' if summary['conversion_feasible'] else '❌ Нет'}")
        print(f"  Рекомендуемый подход: {summary['recommended_approach']}")
        print(f"  Уверенность: {summary['confidence']:.2%}")
        
        print("\n📁 РЕЗУЛЬТАТЫ:")
        print(f"  Структурное сравнение: {self.structural_comparison_path}")
        if self.semantic_comparison_path.exists():
            print(f"  Семантическое сравнение: {self.semantic_comparison_path}")
        print(f"  Адаптеры: {self.adapter_path}")
        print(f"  Валидация: {self.validation_path}")
        print(f"  Сводка: {self.summary_path}")


def run_comparison_analysis(template1_path: str, template2_path: str,
                            output_dir: str = "hybrid_analysis/comparison/results",
                            template1_structure: Optional[str] = None,
                            template2_structure: Optional[str] = None,
                            template1_semantic: Optional[str] = None,
                            template2_semantic: Optional[str] = None) -> Dict[str, Any]:
    """
    Запуск полного сравнительного анализа.
    
    Args:
        template1_path: Путь к первому шаблону
        template2_path: Путь ко второму шаблону
        output_dir: Директория для результатов
        template1_structure: Путь к JSON структуры первого шаблона
        template2_structure: Путь к JSON структуры второго шаблона
        template1_semantic: Путь к семантическому анализу первого шаблона
        template2_semantic: Путь к семантическому анализу второго шаблона
    
    Returns:
        Словарь с результатами
    """
    pipeline = TemplateComparisonPipeline(
        Path(template1_path),
        Path(template2_path),
        Path(output_dir),
        Path(template1_structure) if template1_structure else None,
        Path(template2_structure) if template2_structure else None,
        Path(template1_semantic) if template1_semantic else None,
        Path(template2_semantic) if template2_semantic else None
    )
    
    return pipeline.run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Полный сравнительный анализ шаблонов")
    parser.add_argument("--template1", required=True, help="Путь к первому шаблону")
    parser.add_argument("--template2", required=True, help="Путь ко второму шаблону")
    parser.add_argument("--output", default="hybrid_analysis/comparison/results", help="Директория для результатов")
    parser.add_argument("--structure1", help="Путь к JSON структуры первого шаблона")
    parser.add_argument("--structure2", help="Путь к JSON структуры второго шаблона")
    parser.add_argument("--semantic1", help="Путь к семантическому анализу первого шаблона")
    parser.add_argument("--semantic2", help="Путь к семантическому анализу второго шаблона")
    
    args = parser.parse_args()
    
    run_comparison_analysis(
        args.template1,
        args.template2,
        args.output,
        args.structure1,
        args.structure2,
        args.semantic1,
        args.semantic2
    )

