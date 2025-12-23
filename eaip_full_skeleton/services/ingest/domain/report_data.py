"""
Единый доменный объект для данных энергоаудита.

Собирает все ключевые КПИ и агрегаты, вычисленные через централизованные функции,
для использования в Excel-паспорте и Word-отчёте.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from .energy_passport_calculations import (
        calculate_total_consumption_by_resource,
        calculate_total_costs,
        calculate_average_payback_period,
        extract_equipment_data,
        EquipmentData,
        QuarterData,
    )

    HAS_CALCULATIONS = True
except ImportError:
    HAS_CALCULATIONS = False
    EquipmentData = None
    QuarterData = None

logger = logging.getLogger(__name__)


@dataclass
class ResourceTotals:
    """Итоговые показатели по ресурсу."""

    total_consumption: float = 0.0  # Общее потребление (кВт·ч, м³, т, Гкал)
    total_cost: float = 0.0  # Общие затраты, сум
    quarters_count: int = 0  # Количество кварталов с данными


@dataclass
class EquipmentSummary:
    """Сводка по оборудованию."""

    total_installed_power_kw: float = 0.0
    total_used_power_kw: float = 0.0
    total_items_count: int = 0
    vfd_count: int = 0


@dataclass
class MeasuresSummary:
    """Сводка по мероприятиям."""

    total_count: int = 0
    total_capex: float = 0.0  # Общая стоимость, сум
    total_saving_kwh: float = 0.0  # Общая экономия, кВт·ч/год
    total_saving_money: float = 0.0  # Общая экономия, сум/год
    average_payback_years: float = 0.0  # Средний срок окупаемости, лет
    items: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ReportData:
    """
    Единый доменный объект для данных энергоаудита.

    Собирает все ключевые КПИ и агрегаты, вычисленные через централизованные функции.
    Используется как в fill_energy_passport.py, так и в word_report_generator.py.
    """

    # Исходные данные (сырые)
    aggregated_data: Dict[str, Any] = field(default_factory=dict)
    equipment_data: Optional[Dict[str, Any]] = None
    nodes_data: Optional[List[Dict[str, Any]]] = None
    envelope_data: Optional[Dict[str, Any]] = None
    measures_data: Optional[List[Dict[str, Any]]] = None
    enterprise_data: Optional[Dict[str, Any]] = None

    # Вычисленные КПИ по ресурсам
    electricity: ResourceTotals = field(default_factory=ResourceTotals)
    gas: ResourceTotals = field(default_factory=ResourceTotals)
    water: ResourceTotals = field(default_factory=ResourceTotals)
    fuel: ResourceTotals = field(default_factory=ResourceTotals)
    coal: ResourceTotals = field(default_factory=ResourceTotals)
    heat: ResourceTotals = field(default_factory=ResourceTotals)

    # Сводка по оборудованию
    equipment: EquipmentSummary = field(default_factory=EquipmentSummary)

    # Сводка по мероприятиям
    measures: MeasuresSummary = field(default_factory=MeasuresSummary)

    # Общие показатели
    total_energy_cost: float = 0.0  # Общие затраты на все ресурсы, сум

    # Метаданные
    generated_at: datetime = field(default_factory=datetime.now)
    source_files: List[str] = field(default_factory=list)

    @classmethod
    def from_raw_data(
        cls,
        aggregated_data: Dict[str, Any],
        equipment_data: Optional[Dict[str, Any]] = None,
        nodes_data: Optional[List[Dict[str, Any]]] = None,
        envelope_data: Optional[Dict[str, Any]] = None,
        measures_data: Optional[List[Dict[str, Any]]] = None,
        enterprise_data: Optional[Dict[str, Any]] = None,
    ) -> "ReportData":
        """
        Создает ReportData из сырых данных, вычисляя все КПИ.

        Args:
            aggregated_data: Агрегированные данные энергопотребления
            equipment_data: Данные оборудования (опционально)
            nodes_data: Данные узлов учета (опционально)
            envelope_data: Данные расчета теплопотерь по зданиям (опционально)
            measures_data: Данные мероприятий (опционально)
            enterprise_data: Данные предприятия (опционально)

        Returns:
            ReportData с вычисленными КПИ
        """
        instance = cls(
            aggregated_data=aggregated_data,
            equipment_data=equipment_data,
            nodes_data=nodes_data,
            envelope_data=envelope_data,
            measures_data=measures_data,
            enterprise_data=enterprise_data,
        )

        # Вычисляем КПИ по ресурсам
        instance._calculate_resource_totals()

        # Вычисляем сводку по оборудованию
        if equipment_data:
            instance._calculate_equipment_summary()

        # Вычисляем сводку по мероприятиям
        if measures_data:
            instance._calculate_measures_summary()

        # Вычисляем общие затраты
        instance._calculate_total_costs()

        return instance

    def _calculate_resource_totals(self) -> None:
        """Вычисляет итоговые показатели по всем ресурсам."""
        if not HAS_CALCULATIONS:
            logger.warning("Модуль расчётов недоступен. КПИ не будут вычислены.")
            return

        resource_types = ["electricity", "gas", "water", "fuel", "coal", "heat"]

        for resource_type in resource_types:
            try:
                # Общее потребление
                total_consumption = calculate_total_consumption_by_resource(
                    self.aggregated_data, resource_type
                )

                # Общие затраты
                total_cost = (
                    calculate_total_cost_by_resource(
                        self.aggregated_data, resource_type
                    )
                    if HAS_CALCULATIONS
                    else 0.0
                )

                # Количество кварталов
                resources = self.aggregated_data.get("resources", {})
                resource_data = resources.get(resource_type, {})
                quarters_count = len(resource_data)

                # Сохраняем в соответствующий атрибут
                totals = ResourceTotals(
                    total_consumption=total_consumption,
                    total_cost=total_cost,
                    quarters_count=quarters_count,
                )

                setattr(self, resource_type, totals)

            except Exception as e:
                logger.warning(
                    f"Ошибка вычисления КПИ для ресурса {resource_type}: {e}"
                )
                # Устанавливаем значения по умолчанию
                setattr(self, resource_type, ResourceTotals())

    def _calculate_equipment_summary(self) -> None:
        """Вычисляет сводку по оборудованию."""
        if not self.equipment_data:
            return

        if HAS_CALCULATIONS:
            try:
                eq_data = extract_equipment_data(self.equipment_data)
                self.equipment = EquipmentSummary(
                    total_installed_power_kw=eq_data.total_installed_power_kw,
                    total_used_power_kw=eq_data.total_used_power_kw,
                    total_items_count=eq_data.total_items_count,
                    vfd_count=eq_data.vfd_count,
                )
            except Exception as e:
                logger.warning(f"Ошибка извлечения данных оборудования: {e}")
                # Fallback на прямое извлечение из summary
                summary = self.equipment_data.get("summary", {})
                self.equipment = EquipmentSummary(
                    total_installed_power_kw=summary.get("total_power_kw", 0.0) or 0.0,
                    total_used_power_kw=summary.get("total_power_kw", 0.0)
                    or 0.0 * 0.8,  # Приблизительно
                    total_items_count=summary.get("total_items", 0) or 0,
                    vfd_count=summary.get("vfd_with_frequency_drive", 0) or 0,
                )
        else:
            # Fallback без централизованных функций
            summary = self.equipment_data.get("summary", {})
            self.equipment = EquipmentSummary(
                total_installed_power_kw=summary.get("total_power_kw", 0.0) or 0.0,
                total_used_power_kw=summary.get("total_power_kw", 0.0) or 0.0 * 0.8,
                total_items_count=summary.get("total_items", 0) or 0,
                vfd_count=summary.get("vfd_with_frequency_drive", 0) or 0,
            )

    def _calculate_measures_summary(self) -> None:
        """Вычисляет сводку по мероприятиям."""
        if not self.measures_data:
            return

        total_capex = 0.0
        total_saving_kwh = 0.0
        total_saving_money = 0.0

        for measure in self.measures_data:
            capex = (
                measure.get("capex")
                or measure.get("cost_usd")
                or measure.get("cost")
                or 0.0
            )
            saving_kwh = measure.get("saving_kwh") or 0.0
            saving_money = measure.get("saving_money") or 0.0

            total_capex += capex
            total_saving_kwh += saving_kwh
            total_saving_money += saving_money

        # Вычисляем средний срок окупаемости
        if HAS_CALCULATIONS:
            avg_payback = calculate_average_payback_period(
                total_capex=total_capex,
                total_saving_kwh=total_saving_kwh,
                tariff_per_kwh=0.15,  # Можно сделать конфигурируемым
            )
        else:
            # Fallback
            avg_payback = (
                total_capex / (total_saving_kwh * 0.15) if total_saving_kwh > 0 else 0.0
            )

        self.measures = MeasuresSummary(
            total_count=len(self.measures_data),
            total_capex=total_capex,
            total_saving_kwh=total_saving_kwh,
            total_saving_money=total_saving_money,
            average_payback_years=avg_payback,
            items=self.measures_data.copy() if self.measures_data else [],
        )

    def _calculate_total_costs(self) -> None:
        """Вычисляет общие затраты на все ресурсы."""
        if HAS_CALCULATIONS:
            try:
                costs = calculate_total_costs(self.aggregated_data)
                self.total_energy_cost = costs.get("total", 0.0)
            except Exception as e:
                logger.warning(f"Ошибка вычисления общих затрат: {e}")
                # Fallback: суммируем вручную
                self.total_energy_cost = (
                    self.electricity.total_cost
                    + self.gas.total_cost
                    + self.water.total_cost
                )
        else:
            # Fallback: суммируем вручную
            self.total_energy_cost = (
                self.electricity.total_cost
                + self.gas.total_cost
                + self.water.total_cost
            )

    def get_resource_total(self, resource_type: str) -> ResourceTotals:
        """Получает итоговые показатели по ресурсу."""
        return getattr(self, resource_type, ResourceTotals())

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует ReportData в словарь для сериализации."""
        return {
            "enterprise": self.enterprise_data,
            "resources": {
                "electricity": {
                    "total_consumption": self.electricity.total_consumption,
                    "total_cost": self.electricity.total_cost,
                    "quarters_count": self.electricity.quarters_count,
                },
                "gas": {
                    "total_consumption": self.gas.total_consumption,
                    "total_cost": self.gas.total_cost,
                    "quarters_count": self.gas.quarters_count,
                },
                "water": {
                    "total_consumption": self.water.total_consumption,
                    "total_cost": self.water.total_cost,
                    "quarters_count": self.water.quarters_count,
                },
            },
            "equipment": {
                "total_installed_power_kw": self.equipment.total_installed_power_kw,
                "total_used_power_kw": self.equipment.total_used_power_kw,
                "total_items_count": self.equipment.total_items_count,
                "vfd_count": self.equipment.vfd_count,
            },
            "measures": {
                "total_count": self.measures.total_count,
                "total_capex": self.measures.total_capex,
                "total_saving_kwh": self.measures.total_saving_kwh,
                "total_saving_money": self.measures.total_saving_money,
                "average_payback_years": self.measures.average_payback_years,
            },
            "total_energy_cost": self.total_energy_cost,
            "generated_at": self.generated_at.isoformat(),
        }


# Вспомогательная функция для импорта calculate_total_cost_by_resource
if HAS_CALCULATIONS:
    try:
        from .energy_passport_calculations import calculate_total_cost_by_resource
    except ImportError:

        def calculate_total_cost_by_resource(
            agg_data: Dict[str, Any], resource_type: str
        ) -> float:
            """Fallback функция для расчета затрат."""
            resources = agg_data.get("resources", {})
            resource_data = resources.get(resource_type, {})
            total_cost = 0.0
            for quarter_data in resource_data.values():
                if isinstance(quarter_data, dict):
                    totals = quarter_data.get("quarter_totals", {})
                    total_cost += totals.get("cost_sum", 0) or 0
            return total_cost
else:

    def calculate_total_cost_by_resource(
        agg_data: Dict[str, Any], resource_type: str
    ) -> float:
        """Fallback функция для расчета затрат."""
        resources = agg_data.get("resources", {})
        resource_data = resources.get(resource_type, {})
        total_cost = 0.0
        for quarter_data in resource_data.values():
            if isinstance(quarter_data, dict):
                totals = quarter_data.get("quarter_totals", {})
                total_cost += totals.get("cost_sum", 0) or 0
        return total_cost
