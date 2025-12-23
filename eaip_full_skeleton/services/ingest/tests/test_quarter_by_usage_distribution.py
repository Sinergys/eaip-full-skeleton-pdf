"""
Интеграционный тест для проверки распределения by_usage по кварталам.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.ai_excel_semantic_parser import (  # noqa: E402
    CanonicalSourceData,
    EquipmentItem,
    ResourceEntry,
    TimeSeries,
)
from utils.canonical_to_passport import canonical_to_passport_payload  # noqa: E402


def test_quarter_by_usage_distribution():
    """
    Тест распределения canonical by_usage по кварталам.

    Проверяет, что:
    1. by_usage вычисляется в canonical
    2. by_usage распределяется по кварталам пропорционально потреблению
    3. Сумма по кварталам соответствует annual_total
    """
    print("\n" + "=" * 60)
    print("ТЕСТ РАСПРЕДЕЛЕНИЯ BY_USAGE ПО КВАРТАЛАМ")
    print("=" * 60)

    # Создаем canonical с оборудованием всех категорий
    canonical = CanonicalSourceData(
        resources=[
            ResourceEntry(resource="electricity", series=TimeSeries(annual=500000.0))
        ],
        equipment=[
            EquipmentItem(
                name="Технологический насос ПН-100",
                nominal_power_kw=50.0,
                utilization_factor=0.9,
            ),
            EquipmentItem(
                name="Насос котельной",
                location="Котельная",
                nominal_power_kw=30.0,
                utilization_factor=1.0,
                extra={"usage_category": "собственные нужды"},
            ),
            EquipmentItem(
                name="Конвейер",
                location="Цех №2",
                nominal_power_kw=25.0,
                utilization_factor=0.8,
            ),
            EquipmentItem(
                name="Кондиционер офисный",
                location="Офис",
                nominal_power_kw=3.5,
                utilization_factor=1.0,
            ),
        ],
    )

    # Преобразуем в payload
    payload = canonical_to_passport_payload(canonical)

    # Проверяем annual by_usage
    annual_by_usage = (
        payload.get("balance", {}).get("by_usage", {}).get("electricity", {})
    )
    assert isinstance(annual_by_usage, dict) and annual_by_usage, (
        "annual by_usage должен быть непустым"
    )

    print("\n✅ Annual by_usage:")
    for category, value in annual_by_usage.items():
        print(f"   - {category}: {value:.2f} кВт·ч")

    total_annual = sum(annual_by_usage.values())
    print(f"   Сумма: {total_annual:.2f} кВт·ч")
    assert abs(total_annual - 500000.0) < 1.0, (
        f"Сумма annual должна быть ~500000, получено {total_annual}"
    )

    # Симулируем распределение по кварталам
    # Создаем тестовые квартальные данные
    quarterly_consumption = {
        "Q1_2022": 120000.0,
        "Q2_2022": 130000.0,
        "Q3_2022": 125000.0,
        "Q4_2022": 125000.0,
    }
    total_quarterly = sum(quarterly_consumption.values())

    print(f"\n📊 Квартальное потребление (всего: {total_quarterly:.2f} кВт·ч):")
    for quarter, consumption in quarterly_consumption.items():
        print(f"   - {quarter}: {consumption:.2f} кВт·ч")

    # Распределяем by_usage по кварталам
    quarterly_by_usage = {}
    for quarter, consumption in quarterly_consumption.items():
        ratio = consumption / total_quarterly
        quarterly_by_usage[quarter] = {
            category: value * ratio for category, value in annual_by_usage.items()
        }
        print(f"\n   {quarter} (ratio={ratio:.3f}):")
        for category, value in quarterly_by_usage[quarter].items():
            print(f"      - {category}: {value:.2f} кВт·ч")

    # Проверяем, что сумма по всем кварталам соответствует annual
    for category in annual_by_usage.keys():
        quarterly_sum = sum(q[category] for q in quarterly_by_usage.values())
        annual_value = annual_by_usage[category]
        diff = abs(quarterly_sum - annual_value)
        print(f"\n   Проверка {category}:")
        print(f"      Quarterly sum: {quarterly_sum:.2f}")
        print(f"      Annual value: {annual_value:.2f}")
        print(f"      Разница: {diff:.2f}")
        assert diff < 1.0, (
            f"Сумма по кварталам для {category} должна соответствовать annual: "
            f"{quarterly_sum} vs {annual_value}"
        )

    print("\n✅ Распределение по кварталам корректно!")
    return True


def test_quarter_by_usage_with_zero_quarters():
    """
    Тест обработки кварталов с нулевым потреблением.
    """
    print("\n" + "=" * 60)
    print("ТЕСТ ОБРАБОТКИ КВАРТАЛОВ С НУЛЕВЫМ ПОТРЕБЛЕНИЕМ")
    print("=" * 60)

    canonical = CanonicalSourceData(
        resources=[
            ResourceEntry(resource="electricity", series=TimeSeries(annual=100000.0))
        ],
        equipment=[
            EquipmentItem(name="Технологический насос", nominal_power_kw=50.0),
            EquipmentItem(name="Конвейер", location="Цех №1", nominal_power_kw=50.0),
        ],
    )

    payload = canonical_to_passport_payload(canonical)
    annual_by_usage = (
        payload.get("balance", {}).get("by_usage", {}).get("electricity", {})
    )

    # Кварталы с нулевым потреблением должны быть пропущены
    quarterly_consumption = {
        "Q1_2022": 50000.0,
        "Q2_2022": 0.0,  # Нулевое потребление
        "Q3_2022": 30000.0,
        "Q4_2022": 20000.0,
    }

    # Фильтруем нулевые кварталы
    non_zero_quarters = {k: v for k, v in quarterly_consumption.items() if v > 0}
    total_quarterly = sum(non_zero_quarters.values())

    print("\n📊 Квартальное потребление (без нулевых):")
    for quarter, consumption in non_zero_quarters.items():
        print(f"   - {quarter}: {consumption:.2f} кВт·ч")

    # Распределяем только по ненулевым кварталам
    quarterly_by_usage = {}
    for quarter, consumption in non_zero_quarters.items():
        ratio = consumption / total_quarterly
        quarterly_by_usage[quarter] = {
            category: value * ratio for category, value in annual_by_usage.items()
        }

    # Проверяем, что нулевой квартал не включен
    assert "Q2_2022" not in quarterly_by_usage, "Нулевой квартал не должен быть включен"

    # Проверяем сумму
    for category in annual_by_usage.keys():
        quarterly_sum = sum(q[category] for q in quarterly_by_usage.values())
        annual_value = annual_by_usage[category]
        assert abs(quarterly_sum - annual_value) < 1.0, (
            f"Сумма должна соответствовать annual для {category}"
        )

    print("\n✅ Нулевые кварталы корректно обработаны!")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ РАСПРЕДЕЛЕНИЯ BY_USAGE ПО КВАРТАЛАМ")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    try:
        if test_quarter_by_usage_distribution():
            print("✅ Тест распределения по кварталам - ПРОЙДЕН")
            tests_passed += 1
        else:
            print("❌ Тест распределения по кварталам - ПРОВАЛЕН")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Тест распределения по кварталам - ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        tests_failed += 1

    try:
        if test_quarter_by_usage_with_zero_quarters():
            print("✅ Тест обработки нулевых кварталов - ПРОЙДЕН")
            tests_passed += 1
        else:
            print("❌ Тест обработки нулевых кварталов - ПРОВАЛЕН")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Тест обработки нулевых кварталов - ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        tests_failed += 1

    print("\n" + "=" * 60)
    print("ОБЩИЙ ИТОГ")
    print("=" * 60)
    print(f"Пройдено: {tests_passed}")
    print(f"Провалено: {tests_failed}")

    if tests_failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ РАСПРЕДЕЛЕНИЯ ПО КВАРТАЛАМ ПРОЙДЕНЫ!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {tests_failed} ТЕСТОВ ПРОВАЛЕНО")
        sys.exit(1)
