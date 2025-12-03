"""
Модуль конвертации единиц измерения для энергопаспорта
Нормализует единицы измерения (кВт·ч ↔ Гкал ↔ ГДж и т.д.)
"""

from typing import Union
from enum import Enum


class EnergyUnit(Enum):
    """Единицы измерения энергии"""

    KWH = "кВт·ч"  # Килловатт-час (базовая единица для электроэнергии)
    MWH = "МВт·ч"  # Мегаватт-час
    GWH = "ГВт·ч"  # Гигаватт-час

    GCAL = "Гкал"  # Гигакалория (базовая единица для тепловой энергии)
    MCAL = "Мкал"  # Мегакалория
    KCAL = "ккал"  # Килокалория

    GJ = "ГДж"  # Гигаджоуль
    MJ = "МДж"  # Мегаджоуль
    KJ = "кДж"  # Килоджоуль

    # Топливный эквивалент
    TUT = "т.у.т."  # Тонна условного топлива


class VolumeUnit(Enum):
    """Единицы измерения объема"""

    M3 = "м³"  # Кубический метр (базовая единица)
    M3_THOUSAND = "тыс. м³"  # Тысяча кубометров
    LITER = "л"  # Литр


class WeightUnit(Enum):
    """Единицы измерения веса"""

    TON = "тонна"  # Тонна (базовая единица)
    TON_SHORT = "т"  # Тонна (сокращенно)
    KG = "кг"  # Килограмм
    G = "г"  # Грамм


class PowerUnit(Enum):
    """Единицы измерения мощности"""

    KW = "кВт"  # Киловатт (базовая единица)
    MW = "МВт"  # Мегаватт
    GW = "ГВт"  # Гигаватт
    KVA = "кВА"  # Киловольт-ампер (для трансформаторов)


class UnitConverter:
    """
    Класс для конвертации единиц измерения в энергопаспорте
    """

    # Коэффициенты конвертации энергии
    # Базовые соотношения:
    # 1 кВт·ч = 3.6 МДж = 0.859845 ккал = 0.00086 Гкал
    # 1 Гкал = 1.163 МВт·ч = 4.1868 ГДж
    # 1 ГДж = 0.277778 МВт·ч = 0.238846 Гкал

    # Конвертация: кВт·ч ↔ Гкал
    KWH_TO_GCAL = 0.000859845  # 1 кВт·ч = 0.000859845 Гкал
    GCAL_TO_KWH = 1 / KWH_TO_GCAL  # ~1163 кВт·ч

    # Конвертация: кВт·ч ↔ ГДж
    KWH_TO_GJ = 0.0036  # 1 кВт·ч = 0.0036 ГДж
    GJ_TO_KWH = 1 / KWH_TO_GJ  # ~277.778 кВт·ч

    # Конвертация: Гкал ↔ ГДж
    GCAL_TO_GJ = 4.1868  # 1 Гкал = 4.1868 ГДж
    GJ_TO_GCAL = 1 / GCAL_TO_GJ  # ~0.238846 Гкал

    # Конвертация: кВт·ч ↔ МВт·ч
    KWH_TO_MWH = 0.001  # 1 кВт·ч = 0.001 МВт·ч
    MWH_TO_KWH = 1000  # 1 МВт·ч = 1000 кВт·ч

    # Конвертация объема
    M3_TO_THOUSAND_M3 = 0.001  # 1 м³ = 0.001 тыс. м³
    THOUSAND_M3_TO_M3 = 1000  # 1 тыс. м³ = 1000 м³

    # Конвертация веса
    TON_TO_KG = 1000  # 1 тонна = 1000 кг
    KG_TO_TON = 0.001  # 1 кг = 0.001 тонна

    # Конвертация мощности
    KW_TO_MW = 0.001  # 1 кВт = 0.001 МВт
    MW_TO_KW = 1000  # 1 МВт = 1000 кВт

    # Топливный эквивалент (условное топливо)
    # 1 т.у.т. = 7000 ккал/кг = 29.3 ГДж = 8.14 МВт·ч
    TUT_TO_KWH = 8140  # 1 т.у.т. = 8140 кВт·ч
    KWH_TO_TUT = 1 / TUT_TO_KWH  # ~0.0001229 т.у.т.

    @staticmethod
    def convert_energy(
        value: float, from_unit: Union[str, EnergyUnit], to_unit: Union[str, EnergyUnit]
    ) -> float:
        """
        Конвертировать значение энергии из одной единицы в другую

        Args:
            value: Значение для конвертации
            from_unit: Исходная единица измерения
            to_unit: Целевая единица измерения

        Returns:
            Конвертированное значение

        Raises:
            ValueError: Если единицы не поддерживаются
        """
        if isinstance(from_unit, str):
            from_unit = EnergyUnit(from_unit)
        if isinstance(to_unit, str):
            to_unit = EnergyUnit(to_unit)

        if from_unit == to_unit:
            return value

        # Конвертируем в базовую единицу (кВт·ч), затем в целевую
        base_value = UnitConverter._to_base_energy(value, from_unit)
        return UnitConverter._from_base_energy(base_value, to_unit)

    @staticmethod
    def _to_base_energy(value: float, unit: EnergyUnit) -> float:
        """Конвертировать в базовую единицу (кВт·ч)"""
        if unit == EnergyUnit.KWH:
            return value
        elif unit == EnergyUnit.MWH:
            return value * UnitConverter.MWH_TO_KWH
        elif unit == EnergyUnit.GWH:
            return value * UnitConverter.MWH_TO_KWH * 1000
        elif unit == EnergyUnit.GCAL:
            return value * UnitConverter.GCAL_TO_KWH
        elif unit == EnergyUnit.MCAL:
            return value * UnitConverter.GCAL_TO_KWH / 1000
        elif unit == EnergyUnit.KCAL:
            return value * UnitConverter.GCAL_TO_KWH / 1000000
        elif unit == EnergyUnit.GJ:
            return value * UnitConverter.GJ_TO_KWH
        elif unit == EnergyUnit.MJ:
            return value * UnitConverter.GJ_TO_KWH / 1000
        elif unit == EnergyUnit.KJ:
            return value * UnitConverter.GJ_TO_KWH / 1000000
        elif unit == EnergyUnit.TUT:
            return value * UnitConverter.TUT_TO_KWH
        else:
            raise ValueError(f"Неподдерживаемая единица измерения энергии: {unit}")

    @staticmethod
    def _from_base_energy(value: float, unit: EnergyUnit) -> float:
        """Конвертировать из базовой единицы (кВт·ч)"""
        if unit == EnergyUnit.KWH:
            return value
        elif unit == EnergyUnit.MWH:
            return value * UnitConverter.KWH_TO_MWH
        elif unit == EnergyUnit.GWH:
            return value * UnitConverter.KWH_TO_MWH / 1000
        elif unit == EnergyUnit.GCAL:
            return value * UnitConverter.KWH_TO_GCAL
        elif unit == EnergyUnit.MCAL:
            return value * UnitConverter.KWH_TO_GCAL * 1000
        elif unit == EnergyUnit.KCAL:
            return value * UnitConverter.KWH_TO_GCAL * 1000000
        elif unit == EnergyUnit.GJ:
            return value * UnitConverter.KWH_TO_GJ
        elif unit == EnergyUnit.MJ:
            return value * UnitConverter.KWH_TO_GJ * 1000
        elif unit == EnergyUnit.KJ:
            return value * UnitConverter.KWH_TO_GJ * 1000000
        elif unit == EnergyUnit.TUT:
            return value * UnitConverter.KWH_TO_TUT
        else:
            raise ValueError(f"Неподдерживаемая единица измерения энергии: {unit}")

    @staticmethod
    def convert_volume(
        value: float, from_unit: Union[str, VolumeUnit], to_unit: Union[str, VolumeUnit]
    ) -> float:
        """
        Конвертировать значение объема из одной единицы в другую

        Args:
            value: Значение для конвертации
            from_unit: Исходная единица измерения
            to_unit: Целевая единица измерения

        Returns:
            Конвертированное значение
        """
        if isinstance(from_unit, str):
            from_unit = VolumeUnit(from_unit)
        if isinstance(to_unit, str):
            to_unit = VolumeUnit(to_unit)

        if from_unit == to_unit:
            return value

        # Конвертируем в базовую единицу (м³)
        if from_unit == VolumeUnit.M3:
            base_value = value
        elif from_unit == VolumeUnit.M3_THOUSAND:
            base_value = value * UnitConverter.THOUSAND_M3_TO_M3
        elif from_unit == VolumeUnit.LITER:
            base_value = value / 1000  # 1 м³ = 1000 л
        else:
            raise ValueError(f"Неподдерживаемая единица измерения объема: {from_unit}")

        # Конвертируем из базовой единицы
        if to_unit == VolumeUnit.M3:
            return base_value
        elif to_unit == VolumeUnit.M3_THOUSAND:
            return base_value * UnitConverter.M3_TO_THOUSAND_M3
        elif to_unit == VolumeUnit.LITER:
            return base_value * 1000
        else:
            raise ValueError(f"Неподдерживаемая единица измерения объема: {to_unit}")

    @staticmethod
    def convert_weight(
        value: float, from_unit: Union[str, WeightUnit], to_unit: Union[str, WeightUnit]
    ) -> float:
        """
        Конвертировать значение веса из одной единицы в другую

        Args:
            value: Значение для конвертации
            from_unit: Исходная единица измерения
            to_unit: Целевая единица измерения

        Returns:
            Конвертированное значение
        """
        if isinstance(from_unit, str):
            from_unit = WeightUnit(from_unit)
        if isinstance(to_unit, str):
            to_unit = WeightUnit(to_unit)

        if from_unit == to_unit:
            return value

        # Конвертируем в базовую единицу (тонна)
        if from_unit == WeightUnit.TON or from_unit == WeightUnit.TON_SHORT:
            base_value = value
        elif from_unit == WeightUnit.KG:
            base_value = value * UnitConverter.KG_TO_TON
        elif from_unit == WeightUnit.G:
            base_value = value * UnitConverter.KG_TO_TON / 1000
        else:
            raise ValueError(f"Неподдерживаемая единица измерения веса: {from_unit}")

        # Конвертируем из базовой единицы
        if to_unit == WeightUnit.TON or to_unit == WeightUnit.TON_SHORT:
            return base_value
        elif to_unit == WeightUnit.KG:
            return base_value * UnitConverter.TON_TO_KG
        elif to_unit == WeightUnit.G:
            return base_value * UnitConverter.TON_TO_KG * 1000
        else:
            raise ValueError(f"Неподдерживаемая единица измерения веса: {to_unit}")

    @staticmethod
    def convert_power(
        value: float, from_unit: Union[str, PowerUnit], to_unit: Union[str, PowerUnit]
    ) -> float:
        """
        Конвертировать значение мощности из одной единицы в другую

        Args:
            value: Значение для конвертации
            from_unit: Исходная единица измерения
            to_unit: Целевая единица измерения

        Returns:
            Конвертированное значение
        """
        if isinstance(from_unit, str):
            from_unit = PowerUnit(from_unit)
        if isinstance(to_unit, str):
            to_unit = PowerUnit(to_unit)

        if from_unit == to_unit:
            return value

        # Конвертируем в базовую единицу (кВт)
        if from_unit == PowerUnit.KW:
            base_value = value
        elif from_unit == PowerUnit.MW:
            base_value = value * UnitConverter.MW_TO_KW
        elif from_unit == PowerUnit.GW:
            base_value = value * UnitConverter.MW_TO_KW * 1000
        elif from_unit == PowerUnit.KVA:
            # кВА ≈ кВт для активной мощности (коэффициент может варьироваться)
            base_value = value  # Упрощенная конвертация
        else:
            raise ValueError(
                f"Неподдерживаемая единица измерения мощности: {from_unit}"
            )

        # Конвертируем из базовой единицы
        if to_unit == PowerUnit.KW:
            return base_value
        elif to_unit == PowerUnit.MW:
            return base_value * UnitConverter.KW_TO_MW
        elif to_unit == PowerUnit.GW:
            return base_value * UnitConverter.KW_TO_MW / 1000
        elif to_unit == PowerUnit.KVA:
            return base_value  # Упрощенная конвертация
        else:
            raise ValueError(f"Неподдерживаемая единица измерения мощности: {to_unit}")

    @staticmethod
    def normalize_unit(unit: str) -> str:
        """
        Нормализовать строку единицы измерения (убрать вариации)

        Args:
            unit: Единица измерения в виде строки

        Returns:
            Нормализованная единица измерения
        """
        unit_lower = unit.lower().strip()

        # Энергия
        if unit_lower in ["квт·ч", "квтч", "кwh", "kw·h", "kwh"]:
            return "кВт·ч"
        elif unit_lower in ["мвт·ч", "мвтч", "mwh", "mw·h"]:
            return "МВт·ч"
        elif unit_lower in ["гкал", "gcal"]:
            return "Гкал"
        elif unit_lower in ["гдж", "gj"]:
            return "ГДж"
        elif unit_lower in ["т.у.т.", "тут", "tut"]:
            return "т.у.т."

        # Объем
        elif unit_lower in ["м³", "м3", "m3", "m³", "куб.м"]:
            return "м³"
        elif unit_lower in ["тыс. м³", "тыс.м³", "тыс м³", "thousand m3"]:
            return "тыс. м³"

        # Вес
        elif unit_lower in ["тонна", "т", "ton", "tonne"]:
            return "тонна"
        elif unit_lower in ["кг", "kg"]:
            return "кг"

        # Мощность
        elif unit_lower in ["квт", "kw"]:
            return "кВт"
        elif unit_lower in ["мвт", "mw"]:
            return "МВт"
        elif unit_lower in ["ква", "kva"]:
            return "кВА"

        # Если не найдено, возвращаем как есть
        return unit


def convert_energy(value: float, from_unit: str, to_unit: str) -> float:
    """Удобная функция для конвертации энергии"""
    return UnitConverter.convert_energy(value, from_unit, to_unit)


def convert_volume(value: float, from_unit: str, to_unit: str) -> float:
    """Удобная функция для конвертации объема"""
    return UnitConverter.convert_volume(value, from_unit, to_unit)


def convert_weight(value: float, from_unit: str, to_unit: str) -> float:
    """Удобная функция для конвертации веса"""
    return UnitConverter.convert_weight(value, from_unit, to_unit)


def normalize_unit(unit: str) -> str:
    """Удобная функция для нормализации единицы измерения"""
    return UnitConverter.normalize_unit(unit)
