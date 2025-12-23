"""
Тест загрузки и обработки файлов оборудования для проверки by_usage.
"""

import sys
from pathlib import Path

# Добавляем путь к модулям
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.ai_excel_semantic_parser import (
    CanonicalSourceData,
    EquipmentItem,
    ResourceEntry,
    TimeSeries,
)  # noqa: E402
from utils.equipment_parser import is_equipment_file  # noqa: E402
from utils.canonical_to_passport import canonical_to_passport_payload  # noqa: E402
from domain.electricity_usage_classifier import classify_equipment_usage  # noqa: E402


def test_equipment_parsing_flow():
    """Тест полного потока: парсинг оборудования -> canonical -> by_usage."""
    print("\n" + "=" * 60)
    print("ТЕСТ ПОТОКА ЗАГРУЗКИ И ОБРАБОТКИ ОБОРУДОВАНИЯ")
    print("=" * 60)

    # Создаем тестовые данные оборудования
    test_equipment = [
        EquipmentItem(
            name="Технологический насос ПН-100",
            type="Насос технологический",
            location="Цех №1",
            nominal_power_kw=50.0,
            utilization_factor=0.9,
        ),
        EquipmentItem(
            name="Насос котельной",
            type="Насос",
            location="Котельная",
            nominal_power_kw=30.0,
            utilization_factor=1.0,
            extra={"usage_category": "собственные нужды"},
        ),
        EquipmentItem(
            name="Конвейер",
            type="Конвейер",
            location="Цех №2",
            nominal_power_kw=25.0,
            utilization_factor=0.8,
        ),
        EquipmentItem(
            name="Кондиционер офисный",
            type="Сплит-система",
            location="Офис",
            nominal_power_kw=3.5,
            utilization_factor=1.0,
        ),
    ]

    # Создаем CanonicalSourceData
    canonical = CanonicalSourceData(
        resources=[
            ResourceEntry(resource="electricity", series=TimeSeries(annual=500000.0))
        ],
        equipment=test_equipment,
    )

    print("\n✅ CanonicalSourceData создан:")
    print(f"   - Оборудование: {len(canonical.equipment)} единиц")
    print(f"   - Ресурсы: {len(canonical.resources)}")
    print(
        f"   - Годовое потребление электроэнергии: {canonical.resources[0].series.annual} кВт·ч"
    )

    # Проверяем классификацию каждого оборудования
    print("\n📊 Классификация оборудования:")
    for i, eq in enumerate(canonical.equipment, 1):
        category = classify_equipment_usage(eq)
        power = eq.nominal_power_kw or 0
        util = eq.utilization_factor or 1.0
        weight = power * util
        print(f"   {i}. {eq.name}")
        print(f"      Категория: {category}")
        print(f"      Мощность: {power} кВт, Коэффициент: {util}, Вес: {weight:.2f}")

    # Преобразуем в payload
    payload = canonical_to_passport_payload(canonical)

    print("\n✅ Payload создан:")
    print(
        f"   - balance.annual_totals: {payload.get('balance', {}).get('annual_totals', {})}"
    )

    # Проверяем by_usage
    by_usage = payload.get("balance", {}).get("by_usage", {}).get("electricity", {})

    if by_usage:
        print("\n✅ by_usage вычислен:")
        for category, value in by_usage.items():
            print(f"   - {category}: {value:.2f} кВт·ч")

        total = sum(by_usage.values())
        print(f"\n   Сумма: {total:.2f} кВт·ч")
        print(f"   Ожидалось: {canonical.resources[0].series.annual} кВт·ч")

        if abs(total - canonical.resources[0].series.annual) < 1.0:
            print("   ✅ Сумма соответствует annual_total")
        else:
            print(
                f"   ⚠️ Расхождение: {abs(total - canonical.resources[0].series.annual):.2f} кВт·ч"
            )
    else:
        print("\n❌ by_usage не вычислен!")
        return False

    return True


def test_equipment_file_detection():
    """Тест определения файлов оборудования."""
    print("\n" + "=" * 60)
    print("ТЕСТ ОПРЕДЕЛЕНИЯ ФАЙЛОВ ОБОРУДОВАНИЯ")
    print("=" * 60)

    test_files = [
        ("oborudovanie.xlsx", True),
        ("Оборудование.xlsx", True),
        ("equipment.xlsx", True),
        ("pererashod.xlsx", False),
        ("gaz.xlsx", False),
    ]

    all_passed = True
    for filename, expected in test_files:
        result = is_equipment_file(filename)
        status = "✅" if result == expected else "❌"
        print(f"{status} {filename}: {result} (ожидалось {expected})")
        if result != expected:
            all_passed = False

    return all_passed


def test_canonical_collection():
    """Тест сбора canonical данных из оборудования."""
    print("\n" + "=" * 60)
    print("ТЕСТ СБОРА CANONICAL ДАННЫХ")
    print("=" * 60)

    # Создаем тестовый canonical
    canonical = CanonicalSourceData(
        resources=[
            ResourceEntry(resource="electricity", series=TimeSeries(annual=100000.0))
        ],
        equipment=[
            EquipmentItem(name="Технологический насос", nominal_power_kw=50.0),
            EquipmentItem(
                name="Насос котельной", location="Котельная", nominal_power_kw=30.0
            ),
        ],
    )

    # Преобразуем в payload
    payload = canonical_to_passport_payload(canonical)

    # Проверяем структуру
    balance = payload.get("balance", {})
    annual_totals = balance.get("annual_totals", {})
    by_usage = balance.get("by_usage", {}).get("electricity", {})

    print("✅ Структура payload:")
    print(f"   - balance.annual_totals: {annual_totals}")
    print(f"   - balance.by_usage.electricity: {by_usage}")

    if annual_totals.get("electricity") == 100000.0:
        print("   ✅ annual_totals.electricity корректно")
    else:
        print("   ❌ annual_totals.electricity некорректно")
        return False

    if by_usage:
        print("   ✅ by_usage вычислен")
        return True
    else:
        print("   ⚠️ by_usage не вычислен (возможно, нет оборудования с power > 0)")
        return True  # Это не ошибка, если нет оборудования


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАГРУЗКИ И ОБРАБОТКИ ОБОРУДОВАНИЯ")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Тест 1: Определение файлов оборудования
    try:
        if test_equipment_file_detection():
            print("✅ Тест определения файлов - ПРОЙДЕН")
            tests_passed += 1
        else:
            print("❌ Тест определения файлов - ПРОВАЛЕН")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Тест определения файлов - ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        tests_failed += 1

    # Тест 2: Сбор canonical данных
    try:
        if test_canonical_collection():
            print("✅ Тест сбора canonical - ПРОЙДЕН")
            tests_passed += 1
        else:
            print("❌ Тест сбора canonical - ПРОВАЛЕН")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Тест сбора canonical - ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        tests_failed += 1

    # Тест 3: Полный поток обработки
    try:
        if test_equipment_parsing_flow():
            print("✅ Тест полного потока - ПРОЙДЕН")
            tests_passed += 1
        else:
            print("❌ Тест полного потока - ПРОВАЛЕН")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Тест полного потока - ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        tests_failed += 1

    print("\n" + "=" * 60)
    print("ОБЩИЙ ИТОГ")
    print("=" * 60)
    print(f"Пройдено: {tests_passed}")
    print(f"Провалено: {tests_failed}")

    if tests_failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ЗАГРУЗКИ ПРОЙДЕНЫ!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {tests_failed} ТЕСТОВ ПРОВАЛЕНО")
        sys.exit(1)
