"""Тест расчётов балансов"""
import sys
from pathlib import Path

# Добавляем пути для импорта
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton" / "services" / "ingest" / "domain"))

try:
    from energy_passport_calculations import (
        calculate_balance_total,
        distribute_quarter_by_usage_categories,
    )
    print("✅ Модуль energy_passport_calculations импортирован")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

# Тест 1: calculate_balance_total
print("\n" + "="*60)
print("ТЕСТ 1: calculate_balance_total")
print("="*60)

test_cases = [
    {
        "name": "Нормальные значения",
        "tech": 1000.0,
        "own": 200.0,
        "prod": 300.0,
        "house": 100.0,
        "expected": 1600.0
    },
    {
        "name": "С нулевыми значениями",
        "tech": 1000.0,
        "own": 0.0,
        "prod": 0.0,
        "house": 0.0,
        "expected": 1000.0
    },
    {
        "name": "С отрицательными значениями (должны нормализоваться)",
        "tech": 1000.0,
        "own": -50.0,
        "prod": 300.0,
        "house": 100.0,
        "expected": 1400.0
    },
    {
        "name": "Все нули",
        "tech": 0.0,
        "own": 0.0,
        "prod": 0.0,
        "house": 0.0,
        "expected": 0.0
    },
]

all_passed = True
for test in test_cases:
    result = calculate_balance_total(
        technological=test["tech"],
        own_needs=test["own"],
        production=test["prod"],
        household=test["house"]
    )
    passed = abs(result - test["expected"]) < 0.01
    status = "✅" if passed else "❌"
    print(f"{status} {test['name']}: {result} (ожидалось {test['expected']})")
    if not passed:
        all_passed = False

# Тест 2: distribute_quarter_by_usage_categories
print("\n" + "="*60)
print("ТЕСТ 2: distribute_quarter_by_usage_categories")
print("="*60)

test_cases_dist = [
    {
        "name": "Пропорциональное распределение",
        "quarter_total": 400.0,
        "yearly_categories": {
            "technological": 1000.0,
            "own_needs": 500.0,
            "production": 300.0,
            "household": 200.0
        },
        "expected_total": 400.0
    },
    {
        "name": "Равномерное распределение (годовой итог = 0)",
        "quarter_total": 400.0,
        "yearly_categories": {
            "technological": 0.0,
            "own_needs": 0.0,
            "production": 0.0,
            "household": 0.0
        },
        "expected_total": 400.0
    },
]

for test in test_cases_dist:
    result = distribute_quarter_by_usage_categories(
        quarter_total_kwh=test["quarter_total"],
        yearly_categories=test["yearly_categories"]
    )
    result_total = sum(result.values())
    passed = abs(result_total - test["expected_total"]) < 0.01
    status = "✅" if passed else "❌"
    print(f"{status} {test['name']}: итог={result_total} (ожидалось {test['expected_total']})")
    print(f"   Распределение: {result}")
    if not passed:
        all_passed = False

# Итог
print("\n" + "="*60)
if all_passed:
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
else:
    print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
print("="*60)

