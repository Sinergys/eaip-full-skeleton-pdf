"""
Mock-данные для энергетических паспортов
"""
from typing import Dict, Any


def get_mock_energy_passport_data() -> Dict[str, Any]:
    """
    Возвращает mock-данные энергетического паспорта
    
    Returns:
        Словарь с полными данными энергетического паспорта
    """
    return {
        "enterprise": {
            "id": 1,
            "name": "ООО 'Тестовое предприятие'",
            "inn": "1234567890",
            "kpp": "987654321",
            "address": "г. Москва, ул. Тестовая, д. 1",
            "director_name": "Иванов Иван Иванович",
            "industry": "Производство",
            "reporting_year": 2024,
            "reporting_period": "год"
        },
        "resources": {
            "electricity": {
                "Q1": {
                    "consumption": 1000.0,
                    "cost": 50000.0,
                    "unit": "кВт*ч"
                },
                "Q2": {
                    "consumption": 1200.0,
                    "cost": 60000.0,
                    "unit": "кВт*ч"
                },
                "Q3": {
                    "consumption": 1100.0,
                    "cost": 55000.0,
                    "unit": "кВт*ч"
                },
                "Q4": {
                    "consumption": 1300.0,
                    "cost": 65000.0,
                    "unit": "кВт*ч"
                },
                "total": {
                    "consumption": 4600.0,
                    "cost": 230000.0,
                    "unit": "кВт*ч"
                }
            },
            "gas": {
                "Q1": {
                    "consumption": 500.0,
                    "cost": 25000.0,
                    "unit": "м³"
                },
                "Q2": {
                    "consumption": 600.0,
                    "cost": 30000.0,
                    "unit": "м³"
                },
                "Q3": {
                    "consumption": 550.0,
                    "cost": 27500.0,
                    "unit": "м³"
                },
                "Q4": {
                    "consumption": 650.0,
                    "cost": 32500.0,
                    "unit": "м³"
                },
                "total": {
                    "consumption": 2300.0,
                    "cost": 115000.0,
                    "unit": "м³"
                }
            },
            "heat": {
                "Q1": {
                    "consumption": 200.0,
                    "cost": 10000.0,
                    "unit": "Гкал"
                },
                "Q2": {
                    "consumption": 150.0,
                    "cost": 7500.0,
                    "unit": "Гкал"
                },
                "Q3": {
                    "consumption": 100.0,
                    "cost": 5000.0,
                    "unit": "Гкал"
                },
                "Q4": {
                    "consumption": 250.0,
                    "cost": 12500.0,
                    "unit": "Гкал"
                },
                "total": {
                    "consumption": 700.0,
                    "cost": 35000.0,
                    "unit": "Гкал"
                }
            },
            "water": {
                "Q1": {
                    "consumption": 100.0,
                    "cost": 5000.0,
                    "unit": "м³"
                },
                "Q2": {
                    "consumption": 120.0,
                    "cost": 6000.0,
                    "unit": "м³"
                },
                "Q3": {
                    "consumption": 110.0,
                    "cost": 5500.0,
                    "unit": "м³"
                },
                "Q4": {
                    "consumption": 130.0,
                    "cost": 6500.0,
                    "unit": "м³"
                },
                "total": {
                    "consumption": 460.0,
                    "cost": 23000.0,
                    "unit": "м³"
                }
            }
        },
        "equipment": [
            {
                "name": "Насос центробежный",
                "type": "Насосное оборудование",
                "power_kw": 10.5,
                "quantity": 2,
                "hours_per_year": 8760,
                "annual_consumption_kwh": 183960.0
            },
            {
                "name": "Вентилятор",
                "type": "Вентиляционное оборудование",
                "power_kw": 5.0,
                "quantity": 4,
                "hours_per_year": 4380,
                "annual_consumption_kwh": 87600.0
            },
            {
                "name": "Освещение",
                "type": "Электроосвещение",
                "power_kw": 2.0,
                "quantity": 50,
                "hours_per_year": 4000,
                "annual_consumption_kwh": 400000.0
            }
        ],
        "envelope": {
            "total_area_m2": 1000.0,
            "total_heat_loss": 50000.0,
            "sections": [
                {
                    "name": "Стены",
                    "area_m2": 400.0,
                    "heat_loss": 20000.0,
                    "material": "Кирпич"
                },
                {
                    "name": "Кровля",
                    "area_m2": 300.0,
                    "heat_loss": 15000.0,
                    "material": "Металлочерепица"
                },
                {
                    "name": "Окна",
                    "area_m2": 200.0,
                    "heat_loss": 10000.0,
                    "material": "Двойной стеклопакет"
                },
                {
                    "name": "Пол",
                    "area_m2": 100.0,
                    "heat_loss": 5000.0,
                    "material": "Бетон"
                }
            ]
        },
        "nodes": [
            {
                "name": "Узел учета электроэнергии №1",
                "type": "Электроэнергия",
                "location": "Главный корпус",
                "meter_type": "Счетчик электроэнергии",
                "serial_number": "SN123456"
            },
            {
                "name": "Узел учета газа №1",
                "type": "Газ",
                "location": "Котельная",
                "meter_type": "Счетчик газа",
                "serial_number": "SN789012"
            }
        ],
        "metadata": {
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-12-31T23:59:59Z",
            "version": "1.0",
            "template": "PKM690"
        }
    }


def get_mock_energy_passport_data_minimal() -> Dict[str, Any]:
    """
    Возвращает минимальные mock-данные энергетического паспорта
    
    Returns:
        Словарь с минимальными данными
    """
    return {
        "enterprise": {
            "id": 1,
            "name": "Тестовое предприятие",
            "reporting_year": 2024
        },
        "resources": {
            "electricity": {
                "Q1": {"consumption": 1000.0, "cost": 5000.0}
            }
        }
    }


def get_mock_energy_passport_data_with_anomalies() -> Dict[str, Any]:
    """
    Возвращает mock-данные с аномалиями для тестирования детектора
    
    Returns:
        Словарь с данными, содержащими аномалии
    """
    data = get_mock_energy_passport_data()
    # Добавляем аномалии
    data["resources"]["electricity"]["Q2"]["consumption"] = 50000.0  # Аномально высокое
    data["resources"]["gas"]["Q3"]["consumption"] = -100.0  # Отрицательное значение
    return data


def get_mock_parsed_pdf_data() -> Dict[str, Any]:
    """
    Возвращает mock-данные распарсенного PDF
    
    Returns:
        Словарь с данными распарсенного PDF
    """
    return {
        "parsed": True,
        "file_type": "pdf",
        "data": {
            "text": "Энергетический паспорт\nООО 'Тестовое предприятие'\nЭлектроэнергия: 1000 кВт*ч",
            "metadata": {
                "num_pages": 5,
                "title": "Энергетический паспорт"
            },
            "tables": [
                {
                    "page": 1,
                    "rows": [
                        ["Месяц", "Потребление", "Стоимость"],
                        ["Январь", "100", "5000"],
                        ["Февраль", "120", "6000"]
                    ]
                }
            ],
            "total_characters": 500,
            "total_tables": 1
        }
    }

