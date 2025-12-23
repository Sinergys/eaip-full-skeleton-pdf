"""
Маппинг полей нового шаблона new_energy_passport.xlsx к данным из aggregated JSON.

Структура данных в aggregated JSON:
{
    "resources": {
        "electricity": {
            "2022-Q1": {
                "year": 2022,
                "quarter": 1,
                "months": [...],
                "quarter_totals": {
                    "active_kwh": ...,
                    "reactive_kvarh": ...,
                    "cost_sum": ...
                },
                "by_usage": {
                    "technological": ...,
                    "own_needs": ...,
                    "production": ...,
                    "household": ...
                }
            }
        },
        "gas": {...},
        "water": {...},
        "production": {...}
    }
}
"""

from typing import Dict, Any, Optional


# Маппинг листов нового шаблона
NEW_TEMPLATE_SHEETS = {
    "Sheet1": {
        "name": "Титульный лист",
        "description": "Основная информация, нормативные документы",
        "fill_function": "fill_title_sheet",
        "data_mapping": {
            "enterprise_name": "enterprise.name",
            "year": "period.year",
            "quarter": "period.quarter"
        }
    },
    "Узел учета ": {
        "name": "Узлы учета",
        "description": "Данные по приборам учета электроэнергии",
        "fill_function": "fill_nodes_sheet",
        "data_mapping": {
            "nodes": "nodes.list"
        }
    },
    "Структура пр 2 ": {
        "name": "Структура параметров энергетического баланса",
        "description": "Квартальные данные по видам энергоресурсов",
        "fill_function": "fill_structure_sheet",
        "data_mapping": {
            "year": "period.year",
            "quarter": "period.quarter",
            "electricity_active": "resources.electricity.{quarter}.quarter_totals.active_kwh",
            "electricity_reactive": "resources.electricity.{quarter}.quarter_totals.reactive_kvarh",
            "gas_volume": "resources.gas.{quarter}.quarter_totals.volume_m3",
            "water_volume": "resources.water.{quarter}.quarter_totals.volume_m3"
        }
    },
    "Баланс": {
        "name": "Энергетический баланс",
        "description": "Баланс по категориям потребления",
        "fill_function": "fill_balance_sheet",
        "data_mapping": {
            "electricity_by_usage": "resources.electricity.{quarter}.by_usage",
            "technological": "resources.electricity.{quarter}.by_usage.technological",
            "own_needs": "resources.electricity.{quarter}.by_usage.own_needs",
            "production": "resources.electricity.{quarter}.by_usage.production",
            "household": "resources.electricity.{quarter}.by_usage.household"
        }
    },
    "Динамика ср": {
        "name": "Динамика потребления",
        "description": "Сравнительные показатели динамики расходов",
        "fill_function": "fill_dynamics_sheet",
        "data_mapping": {
            "year": "period.year",
            "electricity": "resources.electricity.{quarter}.quarter_totals.active_kwh",
            "gas": "resources.gas.{quarter}.quarter_totals.volume_m3",
            "water": "resources.water.{quarter}.quarter_totals.volume_m3",
            "heat": "resources.heat.{quarter}.quarter_totals.volume_m3",
            "production": "resources.production.{quarter}.quarter_totals.total_kg"
        }
    },
    "мазут,уголь 5 ": {
        "name": "Мазут и уголь",
        "description": "Динамика изменения удельных показателей",
        "fill_function": "fill_fuel_sheet",
        "data_mapping": {
            "year": "period.year",
            "fuel_data": "resources.fuel.{quarter}.quarter_totals"
        }
    },
    "Расход  на ед.п": {
        "name": "Расход на единицу продукции",
        "description": "Динамика изменения энергетических показателей",
        "fill_function": "fill_specific_consumption_sheet",
        "data_mapping": {
            "year": "period.year",
            "electricity": "resources.electricity.{quarter}.quarter_totals.active_kwh",
            "production": "resources.production.{quarter}.quarter_totals.total_kg",
            "specific_consumption": "calculated: electricity / production"
        }
    },
    "Мериаприятия 1 ": {
        "name": "Мероприятия",
        "description": "Энергосберегающие мероприятия",
        "fill_function": "fill_measures_sheet",
        "data_mapping": {
            "measures": "measures.list"
        }
    }
}


# Маппинг placeholder'ов к путям данных
PLACEHOLDER_MAPPING = {
    # Базовые placeholder'ы
    "year": {
        "source": "period",
        "extract": lambda data, quarter: quarter.split("-")[0] if quarter and "-" in quarter else None
    },
    "quarter": {
        "source": "period",
        "extract": lambda data, quarter: quarter.split("-Q")[1] if quarter and "-Q" in quarter else None
    },
    "enterprise.name": {
        "source": "metadata",
        "extract": lambda data, quarter: data.get("enterprise_name", "ООО Синергис")
    },
    
    # Данные по электроэнергии
    "electricity.active_kwh": {
        "source": "resources.electricity",
        "extract": lambda data, quarter: data.get("resources", {}).get("electricity", {}).get(quarter, {}).get("quarter_totals", {}).get("active_kwh", 0)
    },
    "electricity.reactive_kvarh": {
        "source": "resources.electricity",
        "extract": lambda data, quarter: data.get("resources", {}).get("electricity", {}).get(quarter, {}).get("quarter_totals", {}).get("reactive_kvarh", 0)
    },
    "electricity.cost_sum": {
        "source": "resources.electricity",
        "extract": lambda data, quarter: data.get("resources", {}).get("electricity", {}).get(quarter, {}).get("quarter_totals", {}).get("cost_sum", 0)
    },
    
    # Данные по газу
    "gas.volume_m3": {
        "source": "resources.gas",
        "extract": lambda data, quarter: data.get("resources", {}).get("gas", {}).get(quarter, {}).get("quarter_totals", {}).get("volume_m3", 0)
    },
    "gas.cost_sum": {
        "source": "resources.gas",
        "extract": lambda data, quarter: data.get("resources", {}).get("gas", {}).get(quarter, {}).get("quarter_totals", {}).get("cost_sum", 0)
    },
    
    # Данные по воде
    "water.volume_m3": {
        "source": "resources.water",
        "extract": lambda data, quarter: data.get("resources", {}).get("water", {}).get(quarter, {}).get("quarter_totals", {}).get("volume_m3", 0)
    },
    
    # Данные по производству
    "production.total_kg": {
        "source": "resources.production",
        "extract": lambda data, quarter: data.get("resources", {}).get("production", {}).get(quarter, {}).get("quarter_totals", {}).get("total_kg", 0)
    },
    
    # Данные по категориям потребления
    "electricity.by_usage.technological": {
        "source": "resources.electricity",
        "extract": lambda data, quarter: data.get("resources", {}).get("electricity", {}).get(quarter, {}).get("by_usage", {}).get("technological", 0)
    },
    "electricity.by_usage.own_needs": {
        "source": "resources.electricity",
        "extract": lambda data, quarter: data.get("resources", {}).get("electricity", {}).get(quarter, {}).get("by_usage", {}).get("own_needs", 0)
    },
    "electricity.by_usage.production": {
        "source": "resources.electricity",
        "extract": lambda data, quarter: data.get("resources", {}).get("electricity", {}).get(quarter, {}).get("by_usage", {}).get("production", 0)
    },
    "electricity.by_usage.household": {
        "source": "resources.electricity",
        "extract": lambda data, quarter: data.get("resources", {}).get("electricity", {}).get(quarter, {}).get("by_usage", {}).get("household", 0)
    }
}


def get_quarter_mapping(agg_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Получить маппинг кварталов из aggregated данных.
    
    Returns:
        Dict с ключами типа "2022-Q1" и значениями - нормализованные кварталы
    """
    quarters = set()
    resources = agg_data.get("resources", {})
    
    for resource_type, resource_data in resources.items():
        quarters.update(resource_data.keys())
    
    return {q: q for q in sorted(quarters)}


def extract_data_by_path(agg_data: Dict[str, Any], path: str, quarter: Optional[str] = None) -> Any:
    """
    Извлечь данные по пути из aggregated JSON.
    
    Args:
        agg_data: Агрегированные данные
        path: Путь к данным (например, "resources.electricity.{quarter}.quarter_totals.active_kwh")
        quarter: Квартал для подстановки в {quarter}
    
    Returns:
        Значение или None
    """
    if "{quarter}" in path and quarter:
        path = path.replace("{quarter}", quarter)
    
    parts = path.split(".")
    current = agg_data
    
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
            if current is None:
                return None
        else:
            return None
    
    return current


def get_placeholder_value(agg_data: Dict[str, Any], placeholder: str, quarter: Optional[str] = None) -> Any:
    """
    Получить значение для placeholder'а из aggregated данных.
    
    Args:
        agg_data: Агрегированные данные
        placeholder: Имя placeholder'а
        quarter: Квартал (если нужен)
    
    Returns:
        Значение для замены
    """
    if placeholder in PLACEHOLDER_MAPPING:
        mapping = PLACEHOLDER_MAPPING[placeholder]
        return mapping["extract"](agg_data, quarter)
    
    # Попытка извлечь по пути напрямую
    return extract_data_by_path(agg_data, placeholder, quarter)


# Экспорт для использования в других модулях
__all__ = [
    "NEW_TEMPLATE_SHEETS",
    "PLACEHOLDER_MAPPING",
    "get_quarter_mapping",
    "extract_data_by_path",
    "get_placeholder_value"
]

