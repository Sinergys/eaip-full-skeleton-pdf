"""
Матрица обязательных данных для генерации энергетического паспорта.

Определяет требования к загружаемым файлам, минимальный набор данных
и критерии готовности для генерации паспорта.
"""

from typing import Dict, List, Any

# Матрица требований к данным
REQUIRED_DATA_MATRIX: Dict[str, Dict[str, Any]] = {
    "energy_resources": {
        "electricity": {
            "required": True,
            "file_patterns": [
                "pererashod.xlsx",
                "electricity.xlsx",
                "electro act react.xlsx",
                "electro",
                "потребление энергоресурсов.xlsx",
                "consumption",
                "energy_resources",
                "edenic",
                "единиц",
                "kvt",
            ],
            "keywords": [
                "электр",
                "electricity",
                "потребление",
                "consumption",
                "edenic",
                "единиц",
                "единицы",
                "единиц на",
                "единицы на",
                "kvt",
                "квт",
                "kw",
                "реализация",  # Акты балансов с данными по реализации электроэнергии
                "баланс",  # Акты балансов
                "акт баланс",  # Акты балансов
                "акт баланса",  # Акты балансов
                "коммерческий учёт",  # Коммерческий учёт электроэнергии
                "коммерческий учет",  # Коммерческий учёт электроэнергии
                "электроэнергия",
                "энергопотребление",
                "энергоресурсы",
                "эл",
                "электро",
                "энергия",
                "активная",
                "реактивная",
                "перерасход",
                "pererashod",
            ],
            "min_quarters": 4,  # Минимум 4 квартала данных
            "fields": ["consumption", "cost", "consumption_kwh", "cost_sum"],
            "description": "Электроэнергия - обязательный ресурс",
        },
        "gas": {
            "required": True,
            "file_patterns": [
                "gaz.xlsx",
                "газ.xlsx",
                "gas",
                "расчет газа",
                "расчет газа для",
                "отопл",
                "неотпл",
            ],
            "keywords": [
                "газ",
                "gas",
                "расчет газа",
                "отопление",
                "неотопление",
                "газоснабжение",
                "природный газ",
                "газовое",
                "газопотребление",
                "м³",
                "м3",
                "куб",
                "кубометр",
            ],
            "min_quarters": 4,
            "fields": ["volume", "cost", "volume_m3", "cost_sum"],
            "description": "Газ - обязательный ресурс",
        },
        "water": {
            "required": False,  # Опциональный, но желательный
            "file_patterns": ["voda.xlsx", "вода.xlsx", "water", "сув"],
            "keywords": [
                "вода",
                "water",
                "сув",
                "водоснабжение",
                "водопотребление",
                "холодная вода",
                "горячая вода",
                "гвс",
                "хвс",
                "водоотведение",
            ],
            "min_quarters": 2,  # Минимум 2 квартала для опциональных
            "fields": ["volume", "cost", "volume_m3", "cost_sum"],
            "description": "Водоснабжение - опциональный ресурс",
        },
        "fuel": {
            "required": False,
            "file_patterns": ["fuel.xlsx", "топливо.xlsx", "мазут", "mazut"],
            "keywords": [
                "мазут",
                "топливо",
                "fuel",
                "mazut",
                "нефтепродукты",
                "дизельное топливо",
                "топливный",
                "мазутное",
            ],
            "min_quarters": 2,
            "fields": ["volume", "cost", "volume_ton", "cost_sum"],
            "description": "Топливо (мазут) - опциональный ресурс",
        },
        "coal": {
            "required": False,
            "file_patterns": ["coal.xlsx", "уголь.xlsx", "ugol"],
            "keywords": ["уголь", "coal", "ugol"],
            "min_quarters": 2,
            "fields": ["volume", "cost", "volume_ton", "cost_sum"],
            "description": "Уголь - опциональный ресурс",
        },
        "heat": {
            "required": False,
            "file_patterns": ["otoplenie.xlsx", "отопление.xlsx", "heat", "kotel"],
            "keywords": [
                "отопление",
                "тепло",
                "heat",
                "otoplenie",
                "котел",
                "kotel",
                "теплоэнергия",
                "теплоснабжение",
                "гкал",
                "gcal",
                "тепловая энергия",
            ],
            "min_quarters": 2,
            "fields": ["volume", "cost", "volume_gcal", "cost_sum"],
            "description": "Теплоэнергия - опциональный ресурс",
        },
    },
    "infrastructure": {
        "equipment": {
            "required": False,
            "file_patterns": ["oborudovanie.xlsx", "оборудование.xlsx", "equipment"],
            "keywords": ["оборудование", "equipment", "oborudovanie"],
            "description": "Оборудование - опциональный ресурс",
        },
        "envelope": {
            "required": True,
            "file_patterns": [
                "ograjdayuschie",
                "ograjdayuschie.xlsx",
                "ограждающие",
                "ограждающие.xlsx",
                "envelope",
                "teploprovodnost",
                "teploprovodnost.xlsx",
                "теплопроводность",
                "теплопроводность.xlsx",
                "паспорт здани",
                "паспорт здании",
                "паспорт здания",
                "ццр",
                "ццр паспорт",
                "паспорт зданий",
                "здания",
                "здани",
                "строительные конструкции",
            ],
            "keywords": [
                "ограждающие",
                "envelope",
                "конструкции",
                "ograjdayuschie",
                "расчет теплопотерь",
                "теплопотери по зданиям",
                "теплопроводность",
                "teploprovodnost",
                "λ",
                "лямбда",
                "lambda",
                "паспорт здани",
                "паспорт здании",
                "паспорт здания",
                "ццр",
                "здания",
                "здани",
                "строительные конструкции",
                "строительная конструкция",
                "стены",
                "окна",
                "двери",
                "крыша",
                "пол",
                "перекрытия",
                "фундамент",
            ],
            "description": "Расчет теплопотерь по зданиям - обязательный ресурс",
        },
        "nodes": {
            "required": True,  # Обязательный ресурс
            "file_patterns": [
                "uzly_ucheta",
                "uzly_ucheta.xlsx",
                "узлы",
                "узлы учета",
                "узлы учета.xlsx",
                "nodes",
                "schetchiki",
                "schetchiki.xlsx",
                "счетчики",
                "счётчики",
                "счетчики.xlsx",
                "счётчики.xlsx",
                "metering",
                "прибор",
                "приборы",
            ],
            "keywords": [
                "узлы",
                "учет",
                "учёт",
                "узел",
                "nodes",
                "metering",
                "метр",
                "meter",
                "счётчик",
                "счетчик",
                "schetchiki",
                "счетчики",
                "счётчики",
                "прибор учета",
                "приборы учета",
                "измерительный",
                "измерение",
                "показания",
                "учетный",
                "учётный",
            ],
            "description": "Узлы учета - обязательный ресурс",
        },
    },
}

# Минимальный набор для генерации паспорта
MINIMAL_REQUIREMENTS = {
    "required_resources": ["electricity", "gas", "nodes", "envelope"],
    "min_quarters": 4,
    "min_completeness_score": 0.6,  # Минимум 60% готовности
}


def get_required_resources() -> List[str]:
    """Возвращает список обязательных ресурсов из всех категорий."""
    required = []
    # Добавляем обязательные ресурсы из energy_resources
    for resource, config in REQUIRED_DATA_MATRIX["energy_resources"].items():
        if config.get("required", False):
            required.append(resource)
    # Добавляем обязательные ресурсы из infrastructure
    for resource, config in REQUIRED_DATA_MATRIX["infrastructure"].items():
        if config.get("required", False):
            required.append(resource)
    return required


def get_optional_resources() -> List[str]:
    """Возвращает список опциональных ресурсов из всех категорий."""
    optional = []
    # Добавляем опциональные ресурсы из energy_resources
    for resource, config in REQUIRED_DATA_MATRIX["energy_resources"].items():
        if not config.get("required", False):
            optional.append(resource)
    # Добавляем опциональные ресурсы из infrastructure
    for resource, config in REQUIRED_DATA_MATRIX["infrastructure"].items():
        if not config.get("required", False):
            optional.append(resource)
    return optional


def matches_file_pattern(filename: str, resource_config: Dict[str, Any]) -> bool:
    """
    Проверяет, соответствует ли имя файла паттернам ресурса.

    Args:
        filename: Имя файла
        resource_config: Конфигурация ресурса из матрицы

    Returns:
        True если файл соответствует паттернам
    """
    filename_lower = filename.lower()
    # Убираем расширение для более гибкой проверки
    filename_no_ext = (
        filename_lower.rsplit(".", 1)[0] if "." in filename_lower else filename_lower
    )

    # Проверяем паттерны имен файлов
    patterns = resource_config.get("file_patterns", [])
    for pattern in patterns:
        pattern_lower = pattern.lower()
        pattern_no_ext = (
            pattern_lower.rsplit(".", 1)[0] if "." in pattern_lower else pattern_lower
        )
        # Проверяем как полное совпадение паттерна, так и совпадение без расширения
        if pattern_lower in filename_lower or pattern_no_ext in filename_no_ext:
            return True

    # Проверяем ключевые слова
    keywords = resource_config.get("keywords", [])
    if any(keyword.lower() in filename_lower for keyword in keywords):
        return True

    return False


def get_resource_for_file(filename: str) -> str:
    """
    Определяет тип ресурса по имени файла.

    Args:
        filename: Имя файла

    Returns:
        Имя ресурса или пустая строка
    """
    for category, resources in REQUIRED_DATA_MATRIX.items():
        for resource_name, resource_config in resources.items():
            if matches_file_pattern(filename, resource_config):
                return resource_name
    return ""


def get_resource_config(resource_name: str) -> Dict[str, Any]:
    """
    Возвращает конфигурацию ресурса.

    Args:
        resource_name: Имя ресурса

    Returns:
        Конфигурация ресурса или пустой словарь
    """
    for category, resources in REQUIRED_DATA_MATRIX.items():
        if resource_name in resources:
            return resources[resource_name]
    return {}


def is_resource_required(resource_name: str) -> bool:
    """Проверяет, является ли ресурс обязательным."""
    config = get_resource_config(resource_name)
    return config.get("required", False)
