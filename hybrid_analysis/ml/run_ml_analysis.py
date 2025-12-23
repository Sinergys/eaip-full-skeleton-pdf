"""
Запуск всех модулей статистического анализа (Этап 3)
"""

import sys
from pathlib import Path
from typing import Optional

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from hybrid_analysis.ml.pattern_analyzer import analyze_patterns
from hybrid_analysis.ml.format_predictor import predict_formats
from hybrid_analysis.ml.adaptation_model import train_adaptation_model
from hybrid_analysis.ml.ml_validator import validate_ml_models

from templates.pcm690.templates_config import get_template_path


def run_ml_analysis(
    template_name: str = "new_energy_passport",
    semantic_dir: Path = None,
    technical_dir: Path = None,
    output_dir: Path = None,
    filled_template_path: Optional[Path] = None
):
    """
    Запуск полного статистического анализа.
    
    Args:
        template_name: Имя шаблона
        semantic_dir: Директория с результатами семантического анализа
        technical_dir: Директория с результатами технического анализа
        output_dir: Директория для сохранения результатов
        filled_template_path: Путь к заполненному шаблону (опционально)
    """
    if semantic_dir is None:
        semantic_dir = Path(__file__).parent.parent / "semantic"
    if technical_dir is None:
        technical_dir = Path(__file__).parent.parent / "technical"
    if output_dir is None:
        output_dir = Path(__file__).parent
    
    template_path = get_template_path(template_name)
    semantic_mapping_path = semantic_dir / "semantic_mapping.json"
    
    print("=" * 80)
    print("🤖 ЭТАП 3: СТАТИСТИЧЕСКИЙ АНАЛИЗ (ML)")
    print("=" * 80)
    print(f"Шаблон: {template_path}")
    print(f"Семантический анализ: {semantic_dir}")
    print(f"Выходная директория: {output_dir}")
    print()
    
    # 3.1 Анализ паттернов заполнения
    print("📊 3.1 Анализ паттернов заполнения...")
    patterns_path = output_dir / "filling_patterns.json"
    patterns = analyze_patterns(template_path, patterns_path, filled_template_path)
    print(f"   ✅ Сохранено: {patterns_path}")
    print(f"   📊 Форматов чисел: {patterns['statistics']['total_number_formats']}")
    print()
    
    # 3.2 Предсказание форматов
    print("🔮 3.2 Предсказание форматов отображения...")
    format_predictions_path = output_dir / "format_predictions.json"
    predictions = predict_formats(semantic_mapping_path, format_predictions_path, patterns_path)
    print(f"   ✅ Сохранено: {format_predictions_path}")
    print(f"   📊 Всего предсказаний: {predictions['statistics']['total_predictions']}")
    print()
    
    # 3.3 Обучение модели адаптации
    print("🎓 3.3 Обучение на существующих данных...")
    adaptation_model_path = output_dir / "adaptation_model.pkl"
    model = train_adaptation_model(
        semantic_mapping_path,
        format_predictions_path,
        adaptation_model_path,
        patterns_path
    )
    print(f"   ✅ Сохранено: {adaptation_model_path}")
    print(f"   📊 Правил: {model.model['statistics']['total_rules']}")
    print(f"   📊 Покрытие: {model.model['statistics']['mapping_coverage']:.2f}%")
    print()
    
    # 3.4 Валидация ML-моделей
    print("✅ 3.4 Валидация ML-моделей...")
    ml_validation_path = output_dir / "ml_validation_report.json"
    validation = validate_ml_models(
        adaptation_model_path,
        format_predictions_path,
        semantic_mapping_path,
        ml_validation_path
    )
    print(f"   ✅ Сохранено: {ml_validation_path}")
    print(f"   📊 Проверок: {validation['summary']['total_checks']}")
    print(f"   📊 Пройдено: {validation['summary']['passed']}")
    print()
    
    print("=" * 80)
    print("✅ ЭТАП 3 ЗАВЕРШЕН")
    print("=" * 80)
    print(f"\nРезультаты сохранены в: {output_dir}")
    print("  - filling_patterns.json")
    print("  - format_predictions.json")
    print("  - adaptation_model.pkl")
    print("  - ml_validation_report.json")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Запуск статистического анализа")
    parser.add_argument("--template-name", default="new_energy_passport", help="Имя шаблона")
    parser.add_argument("--semantic-dir", help="Директория с семантическим анализом")
    parser.add_argument("--technical-dir", help="Директория с техническим анализом")
    parser.add_argument("--output-dir", help="Директория для сохранения результатов")
    parser.add_argument("--filled-template", help="Путь к заполненному шаблону")
    
    args = parser.parse_args()
    
    semantic_dir = Path(args.semantic_dir) if args.semantic_dir else None
    technical_dir = Path(args.technical_dir) if args.technical_dir else None
    output_dir = Path(args.output_dir) if args.output_dir else None
    filled_template = Path(args.filled_template) if args.filled_template else None
    
    run_ml_analysis(
        template_name=args.template_name,
        semantic_dir=semantic_dir,
        technical_dir=technical_dir,
        output_dir=output_dir,
        filled_template_path=filled_template
    )

