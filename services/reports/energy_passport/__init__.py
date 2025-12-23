"""Модуль для генерации энергопаспорта."""

from .generator import generate_energy_passport
from .data_collector import (
    collect_energy_passport_data,
    EnergyPassportData,
    ElectricityProductData,
    GasConsumptionData,
)

__all__ = [
    "generate_energy_passport",
    "collect_energy_passport_data",
    "EnergyPassportData",
    "ElectricityProductData",
    "GasConsumptionData",
]
