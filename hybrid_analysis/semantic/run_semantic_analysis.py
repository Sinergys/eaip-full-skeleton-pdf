"""
Запуск всех модулей семантического анализа (Этап 2)
"""

import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from hybrid_analysis.semantic.cell_semantics_analyzer import analyze_cell_semantics
from hybrid_analysis.semantic.ontology_builder import build_ontology
from hybrid_analysis.semantic.semantic_mapper import create_semantic_mapping
from hybrid_analysis.semantic.semantics_validator import validate_semantics


def run_semantic_analysis(
    technical_dir: Path,
    aggregated_data_path: Path,
    output_dir: Path = None
):
    """
    Запуск полного семантического анализа.
    
    Args:
        technical_dir: Директория с результатами технического анализа
        aggregated_data_path: Путь к aggregated_data.json
        output_dir: Директория для сохранения результатов
    """
    if output_dir is None:
        output_dir = Path(__file__).parent
    
    cell_coords_path = technical_dir / "cell_coordinates.json"
    data_types_path = technical_dir / "data_types.json"
    
    print("=" * 80)
    print("🧠 ЭТАП 2: СЕМАНТИЧЕСКИЙ АНАЛИЗ")
    print("=" * 80)
    print(f"Технический анализ: {technical_dir}")
    print(f"Данные: {aggregated_data_path}")
    print(f"Выходная директория: {output_dir}")
    print()
    
    # 2.1 Семантический профиль ячеек
    print("📋 2.1 Создание семантического профиля ячеек...")
    cell_semantics_path = output_dir / "cell_semantics.json"
    semantics = analyze_cell_semantics(cell_coords_path, data_types_path, cell_semantics_path)
    print(f"   ✅ Сохранено: {cell_semantics_path}")
    print(f"   📊 Проанализировано ячеек: {semantics['summary']['total_cells_analyzed']}")
    print(f"   📊 Категории: {len(semantics['summary']['semantic_categories'])}")
    print()
    
    # 2.2 Генерация онтологии
    print("🔗 2.2 Генерация бизнес-онтологии...")
    ontology_path = output_dir / "energy_passport_ontology.json"
    ontology = build_ontology(cell_semantics_path, ontology_path)
    print(f"   ✅ Сохранено: {ontology_path}")
    print(f"   📊 Концептов: {len(ontology['concepts'])}")
    print(f"   📊 Отношений: {len(ontology['relationships'])}")
    print()
    
    # 2.3 Сопоставление с данными
    print("🗺️  2.3 Сопоставление с данными...")
    semantic_mapping_path = output_dir / "semantic_mapping.json"
    mapping = create_semantic_mapping(cell_semantics_path, aggregated_data_path, semantic_mapping_path)
    print(f"   ✅ Сохранено: {semantic_mapping_path}")
    print(f"   📊 Сопоставлено ячеек: {mapping['statistics']['mapped_cells']}")
    print(f"   📊 Не сопоставлено: {mapping['statistics']['unmapped_cells']}")
    print()
    
    # 2.4 Валидация семантики
    print("✅ 2.4 Валидация семантики...")
    validation_path = output_dir / "semantics_validation_report.json"
    validation = validate_semantics(cell_semantics_path, semantic_mapping_path, validation_path)
    print(f"   ✅ Сохранено: {validation_path}")
    print(f"   📊 Проверок: {validation['summary']['total_checks']}")
    print(f"   📊 Пройдено: {validation['summary']['passed']}")
    print(f"   📊 Провалено: {validation['summary']['failed']}")
    print(f"   📊 Предупреждений: {validation['summary']['warnings_count']}")
    print()
    
    print("=" * 80)
    print("✅ ЭТАП 2 ЗАВЕРШЕН")
    print("=" * 80)
    print(f"\nРезультаты сохранены в: {output_dir}")
    print("  - cell_semantics.json")
    print("  - energy_passport_ontology.json")
    print("  - semantic_mapping.json")
    print("  - semantics_validation_report.json")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Запуск семантического анализа")
    parser.add_argument("--technical-dir", required=True, help="Директория с техническим анализом")
    parser.add_argument("--aggregated-data", required=True, help="Путь к aggregated_data.json")
    parser.add_argument("--output-dir", help="Директория для сохранения результатов")
    
    args = parser.parse_args()
    
    technical_dir = Path(args.technical_dir)
    aggregated_data_path = Path(args.aggregated_data)
    output_dir = Path(args.output_dir) if args.output_dir else None
    
    run_semantic_analysis(technical_dir, aggregated_data_path, output_dir)

