"""
Централизованные формулы и расчёты для заполнения энергопаспорта.

Все расчёты для Excel-паспорта должны выполняться через функции этого модуля
для обеспечения консистентности, правильности единиц измерения и обработки edge-кейсов.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

try:
    from .energy_units import HOURS_PER_YEAR, MONTHS_PER_QUARTER
except ImportError:
    # Fallback для случаев, когда модуль импортируется напрямую
    from energy_units import HOURS_PER_YEAR, MONTHS_PER_QUARTER

logger = logging.getLogger(__name__)


# ============================================================================
# Структуры данных для расчётов
# ============================================================================


@dataclass
class QuarterData:
    """Данные по кварталу."""

    quarter: str  # "2022-Q1"
    year: int
    quarter_num: int
    electricity_active_kwh: float = 0.0
    electricity_reactive_kvarh: float = 0.0
    gas_m3: float = 0.0
    water_m3: float = 0.0
    fuel_ton: float = 0.0
    coal_ton: float = 0.0
    heat_gcal: float = 0.0
    production_kg: float = 0.0
    by_usage: Optional[Dict[str, float]] = (
        None  # {"technological": ..., "own_needs": ..., ...}
    )


@dataclass
class EquipmentData:
    """Данные по оборудованию."""

    total_installed_power_kw: float = 0.0
    total_used_power_kw: float = 0.0
    total_items_count: int = 0
    vfd_count: int = 0


@dataclass
class LossesData:
    """Данные по потерям."""

    loss_active_month_kwh: float = 0.0
    loss_reactive_month_kvarh: float = 0.0
    transformer_power_kva: float = 0.0
    hours_per_month: float = 720.0


# ============================================================================
# Формулы по листам
# ============================================================================


def calculate_quarter_losses(loss_month_kwh: float) -> float:
    """
    Расчёт потерь за квартал.

    Формула: Потери_квартал = Потери_месяц * 3

    Единицы: кВт·ч

    Args:
        loss_month_kwh: Потери за месяц, кВт·ч

    Returns:
        Потери за квартал, кВт·ч
    """
    return loss_month_kwh * MONTHS_PER_QUARTER


def calculate_loss_percentage(
    loss_kwh: float, transformer_power_kva: float, hours: float
) -> float:
    """
    Расчёт процента потерь.

    Формула: Процент_потерь = (Потери / (Мощность * Часы)) * 100

    Единицы: %

    Args:
        loss_kwh: Потери, кВт·ч
        transformer_power_kva: Мощность трансформатора, кВА
        hours: Количество часов

    Returns:
        Процент потерь (0-100)

    Edge-кейсы:
        - Если мощность или часы = 0, возвращает 0
    """
    if transformer_power_kva <= 0 or hours <= 0:
        logger.warning(
            f"Невозможно рассчитать процент потерь: мощность={transformer_power_kva} кВА, "
            f"часы={hours}. Возвращаю 0."
        )
        return 0.0

    # Конвертируем кВА в кВт (приблизительно, cos φ = 0.9)
    transformer_power_kw = transformer_power_kva * 0.9
    total_energy = transformer_power_kw * hours

    if total_energy <= 0:
        return 0.0

    percentage = (loss_kwh / total_energy) * 100.0
    return min(100.0, max(0.0, percentage))  # Ограничиваем 0-100%


def calculate_specific_consumption(
    energy_kwh: float, production_kg: float, default_on_zero: float = 0.0
) -> float:
    """
    Расчёт удельного расхода энергии на единицу продукции.

    Формула: Удельный_расход = Энергия / Производство

    Единицы: кВт·ч/кг

    Args:
        energy_kwh: Потребление энергии, кВт·ч
        production_kg: Объём производства, кг
        default_on_zero: Значение при отсутствии производства (по умолчанию 0)

    Returns:
        Удельный расход, кВт·ч/кг

    Edge-кейсы:
        - Если производство = 0, возвращает default_on_zero
        - Если производство < 0.001 кг, возвращает default_on_zero (защита от деления на очень малое число)
    """
    if production_kg <= 0.001:  # Порог для защиты от деления на очень малое число
        logger.warning(
            f"Невозможно рассчитать удельный расход: производство={production_kg} кг. "
            f"Возвращаю {default_on_zero}."
        )
        return default_on_zero

    if energy_kwh < 0:
        logger.warning(
            f"Отрицательное потребление энергии: {energy_kwh} кВт·ч. Использую 0."
        )
        energy_kwh = 0.0

    specific = energy_kwh / production_kg

    # Проверка на разумность результата (защита от астрономических чисел)
    if specific > 1000000:  # 1 МВт·ч/кг - явно нереалистично
        logger.error(
            f"Нереалистичный удельный расход: {specific} кВт·ч/кг "
            f"(энергия={energy_kwh}, производство={production_kg}). "
            f"Возвращаю {default_on_zero}."
        )
        return default_on_zero

    return specific


def calculate_equipment_usage_coefficient(
    used_power_kw: float, installed_power_kw: float
) -> float:
    """
    Расчёт коэффициента использования оборудования.

    Формула: Коэффициент = Используемая_мощность / Установленная_мощность

    Единицы: безразмерный (0-1)

    Args:
        used_power_kw: Используемая мощность, кВт
        installed_power_kw: Установленная мощность, кВт

    Returns:
        Коэффициент использования (0-1)

    Edge-кейсы:
        - Если установленная мощность = 0, возвращает 0
        - Ограничивается максимумом 1.0
    """
    if installed_power_kw <= 0:
        logger.warning(
            f"Невозможно рассчитать коэффициент использования: "
            f"установленная мощность={installed_power_kw} кВт. Возвращаю 0."
        )
        return 0.0

    if used_power_kw < 0:
        logger.warning(
            f"Отрицательная используемая мощность: {used_power_kw} кВт. Использую 0."
        )
        used_power_kw = 0.0

    coefficient = used_power_kw / installed_power_kw

    # Коэффициент не может быть больше 1.0
    return min(1.0, max(0.0, coefficient))


def calculate_annual_consumption_from_power(
    power_kw: float, hours_per_year: float = None
) -> float:
    """
    Расчёт годового потребления из мощности.

    Формула: Потребление_год = Мощность * Часы_в_году

    Единицы: кВт·ч

    Args:
        power_kw: Мощность, кВт
        hours_per_year: Количество часов в году (по умолчанию 8760)

    Returns:
        Годовое потребление, кВт·ч
    """
    if hours_per_year is None:
        hours_per_year = HOURS_PER_YEAR

    if power_kw < 0:
        logger.warning(f"Отрицательная мощность: {power_kw} кВт. Использую 0.")
        power_kw = 0.0

    return power_kw * hours_per_year


def calculate_consumption_from_monthly_power(
    monthly_power_kw: float, hours_per_month: float = None
) -> float:
    """
    Расчёт месячного потребления из средней мощности за месяц.

    Формула: Потребление_месяц = Средняя_мощность * Часы_в_месяце

    Единицы: кВт·ч

    Args:
        monthly_power_kw: Средняя мощность за месяц, кВт
        hours_per_month: Количество часов в месяце (по умолчанию 720)

    Returns:
        Месячное потребление, кВт·ч
    """
    try:
        from .energy_units import HOURS_PER_MONTH
    except ImportError:
        from energy_units import HOURS_PER_MONTH

    if hours_per_month is None:
        hours_per_month = HOURS_PER_MONTH

    if monthly_power_kw < 0:
        logger.warning(f"Отрицательная мощность: {monthly_power_kw} кВт. Использую 0.")
        monthly_power_kw = 0.0

    return monthly_power_kw * hours_per_month


def calculate_quarter_consumption_from_monthly_power(
    monthly_power_kw: float, hours_per_month: float = None
) -> float:
    """
    Расчёт квартального потребления из средней мощности за месяц.

    Формула: Потребление_квартал = Средняя_мощность_месяц * Часы_в_месяце * 3

    Единицы: кВт·ч

    Args:
        monthly_power_kw: Средняя мощность за месяц, кВт
        hours_per_month: Количество часов в месяце (по умолчанию 720)

    Returns:
        Квартальное потребление, кВт·ч
    """
    monthly_consumption = calculate_consumption_from_monthly_power(
        monthly_power_kw, hours_per_month
    )
    try:
        from .energy_units import MONTHS_PER_QUARTER
    except ImportError:
        from energy_units import MONTHS_PER_QUARTER

    return monthly_consumption * MONTHS_PER_QUARTER


def calculate_quarter_reactive_consumption_from_monthly_power(
    monthly_reactive_power_kvar: float, hours_per_month: float = None
) -> float:
    """
    Расчёт квартального реактивного потребления из средней реактивной мощности за месяц.

    Формула: Реактивное_потребление_квартал = Средняя_реактивная_мощность_месяц * Часы_в_месяце * 3

    Единицы: кВАр·ч

    Args:
        monthly_reactive_power_kvar: Средняя реактивная мощность за месяц, кВАр
        hours_per_month: Количество часов в месяце (по умолчанию 720)

    Returns:
        Квартальное реактивное потребление, кВАр·ч
    """
    try:
        from .energy_units import HOURS_PER_MONTH, MONTHS_PER_QUARTER
    except ImportError:
        from energy_units import HOURS_PER_MONTH, MONTHS_PER_QUARTER

    if hours_per_month is None:
        hours_per_month = HOURS_PER_MONTH

    if monthly_reactive_power_kvar < 0:
        logger.warning(
            f"Отрицательная реактивная мощность: {monthly_reactive_power_kvar} кВАр. Использую 0."
        )
        monthly_reactive_power_kvar = 0.0

    # Месячное реактивное потребление
    monthly_reactive_consumption = monthly_reactive_power_kvar * hours_per_month

    # Квартальное реактивное потребление
    return monthly_reactive_consumption * MONTHS_PER_QUARTER


def calculate_average_power_per_unit(total_power_kw: float, items_count: int) -> float:
    """
    Расчёт средней мощности на единицу оборудования.

    Формула: Средняя_мощность = Общая_мощность / Количество_единиц

    Единицы: кВт

    Args:
        total_power_kw: Общая мощность, кВт
        items_count: Количество единиц оборудования

    Returns:
        Средняя мощность на единицу, кВт

    Edge-кейсы:
        - Если количество единиц = 0, возвращает 0
    """
    if items_count <= 0:
        logger.warning(
            f"Невозможно рассчитать среднюю мощность: количество единиц={items_count}. "
            f"Возвращаю 0."
        )
        return 0.0

    if total_power_kw < 0:
        logger.warning(
            f"Отрицательная общая мощность: {total_power_kw} кВт. Использую 0."
        )
        total_power_kw = 0.0

    return total_power_kw / items_count


def calculate_balance_total(
    technological: float, own_needs: float, production: float, household: float
) -> float:
    """
    Расчёт итогового потребления по балансу.

    Формула: Итого = Технологические + Собственные_нужды + Производственные + Хоз-бытовые

    Единицы: кВт·ч

    Args:
        technological: Технологические нужды, кВт·ч
        own_needs: Собственные нужды, кВт·ч
        production: Производственные нужды, кВт·ч
        household: Хоз-бытовые нужды, кВт·ч

    Returns:
        Итого, кВт·ч
    """
    # Нормализуем отрицательные значения
    values = [technological, own_needs, production, household]
    normalized = [max(0.0, v) if v is not None else 0.0 for v in values]

    total = sum(normalized)

    if total < 0:
        logger.warning(f"Отрицательный итог баланса: {total} кВт·ч. Возвращаю 0.")
        return 0.0

    return total


def distribute_quarter_by_usage_categories(
    quarter_total_kwh: float, yearly_categories: Dict[str, float]
) -> Dict[str, float]:
    """
    Распределение квартального потребления по категориям на основе годовых данных.

    Формула: Категория_квартал = (Категория_год / Итого_год) * Итого_квартал

    Единицы: кВт·ч

    Args:
        quarter_total_kwh: Итого по кварталу, кВт·ч
        yearly_categories: Словарь категорий по году, кВт·ч

    Returns:
        Словарь категорий по кварталу, кВт·ч

    Edge-кейсы:
        - Если годовой итог = 0, возвращает равномерное распределение
    """
    yearly_total = sum(yearly_categories.values())

    if yearly_total <= 0:
        logger.warning(
            "Годовой итог по категориям = 0. Равномерно распределяю квартальное потребление."
        )
        # Равномерное распределение
        category_count = len(yearly_categories)
        if category_count > 0:
            per_category = quarter_total_kwh / category_count
            return {cat: per_category for cat in yearly_categories.keys()}
        else:
            return {}

    # Пропорциональное распределение
    result = {}
    for category, yearly_value in yearly_categories.items():
        if yearly_value < 0:
            logger.warning(
                f"Отрицательное значение категории {category}: {yearly_value}. Использую 0."
            )
            yearly_value = 0.0

        quarter_value = (yearly_value / yearly_total) * quarter_total_kwh
        result[category] = max(0.0, quarter_value)

    return result


def calculate_equipment_used_power(
    installed_power_kw: float, usage_factor: float = 0.8
) -> float:
    """
    Расчёт используемой мощности оборудования.

    Формула: Используемая_мощность = Установленная_мощность * Коэффициент_использования

    Единицы: кВт

    Args:
        installed_power_kw: Установленная мощность, кВт
        usage_factor: Коэффициент использования (по умолчанию 0.8 = 80%)

    Returns:
        Используемая мощность, кВт
    """
    if installed_power_kw < 0:
        logger.warning(
            f"Отрицательная установленная мощность: {installed_power_kw} кВт. Использую 0."
        )
        installed_power_kw = 0.0

    if usage_factor < 0 or usage_factor > 1:
        logger.warning(
            f"Некорректный коэффициент использования: {usage_factor}. "
            f"Ограничиваю до диапазона [0, 1]."
        )
        usage_factor = max(0.0, min(1.0, usage_factor))

    return installed_power_kw * usage_factor


# ============================================================================
# Вспомогательные функции для работы с данными
# ============================================================================


def extract_quarter_data(quarter: str, agg_data: Dict[str, Any]) -> QuarterData:
    """
    Извлекает и нормализует данные по кварталу.

    Args:
        quarter: Квартал (например, "2022-Q1")
        agg_data: Агрегированные данные

    Returns:
        QuarterData объект
    """
    resources = agg_data.get("resources", {})

    # Парсим квартал
    year = int(quarter.split("-")[0]) if "-" in quarter else 2022
    quarter_num = int(quarter.split("-Q")[1]) if "-Q" in quarter else 1

    # Электроэнергия
    electricity = resources.get("electricity", {}).get(quarter, {})
    elec_totals = electricity.get("quarter_totals", {})
    active_kwh = elec_totals.get("active_kwh", 0) or 0
    reactive_kvarh = elec_totals.get("reactive_kvarh", 0) or 0

    # Газ
    gas = resources.get("gas", {}).get(quarter, {})
    gas_totals = gas.get("quarter_totals", {})
    gas_m3 = gas_totals.get("volume_m3", 0) or 0

    # Вода
    water = resources.get("water", {}).get(quarter, {})
    water_totals = water.get("quarter_totals", {})
    water_m3 = water_totals.get("volume_m3", 0) or 0

    # Топливо
    fuel = resources.get("fuel", {}).get(quarter, {})
    fuel_totals = fuel.get("quarter_totals", {})
    fuel_ton = fuel_totals.get("volume_ton", fuel_totals.get("volume_t", 0)) or 0

    # Уголь
    coal = resources.get("coal", {}).get(quarter, {})
    coal_totals = coal.get("quarter_totals", {})
    coal_ton = coal_totals.get("volume_ton", coal_totals.get("volume_t", 0)) or 0

    # Тепло
    heat = resources.get("heat", {}).get(quarter, {})
    heat_totals = heat.get("quarter_totals", {})
    heat_gcal = heat_totals.get("volume_gcal", 0) or 0

    # Производство
    production = resources.get("production", {}).get(quarter, {})
    prod_totals = production.get("quarter_totals", {})
    production_kg = (
        sum(v for v in prod_totals.values() if isinstance(v, (int, float)) and v > 0)
        if prod_totals
        else 0.0
    )

    # Категории потребления
    by_usage = electricity.get("by_usage")

    return QuarterData(
        quarter=quarter,
        year=year,
        quarter_num=quarter_num,
        electricity_active_kwh=active_kwh,
        electricity_reactive_kvarh=reactive_kvarh,
        gas_m3=gas_m3,
        water_m3=water_m3,
        fuel_ton=fuel_ton,
        coal_ton=coal_ton,
        heat_gcal=heat_gcal,
        production_kg=production_kg,
        by_usage=by_usage,
    )


def extract_equipment_data(equipment_data: Dict[str, Any]) -> EquipmentData:
    """
    Извлекает данные по оборудованию.

    Args:
        equipment_data: Данные оборудования из JSON

    Returns:
        EquipmentData объект
    """
    summary = equipment_data.get("summary", {})

    total_power_kw = summary.get("total_power_kw", 0.0) or 0.0
    total_items = summary.get("total_items", 0) or 0
    vfd_count = summary.get("vfd_with_frequency_drive", 0) or 0

    # Используемая мощность = 80% от установленной (по умолчанию)
    used_power_kw = calculate_equipment_used_power(total_power_kw, usage_factor=0.8)

    return EquipmentData(
        total_installed_power_kw=total_power_kw,
        total_used_power_kw=used_power_kw,
        total_items_count=total_items,
        vfd_count=vfd_count,
    )


# ============================================================================
# Валидация данных перед расчётами
# ============================================================================


def validate_quarter_data(quarter_data: QuarterData) -> Tuple[bool, List[str]]:
    """
    Валидирует данные квартала перед расчётами.

    Returns:
        (is_valid, list_of_warnings)
    """
    warnings = []

    # Проверка на отрицательные значения
    if quarter_data.electricity_active_kwh < 0:
        warnings.append(
            f"Отрицательное потребление электроэнергии: {quarter_data.electricity_active_kwh} кВт·ч"
        )

    if quarter_data.gas_m3 < 0:
        warnings.append(f"Отрицательное потребление газа: {quarter_data.gas_m3} м³")

    if quarter_data.production_kg < 0:
        warnings.append(f"Отрицательное производство: {quarter_data.production_kg} кг")

    # Проверка на нереалистично большие значения
    if quarter_data.electricity_active_kwh > 100000000:  # 100 ГВт·ч
        warnings.append(
            f"Нереалистично большое потребление электроэнергии: {quarter_data.electricity_active_kwh} кВт·ч"
        )

    is_valid = len(warnings) == 0

    return is_valid, warnings


# ============================================================================
# Функции для агрегации данных по всем кварталам (для Word-отчётов)
# ============================================================================


def calculate_total_consumption_by_resource(
    agg_data: Dict[str, Any], resource_type: str
) -> float:
    """
    Рассчитывает общее потребление ресурса за все кварталы.

    Args:
        agg_data: Агрегированные данные
        resource_type: Тип ресурса ("electricity", "gas", "water", etc.)

    Returns:
        Общее потребление за все кварталы
        - Для electricity: кВт·ч
        - Для gas, water: м³
        - Для fuel, coal: т
        - Для heat: Гкал
    """
    resources = agg_data.get("resources", {})
    resource_data = resources.get(resource_type, {})

    total = 0.0

    for quarter_data in resource_data.values():
        if isinstance(quarter_data, dict):
            totals = quarter_data.get("quarter_totals", {})

            if resource_type == "electricity":
                total += totals.get("active_kwh", 0) or 0
            elif resource_type in ("gas", "water"):
                total += totals.get("volume_m3", 0) or 0
            elif resource_type in ("fuel", "coal"):
                total += totals.get("volume_ton", totals.get("volume_t", 0)) or 0
            elif resource_type == "heat":
                total += totals.get("volume_gcal", 0) or 0

    return total


def calculate_total_cost_by_resource(
    agg_data: Dict[str, Any], resource_type: str
) -> float:
    """
    Рассчитывает общие затраты на ресурс за все кварталы.

    Args:
        agg_data: Агрегированные данные
        resource_type: Тип ресурса ("electricity", "gas", "water", etc.)

    Returns:
        Общие затраты, сум
    """
    resources = agg_data.get("resources", {})
    resource_data = resources.get(resource_type, {})

    total_cost = 0.0

    for quarter_data in resource_data.values():
        if isinstance(quarter_data, dict):
            totals = quarter_data.get("quarter_totals", {})
            total_cost += totals.get("cost_sum", 0) or 0

    return total_cost


def calculate_total_costs(agg_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Рассчитывает общие затраты по всем ресурсам.

    Args:
        agg_data: Агрегированные данные

    Returns:
        Словарь с затратами по каждому ресурсу и общими затратами:
        {
            "electricity": float,
            "gas": float,
            "water": float,
            "total": float
        }
    """
    electricity_cost = calculate_total_cost_by_resource(agg_data, "electricity")
    gas_cost = calculate_total_cost_by_resource(agg_data, "gas")
    water_cost = calculate_total_cost_by_resource(agg_data, "water")

    total = electricity_cost + gas_cost + water_cost

    return {
        "electricity": electricity_cost,
        "gas": gas_cost,
        "water": water_cost,
        "total": total,
    }


def calculate_average_payback_period(
    total_capex: float, total_saving_kwh: float, tariff_per_kwh: float = 0.15
) -> float:
    """
    Рассчитывает средний срок окупаемости мероприятий.

    Формула: Срок_окупаемости = CAPEX / (Экономия_кВт·ч * Тариф)

    Args:
        total_capex: Общая стоимость реализации мероприятий, сум
        total_saving_kwh: Общая годовая экономия электроэнергии, кВт·ч/год
        tariff_per_kwh: Тариф за кВт·ч, сум/кВт·ч (по умолчанию 0.15)

    Returns:
        Средний срок окупаемости, лет

    Edge-кейсы:
        - Если экономия = 0, возвращает 0
        - Если CAPEX = 0, возвращает 0
    """
    if total_saving_kwh <= 0 or total_capex <= 0:
        return 0.0

    annual_saving_money = total_saving_kwh * tariff_per_kwh

    if annual_saving_money <= 0:
        return 0.0

    payback_years = total_capex / annual_saving_money

    return max(0.0, payback_years)
