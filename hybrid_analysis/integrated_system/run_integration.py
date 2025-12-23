"""
Этап 5: Полный цикл интеграции и валидации
Запуск универсального заполнения с валидацией
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from universal_filler import fill_template
from validator import validate_filling


class IntegrationPipeline:
    """Пайплайн для полного цикла интеграции и валидации."""
    
    def __init__(self,
                 template_path: Path,
                 data_path: Path,
                 output_dir: Path,
                 structural_analysis_path: Optional[Path] = None,
                 semantic_mapping_path: Optional[Path] = None,
                 ml_patterns_path: Optional[Path] = None,
                 adapter_path: Optional[Path] = None):
        """
        Инициализация пайплайна.
        
        Args:
            template_path: Путь к шаблону
            data_path: Путь к данным
            output_dir: Директория для результатов
            structural_analysis_path: Путь к техническому анализу (опционально)
            semantic_mapping_path: Путь к семантическому маппингу (опционально)
            ml_patterns_path: Путь к ML паттернам (опционально)
            adapter_path: Путь к адаптерам (опционально)
        """
        self.template_path = Path(template_path)
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.structural_analysis_path = Path(structural_analysis_path) if structural_analysis_path else None
        self.semantic_mapping_path = Path(semantic_mapping_path) if semantic_mapping_path else None
        self.ml_patterns_path = Path(ml_patterns_path) if ml_patterns_path else None
        self.adapter_path = Path(adapter_path) if adapter_path else None
        
        # Пути к результатам
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.filled_template_path = self.output_dir / "filled_template.xlsx"
        self.validation_report_path = self.output_dir / "validation_report.json"
        self.summary_path = self.output_dir / "integration_summary.json"
        
        self.results = {}
    
    def run(self) -> Dict[str, Any]:
        """
        Запуск полного цикла интеграции и валидации.
        
        Returns:
            Словарь с результатами всех этапов
        """
        print("=" * 80)
        print("ЭТАП 5: ИНТЕГРАЦИЯ И ВАЛИДАЦИЯ")
        print("=" * 80)
        
        self.results = {
            "pipeline_start": datetime.now().isoformat(),
            "template_path": str(self.template_path),
            "data_path": str(self.data_path),
            "stages": {}
        }
        
        # Этап 1: Заполнение шаблона
        print("\n📝 Этап 1: Заполнение шаблона...")
        fill_result = self._run_filling()
        self.results["stages"]["filling"] = {
            "status": "completed",
            "output_file": str(self.filled_template_path),
            "summary": self._summarize_filling(fill_result)
        }
        
        # Этап 2: Валидация заполнения
        print("\n✅ Этап 2: Валидация заполнения...")
        validation_result = self._run_validation()
        self.results["stages"]["validation"] = {
            "status": "completed",
            "output_file": str(self.validation_report_path),
            "summary": self._summarize_validation(validation_result)
        }
        
        # Финальная сводка
        self.results["pipeline_end"] = datetime.now().isoformat()
        self.results["overall_summary"] = self._create_overall_summary(fill_result, validation_result)
        
        # Сохранение сводки
        self._save_summary()
        
        print("\n" + "=" * 80)
        print("✅ ИНТЕГРАЦИЯ И ВАЛИДАЦИЯ ЗАВЕРШЕНЫ")
        print("=" * 80)
        self._print_summary()
        
        return self.results
    
    def _run_filling(self) -> Dict[str, Any]:
        """Запуск заполнения шаблона."""
        result = fill_template(
            self.template_path,
            self.data_path,
            self.filled_template_path,
            self.structural_analysis_path,
            self.semantic_mapping_path,
            self.ml_patterns_path,
            self.adapter_path
        )
        return result
    
    def _run_validation(self) -> Dict[str, Any]:
        """Запуск валидации заполнения."""
        result = validate_filling(
            self.filled_template_path,
            self.validation_report_path,
            self.template_path,  # Используем оригинальный шаблон для сравнения
            self.semantic_mapping_path
        )
        return result
    
    def _summarize_filling(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Создание сводки заполнения."""
        total = result.get("filled_cells", 0) + result.get("skipped_cells", 0)
        success_rate = (result.get("filled_cells", 0) / total * 100) if total > 0 else 0
        
        return {
            "filled_cells": result.get("filled_cells", 0),
            "skipped_cells": result.get("skipped_cells", 0),
            "total_attempted": total,
            "success_rate": round(success_rate, 2),
            "errors_count": len(result.get("errors", [])),
            "warnings_count": len(result.get("warnings", []))
        }
    
    def _summarize_validation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Создание сводки валидации."""
        return {
            "status": result.get("status", "unknown"),
            "score": result.get("score", 0.0),
            "issues_count": len(result.get("issues", [])),
            "warnings_count": len(result.get("warnings", [])),
            "validations": {
                k: {"status": v.get("status", "unknown")}
                for k, v in result.get("validations", {}).items()
            }
        }
    
    def _create_overall_summary(self, fill_result: Dict[str, Any],
                                validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Создание общей сводки."""
        fill_stats = self._summarize_filling(fill_result)
        validation_stats = self._summarize_validation(validation_result)
        
        return {
            "filling_success_rate": fill_stats["success_rate"],
            "validation_status": validation_stats["status"],
            "validation_score": validation_stats["score"],
            "overall_status": self._calculate_overall_status(fill_stats, validation_stats),
            "ready_for_use": validation_stats["status"] in ["good", "excellent"] and
                           fill_stats["success_rate"] > 50
        }
    
    def _calculate_overall_status(self, fill_stats: Dict[str, Any],
                                  validation_stats: Dict[str, Any]) -> str:
        """Расчет общего статуса."""
        fill_rate = fill_stats["success_rate"]
        validation_score = validation_stats["score"]
        
        # Средняя оценка
        overall_score = (fill_rate / 100.0 + validation_score) / 2
        
        if overall_score >= 0.8:
            return "excellent"
        elif overall_score >= 0.6:
            return "good"
        elif overall_score >= 0.4:
            return "acceptable"
        else:
            return "poor"
    
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
        print(f"  Статус заполнения: {summary['filling_success_rate']:.1f}%")
        print(f"  Статус валидации: {summary['validation_status']} ({summary['validation_score']:.2%})")
        print(f"  Общий статус: {summary['overall_status']}")
        print(f"  Готов к использованию: {'✅ Да' if summary['ready_for_use'] else '❌ Нет'}")
        
        print("\n📁 РЕЗУЛЬТАТЫ:")
        print(f"  Заполненный шаблон: {self.filled_template_path}")
        print(f"  Отчет валидации: {self.validation_report_path}")
        print(f"  Сводка: {self.summary_path}")


def run_integration_pipeline(template_path: str,
                             data_path: str,
                             output_dir: str,
                             structural_analysis_path: Optional[str] = None,
                             semantic_mapping_path: Optional[str] = None,
                             ml_patterns_path: Optional[str] = None,
                             adapter_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Запуск полного цикла интеграции и валидации.
    
    Args:
        template_path: Путь к шаблону
        data_path: Путь к данным
        output_dir: Директория для результатов
        structural_analysis_path: Путь к техническому анализу (опционально)
        semantic_mapping_path: Путь к семантическому маппингу (опционально)
        ml_patterns_path: Путь к ML паттернам (опционально)
        adapter_path: Путь к адаптерам (опционально)
    
    Returns:
        Словарь с результатами
    """
    pipeline = IntegrationPipeline(
        Path(template_path),
        Path(data_path),
        Path(output_dir),
        Path(structural_analysis_path) if structural_analysis_path else None,
        Path(semantic_mapping_path) if semantic_mapping_path else None,
        Path(ml_patterns_path) if ml_patterns_path else None,
        Path(adapter_path) if adapter_path else None
    )
    
    return pipeline.run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Полный цикл интеграции и валидации")
    parser.add_argument("--template", required=True, help="Путь к шаблону")
    parser.add_argument("--data", required=True, help="Путь к данным JSON")
    parser.add_argument("--output", required=True, help="Директория для результатов")
    parser.add_argument("--structural", help="Путь к техническому анализу")
    parser.add_argument("--semantic", help="Путь к семантическому маппингу")
    parser.add_argument("--ml", help="Путь к ML паттернам")
    parser.add_argument("--adapter", help="Путь к адаптерам")
    
    args = parser.parse_args()
    
    run_integration_pipeline(
        args.template,
        args.data,
        args.output,
        args.structural,
        args.semantic,
        args.ml,
        args.adapter
    )

