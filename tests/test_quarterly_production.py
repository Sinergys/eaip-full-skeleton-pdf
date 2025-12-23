"""
Тесты для модуля квартальной агрегации производства.
"""
import pytest
from services.reports.energy_passport.quarterly_production import (
    aggregate_quarters_by_product,
    normalize_product_name,
    MONTH_TO_QUARTER,
    PRODUCT_COLUMNS,
)


def test_normalize_product_name():
    """Тест нормализации названий продуктов"""
    assert normalize_product_name("Труба ХВС") == "Труба ХВС"
    assert normalize_product_name("труба хвс") == "Труба ХВС"
    assert normalize_product_name("Канализационные трубы") == "Канал труба"
    assert normalize_product_name("тёплый пол") == "Топ. пол"
    assert normalize_product_name("теплый пол") == "Топ. пол"


def test_aggregate_quarters_by_product():
    """Тест агрегации по кварталам"""
    monthly_production = {
        2022: {
            "Январь": {
                "Труба ХВС": 260800,
                "Канал труба": 2420,
                "Канал фитинг": 4409,
                "Фит ХВС и ГВС": 17815,
                "Топ. пол": 30698,
            },
            "Февраль": {
                "Труба ХВС": 209667.5,
                "Канал труба": 4928,
                "Канал фитинг": 11845,
                "Фит ХВС и ГВС": 15449,
                "Топ. пол": 48098,
            },
            "Март": {
                "Труба ХВС": 224469,
                "Канал труба": 3899,
                "Канал фитинг": 7388.5,
                "Фит ХВС и ГВС": 103846.28,
                "Топ. пол": 70998,
            },
        }
    }
    
    result = aggregate_quarters_by_product(monthly_production, 2022)
    
    # Проверяем, что есть квартал 1
    assert 1 in result
    
    q1 = result[1]
    
    # Проверяем суммы по продуктам
    assert abs(q1["Труба ХВС"] - (260800 + 209667.5 + 224469)) < 0.01
    assert abs(q1["Канал труба"] - (2420 + 4928 + 3899)) < 0.01
    
    # Проверяем ИТОГО
    assert "ИТОГО" in q1
    expected_total = sum(
        q1[prod] for prod in PRODUCT_COLUMNS if prod in q1
    )
    assert abs(q1["ИТОГО"] - expected_total) < 0.01


def test_month_to_quarter_mapping():
    """Тест маппинга месяцев к кварталам"""
    assert MONTH_TO_QUARTER["Январь"] == 1
    assert MONTH_TO_QUARTER["Март"] == 1
    assert MONTH_TO_QUARTER["Апрель"] == 2
    assert MONTH_TO_QUARTER["Июнь"] == 2
    assert MONTH_TO_QUARTER["Июль"] == 3
    assert MONTH_TO_QUARTER["Сентябрь"] == 3
    assert MONTH_TO_QUARTER["Октябрь"] == 4
    assert MONTH_TO_QUARTER["Декабрь"] == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

