"""
Запуск всех модулей технического анализа (Этап 1)
"""

import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from hybrid_analysis.technical.structural_parser import parse_template
from hybrid_analysis.technical.formula_analyzer import analyze_formulas
from hybrid_analysis.technical.data_type_classifier import classify_data_types

from templates.pcm690.templates_config import get_template_path


def run_technical_analysis(template_name: str = "new_energy_passport", output_dir: Path = None):
    """
    Запуск полного технического анализа шаблона.
    
    Args:
        template_name: Имя шаблона из templates_config
        output_dir: Директория для сохранения результатов
    """
    if output_dir is None:
        output_dir = Path(__file__).parent
    
    # Получение пути к шаблону
    template_path = get_template_path(template_name)
    
    print("=" * 80)
    print("🔬 ЭТАП 1: ТЕХНИЧЕСКИЙ АНАЛИЗ")
    print("=" * 80)
    print(f"Шаблон: {template_path}")
    print(f"Выходная директория: {output_dir}")
    print()
    
    # 1.1 Структурный парсинг
    print("📋 1.1 Структурный парсинг шаблонов...")
    cell_coords_path = output_dir / "cell_coordinates.json"
    structure = parse_template(template_path, cell_coords_path, max_rows=200)
    print(f"   ✅ Сохранено: {cell_coords_path}")
    print(f"   📊 Листов: {structure['total_sheets']}")
    print()
    
    # 1.2 Анализ формул
    print("🔢 1.2 Анализ формул и ссылок...")
    formulas_path = output_dir / "formulas_map.json"
    formulas_result = analyze_formulas(template_path, formulas_path)
    print(f"   ✅ Сохранено: {formulas_path}")
    print(f"   📊 Всего формул: {formulas_result['total_formulas']}")
    print()
    
    # 1.3 Классификация типов данных
    print("🏷️  1.3 Определение типов данных...")
    data_types_path = output_dir / "data_types.json"
    classification = classify_data_types(template_path, data_types_path, max_rows=200)
    print(f"   ✅ Сохранено: {data_types_path}")
    print("   📊 Категории:")
    for cat, count in classification["summary"]["categories"].items():
        if count > 0:
            print(f"      - {cat}: {count}")
    print()
    
    print("=" * 80)
    print("✅ ЭТАП 1 ЗАВЕРШЕН")
    print("=" * 80)
    print(f"\nРезультаты сохранены в: {output_dir}")
    print("  - cell_coordinates.json")
    print("  - formulas_map.json")
    print("  - data_types.json")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Запуск технического анализа")
    parser.add_argument("--template-name", default="new_energy_passport", help="Имя шаблона")
    parser.add_argument("--output-dir", help="Директория для сохранения результатов")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir) if args.output_dir else None
    
    run_technical_analysis(template_name=args.template_name, output_dir=output_dir)

