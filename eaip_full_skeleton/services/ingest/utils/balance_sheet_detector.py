"""
Модуль для определения и классификации файлов актов балансов.
Согласно рекомендациям экспертов: сначала определить файлы, затем тестировать на нескольких.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Ключевые слова для определения актов балансов
BALANCE_SHEET_KEYWORDS = [
    "акт баланс",
    "акт баланса",
    "акт реализации",
    "баланс",
    "коммерческий учёт",
    "коммерческий учет",
    "узел учёта",
    "узел учета",
    "трансформаторная подстанция",
    "тп",
    "подстанция",
    "счетчик",
    "счётчик",
    "акт на поставку",
    "акт поставки",
    "реализация нэс",
    "реализация",  # Добавлено для файлов типа "Реализация 2022.xlsx"
    "нэс руз",
]

# Расширения файлов, которые могут содержать акты балансов
BALANCE_SHEET_EXTENSIONS = [".pdf", ".xlsx", ".xls", ".docx", ".doc"]


def is_balance_sheet_file(
    filename: str, raw_json: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Определяет, является ли файл актом баланса.
    
    Согласно рекомендациям экспертов:
    - Software Engineer: "Распаковать и обработать через OCR модуль"
    - QA Engineer: "Тестировать на нескольких файлах сначала"
    
    Args:
        filename: Имя файла
        raw_json: Распарсенные данные файла (опционально, для анализа содержимого)
    
    Returns:
        True если файл является актом баланса
    """
    filename_lower = filename.lower()
    
    # Проверка расширения файла
    file_ext = Path(filename).suffix.lower()
    if file_ext not in BALANCE_SHEET_EXTENSIONS:
        return False
    
    # Проверка ключевых слов в имени файла
    for keyword in BALANCE_SHEET_KEYWORDS:
        if keyword in filename_lower:
            logger.info(
                f"✅ Файл определен как акт баланса по ключевому слову '{keyword}': {filename}"
            )
            return True
    
    # Если доступен raw_json, проверяем содержимое
    if raw_json:
        # Проверяем наличие таблиц с данными по узлам учёта
        if _has_node_consumption_tables(raw_json):
            logger.debug(
                f"Файл определен как акт баланса по содержимому (таблицы узлов учёта): {filename}"
            )
            return True
        
        # Проверяем наличие ключевых слов в тексте/таблицах
        if _has_balance_sheet_content(raw_json):
            logger.debug(
                f"Файл определен как акт баланса по содержимому: {filename}"
            )
            return True
    
    return False


def _has_node_consumption_tables(raw_json: Dict[str, Any]) -> bool:
    """
    Проверяет, содержит ли файл таблицы с данными по узлам учёта.
    
    Args:
        raw_json: Распарсенные данные файла
    
    Returns:
        True если найдены таблицы с данными по узлам учёта
    """
    # Проверяем таблицы в Word файлах
    tables = raw_json.get("tables", [])
    for table in tables:
        rows = table.get("rows", [])
        if not rows:
            continue
        
        # Проверяем заголовки таблицы
        headers = table.get("headers", [])
        header_text = " ".join(str(h).lower() for h in headers if h)
        
        # Ищем ключевые слова в заголовках
        node_keywords = ["узел", "тп", "подстанция", "счетчик", "активная", "реактивная"]
        if any(keyword in header_text for keyword in node_keywords):
            # Проверяем, есть ли числовые данные (потребление)
            for row in rows[:5]:  # Проверяем первые 5 строк
                if row and any(
                    isinstance(cell, (int, float)) and cell > 0
                    for cell in row
                    if cell is not None
                ):
                    return True
    
    # Проверяем листы в Excel файлах
    sheets = raw_json.get("sheets", [])
    for sheet in sheets:
        sheet_name = sheet.get("name", "").lower()
        if any(keyword in sheet_name for keyword in ["узел", "тп", "баланс", "акт"]):
            rows = sheet.get("rows", [])
            if rows and len(rows) > 1:  # Есть данные
                return True
    
    return False


def _has_balance_sheet_content(raw_json: Dict[str, Any]) -> bool:
    """
    Проверяет, содержит ли файл контент, характерный для актов балансов.
    
    Args:
        raw_json: Распарсенные данные файла
    
    Returns:
        True если найдены признаки акта баланса
    """
    # Собираем весь текст из файла
    all_text = ""
    
    # Из таблиц
    for table in raw_json.get("tables", []):
        for row in table.get("rows", []):
            all_text += " ".join(str(cell).lower() for cell in row if cell) + " "
    
    # Из листов Excel
    for sheet in raw_json.get("sheets", []):
        for row in sheet.get("rows", []):
            all_text += " ".join(str(cell).lower() for cell in row if cell) + " "
    
    # Проверяем наличие ключевых слов
    balance_keywords = [
        "акт баланс",
        "коммерческий учёт",
        "реализация нэс",
        "трансформаторная подстанция",
    ]
    
    return any(keyword in all_text for keyword in balance_keywords)


def get_balance_sheet_type(filename: str) -> Optional[str]:
    """
    Определяет тип акта баланса по имени файла.
    
    Args:
        filename: Имя файла
    
    Returns:
        Тип акта баланса: "monthly", "quarterly", "annual", "node_consumption" или None
    """
    filename_lower = filename.lower()
    
    # Месячные акты
    month_keywords = [
        "январь", "февраль", "март", "апрель", "май", "июнь",
        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
        "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"
    ]
    if any(keyword in filename_lower for keyword in month_keywords):
        return "monthly"
    
    # Квартальные акты
    quarter_keywords = ["q1", "q2", "q3", "q4", "квартал", "кв"]
    if any(keyword in filename_lower for keyword in quarter_keywords):
        return "quarterly"
    
    # Годовые акты
    year_keywords = ["год", "annual", "2022", "2023", "2024", "2025"]
    if any(keyword in filename_lower for keyword in year_keywords):
        return "annual"
    
    # Акты с данными по узлам учёта
    node_keywords = ["узел", "тп", "подстанция", "счетчик", "нэс"]
    if any(keyword in filename_lower for keyword in node_keywords):
        return "node_consumption"
    
    return None

