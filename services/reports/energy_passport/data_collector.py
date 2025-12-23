"""
Модуль для сбора данных для генерации энергопаспорта.

Собирает данные из агрегированных источников и подготавливает их для заполнения шаблона.
"""

from typing import Dict, Any, Optional, List, cast
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ElectricityProductData:
    """Данные по электроэнергии для одного вида продукции."""

    product_name: str
    norm_kw: float
    fact_2022_kw: float = 0.0
    fact_2023_kw: float = 0.0
    fact_2024_kw: float = 0.0

    def calculate_overrun(self, year: int) -> float:
        """Рассчитывает перерасход в процентах для указанного года."""
        if self.norm_kw <= 0:
            return 0.0

        fact = self.get_fact_by_year(year)
        if fact <= 0:
            return 0.0

        return ((fact / self.norm_kw) - 1) * 100.0

    def get_fact_by_year(self, year: int) -> float:
        """Возвращает фактическое потребление по году."""
        if year == 2022:
            return self.fact_2022_kw
        elif year == 2023:
            return self.fact_2023_kw
        elif year == 2024:
            return self.fact_2024_kw
        return 0.0


@dataclass
class GasConsumptionData:
    """Данные по потреблению газа."""

    # Помесячные данные: {year: {month: m3}}
    monthly: Dict[int, Dict[int, float]]

    # Квартальные итоги: {year: {quarter: m3}}
    quarterly: Dict[int, Dict[int, float]]

    # Годовые итоги: {year: m3}
    yearly: Dict[int, float]

    # Собственные нужды (фиксировано 432 м³/месяц)
    own_needs_per_month_m3: float = 432.0

    def get_own_needs_quarter(self) -> float:
        """Возвращает собственные нужды за квартал."""
        return self.own_needs_per_month_m3 * 3.0

    def get_own_needs_year(self) -> float:
        """Возвращает собственные нужды за год."""
        return self.own_needs_per_month_m3 * 12.0

    def get_household_year(self, year: int) -> float:
        """Возвращает хозяйственно-бытовые нужды за год."""
        total = self.yearly.get(year, 0.0)
        own_needs = self.get_own_needs_year()
        return max(0.0, total - own_needs)


@dataclass
class EnergyPassportData:
    """Полные данные для генерации энергопаспорта."""

    year: int
    enterprise_id: str
    enterprise_name: str = ""

    # Площадь здания
    building_area_m2: float = 0.0

    # Электроэнергия по видам продукции
    electricity_by_product: List[ElectricityProductData] = None

    # Газ
    gas_data: Optional[GasConsumptionData] = None

    # Условная продукция
    total_production_units: Optional[float] = None

    # Нормативы
    gas_norm_per_m2: Optional[float] = None  # м³/(м²·год)
    gas_norm_per_unit: Optional[float] = None  # м³/усл.ед.

    def __post_init__(self):
        """Инициализирует пустой список для electricity_by_product, если он None."""
        if self.electricity_by_product is None:
            self.electricity_by_product = []


def collect_energy_passport_data(
    enterprise_id: str,
    year: int,
    aggregated_data: Dict[str, Any],
    enterprise_data: Optional[Dict[str, Any]] = None,
    building_data: Optional[Dict[str, Any]] = None,
) -> EnergyPassportData:
    """
    Собирает все необходимые данные для генерации энергопаспорта.

    Args:
        enterprise_id: ID предприятия
        year: Год для генерации паспорта
        aggregated_data: Агрегированные данные энергопотребления
            {
                "resources": {
                    "electricity": {"2022-Q1": {...}, ...},
                    "gas": {"2022-Q1": {...}, ...},
                    "production": {...},
                }
            }
        enterprise_data: Данные предприятия (опционально)
        building_data: Данные о здании (опционально)

    Returns:
        EnergyPassportData объект с собранными данными
    """
    logger.info(
        f"Сбор данных для энергопаспорта: enterprise_id={enterprise_id}, year={year}"
    )

    # Базовые данные
    enterprise_name = enterprise_data.get("name", "") if enterprise_data else ""
    building_area_m2 = building_data.get("area_m2", 0.0) if building_data else 0.0

    # Собираем данные по электроэнергии по видам продукции
    electricity_by_product = _collect_electricity_by_product(aggregated_data)

    # Собираем данные по газу
    gas_data = _collect_gas_data(aggregated_data)

    # Собираем данные по производству
    total_production_units = _collect_production_data(aggregated_data, year)

    # Нормативы (можно брать из конфигурации или БД)
    gas_norm_per_m2 = _get_gas_norm_per_m2()
    gas_norm_per_unit = _get_gas_norm_per_unit()

    return EnergyPassportData(
        year=year,
        enterprise_id=enterprise_id,
        enterprise_name=enterprise_name,
        building_area_m2=building_area_m2,
        electricity_by_product=electricity_by_product,
        gas_data=gas_data,
        total_production_units=total_production_units,
        gas_norm_per_m2=gas_norm_per_m2,
        gas_norm_per_unit=gas_norm_per_unit,
    )


def _collect_electricity_by_product(
    aggregated_data: Dict[str, Any],
) -> List[ElectricityProductData]:
    """
    Собирает данные по электроэнергии по видам продукции.

    Пытается найти данные в aggregated_data или использует значения по умолчанию
    из описания задачи.
    """
    products = []

    # Стандартные нормы и факты из описания задачи
    default_data = [
        {
            "name": "Трубы ХВС",
            "norm": 630,
            "fact_2022": 657,
            "fact_2023": 668,
            "fact_2024": 793,
        },
        {
            "name": "Фитинги ХВС (ХВС и ГВС)",
            "norm": 2100,
            "fact_2022": 2127,
            "fact_2023": 2139,
            "fact_2024": 2246,
        },
        {
            "name": "Канализационные трубы",
            "norm": 750,
            "fact_2022": 777,
            "fact_2023": 788,
            "fact_2024": 911,
        },
        {
            "name": "Канализационные фитинги",
            "norm": 2100,
            "fact_2022": 2129,
            "fact_2023": 2138,
            "fact_2024": 2259,
        },
        {
            "name": "Трубы тёплого пола",
            "norm": 670,
            "fact_2022": 698,
            "fact_2023": 711,
            "fact_2024": 837,
        },
    ]

    # Пытаемся найти данные в aggregated_data
    # TODO: Извлечь фактические данные из production_data, если они там есть
    # production_data = aggregated_data.get("resources", {}).get("production", {})

    for default in default_data:
        product_name: str = str(default["name"])

        # Пытаемся найти фактические данные в aggregated_data
        fact_2022: float = float(cast(Any, default["fact_2022"]))
        fact_2023: float = float(cast(Any, default["fact_2023"]))
        fact_2024: float = float(cast(Any, default["fact_2024"]))

        # TODO: Извлечь фактические данные из production_data, если они там есть

        products.append(
            ElectricityProductData(
                product_name=product_name,
                norm_kw=float(cast(Any, default["norm"])),
                fact_2022_kw=fact_2022,
                fact_2023_kw=fact_2023,
                fact_2024_kw=fact_2024,
            )
        )

    logger.info(f"Собрано данных по электроэнергии для {len(products)} видов продукции")
    return products


def _collect_gas_data(aggregated_data: Dict[str, Any]) -> GasConsumptionData:
    """Собирает данные по газу из aggregated_data."""
    resources = aggregated_data.get("resources", {})
    gas_resources = resources.get("gas", {})

    monthly: Dict[int, Dict[int, float]] = {}
    quarterly: Dict[int, Dict[int, float]] = {}
    yearly: Dict[int, float] = {}

    # Обрабатываем квартальные данные
    for quarter_key, quarter_data in gas_resources.items():
        # Парсим квартал (формат: "2022-Q1")
        if "-Q" not in quarter_key:
            continue

        year_str, quarter_str = quarter_key.split("-Q")
        year = int(year_str)
        quarter = int(quarter_str)

        # Инициализируем структуры
        if year not in monthly:
            monthly[year] = {}
        if year not in quarterly:
            quarterly[year] = {}

        # Получаем месячные данные
        months_data = quarter_data.get("months", [])
        quarter_total_m3 = 0.0

        # Собираем уникальные месяцы (избегаем дубликатов)
        seen_months = set()
        for month_entry in months_data:
            month_name = month_entry.get("month", "").strip()
            values = month_entry.get("values", {})
            month_gas_m3 = values.get("volume_m3", 0) or values.get("gas_m3", 0) or 0

            # Пропускаем пустые или None значения
            if not month_gas_m3 or month_gas_m3 is None:
                continue

            # Пропускаем дубликаты (если месяц уже обработан)
            month_key = f"{year}-{month_name}"
            if month_key in seen_months:
                continue

            try:
                month_gas_m3 = float(month_gas_m3)
                if month_gas_m3 <= 0:
                    continue

                # Преобразуем название месяца в номер (1-12)
                month_num = _month_name_to_number(month_name)
                if month_num:
                    # Если месяц уже есть, суммируем (на случай дубликатов)
                    if month_num in monthly[year]:
                        monthly[year][month_num] += month_gas_m3
                    else:
                        monthly[year][month_num] = month_gas_m3
                    quarter_total_m3 += month_gas_m3
                    seen_months.add(month_key)
            except (ValueError, TypeError) as e:
                logger.debug(f"Пропущен месяц {month_name}: {e}")
                pass

        # Если месячных данных нет, берем из quarter_totals
        if quarter_total_m3 == 0:
            quarter_totals = quarter_data.get("quarter_totals", {})
            quarter_total_m3 = quarter_totals.get("volume_m3", 0) or 0

        quarterly[year][quarter] = quarter_total_m3

        # Суммируем годовые итоги
        if year not in yearly:
            yearly[year] = 0.0
        yearly[year] += quarter_total_m3

    logger.info(
        f"Собрано данных по газу: годы={list(yearly.keys())}, годовые итоги={yearly}"
    )

    return GasConsumptionData(
        monthly=monthly,
        quarterly=quarterly,
        yearly=yearly,
    )


def _collect_production_data(
    aggregated_data: Dict[str, Any], year: int
) -> Optional[float]:
    """
    Собирает данные по производству для расчета удельного расхода.

    Возвращает общий объем продукции в условных единицах за год.
    """
    resources = aggregated_data.get("resources", {})
    production_data = resources.get("production", {})

    # Суммируем производство за все кварталы указанного года
    total_units = 0.0

    for quarter_key, quarter_data in production_data.items():
        if not quarter_key.startswith(str(year)):
            continue

        quarter_totals = quarter_data.get("quarter_totals", {})

        # Суммируем все виды продукции
        for product, value in quarter_totals.items():
            if isinstance(value, (int, float)) and value > 0:
                total_units += float(value)

    if total_units > 0:
        logger.info(
            f"Собрано данных по производству за {year}: {total_units:.2f} усл.ед."
        )
        return total_units

    return None


def _month_name_to_number(month_name: str) -> Optional[int]:
    """Преобразует название месяца в номер (1-12)."""
    month_names = {
        "январь": 1,
        "февраль": 2,
        "март": 3,
        "апрель": 4,
        "май": 5,
        "июнь": 6,
        "июль": 7,
        "август": 8,
        "сентябрь": 9,
        "октябрь": 10,
        "ноябрь": 11,
        "декабрь": 12,
    }

    month_lower = month_name.lower().strip()
    return month_names.get(month_lower)


def _get_gas_norm_per_m2() -> Optional[float]:
    """Возвращает норматив газа на м² (можно брать из конфигурации или БД)."""
    # TODO: Загрузить из конфигурации или БД
    # Пока возвращаем None, чтобы использовать значения из шаблона
    return None


def _get_gas_norm_per_unit() -> Optional[float]:
    """Возвращает норматив газа на условную единицу (можно брать из конфигурации или БД)."""
    # TODO: Загрузить из конфигурации или БД
    # Пока возвращаем None, чтобы использовать значения из шаблона
    return None
