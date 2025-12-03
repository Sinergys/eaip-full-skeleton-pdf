"""
Тесты для классификатора использования электроэнергии.
"""

from __future__ import annotations


from ai.ai_excel_semantic_parser import EquipmentItem, NodeItem
from domain.electricity_usage_classifier import classify_equipment_usage
from domain.passport_field_map import (
    ELECTRICITY_USAGE_TECH,
    ELECTRICITY_USAGE_OWN,
    ELECTRICITY_USAGE_PROD,
    ELECTRICITY_USAGE_HOUSEHOLD,
)


class TestElectricityUsageClassifier:
    """Тесты для классификатора использования электроэнергии."""

    def test_technological_equipment_by_name(self):
        """Тест 1: Технологическое оборудование по названию."""
        item = EquipmentItem(
            name="Технологический насос ПН-100",
            nominal_power_kw=50.0,
            utilization_factor=1.0,
        )
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_TECH, (
            f"Ожидалось {ELECTRICITY_USAGE_TECH}, получено {result}"
        )

    def test_household_equipment_by_location(self):
        """Тест 2: Хоз-бытовое оборудование по месту установки."""
        item = EquipmentItem(
            name="Кондиционер",
            location="Административный корпус",
            nominal_power_kw=10.0,
        )
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_HOUSEHOLD, (
            f"Ожидалось {ELECTRICITY_USAGE_HOUSEHOLD}, получено {result}"
        )

    def test_production_equipment_default(self):
        """Тест 3: Производственное оборудование (по умолчанию)."""
        item = EquipmentItem(name="Насос цеха №1", nominal_power_kw=30.0)
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_PROD, (
            f"Ожидалось {ELECTRICITY_USAGE_PROD}, получено {result}"
        )

    def test_own_needs_by_explicit_category(self):
        """Тест 4: Собственные нужды по явной категории в extra."""
        item = EquipmentItem(
            name="Насос",
            location="Котельная",
            nominal_power_kw=25.0,
            extra={"usage_category": "собственные нужды"},
        )
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_OWN, (
            f"Ожидалось {ELECTRICITY_USAGE_OWN}, получено {result}"
        )

    def test_technological_by_type(self):
        """Тест 5: Технологическое по типу оборудования."""
        item = EquipmentItem(
            name="Агрегат", type="Технологический агрегат", nominal_power_kw=100.0
        )
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_TECH, (
            f"Ожидалось {ELECTRICITY_USAGE_TECH}, получено {result}"
        )

    def test_own_needs_by_location(self):
        """Тест 6: Собственные нужды по месту установки (подстанция)."""
        item = EquipmentItem(
            name="Трансформатор", location="ТП-1", nominal_power_kw=200.0
        )
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_OWN, (
            f"Ожидалось {ELECTRICITY_USAGE_OWN}, получено {result}"
        )

    def test_household_by_name_keywords(self):
        """Тест 7: Хоз-бытовое по ключевым словам в названии."""
        item = EquipmentItem(name="Освещение офисное", nominal_power_kw=5.0)
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_HOUSEHOLD, (
            f"Ожидалось {ELECTRICITY_USAGE_HOUSEHOLD}, получено {result}"
        )

    def test_production_by_workshop_keyword(self):
        """Тест 8: Производственное по ключевому слову 'цех'."""
        item = EquipmentItem(name="Конвейер", location="Цех №2", nominal_power_kw=15.0)
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_PROD, (
            f"Ожидалось {ELECTRICITY_USAGE_PROD}, получено {result}"
        )

    def test_classification_with_nodes(self):
        """Тест 9: Классификация с использованием узлов учета."""
        item = EquipmentItem(name="Насос", location="Котельная", nominal_power_kw=30.0)
        nodes = [
            NodeItem(node_id="Узел-1", location="Котельная", resource="electricity")
        ]
        result = classify_equipment_usage(item, nodes)
        assert result == ELECTRICITY_USAGE_OWN, (
            f"Ожидалось {ELECTRICITY_USAGE_OWN}, получено {result}"
        )

    def test_default_when_no_match(self):
        """Тест 10: Значение по умолчанию при отсутствии совпадений."""
        item = EquipmentItem(name="Оборудование", nominal_power_kw=20.0)
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_PROD, (
            f"Ожидалось {ELECTRICITY_USAGE_PROD} (по умолчанию), получено {result}"
        )

    def test_priority_technological_over_production(self):
        """Тест 11: Приоритет технологического над производственным."""
        item = EquipmentItem(
            name="Технологический насос цеха №1",
            location="Цех №1",
            nominal_power_kw=50.0,
        )
        result = classify_equipment_usage(item)
        # "технологический" имеет более высокий приоритет, чем "цех"
        assert result == ELECTRICITY_USAGE_TECH, (
            f"Ожидалось {ELECTRICITY_USAGE_TECH} (приоритет), получено {result}"
        )

    def test_household_office_keyword(self):
        """Тест 12: Хоз-бытовое по ключевому слову 'офис'."""
        item = EquipmentItem(name="Кондиционер", location="Офис", nominal_power_kw=3.5)
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_HOUSEHOLD, (
            f"Ожидалось {ELECTRICITY_USAGE_HOUSEHOLD}, получено {result}"
        )
