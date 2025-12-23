"""
Тест API для загрузки нормализованных таблиц.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eaip_full_skeleton" / "services" / "ingest" / "utils"))

from reference_tables_loader import (
    get_all_measures,
    get_equipment_by_section,
    get_losses_data,
    get_table_statistics,
    get_measures_mapping,
)


def main():
    """Тестирует API загрузки таблиц."""
    print("🧪 ТЕСТ API ЗАГРУЗКИ ТАБЛИЦ ИЗ ОБРАЗЦОВОГО ОТЧЁТА")
    print("=" * 80)
    
    # Статистика
    print("\n📊 Статистика по таблицам:")
    stats = get_table_statistics()
    for table_type, stat in stats.items():
        print(f"  - {table_type}: {stat['tables_count']} таблиц, {stat['total_items']} записей")
    
    # Тест загрузки мероприятий
    print("\n📋 Тест загрузки мероприятий:")
    measures = get_all_measures()
    print(f"  - Найдено мероприятий: {len(measures)}")
    for i, measure in enumerate(measures[:3], 1):
        print(f"    {i}. {measure.get('name', 'Без названия')}")
        if measure.get('raw_data'):
            print(f"       Сырые данные: {list(measure['raw_data'].keys())[:3]}...")
    
    # Тест загрузки оборудования
    print("\n⚙️  Тест загрузки оборудования:")
    equipment = get_equipment_by_section()
    print(f"  - Всего оборудования: {len(equipment)}")
    if equipment:
        print(f"    Пример: {equipment[0].get('name', 'N/A')} ({equipment[0].get('power_kw', 0)} кВт)")
    
    # Тест загрузки потерь
    print("\n📉 Тест загрузки потерь:")
    losses = get_losses_data()
    print(f"  - Найдено записей о потерях: {len(losses)}")
    if losses:
        print(f"    Пример: {losses[0].get('transformer', 'N/A')} ({losses[0].get('power_kva', 0)} кВА)")
    
    # Тест маппинга мероприятий
    print("\n🗺️  Тест маппинга мероприятий:")
    mapping = get_measures_mapping()
    print(f"  - Поля маппинга: {list(mapping.keys())}")
    print(f"    Пример для 'name': {mapping['name']}")
    
    print("\n✅ Все тесты пройдены!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

