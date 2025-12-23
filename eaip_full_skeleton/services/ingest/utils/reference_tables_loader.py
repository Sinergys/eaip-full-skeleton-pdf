"""
API для загрузки нормализованных таблиц из образцового отчёта.

Предоставляет функции для доступа к эталонным таблицам для использования
в тестах, генерации Excel-паспорта и Word-отчётов.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Определяем путь к корню проекта
_current_file = Path(__file__).resolve()
# От utils/ поднимаемся до корня: utils -> ingest -> services -> eaip_full_skeleton -> eaip
if "eaip_full_skeleton" in str(_current_file):
    PROJECT_ROOT = _current_file.parent.parent.parent.parent.parent
else:
    PROJECT_ROOT = _current_file.parent.parent.parent.parent

TABLES_DIR = PROJECT_ROOT / "data" / "reference_analysis" / "tables"

# Поддерживаемые типы таблиц
TABLE_TYPES = [
    "equipment",
    "specific_consumption",
    "consumption_structure",
    "losses",
    "measures",
    "other",
]


def load_reference_table(table_type: str) -> List[Dict[str, Any]]:
    """
    Загружает все таблицы указанного типа из образцового отчёта.

    Args:
        table_type: Тип таблицы (equipment, specific_consumption, consumption_structure,
                    losses, measures, other)

    Returns:
        Список нормализованных таблиц (каждая таблица содержит normalized_data)

    Raises:
        ValueError: Если table_type не поддерживается
        FileNotFoundError: Если файл с таблицами не найден
    """
    if table_type not in TABLE_TYPES:
        raise ValueError(
            f"Неподдерживаемый тип таблицы: {table_type}. "
            f"Доступные типы: {', '.join(TABLE_TYPES)}"
        )

    tables_file = TABLES_DIR / f"tables_{table_type}.json"

    if not tables_file.exists():
        raise FileNotFoundError(
            f"Файл с таблицами не найден: {tables_file}. "
            f"Запустите scripts/extract_reference_tables.py для извлечения таблиц."
        )

    with open(tables_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("tables", [])


def load_single_table(table_type: str, table_index: int) -> Optional[Dict[str, Any]]:
    """
    Загружает одну конкретную таблицу по типу и индексу.

    Args:
        table_type: Тип таблицы
        table_index: Индекс таблицы в документе (0-based)

    Returns:
        Словарь с данными таблицы или None, если не найдена
    """
    tables = load_reference_table(table_type)

    for table in tables:
        if table.get("table_index") == table_index:
            return table

    return None


def get_all_measures() -> List[Dict[str, Any]]:
    """
    Получает все мероприятия из всех таблиц типа "measures".

    Returns:
        Список нормализованных мероприятий
    """
    measures_tables = load_reference_table("measures")
    all_measures = []

    for table in measures_tables:
        normalized_data = table.get("normalized_data", [])
        if isinstance(normalized_data, list):
            all_measures.extend(normalized_data)

    return all_measures


def get_equipment_by_section(section: str = None) -> List[Dict[str, Any]]:
    """
    Получает оборудование, опционально фильтруя по разделу/цеху.

    Args:
        section: Название раздела/цеха (если None, возвращает всё оборудование)

    Returns:
        Список нормализованных записей оборудования
    """
    equipment_tables = load_reference_table("equipment")
    all_equipment = []

    for table in equipment_tables:
        normalized_data = table.get("normalized_data", [])
        if isinstance(normalized_data, list):
            all_equipment.extend(normalized_data)

    if section:
        # Фильтруем по разделу
        all_equipment = [
            item
            for item in all_equipment
            if section.lower() in item.get("section", "").lower()
        ]

    return all_equipment


def get_specific_consumption_by_period(period: str = None) -> List[Dict[str, Any]]:
    """
    Получает данные удельного расхода, опционально фильтруя по периоду.

    Args:
        period: Период (квартал/год), если None - возвращает все

    Returns:
        Список нормализованных записей удельного расхода
    """
    consumption_tables = load_reference_table("specific_consumption")
    all_consumption = []

    for table in consumption_tables:
        normalized_data = table.get("normalized_data", [])
        if isinstance(normalized_data, list):
            all_consumption.extend(normalized_data)

    if period:
        # Фильтруем по периоду
        all_consumption = [
            item
            for item in all_consumption
            if period.lower() in item.get("period", "").lower()
        ]

    return all_consumption


def get_losses_data() -> List[Dict[str, Any]]:
    """
    Получает все данные о потерях.

    Returns:
        Список нормализованных записей потерь
    """
    losses_tables = load_reference_table("losses")
    all_losses = []

    for table in losses_tables:
        normalized_data = table.get("normalized_data", [])
        if isinstance(normalized_data, list):
            all_losses.extend(normalized_data)

    return all_losses


def get_consumption_structure_by_period(period: str = None) -> List[Dict[str, Any]]:
    """
    Получает структуру потребления, опционально фильтруя по периоду.

    Args:
        period: Период (квартал/год), если None - возвращает все

    Returns:
        Список нормализованных записей структуры потребления
    """
    structure_tables = load_reference_table("consumption_structure")
    all_structure = []

    for table in structure_tables:
        normalized_data = table.get("normalized_data", [])
        if isinstance(normalized_data, list):
            all_structure.extend(normalized_data)

    if period:
        # Фильтруем по периоду
        all_structure = [
            item
            for item in all_structure
            if period.lower() in item.get("period", "").lower()
        ]

    return all_structure


def get_table_statistics() -> Dict[str, Any]:
    """
    Получает статистику по всем таблицам.

    Returns:
        Словарь со статистикой по каждому типу таблиц
    """
    stats = {}

    for table_type in TABLE_TYPES:
        try:
            tables = load_reference_table(table_type)
            total_items = 0

            for table in tables:
                normalized_data = table.get("normalized_data", [])
                if isinstance(normalized_data, list):
                    total_items += len(normalized_data)
                else:
                    total_items += 1

            stats[table_type] = {
                "tables_count": len(tables),
                "total_items": total_items,
            }
        except FileNotFoundError:
            stats[table_type] = {
                "tables_count": 0,
                "total_items": 0,
                "error": "File not found",  # type: ignore[dict-item]
            }

    return stats


# Маппинг для таблицы мероприятий (для использования в Excel/Word)
MEASURES_COLUMN_MAPPING = {
    "id": ["№", "номер", "id", "n", "#"],
    "name": ["наименование", "название", "мероприятие", "name", "measure"],
    "essence": ["суть", "описание", "описание мероприятия", "essence", "description"],
    "capex": [
        "капитальные",
        "затраты",
        "инвестиции",
        "capex",
        "investment",
        "стоимость",
        "руб",
        "сум",
    ],
    "saving_kwh": [
        "экономия",
        "квт·ч",
        "kwh",
        "электроэнергия",
        "saving",
        "экономия квт",
    ],
    "saving_money": [
        "экономия",
        "руб",
        "сум",
        "деньги",
        "saving_money",
        "экономия денег",
    ],
    "payback_years": ["окупаемость", "лет", "год", "payback", "срок окупаемости"],
    "priority": ["приоритет", "важность", "priority", "важность"],
}


def get_measures_mapping() -> Dict[str, List[str]]:
    """
    Возвращает маппинг колонок таблицы мероприятий.

    Returns:
        Словарь: поле модели -> список возможных названий колонок
    """
    return MEASURES_COLUMN_MAPPING.copy()
