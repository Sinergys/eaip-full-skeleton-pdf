"""
Модуль постобработки числовых значений для OCR
Исправляет распространенные ошибки распознавания чисел
"""
import re
from typing import Any, List, Dict, Optional

def normalize_number(value: str) -> str:
    """
    Нормализует числовое значение, исправляя распространенные ошибки OCR
    
    Args:
        value: Строка с числовым значением (может содержать ошибки)
    
    Returns:
        Нормализованное числовое значение
    """
    if not value or not isinstance(value, str):
        return value
    
    # Убираем лишние пробелы
    value = value.strip()
    
    # Если пустая строка или не число - возвращаем как есть
    if not value:
        return value
    
    # Убираем все пробелы (разделители тысяч могут быть пробелами)
    value = value.replace(' ', '')
    
    # Заменяем запятую на точку (стандартизация десятичного разделителя)
    # Но только если это действительно десятичный разделитель
    # Проверяем паттерн: цифры, запятая/точка, цифры
    if ',' in value and re.match(r'^\d+[,\.]\d+', value):
        value = value.replace(',', '.')
    
    # Исправляем распространенные ошибки OCR
    # 'O' (буква) -> '0' (ноль)
    value = re.sub(r'[Oo]', '0', value)
    # 'l' (буква) -> '1' (единица) - только если в начале или после цифр
    value = re.sub(r'(?<=\d)l(?=\d)', '1', value)
    value = re.sub(r'^l(?=\d)', '1', value)
    # 'I' (буква) -> '1' (единица) - только в числовом контексте
    value = re.sub(r'(?<=\d)I(?=\d)', '1', value)
    
    # Убираем лишние символы (оставляем только цифры, точку, минус)
    value = re.sub(r'[^\d\.\-]', '', value)
    
    # Исправляем множественные точки (оставляем только первую)
    parts = value.split('.')
    if len(parts) > 2:
        # Если больше 2 частей, вероятно это разделители тысяч
        # Объединяем все кроме последней
        value = ''.join(parts[:-1]) + '.' + parts[-1]
    
    # Убираем минус в середине (оставляем только в начале)
    if '-' in value and not value.startswith('-'):
        value = value.replace('-', '')
    
    return value

def validate_number_format(value: str, expected_type: str = "decimal") -> bool:
    """
    Валидирует формат числового значения
    
    Args:
        value: Строка с числовым значением
        expected_type: Ожидаемый тип ("decimal", "integer", "percentage")
    
    Returns:
        True если формат корректный
    """
    if not value or not isinstance(value, str):
        return False
    
    normalized = normalize_number(value)
    
    if expected_type == "integer":
        return bool(re.match(r'^-?\d+$', normalized))
    elif expected_type == "percentage":
        return bool(re.match(r'^-?\d+(\.\d+)?%?$', normalized))
    else:  # decimal
        return bool(re.match(r'^-?\d+(\.\d+)?$', normalized))

def correct_common_number_errors(value: str) -> str:
    """
    Исправляет распространенные ошибки распознавания чисел
    
    Args:
        value: Строка с числовым значением
    
    Returns:
        Исправленное значение
    """
    if not value or not isinstance(value, str):
        return value
    
    original = value
    value = normalize_number(value)
    
    # Специфические исправления для распространенных ошибок
    corrections = {
        # Потеря десятичного разделителя
        r'^(\d{1,2})00$': r'\1.00',  # "100" -> "1.00" (если было "1.00")
        r'^(\d)0$': r'\1.0',  # "10" -> "1.0" (если было "1.0")
        
        # Неправильное форматирование
        r'^(\d+)\.(\d+)\.(\d+)$': r'\1\2.\3',  # "37.500.00" -> "37500.00"
        r'^(\d+)\s+(\d+)$': r'\1\2',  # "37 500" -> "37500"
    }
    
    for pattern, replacement in corrections.items():
        if re.match(pattern, value):
            value = re.sub(pattern, replacement, value)
            break
    
    return value

def postprocess_table_numbers(table: Dict[str, Any]) -> Dict[str, Any]:
    """
    Постобработка числовых значений в таблице
    
    Args:
        table: Словарь с данными таблицы (rows, headers)
    
    Returns:
        Таблица с исправленными числовыми значениями
    """
    if not table or "rows" not in table:
        return table
    
    processed_table = {
        "rows": [],
        "headers": table.get("headers", [])
    }
    
    # Определяем, какие столбцы содержат числа
    # Обычно это столбцы с заголовками: Количество, Цена, Стоимость, Сумма, НДС
    numeric_headers = ["количество", "цена", "стоимость", "сумма", "ндс", "ставка"]
    numeric_columns = []
    
    for i, header in enumerate(table.get("headers", [])):
        header_lower = str(header).lower()
        if any(nh in header_lower for nh in numeric_headers):
            numeric_columns.append(i)
    
    # Обрабатываем каждую строку
    for row in table.get("rows", []):
        processed_row = []
        for i, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else ""
            
            # Если это числовой столбец, обрабатываем значение
            if i in numeric_columns and cell_str:
                # Пробуем исправить значение
                corrected = correct_common_number_errors(cell_str)
                processed_row.append(corrected)
            else:
                processed_row.append(cell_str)
        
        processed_table["rows"].append(processed_row)
    
    return processed_table

def postprocess_tables_numbers(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Постобработка числовых значений во всех таблицах
    
    Args:
        tables: Список таблиц
    
    Returns:
        Список таблиц с исправленными числовыми значениями
    """
    if not tables:
        return tables
    
    return [postprocess_table_numbers(table) for table in tables]

