"""
Валидатор и корректор идентификационных кодов
Исправляет ошибки распознавания идентификационных кодов в таблицах
"""
import re
from typing import Any, List, Dict, Optional

# Известные паттерны идентификационных кодов
ID_CODE_PATTERNS = {
    # Узбекские идентификационные коды товаров/услуг
    'uzbek_product_code': r'^\d{17}$',  # 17 цифр
    # Примеры известных кодов
    'known_codes': [
        '11302001001000000',  # Услуги по диагностике, ремонту
        '08708001374000000',  # Прочие запчасти
        '03214001044000000',  # Герметик
        '03820001001000000',  # Антифризы
        '02710005002000000',  # Моторное масло
    ]
}

def normalize_id_code(value: str) -> str:
    """
    Нормализует идентификационный код, исправляя ошибки OCR
    
    Args:
        value: Строка с идентификационным кодом (может содержать ошибки)
    
    Returns:
        Нормализованный код
    """
    if not value or not isinstance(value, str):
        return value
    
    # Убираем лишние пробелы
    value = value.strip()
    
    # Убираем все пробелы и дефисы (коды обычно без разделителей)
    value = value.replace(' ', '').replace('-', '').replace('—', '')
    
    # Исправляем распространенные OCR ошибки
    # 'O' (буква) -> '0' (ноль)
    value = re.sub(r'[Oo]', '0', value)
    # 'l' (буква) -> '1' (единица)
    value = re.sub(r'[l|]', '1', value)
    # 'I' (буква) -> '1' (единица)
    value = re.sub(r'I', '1', value)
    # 'S' (буква) -> '5' (пятерка) - только в числовом контексте
    value = re.sub(r'(?<=\d)S(?=\d)', '5', value)
    # 'Z' (буква) -> '2' (двойка) - только в числовом контексте
    value = re.sub(r'(?<=\d)Z(?=\d)', '2', value)
    
    # Убираем все нецифровые символы
    value = re.sub(r'[^\d]', '', value)
    
    return value

def validate_id_code_format(value: str) -> bool:
    """
    Валидирует формат идентификационного кода
    
    Args:
        value: Строка с идентификационным кодом
    
    Returns:
        True если формат корректный
    """
    if not value or not isinstance(value, str):
        return False
    
    normalized = normalize_id_code(value)
    
    # Проверяем, что это 17-значное число
    if len(normalized) == 17 and normalized.isdigit():
        return True
    
    # Также принимаем коды длиной 15-18 цифр (с учетом возможных ошибок)
    if 15 <= len(normalized) <= 18 and normalized.isdigit():
        return True
    
    return False

def correct_id_code(value: str) -> str:
    """
    Исправляет идентификационный код, используя известные паттерны
    
    Args:
        value: Строка с идентификационным кодом
    
    Returns:
        Исправленный код
    """
    if not value or not isinstance(value, str):
        return value
    
    original = value
    normalized = normalize_id_code(value)
    
    # Если код уже валидный, возвращаем его
    if validate_id_code_format(normalized):
        return normalized
    
    # Пробуем найти похожий известный код
    known_codes = ID_CODE_PATTERNS['known_codes']
    for known_code in known_codes:
        # Проверяем сходство (должно совпадать минимум 12 из 17 символов)
        if len(normalized) >= 12:
            matches = sum(1 for a, b in zip(normalized[:17], known_code) if a == b)
            if matches >= 12:
                return known_code
    
    # Если не нашли похожий, возвращаем нормализованный (даже если неполный)
    return normalized

def postprocess_table_id_codes(table: Dict[str, Any]) -> Dict[str, Any]:
    """
    Постобработка идентификационных кодов в таблице
    
    Args:
        table: Словарь с данными таблицы (rows, headers)
    
    Returns:
        Таблица с исправленными идентификационными кодами
    """
    if not table or "rows" not in table:
        return table
    
    processed_table = {
        "rows": [],
        "headers": table.get("headers", [])
    }
    
    # Определяем столбец с идентификационными кодами
    # Обычно это столбец с заголовком, содержащим "идентификационный" или "код"
    id_code_column = None
    for i, header in enumerate(table.get("headers", [])):
        header_lower = str(header).lower()
        if any(keyword in header_lower for keyword in ["идентификационный", "код", "id"]):
            id_code_column = i
            break
    
    # Если не нашли по заголовку, пробуем определить по данным (первый столбец после номера)
    if id_code_column is None and len(table.get("headers", [])) > 1:
        # Обычно идентификационный код во втором столбце (после номера)
        id_code_column = 1
    
    # Обрабатываем каждую строку
    for row in table.get("rows", []):
        processed_row = []
        for i, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else ""
            
            # Если это столбец с идентификационными кодами, обрабатываем значение
            if i == id_code_column and cell_str:
                # Пробуем исправить код
                corrected = correct_id_code(cell_str)
                processed_row.append(corrected)
            else:
                processed_row.append(cell_str)
        
        processed_table["rows"].append(processed_row)
    
    return processed_table

def postprocess_tables_id_codes(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Постобработка идентификационных кодов во всех таблицах
    
    Args:
        tables: Список таблиц
    
    Returns:
        Список таблиц с исправленными идентификационными кодами
    """
    if not tables:
        return tables
    
    return [postprocess_table_id_codes(table) for table in tables]

