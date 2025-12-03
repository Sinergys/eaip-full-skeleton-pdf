"""
Ручной запуск тестов без pytest.
"""

import sys
from pathlib import Path

# Добавляем путь к модулям
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.ai_excel_semantic_parser import (
    EquipmentItem,
    NodeItem,
    CanonicalSourceData,
    ResourceEntry,
    TimeSeries,
)
from domain.electricity_usage_classifier import classify_equipment_usage
from domain.passport_field_map import (
    ELECTRICITY_USAGE_TECH,
    ELECTRICITY_USAGE_OWN,
    ELECTRICITY_USAGE_PROD,
    ELECTRICITY_USAGE_HOUSEHOLD,
)
from utils.canonical_to_passport import canonical_to_passport_payload


def test_classifier():
    """Тесты классификатора."""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ КЛАССИФИКАТОРА ИСПОЛЬЗОВАНИЯ ЭЛЕКТРОЭНЕРГИИ")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Тест 1: Технологическое оборудование по названию
    try:
        item = EquipmentItem(
            name="Технологический насос ПН-100",
            nominal_power_kw=50.0,
            utilization_factor=1.0,
        )
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_TECH, (
            f"Ожидалось {ELECTRICITY_USAGE_TECH}, получено {result}"
        )
        print("✅ Тест 1: Технологическое оборудование по названию - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 1: Технологическое оборудование по названию - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 2: Хоз-бытовое оборудование по месту установки
    try:
        item = EquipmentItem(
            name="Кондиционер",
            location="Административный корпус",
            nominal_power_kw=10.0,
        )
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_HOUSEHOLD, (
            f"Ожидалось {ELECTRICITY_USAGE_HOUSEHOLD}, получено {result}"
        )
        print("✅ Тест 2: Хоз-бытовое оборудование по location - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 2: Хоз-бытовое оборудование по location - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 3: Производственное оборудование (по умолчанию)
    try:
        item = EquipmentItem(name="Насос цеха №1", nominal_power_kw=30.0)
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_PROD, (
            f"Ожидалось {ELECTRICITY_USAGE_PROD}, получено {result}"
        )
        print("✅ Тест 3: Производственное оборудование (по умолчанию) - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 3: Производственное оборудование - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 4: Собственные нужды по явной категории в extra
    try:
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
        print("✅ Тест 4: Собственные нужды по explicit category - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 4: Собственные нужды по explicit category - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 5: Технологическое по типу оборудования
    try:
        item = EquipmentItem(
            name="Агрегат", type="Технологический агрегат", nominal_power_kw=100.0
        )
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_TECH, (
            f"Ожидалось {ELECTRICITY_USAGE_TECH}, получено {result}"
        )
        print("✅ Тест 5: Технологическое по типу - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 5: Технологическое по типу - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 6: Собственные нужды по location (подстанция)
    try:
        item = EquipmentItem(
            name="Трансформатор", location="ТП-1", nominal_power_kw=200.0
        )
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_OWN, (
            f"Ожидалось {ELECTRICITY_USAGE_OWN}, получено {result}"
        )
        print("✅ Тест 6: Собственные нужды по location (ТП) - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 6: Собственные нужды по location - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 7: Хоз-бытовое по ключевым словам в названии
    try:
        item = EquipmentItem(name="Освещение офисное", nominal_power_kw=5.0)
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_HOUSEHOLD, (
            f"Ожидалось {ELECTRICITY_USAGE_HOUSEHOLD}, получено {result}"
        )
        print("✅ Тест 7: Хоз-бытовое по ключевым словам - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 7: Хоз-бытовое по ключевым словам - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 8: Производственное по ключевому слову 'цех'
    try:
        item = EquipmentItem(name="Конвейер", location="Цех №2", nominal_power_kw=15.0)
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_PROD, (
            f"Ожидалось {ELECTRICITY_USAGE_PROD}, получено {result}"
        )
        print("✅ Тест 8: Производственное по 'цех' - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 8: Производственное по 'цех' - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 9: Классификация с использованием узлов учета
    try:
        item = EquipmentItem(name="Насос", location="Котельная", nominal_power_kw=30.0)
        nodes = [
            NodeItem(node_id="Узел-1", location="Котельная", resource="electricity")
        ]
        result = classify_equipment_usage(item, nodes)
        assert result == ELECTRICITY_USAGE_OWN, (
            f"Ожидалось {ELECTRICITY_USAGE_OWN}, получено {result}"
        )
        print("✅ Тест 9: Классификация с узлами учета - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 9: Классификация с узлами - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 10: Значение по умолчанию
    try:
        item = EquipmentItem(name="Оборудование", nominal_power_kw=20.0)
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_PROD, (
            f"Ожидалось {ELECTRICITY_USAGE_PROD} (по умолчанию), получено {result}"
        )
        print("✅ Тест 10: Значение по умолчанию - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 10: Значение по умолчанию - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 11: Приоритет технологического над производственным
    try:
        item = EquipmentItem(
            name="Технологический насос цеха №1",
            location="Цех №1",
            nominal_power_kw=50.0,
        )
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_TECH, (
            f"Ожидалось {ELECTRICITY_USAGE_TECH} (приоритет), получено {result}"
        )
        print("✅ Тест 11: Приоритет технологического - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 11: Приоритет технологического - ПРОВАЛЕН: {e}")
        tests_failed += 1

    # Тест 12: Хоз-бытовое по ключевому слову 'офис'
    try:
        item = EquipmentItem(name="Кондиционер", location="Офис", nominal_power_kw=3.5)
        result = classify_equipment_usage(item)
        assert result == ELECTRICITY_USAGE_HOUSEHOLD, (
            f"Ожидалось {ELECTRICITY_USAGE_HOUSEHOLD}, получено {result}"
        )
        print("✅ Тест 12: Хоз-бытовое по 'офис' - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 12: Хоз-бытовое по 'офис' - ПРОВАЛЕН: {e}")
        tests_failed += 1

    print("\n" + "=" * 60)
    print(f"ИТОГО: {tests_passed} пройдено, {tests_failed} провалено")
    print("=" * 60)

    return tests_passed, tests_failed


def test_canonical_balance_by_usage():
    """Тесты для canonical balance by_usage."""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ CANONICAL BALANCE BY_USAGE")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Тест 1: Пропорциональное распределение
    try:
        resources = [
            ResourceEntry(resource="electricity", series=TimeSeries(annual=100000.0))
        ]
        equipment = [
            EquipmentItem(
                name="Tech Pump",
                nominal_power_kw=50.0,
                extra={"usage_category": "technological"},
            ),
            EquipmentItem(
                name="Prod Fan",
                nominal_power_kw=50.0,
                extra={"usage_category": "production"},
            ),
        ]
        canonical = CanonicalSourceData(resources=resources, equipment=equipment)
        payload = canonical_to_passport_payload(canonical)

        annual = payload.get("balance", {}).get("annual_totals", {}).get("electricity")
        assert annual == 100000.0, f"Ожидалось annual=100000.0, получено {annual}"

        byu = payload.get("balance", {}).get("by_usage", {}).get("electricity", {})
        assert isinstance(byu, dict) and byu, "by_usage должен быть непустым словарем"

        tech = byu.get("technological")
        prod = byu.get("production")
        assert tech is not None and prod is not None, (
            "Обе категории должны присутствовать"
        )

        # Допуск для округления
        assert abs((tech + prod) - 100000.0) < 1.0, (
            f"Сумма должна быть близка к 100000.0, получено {tech + prod}"
        )
        assert abs(tech - 50000.0) < 1000.0, (
            f"technological должен быть ~50000, получено {tech}"
        )
        assert abs(prod - 50000.0) < 1000.0, (
            f"production должен быть ~50000, получено {prod}"
        )

        print("✅ Тест 1: Пропорциональное распределение - ПРОЙДЕН")
        print(
            f"   technological: {tech:.2f}, production: {prod:.2f}, сумма: {tech + prod:.2f}"
        )
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 1: Пропорциональное распределение - ПРОВАЛЕН: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"❌ Тест 1: Пропорциональное распределение - ОШИБКА: {e}")
        tests_failed += 1

    # Тест 2: Пустой by_usage без оборудования
    try:
        canonical = CanonicalSourceData(
            resources=[
                ResourceEntry(
                    resource="electricity", series=TimeSeries(annual=100000.0)
                )
            ]
        )
        payload = canonical_to_passport_payload(canonical)
        byu = payload.get("balance", {}).get("by_usage", {}).get("electricity", {})
        assert byu == {} or byu is None, "by_usage должен быть пустым без оборудования"
        print("✅ Тест 2: Пустой by_usage без оборудования - ПРОЙДЕН")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 2: Пустой by_usage без оборудования - ПРОВАЛЕН: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"❌ Тест 2: Пустой by_usage без оборудования - ОШИБКА: {e}")
        tests_failed += 1

    # Тест 3: Все 4 категории
    try:
        resources = [
            ResourceEntry(resource="electricity", series=TimeSeries(annual=100000.0))
        ]
        equipment = [
            EquipmentItem(
                name="Технологический насос",
                nominal_power_kw=30.0,
                utilization_factor=1.0,
            ),
            EquipmentItem(
                name="Насос",
                location="Котельная",
                nominal_power_kw=20.0,
                utilization_factor=1.0,
            ),
            EquipmentItem(
                name="Конвейер",
                location="Цех №1",
                nominal_power_kw=25.0,
                utilization_factor=1.0,
            ),
            EquipmentItem(
                name="Кондиционер",
                location="Офис",
                nominal_power_kw=15.0,
                utilization_factor=1.0,
            ),
        ]
        canonical = CanonicalSourceData(resources=resources, equipment=equipment)
        payload = canonical_to_passport_payload(canonical)

        annual = payload.get("balance", {}).get("annual_totals", {}).get("electricity")
        assert annual == 100000.0, f"Ожидалось annual=100000.0, получено {annual}"

        byu = payload.get("balance", {}).get("by_usage", {}).get("electricity", {})
        assert isinstance(byu, dict) and byu, "by_usage должен быть непустым словарем"

        technological = byu.get("technological", 0)
        own_needs = byu.get("own_needs", 0)
        production = byu.get("production", 0)
        household = byu.get("household", 0)

        assert technological > 0, "technological должен быть > 0"
        assert own_needs > 0, "own_needs должен быть > 0"
        assert production > 0, "production должен быть > 0"
        assert household > 0, "household должен быть > 0"

        total = technological + own_needs + production + household
        assert abs(total - 100000.0) < 1.0, (
            f"Сумма категорий ({total}) должна быть близка к annual_total (100000.0)"
        )

        print("✅ Тест 3: Все 4 категории - ПРОЙДЕН")
        print(
            f"   technological: {technological:.2f}, own_needs: {own_needs:.2f}, production: {production:.2f}, household: {household:.2f}"
        )
        print(f"   Сумма: {total:.2f}")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 3: Все 4 категории - ПРОВАЛЕН: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"❌ Тест 3: Все 4 категории - ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        tests_failed += 1

    # Тест 4: С коэффициентом использования
    try:
        resources = [
            ResourceEntry(resource="electricity", series=TimeSeries(annual=100000.0))
        ]
        equipment = [
            EquipmentItem(
                name="Технологический насос",
                nominal_power_kw=50.0,
                utilization_factor=0.8,
            ),
            EquipmentItem(
                name="Конвейер",
                location="Цех №1",
                nominal_power_kw=50.0,
                utilization_factor=1.0,
            ),
        ]
        canonical = CanonicalSourceData(resources=resources, equipment=equipment)
        payload = canonical_to_passport_payload(canonical)

        byu = payload.get("balance", {}).get("by_usage", {}).get("electricity", {})
        assert isinstance(byu, dict) and byu

        tech = byu.get("technological", 0)
        prod = byu.get("production", 0)

        # Веса: tech=50*0.8=40, prod=50*1.0=50, total=90
        expected_tech = 100000.0 * (40.0 / 90.0)
        expected_prod = 100000.0 * (50.0 / 90.0)

        assert abs(tech - expected_tech) < 1000.0, (
            f"technological: ожидалось ~{expected_tech}, получено {tech}"
        )
        assert abs(prod - expected_prod) < 1000.0, (
            f"production: ожидалось ~{expected_prod}, получено {prod}"
        )
        assert abs((tech + prod) - 100000.0) < 1.0, (
            f"Сумма должна быть близка к 100000.0, получено {tech + prod}"
        )

        print("✅ Тест 4: С коэффициентом использования - ПРОЙДЕН")
        print(f"   technological: {tech:.2f} (ожидалось ~{expected_tech:.2f})")
        print(f"   production: {prod:.2f} (ожидалось ~{expected_prod:.2f})")
        tests_passed += 1
    except AssertionError as e:
        print(f"❌ Тест 4: С коэффициентом использования - ПРОВАЛЕН: {e}")
        tests_failed += 1
    except Exception as e:
        print(f"❌ Тест 4: С коэффициентом использования - ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        tests_failed += 1

    print("\n" + "=" * 60)
    print(f"ИТОГО: {tests_passed} пройдено, {tests_failed} провалено")
    print("=" * 60)

    return tests_passed, tests_failed


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ЗАПУСК ТЕСТОВ ДЛЯ КЛАССИФИКАЦИИ ИСПОЛЬЗОВАНИЯ ЭЛЕКТРОЭНЕРГИИ")
    print("=" * 60)

    classifier_passed, classifier_failed = test_classifier()
    balance_passed, balance_failed = test_canonical_balance_by_usage()

    total_passed = classifier_passed + balance_passed
    total_failed = classifier_failed + balance_failed

    print("\n" + "=" * 60)
    print("ОБЩИЙ ИТОГ")
    print("=" * 60)
    print(f"Всего тестов: {total_passed + total_failed}")
    print(f"Пройдено: {total_passed}")
    print(f"Провалено: {total_failed}")

    if total_failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total_failed} ТЕСТОВ ПРОВАЛЕНО")
        sys.exit(1)
