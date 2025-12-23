"""
Модуль анализа содержимого файлов для определения типа ресурса.

Анализирует структуру файла (листы, заголовки, данные) для определения
типа ресурса независимо от названия файла.
"""

import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Синонимы и ключевые слова для определения типа ресурса по содержимому
CONTENT_KEYWORDS: Dict[str, List[str]] = {
    "electricity": [
        "электр",
        "electricity",
        "электроэнергия",
        "квтч",
        "квт",
        "kw",
        "kwh",
        "потребление энергоресурсов",
        "энергопотребление",
        "энергоресурсы",
        "эл",
        "электро",
        "энергия",
        "потребление",
        "edenic",
        "единиц",
        "единицы",
        "единиц на",
        "единицы на",
        "kvt",
        "electro",
        "act",
        "react",
        "активная",
        "реактивная",
    ],
    "gas": [
        "газ",
        "gas",
        "м³",
        "м3",
        "куб",
        "кубометр",
        "газоснабжение",
        "природный газ",
        "газовое",
        "газопотребление",
    ],
    "water": [
        "вода",
        "water",
        "водоснабжение",
        "сув",
        "водопотребление",
        "холодная вода",
        "горячая вода",
        "гвс",
        "хвс",
        "водоотведение",
    ],
    "fuel": [
        "мазут",
        "mazut",
        "топливо",
        "fuel",
        "нефтепродукты",
        "дизельное топливо",
        "топливный",
        "мазутное",
    ],
    "coal": ["уголь", "coal", "ugol", "каменный уголь", "углепотребление"],
    "heat": [
        "отопление",
        "тепло",
        "heat",
        "otoplenie",
        "теплоэнергия",
        "теплоснабжение",
        "гкал",
        "gcal",
        "котел",
        "kotel",
        "тепловая энергия",
    ],
    "nodes": [
        "узлы учета",
        "узел учета",
        "узлы",
        "nodes",
        "metering",
        "счётчик",
        "счетчик",
        "schetchiki",
        "счетчики",
        "счётчики",
        "прибор учета",
        "приборы учета",
        "учет",
        "учёт",
        "измерительный",
        "метр",
        "meter",
        "измерение",
        "показания",
    ],
    "envelope": [
        "ограждающие",
        "envelope",
        "конструкции",
        "ograjdayuschie",
        "ограждающие конструкции",
        "расчет теплопотерь",
        "теплопотери по зданиям",
        "стены",
        "окна",
        "двери",
        "крыша",
        "пол",
        "перекрытия",
        "теплоизоляция",
        "изоляция",
        "утепление",
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
        "фундамент",
        "фасад",
        "покрытие",
        "перегородки",
    ],
    "equipment": [
        "оборудование",
        "equipment",
        "oborudovanie",
        "техника",
        "машины",
        "агрегаты",
        "установки",
        "системы",
    ],
}

# Ключевые слова для листов Excel
SHEET_KEYWORDS: Dict[str, List[str]] = {
    "electricity": ["электр", "эл", "electricity", "энергоресурсы", "потребление"],
    "gas": ["газ", "gas"],
    "water": ["сув", "вода", "water"],
    "nodes": ["узлы", "учет", "nodes", "счетчик", "metering"],
    "envelope": [
        "ограждающие",
        "envelope",
        "конструкции",
        "теплопроводность",
        "teploprovodnost",
        "паспорт здани",
        "паспорт здании",
        "паспорт здания",
        "ццр",
        "здания",
        "здани",
        "строительные конструкции",
    ],
    "equipment": ["оборудование", "equipment"],
}

# Единицы измерения для каждого типа ресурса (высокий приоритет)
UNIT_PATTERNS: Dict[str, List[str]] = {
    "electricity": [
        "квт·ч",
        "квтч",
        "квт",
        "kw",
        "kwh",
        "квар·ч",
        "кварч",
        "kvarh",
        "квт*ч",
        "квт/ч",
        "квт/час",
        "квт/мес",
    ],
    "gas": ["м³", "м3", "куб", "кубометр", "куб.м", "m3", "m³"],
    "water": ["м³", "м3", "литр", "л", "л/мес", "сув", "хвс", "гвс", "m3", "m³"],
    "heat": ["гкал", "gcal", "ккал", "ккал/ч", "квт", "квт/ч", "тепло"],
    "fuel": ["тонн", "т", "литр", "л", "кг", "тонн/мес", "т/мес"],
    "coal": ["тонн", "т", "кг", "тонн/мес", "т/мес"],
}

# Паттерны для определения временных рядов
TIME_SERIES_INDICATORS = [
    "январь",
    "февраль",
    "март",
    "апрель",
    "май",
    "июнь",
    "июль",
    "август",
    "сентябрь",
    "октябрь",
    "ноябрь",
    "декабрь",
    "q1",
    "q2",
    "q3",
    "q4",
    "квартал",
    "месяц",
    "месяцы",
    "2022",
    "2023",
    "2024",
    "2025",
]


def analyze_file_content(
    raw_json: Optional[Dict[str, Any]], filename: str
) -> Optional[str]:
    """
    Анализирует содержимое файла для определения типа ресурса.

    Args:
        raw_json: Распарсенные данные файла из БД
        filename: Имя файла

    Returns:
        Имя ресурса или None
    """
    if not raw_json:
        return None

    try:
        # Анализируем структуру файла
        file_type = raw_json.get("file_type", "").lower()

        if file_type == "excel" or file_type == "xlsx":
            return _analyze_excel_content(raw_json, filename)
        elif file_type == "pdf":
            return _analyze_pdf_content(raw_json, filename)

        return None
    except Exception as e:
        logger.warning(f"Ошибка при анализе содержимого файла {filename}: {e}")
        return None


def _analyze_excel_content(raw_json: Dict[str, Any], filename: str) -> Optional[str]:
    """Анализирует содержимое Excel файла с улучшенным анализом единиц измерения и структуры."""
    parsing_data = raw_json.get("parsing", {}).get("data", {})
    if not parsing_data:
        return None

    # Собираем весь текст из файла для анализа
    all_text = filename.lower()
    sheet_names = []
    headers = []
    all_cells = []  # Все ячейки для анализа единиц измерения

    # Анализируем листы
    sheets = parsing_data.get("sheets", [])
    for sheet in sheets:
        sheet_name = sheet.get("name", "").lower()
        if sheet_name:
            sheet_names.append(sheet_name)
            all_text += " " + sheet_name

        # Анализируем заголовки и данные (расширенный анализ)
        rows = sheet.get("rows", [])
        for row in rows[:15]:  # Увеличено до 15 строк для лучшего анализа
            if isinstance(row, list):
                for cell in row:
                    if cell and isinstance(cell, (str, int, float)):
                        cell_text = str(cell).lower()
                        headers.append(cell_text)
                        all_cells.append(cell_text)
                        all_text += " " + cell_text

    # Ищем совпадения по ключевым словам
    resource_scores: Dict[str, int] = {}

    # ПРИОРИТЕТ 1: Анализ единиц измерения (высокий приоритет)
    for resource, units in UNIT_PATTERNS.items():
        for unit in units:
            unit_lower = unit.lower()
            # Проверяем в ячейках (очень высокий приоритет)
            matches = sum(1 for cell in all_cells if unit_lower in cell)
            if matches > 0:
                resource_scores[resource] = (
                    resource_scores.get(resource, 0) + matches * 5
                )
                logger.debug(
                    f"Найдены единицы измерения '{unit}' для ресурса '{resource}': {matches} совпадений"
                )

    # ПРИОРИТЕТ 2: Проверяем названия листов
    for resource, keywords in SHEET_KEYWORDS.items():
        for keyword in keywords:
            if any(keyword in sheet_name for sheet_name in sheet_names):
                resource_scores[resource] = resource_scores.get(resource, 0) + 3

    # ПРИОРИТЕТ 3: Проверяем заголовки и содержимое по ключевым словам
    for resource, keywords in CONTENT_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Проверяем в названиях листов (высокий приоритет)
            if any(keyword_lower in sheet_name for sheet_name in sheet_names):
                score += 3
            # Проверяем в заголовках (средний приоритет)
            if any(keyword_lower in header for header in headers):
                score += 2
            # Проверяем в общем тексте (низкий приоритет)
            if keyword_lower in all_text:
                score += 1
            # Проверяем точное совпадение в имени файла (очень высокий приоритет)
            if keyword_lower in filename.lower():
                score += 4

        if score > 0:
            resource_scores[resource] = resource_scores.get(resource, 0) + score

    # ПРИОРИТЕТ 4: Анализ структуры данных
    structure_type = _analyze_data_structure(raw_json)
    if structure_type:
        resource_scores[structure_type] = resource_scores.get(structure_type, 0) + 2

    # Возвращаем ресурс с наибольшим счетом
    if resource_scores:
        best_resource = max(resource_scores.items(), key=lambda x: x[1])
        # Снижаем минимальный порог до 1 для более гибкой классификации
        # но требуем минимум 2 для уверенности
        min_threshold = 2 if best_resource[1] < 5 else 1
        if best_resource[1] >= min_threshold:
            logger.info(
                f"Определен тип ресурса по содержимому: {best_resource[0]} "
                f"(счет: {best_resource[1]}) для файла {filename}"
            )
            return best_resource[0]
        else:
            logger.debug(
                f"Низкий счет для ресурса {best_resource[0]} "
                f"({best_resource[1]} < {min_threshold}) для файла {filename}"
            )

    return None


def _analyze_data_structure(raw_json: Dict[str, Any]) -> Optional[str]:
    """
    Анализирует структуру данных для определения типа ресурса.

    Определяет временные ряды, структуру таблиц и другие признаки.
    """
    parsing_data = raw_json.get("parsing", {}).get("data", {})
    if not parsing_data:
        return None

    sheets = parsing_data.get("sheets", [])
    if not sheets:
        return None

    # Анализируем структуру первого листа
    sheet = sheets[0]
    rows = sheet.get("rows", [])

    if not rows or len(rows) < 3:
        return None

    # Собираем текст из первых строк для анализа структуры
    structure_text = " ".join(
        str(cell).lower()
        for row in rows[:5]
        if isinstance(row, list)
        for cell in row
        if cell
    )

    # Проверяем наличие временных рядов (месяцы, кварталы)
    has_time_series = any(
        indicator in structure_text for indicator in TIME_SERIES_INDICATORS
    )

    if has_time_series:
        # Если есть временные ряды, проверяем единицы измерения
        # для более точного определения
        if any(unit in structure_text for unit in UNIT_PATTERNS.get("electricity", [])):
            return "electricity"
        elif any(unit in structure_text for unit in UNIT_PATTERNS.get("gas", [])):
            return "gas"
        elif any(unit in structure_text for unit in UNIT_PATTERNS.get("water", [])):
            return "water"
        elif any(unit in structure_text for unit in UNIT_PATTERNS.get("heat", [])):
            return "heat"

    # Проверяем структуру оборудования (секции с номерами)
    if "оборудование" in structure_text and any(
        re.search(r"\d+\.", str(cell))
        for row in rows[:10]
        if isinstance(row, list)
        for cell in row
        if cell
    ):
        return "equipment"

    # Проверяем структуру узлов учета (многострочные заголовки)
    if any(
        keyword in structure_text
        for keyword in [
            "пункты учёта",
            "узел учета",
            "узлы учета",
            "счётчик",
            "счетчик",
            "прибор учета",
            "приборы учета",
            "измерительный",
            "показания",
        ]
    ):
        return "nodes"

    # Проверяем структуру расчета теплопотерь (разделы, конструкции)
    if any(
        keyword in structure_text
        for keyword in [
            "паспорт здани",
            "паспорт здании",
            "паспорт здания",
            "ццр",
            "ограждающие",
            "конструкции",
        ]
    ) and any(
        keyword in structure_text
        for keyword in [
            "раздел",
            "конструкция",
            "стены",
            "окна",
            "двери",
            "крыша",
            "пол",
            "перекрытия",
            "теплопроводность",
            "лямбда",
        ]
    ):
        return "envelope"

    return None


def _analyze_pdf_content(raw_json: Dict[str, Any], filename: str) -> Optional[str]:
    """Анализирует содержимое PDF файла."""
    parsing_data = raw_json.get("parsing", {}).get("data", {})
    if not parsing_data:
        return None

    # Собираем весь текст
    all_text = filename.lower()

    text = parsing_data.get("text", "")
    if text:
        all_text += " " + text.lower()

    # Ищем совпадения по ключевым словам
    resource_scores: Dict[str, int] = {}

    for resource, keywords in CONTENT_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in all_text:
                score += 1

        if score > 0:
            resource_scores[resource] = score

    # Возвращаем ресурс с наибольшим счетом
    if resource_scores:
        best_resource = max(resource_scores.items(), key=lambda x: x[1])
        if best_resource[1] >= 2:  # Минимальный порог уверенности
            logger.info(
                f"Определен тип ресурса по содержимому PDF: {best_resource[0]} (счет: {best_resource[1]}) для файла {filename}"
            )
            return best_resource[0]

    return None


def get_resource_with_content_analysis(
    filename: str, raw_json: Optional[Dict[str, Any]] = None
) -> str:
    """
    Определяет тип ресурса, анализируя как название файла, так и его содержимое.

    НОВАЯ ЛОГИКА: Приоритет содержимого над именем файла.

    Args:
        filename: Имя файла
        raw_json: Распарсенные данные файла (опционально)

    Returns:
        Имя ресурса или пустая строка
    """
    from config.required_data_matrix import get_resource_for_file

    # ПРИОРИТЕТ 1: Анализ содержимого (если доступен)
    if raw_json:
        resource_by_content = analyze_file_content(raw_json, filename)
        if resource_by_content:
            return resource_by_content

    # ПРИОРИТЕТ 2: Анализ имени файла
    resource_by_name = get_resource_for_file(filename)
    if resource_by_name:
        return resource_by_name

    # Fallback: пустая строка (будет обработано как "other" в ResourceClassifier)
    return ""
