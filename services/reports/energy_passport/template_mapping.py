"""
Маппинг структуры шаблона энергопаспорта.

Определяет ячейки и диапазоны для заполнения данных в Excel-шаблоне.
"""

from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class GasMapping:
    """Маппинг ячеек для данных по газу на листе 'Структура пр 2'."""

    # Строка "Общее потребление по предприятию"
    row_total: int = 32
    # Строка "для собственных нужд"
    row_own_needs: int = 34
    # Строка "для хозяйственно-бытовых нужд"
    row_household: int = 35

    # Колонки для кварталов (2022-Q1, 2022-Q2, 2023-Q1, и т.д.)
    # Формат: (year, quarter) -> (col_gas_total, col_gas_own, col_gas_household)
    quarter_columns: Dict[Tuple[int, int], Tuple[int, int, int]] = None

    def __post_init__(self):
        """Инициализирует маппинг кварталов на колонки, если он не задан."""
        if self.quarter_columns is None:
            # Инициализируем маппинг кварталов на колонки
            # Структура: год, квартал -> (колонка общего потребления, собственных нужд, хоз-быт)
            # Колонки для газа в "Структура пр 2":
            # 2022: Q1=6, Q2=22, Q3=38, Q4=54
            # 2023: Q1=70, Q2=86, Q3=102, Q4=118
            # 2024: Q1=134, Q2=150, Q3=166, Q4=182
            self.quarter_columns = {
                (2022, 1): (6, 6, 6),  # Все в одной колонке для общего потребления
                (2022, 2): (22, 22, 22),
                (2022, 3): (38, 38, 38),
                (2022, 4): (54, 54, 54),
                (2023, 1): (
                    70,
                    70,
                    70,
                ),  # E32 для 2023-Q1 = колонка 5 (E), но в маппинге это 70
                (2023, 2): (86, 86, 86),
                (2023, 3): (102, 102, 102),
                (2023, 4): (118, 118, 118),
                (2024, 1): (134, 134, 134),
                (2024, 2): (150, 150, 150),
                (2024, 3): (166, 166, 166),
                (2024, 4): (182, 182, 182),
            }


@dataclass
class ElectricityProductMapping:
    """Маппинг ячеек для таблицы электроэнергии по видам продукции."""

    # Начальная строка таблицы (заголовок)
    start_row: int = 17

    # Виды продукции и их строки
    product_rows: Dict[str, int] = None

    # Колонки: норма, факт 2022, факт 2023, факт 2024, перерасход %
    columns: Dict[str, int] = None

    def __post_init__(self):
        """Инициализирует маппинг продукции и колонок, если они не заданы."""
        if self.product_rows is None:
            self.product_rows = {
                "Трубы ХВС": 17,
                "Фитинги ХВС (ХВС и ГВС)": 18,
                "Канализационные трубы": 19,
                "Канализационные фитинги": 20,
                "Трубы тёплого пола": 21,  # Возможно, нужно проверить
            }

        if self.columns is None:
            # Колонки для данных (нужно уточнить по шаблону)
            self.columns = {
                "norm": 2,  # Норма (кВт)
                "fact_2022": 3,  # Факт 2022 (кВт)
                "fact_2023": 4,  # Факт 2023 (кВт)
                "fact_2024": 5,  # Факт 2024 (кВт)
                "overrun_2022": 6,  # Перерасход 2022 (%)
                "overrun_2023": 7,  # Перерасход 2023 (%)
                "overrun_2024": 8,  # Перерасход 2024 (%)
            }


@dataclass
class GasSpecificConsumptionMapping:
    """Маппинг ячеек для удельного расхода газа."""

    # Лист для удельного расхода (может быть отдельный лист или блок в существующем)
    sheet_name: str = "Удельный расход газа"  # Или может быть в "Расход  на ед.п"

    # Ячейки для удельного расхода на м²
    row_per_m2: int = 10
    col_norm_per_m2: int = 2
    col_fact_per_m2: int = 3
    col_deviation_abs_per_m2: int = 4
    col_deviation_pct_per_m2: int = 5

    # Ячейки для удельного расхода на условную единицу
    row_per_unit: int = 11
    col_norm_per_unit: int = 2
    col_fact_per_unit: int = 3
    col_deviation_abs_per_unit: int = 4
    col_deviation_pct_per_unit: int = 5


# Глобальные экземпляры маппингов
GAS_MAPPING = GasMapping()
ELECTRICITY_PRODUCT_MAPPING = ElectricityProductMapping()
GAS_SPECIFIC_MAPPING = GasSpecificConsumptionMapping()


def get_gas_cell_for_quarter(
    year: int, quarter: int, data_type: str = "total"
) -> Tuple[int, int]:
    """
    Возвращает координаты ячейки для газа по кварталу.

    Args:
        year: Год (2022, 2023, 2024)
        quarter: Квартал (1, 2, 3, 4)
        data_type: Тип данных ("total", "own_needs", "household")

    Returns:
        (row, col) - координаты ячейки
    """
    mapping = GAS_MAPPING.quarter_columns.get((year, quarter))
    if not mapping:
        raise ValueError(f"Нет маппинга для квартала {year}-Q{quarter}")

    col = mapping[0]  # Пока используем одну колонку для всех типов

    if data_type == "total":
        row = GAS_MAPPING.row_total
    elif data_type == "own_needs":
        row = GAS_MAPPING.row_own_needs
    elif data_type == "household":
        row = GAS_MAPPING.row_household
    else:
        raise ValueError(f"Неизвестный тип данных: {data_type}")

    return (row, col)


def get_electricity_product_cell(
    product_name: str, column_type: str
) -> Tuple[int, int]:
    """
    Возвращает координаты ячейки для электроэнергии по виду продукции.

    Args:
        product_name: Название продукции
        column_type: Тип колонки ("norm", "fact_2022", "fact_2023", "fact_2024", "overrun_2022", etc.)

    Returns:
        (row, col) - координаты ячейки
    """
    row = ELECTRICITY_PRODUCT_MAPPING.product_rows.get(product_name)
    if not row:
        raise ValueError(f"Нет маппинга для продукции: {product_name}")

    col = ELECTRICITY_PRODUCT_MAPPING.columns.get(column_type)
    if not col:
        raise ValueError(f"Нет маппинга для колонки: {column_type}")

    return (row, col)
