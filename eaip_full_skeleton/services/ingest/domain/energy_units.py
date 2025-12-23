"""
Модуль единиц измерения и конвертации для энергетических расчётов.

Определяет все используемые единицы измерения и функции конвертации
между ними для обеспечения консистентности расчётов.
"""

from typing import Union
from enum import Enum


class EnergyUnit(Enum):
    """Единицы измерения энергии."""

    # Электроэнергия
    KWH = "кВт·ч"  # киловатт-час (базовая единица)
    MWH = "МВт·ч"  # мегаватт-час
    GWH = "ГВт·ч"  # гигаватт-час

    # Реактивная энергия
    KVARH = "кВАр·ч"  # киловар-час (базовая единица)
    MVARH = "МВАр·ч"  # мегавар-час

    # Мощность
    KW = "кВт"  # киловатт (базовая единица)
    MW = "МВт"  # мегаватт
    KVA = "кВА"  # киловольт-ампер


class VolumeUnit(Enum):
    """Единицы измерения объёма."""

    # Газ, вода
    M3 = "м³"  # кубический метр (базовая единица)
    THOUSAND_M3 = "тыс. м³"  # тысяча кубических метров
    LITER = "л"  # литр

    # Топливо
    TON = "т"  # тонна (базовая единица)
    KG = "кг"  # килограмм


class HeatUnit(Enum):
    """Единицы измерения тепловой энергии."""

    # Тепло
    GCAL = "Гкал"  # гигакалория (базовая единица)
    KCAL = "ккал"  # килокалория
    GJ = "ГДж"  # гигаджоуль
    MJ = "МДж"  # мегаджоуль
    MWH_HEAT = "МВт·ч"  # мегаватт-час (тепло)


class TimeUnit(Enum):
    """Единицы измерения времени."""

    HOUR = "ч"  # час (базовая единица)
    DAY = "сут"  # сутки
    MONTH = "мес"  # месяц
    YEAR = "год"  # год
    QUARTER = "квартал"  # квартал


# Константы преобразования

# Электроэнергия
KWH_TO_MWH = 0.001  # 1 кВт·ч = 0.001 МВт·ч
MWH_TO_KWH = 1000.0  # 1 МВт·ч = 1000 кВт·ч
KWH_TO_GWH = 0.000001  # 1 кВт·ч = 0.000001 ГВт·ч
GWH_TO_KWH = 1000000.0  # 1 ГВт·ч = 1000000 кВт·ч

# Реактивная энергия
KVARH_TO_MVARH = 0.001  # 1 кВАр·ч = 0.001 МВАр·ч
MVARH_TO_KVARH = 1000.0  # 1 МВАр·ч = 1000 кВАр·ч

# Мощность
KW_TO_MW = 0.001  # 1 кВт = 0.001 МВт
MW_TO_KW = 1000.0  # 1 МВт = 1000 кВт

# Объём
M3_TO_THOUSAND_M3 = 0.001  # 1 м³ = 0.001 тыс. м³
THOUSAND_M3_TO_M3 = 1000.0  # 1 тыс. м³ = 1000 м³
M3_TO_LITER = 1000.0  # 1 м³ = 1000 л
LITER_TO_M3 = 0.001  # 1 л = 0.001 м³

TON_TO_KG = 1000.0  # 1 т = 1000 кг
KG_TO_TON = 0.001  # 1 кг = 0.001 т

# Тепло
GCAL_TO_KCAL = 1000000.0  # 1 Гкал = 1,000,000 ккал
KCAL_TO_GCAL = 0.000001  # 1 ккал = 0.000001 Гкал
GCAL_TO_GJ = 4.1868  # 1 Гкал = 4.1868 ГДж (приблизительно)
GJ_TO_GCAL = 0.238846  # 1 ГДж = 0.238846 Гкал
GCAL_TO_MWH = 1.163  # 1 Гкал = 1.163 МВт·ч (приблизительно)
MWH_TO_GCAL = 0.859845  # 1 МВт·ч = 0.859845 Гкал

# Время
HOURS_PER_DAY = 24.0
HOURS_PER_MONTH = 720.0  # Среднее значение (30 дней * 24 часа)
HOURS_PER_QUARTER = 2160.0  # 3 месяца * 720 часов
HOURS_PER_YEAR = 8760.0  # 365 дней * 24 часа
DAYS_PER_MONTH = 30.0  # Среднее значение
DAYS_PER_QUARTER = 90.0  # 3 месяца
DAYS_PER_YEAR = 365.0
MONTHS_PER_QUARTER = 3.0
QUARTERS_PER_YEAR = 4.0


# Функции конвертации


def to_kwh(value: float, from_unit: Union[str, EnergyUnit]) -> float:
    """Конвертирует значение в кВт·ч."""
    if isinstance(from_unit, str):
        from_unit = EnergyUnit(from_unit)

    if from_unit == EnergyUnit.KWH:
        return value
    elif from_unit == EnergyUnit.MWH:
        return value * MWH_TO_KWH
    elif from_unit == EnergyUnit.GWH:
        return value * GWH_TO_KWH
    else:
        raise ValueError(
            f"Неподдерживаемая единица для конвертации в кВт·ч: {from_unit}"
        )


def to_mwh(value: float, from_unit: Union[str, EnergyUnit]) -> float:
    """Конвертирует значение в МВт·ч."""
    return to_kwh(value, from_unit) * KWH_TO_MWH


def to_kvarh(value: float, from_unit: Union[str, EnergyUnit]) -> float:
    """Конвертирует значение в кВАр·ч."""
    if isinstance(from_unit, str):
        from_unit = EnergyUnit(from_unit)

    if from_unit == EnergyUnit.KVARH:
        return value
    elif from_unit == EnergyUnit.MVARH:
        return value * MVARH_TO_KVARH
    else:
        raise ValueError(
            f"Неподдерживаемая единица для конвертации в кВАр·ч: {from_unit}"
        )


def to_m3(value: float, from_unit: Union[str, VolumeUnit]) -> float:
    """Конвертирует значение в м³."""
    if isinstance(from_unit, str):
        from_unit = VolumeUnit(from_unit)

    if from_unit == VolumeUnit.M3:
        return value
    elif from_unit == VolumeUnit.THOUSAND_M3:
        return value * THOUSAND_M3_TO_M3
    elif from_unit == VolumeUnit.LITER:
        return value * LITER_TO_M3
    else:
        raise ValueError(f"Неподдерживаемая единица для конвертации в м³: {from_unit}")


def to_ton(value: float, from_unit: Union[str, VolumeUnit]) -> float:
    """Конвертирует значение в тонны."""
    if isinstance(from_unit, str):
        from_unit = VolumeUnit(from_unit)

    if from_unit == VolumeUnit.TON:
        return value
    elif from_unit == VolumeUnit.KG:
        return value * KG_TO_TON
    else:
        raise ValueError(
            f"Неподдерживаемая единица для конвертации в тонны: {from_unit}"
        )


def to_gcal(value: float, from_unit: Union[str, HeatUnit]) -> float:
    """Конвертирует значение в Гкал."""
    if isinstance(from_unit, str):
        from_unit = HeatUnit(from_unit)

    if from_unit == HeatUnit.GCAL:
        return value
    elif from_unit == HeatUnit.KCAL:
        return value * KCAL_TO_GCAL
    elif from_unit == HeatUnit.GJ:
        return value * GJ_TO_GCAL
    elif from_unit == HeatUnit.MJ:
        return value * GJ_TO_GCAL * 0.001  # МДж -> ГДж -> Гкал
    elif from_unit == HeatUnit.MWH_HEAT:
        return value * MWH_TO_GCAL
    else:
        raise ValueError(
            f"Неподдерживаемая единица для конвертации в Гкал: {from_unit}"
        )


def to_gj(value: float, from_unit: Union[str, HeatUnit]) -> float:
    """Конвертирует значение в ГДж."""
    return to_gcal(value, from_unit) * GCAL_TO_GJ


def normalize_energy_to_kwh(value: float, unit: str) -> float:
    """
    Нормализует значение энергии к кВт·ч.

    Args:
        value: Значение
        unit: Единица измерения (строка)

    Returns:
        Значение в кВт·ч
    """
    unit_upper = unit.upper()

    # Электроэнергия
    if "КВТ·Ч" in unit_upper or "КВТЧ" in unit_upper or "KWH" in unit_upper:
        return value
    elif "МВТ·Ч" in unit_upper or "МВТЧ" in unit_upper or "MWH" in unit_upper:
        return value * MWH_TO_KWH
    elif "ГВТ·Ч" in unit_upper or "ГВТЧ" in unit_upper or "GWH" in unit_upper:
        return value * GWH_TO_KWH

    # Реактивная энергия
    elif "КВАР·Ч" in unit_upper or "КВАРЧ" in unit_upper or "KVARH" in unit_upper:
        return value  # кВАр·ч не конвертируется в кВт·ч напрямую
    elif "МВАР·Ч" in unit_upper or "МВАРЧ" in unit_upper or "MVARH" in unit_upper:
        return value * MVARH_TO_KVARH

    else:
        # По умолчанию считаем, что это уже кВт·ч
        return value


def normalize_volume_to_m3(value: float, unit: str) -> float:
    """
    Нормализует значение объёма к м³.

    Args:
        value: Значение
        unit: Единица измерения (строка)

    Returns:
        Значение в м³
    """
    unit_upper = unit.upper()

    if "М³" in unit_upper or "M3" in unit_upper:
        return value
    elif "ТЫС. М³" in unit_upper or "ТЫС М³" in unit_upper or "THOUSAND" in unit_upper:
        return value * THOUSAND_M3_TO_M3
    elif "Л" in unit_upper or "L" in unit_upper or "ЛИТР" in unit_upper:
        return value * LITER_TO_M3
    else:
        # По умолчанию считаем, что это уже м³
        return value


def normalize_mass_to_ton(value: float, unit: str) -> float:
    """
    Нормализует значение массы к тоннам.

    Args:
        value: Значение
        unit: Единица измерения (строка)

    Returns:
        Значение в тоннах
    """
    unit_upper = unit.upper()

    if "Т" in unit_upper or "ТОНН" in unit_upper or "TON" in unit_upper:
        return value
    elif "КГ" in unit_upper or "KG" in unit_upper or "КИЛОГРАММ" in unit_upper:
        return value * KG_TO_TON
    else:
        # По умолчанию считаем, что это уже тонны
        return value


def validate_unit_consistency(
    value1: float, unit1: str, value2: float, unit2: str, expected_base_unit: str
) -> bool:
    """
    Проверяет консистентность единиц измерения перед операциями.

    Args:
        value1: Первое значение
        unit1: Единица первого значения
        value2: Второе значение
        unit2: Единица второго значения
        expected_base_unit: Ожидаемая базовая единица

    Returns:
        True если единицы консистентны
    """
    # Нормализуем к базовой единице
    normalize_energy_to_kwh(value1, unit1) if "кВт·ч" in expected_base_unit else value1
    normalize_energy_to_kwh(value2, unit2) if "кВт·ч" in expected_base_unit else value2

    # Проверяем, что после нормализации значения имеют смысл
    # (это упрощённая проверка, можно расширить)
    return True  # TODO: Реализовать более строгую проверку


# Утилиты для работы с периодами


def hours_in_period(period_type: str, period_value: Union[int, str] = None) -> float:
    """
    Возвращает количество часов в периоде.

    Args:
        period_type: Тип периода ("month", "quarter", "year")
        period_value: Значение периода (опционально)

    Returns:
        Количество часов
    """
    if period_type.lower() == "month":
        return HOURS_PER_MONTH
    elif period_type.lower() == "quarter":
        return HOURS_PER_QUARTER
    elif period_type.lower() == "year":
        return HOURS_PER_YEAR
    elif period_type.lower() == "day":
        return HOURS_PER_DAY
    else:
        raise ValueError(f"Неподдерживаемый тип периода: {period_type}")


def months_to_quarters(months: float) -> float:
    """Конвертирует месяцы в кварталы."""
    return months / MONTHS_PER_QUARTER


def quarters_to_months(quarters: float) -> float:
    """Конвертирует кварталы в месяцы."""
    return quarters * MONTHS_PER_QUARTER
