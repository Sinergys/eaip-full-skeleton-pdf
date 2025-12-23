"""Проверка расчётов балансов"""
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
    print("✅ Модуль energy_passport_calculations найден")
    print(f"   - calculate_balance_total: {hasattr(calculate_balance_total, '__call__')}")
    print(f"   - distribute_quarter_by_usage_categories: {hasattr(distribute_quarter_by_usage_categories, '__call__')}")
except ImportError as e:
    print(f"❌ Модуль не найден: {e}")

