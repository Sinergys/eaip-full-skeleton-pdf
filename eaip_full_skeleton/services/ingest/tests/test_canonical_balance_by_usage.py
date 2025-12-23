import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eaip_full_skeleton.services.ingest.ai.ai_excel_semantic_parser import (  # type: ignore
    CanonicalSourceData,
    EquipmentItem,
    ResourceEntry,
    TimeSeries,
)
from eaip_full_skeleton.services.ingest.utils.canonical_to_passport import (
    canonical_to_passport_payload,
)  # type: ignore


def build_canonical_for_split():
    # annual electricity=100000
    resources = [
        ResourceEntry(resource="electricity", series=TimeSeries(annual=100000.0))
    ]
    # two equipment items with equal weights into different categories via extra.usage_category
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
    return CanonicalSourceData(resources=resources, equipment=equipment)


def build_canonical_with_all_categories():
    """Создает CanonicalSourceData с оборудованием всех 4 категорий."""
    resources = [
        ResourceEntry(resource="electricity", series=TimeSeries(annual=100000.0))
    ]
    equipment = [
        # Технологическое - по ключевому слову в названии
        EquipmentItem(
            name="Технологический насос", nominal_power_kw=30.0, utilization_factor=1.0
        ),
        # Собственные нужды - по location
        EquipmentItem(
            name="Насос",
            location="Котельная",
            nominal_power_kw=20.0,
            utilization_factor=1.0,
        ),
        # Производственное - по умолчанию/цех
        EquipmentItem(
            name="Конвейер",
            location="Цех №1",
            nominal_power_kw=25.0,
            utilization_factor=1.0,
        ),
        # Хоз-бытовое - по location
        EquipmentItem(
            name="Кондиционер",
            location="Офис",
            nominal_power_kw=15.0,
            utilization_factor=1.0,
        ),
    ]
    return CanonicalSourceData(resources=resources, equipment=equipment)


def test_electricity_by_usage_proportional_split():
    canonical = build_canonical_for_split()
    payload = canonical_to_passport_payload(canonical)
    annual = payload.get("balance", {}).get("annual_totals", {}).get("electricity")
    assert annual == 100000.0
    byu = payload.get("balance", {}).get("by_usage", {}).get("electricity", {})
    assert isinstance(byu, dict) and byu
    tech = byu.get("technological")
    prod = byu.get("production")
    assert tech is not None and prod is not None
    # allow small FP tolerance
    assert abs((tech + prod) - 100000.0) < 1.0
    assert abs(tech - 50000.0) < 1000.0
    assert abs(prod - 50000.0) < 1000.0


def test_electricity_by_usage_empty_without_equipment():
    canonical = CanonicalSourceData(
        resources=[
            ResourceEntry(resource="electricity", series=TimeSeries(annual=100000.0))
        ]
    )
    payload = canonical_to_passport_payload(canonical)
    byu = payload.get("balance", {}).get("by_usage", {}).get("electricity", {})
    # no equipment => by_usage may be missing/empty
    assert byu == {} or byu is None


def test_electricity_by_usage_all_categories():
    """Тест распределения по всем 4 категориям использования."""
    canonical = build_canonical_with_all_categories()
    payload = canonical_to_passport_payload(canonical)

    annual = payload.get("balance", {}).get("annual_totals", {}).get("electricity")
    assert annual == 100000.0, f"Ожидалось annual=100000.0, получено {annual}"

    byu = payload.get("balance", {}).get("by_usage", {}).get("electricity", {})
    assert isinstance(byu, dict) and byu, "by_usage должен быть непустым словарем"

    # Проверяем наличие всех категорий
    technological = byu.get("technological", 0)
    own_needs = byu.get("own_needs", 0)
    production = byu.get("production", 0)
    household = byu.get("household", 0)

    # Все категории должны иметь ненулевые значения
    assert technological > 0, "technological должен быть > 0"
    assert own_needs > 0, "own_needs должен быть > 0"
    assert production > 0, "production должен быть > 0"
    assert household > 0, "household должен быть > 0"

    # Сумма должна быть близка к annual_total (с учетом округления)
    total = technological + own_needs + production + household
    assert abs(total - 100000.0) < 1.0, (
        f"Сумма категорий ({total}) должна быть близка к annual_total (100000.0)"
    )

    # Проверяем пропорциональность весов
    # Ожидаемые веса: tech=30, own=20, prod=25, house=15, total=90
    # Ожидаемые доли: tech=30/90, own=20/90, prod=25/90, house=15/90
    expected_tech = 100000.0 * (30.0 / 90.0)
    expected_own = 100000.0 * (20.0 / 90.0)
    expected_prod = 100000.0 * (25.0 / 90.0)
    expected_house = 100000.0 * (15.0 / 90.0)

    # Допуск 1000 кВт·ч для округления
    assert abs(technological - expected_tech) < 1000.0, (
        f"technological: ожидалось ~{expected_tech}, получено {technological}"
    )
    assert abs(own_needs - expected_own) < 1000.0, (
        f"own_needs: ожидалось ~{expected_own}, получено {own_needs}"
    )
    assert abs(production - expected_prod) < 1000.0, (
        f"production: ожидалось ~{expected_prod}, получено {production}"
    )
    assert abs(household - expected_house) < 1000.0, (
        f"household: ожидалось ~{expected_house}, получено {household}"
    )


def test_electricity_by_usage_with_utilization_factor():
    """Тест распределения с учетом коэффициента использования."""
    resources = [
        ResourceEntry(resource="electricity", series=TimeSeries(annual=100000.0))
    ]
    equipment = [
        EquipmentItem(
            name="Технологический насос", nominal_power_kw=50.0, utilization_factor=0.8
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

    # Веса: tech=50*0.8=40, prod=50*1.0=50, total=90
    # tech должен получить 40/90 * 100000, prod - 50/90 * 100000
    tech = byu.get("technological", 0)
    prod = byu.get("production", 0)

    expected_tech = 100000.0 * (40.0 / 90.0)
    expected_prod = 100000.0 * (50.0 / 90.0)

    assert abs(tech - expected_tech) < 1000.0
    assert abs(prod - expected_prod) < 1000.0
    assert abs((tech + prod) - 100000.0) < 1.0
