"""
Модуль валидации и исправления структуры таблиц, извлеченных через OCR
"""
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def validate_table_structure(table: Dict[str, Any]) -> Dict[str, Any]:
    """
    Валидирует структуру таблицы и исправляет ошибки
    
    Проверки:
    1. Все строки должны иметь одинаковое количество столбцов
    2. Headers должны соответствовать количеству столбцов
    3. Удаление пустых строк
    4. Нормализация пустых значений
    
    Args:
        table: Словарь с данными таблицы (rows, headers, location, etc.)
    
    Returns:
        Валидированная таблица с дополнительными метаданными
    """
    if not isinstance(table, dict):
        logger.warning(f"Таблица не является словарем: {type(table)}")
        return {
            'rows': [],
            'headers': [],
            'row_count': 0,
            'col_count': 0,
            'validated': False,
            'errors': ['Таблица не является словарем']
        }
    
    rows = table.get('rows', [])
    headers = table.get('headers', [])
    location = table.get('location', '')
    confidence = table.get('confidence', 0.0)
    errors = []
    warnings = []
    
    # Проверка 1: rows должен быть списком
    if not isinstance(rows, list):
        logger.warning(f"rows не является списком: {type(rows)}")
        rows = []
        errors.append('rows не является списком')
    
    # Проверка 2: headers должен быть списком
    if not isinstance(headers, list):
        logger.warning(f"headers не является списком: {type(headers)}")
        headers = []
        warnings.append('headers не является списком, будет создан автоматически')
    
    # Проверка 3: Все строки должны быть списками
    valid_rows = []
    for i, row in enumerate(rows):
        if not isinstance(row, list):
            logger.warning(f"Строка {i} не является списком: {type(row)}, пропущена")
            warnings.append(f'Строка {i} пропущена (не список)')
            continue
        valid_rows.append(row)
    rows = valid_rows
    
    # Проверка 4: Все строки должны иметь одинаковое количество столбцов
    if rows:
        # Определяем ожидаемое количество столбцов
        # Приоритет: headers (если есть), иначе максимальное в rows
        max_cols_in_rows = max(len(row) for row in rows) if rows else 0
        headers_cols = len(headers) if headers and isinstance(headers, list) else 0
        
        # Используем максимальное значение между headers и rows
        if headers_cols > 0:
            # Если есть headers, используем максимальное (headers или rows)
            expected_cols = max(headers_cols, max_cols_in_rows)
            if headers_cols < max_cols_in_rows:
                warnings.append(f'Headers имеют меньше столбцов ({headers_cols}), чем rows ({max_cols_in_rows}), будет дополнено до {max_cols_in_rows}')
        else:
            # Нет headers - используем максимальное в rows
            expected_cols = max_cols_in_rows
            if max_cols_in_rows > 0:
                warnings.append(f'Количество столбцов определено автоматически: {max_cols_in_rows}')
        
        if expected_cols == 0:
            warnings.append('Не удалось определить количество столбцов')
        
        # Исправляем строки с неправильным количеством столбцов
        for i, row in enumerate(rows):
            if len(row) != expected_cols:
                if len(row) < expected_cols:
                    # Дополняем пустыми значениями
                    rows[i] = row + [''] * (expected_cols - len(row))
                    warnings.append(f'Строка {i} дополнена до {expected_cols} столбцов')
                else:
                    # Обрезаем лишние столбцы
                    rows[i] = row[:expected_cols]
                    warnings.append(f'Строка {i} обрезана до {expected_cols} столбцов')
    
    # Проверка 5: Headers должны соответствовать количеству столбцов
    if rows and expected_cols > 0:
        if not headers:
            # Создаем headers автоматически
            headers = [f'Столбец {i+1}' for i in range(expected_cols)]
            warnings.append(f'Headers созданы автоматически: {expected_cols} столбцов')
        else:
            # Приводим headers к expected_cols
            if len(headers) < expected_cols:
                # Дополняем headers пустыми значениями
                headers = headers + [''] * (expected_cols - len(headers))
                warnings.append(f'Headers дополнены до {expected_cols} столбцов')
            elif len(headers) > expected_cols:
                # Обрезаем headers
                headers = headers[:expected_cols]
                warnings.append(f'Headers обрезаны до {expected_cols} столбцов')
    
    # Проверка 6: Удаление пустых строк (все ячейки пустые или только пробелы)
    rows = [
        row for row in rows 
        if any(cell and str(cell).strip() for cell in row)
    ]
    
    # Проверка 7: Нормализация пустых значений (None -> '', пробелы -> '')
    for i, row in enumerate(rows):
        rows[i] = [
            '' if cell is None or (isinstance(cell, str) and not cell.strip()) 
            else str(cell).strip() 
            for cell in row
        ]
    
    # Проверка 8: Минимальные требования к таблице
    if len(rows) == 0:
        errors.append('Таблица пуста (нет строк с данными)')
        return {
            'rows': [],
            'headers': headers if headers else [],
            'row_count': 0,
            'col_count': expected_cols if rows else 0,
            'validated': False,
            'errors': errors,
            'warnings': warnings,
            'location': location,
            'confidence': confidence
        }
    
    if expected_cols == 0:
        errors.append('Таблица не имеет столбцов')
        return {
            'rows': [],
            'headers': [],
            'row_count': 0,
            'col_count': 0,
            'validated': False,
            'errors': errors,
            'warnings': warnings,
            'location': location,
            'confidence': confidence
        }
    
    # Логируем предупреждения
    if warnings:
        logger.debug(f"Валидация таблицы: {len(warnings)} предупреждений: {warnings[:3]}")
    
    # Логируем ошибки
    if errors:
        logger.warning(f"Валидация таблицы: {len(errors)} ошибок: {errors}")
    
    return {
        'rows': rows,
        'headers': headers,
        'row_count': len(rows),
        'col_count': expected_cols,
        'validated': True,
        'errors': errors,
        'warnings': warnings,
        'location': location,
        'confidence': confidence
    }


def validate_tables_list(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Валидирует список таблиц
    
    Args:
        tables: Список таблиц для валидации
    
    Returns:
        Список валидированных таблиц
    """
    if not isinstance(tables, list):
        logger.warning(f"tables не является списком: {type(tables)}")
        return []
    
    validated_tables = []
    for i, table in enumerate(tables):
        try:
            validated = validate_table_structure(table)
            if validated.get('validated', False):
                validated_tables.append(validated)
            else:
                logger.warning(f"Таблица {i} не прошла валидацию: {validated.get('errors', [])}")
        except Exception as e:
            logger.error(f"Ошибка валидации таблицы {i}: {e}")
            continue
    
    return validated_tables


def get_table_statistics(table: Dict[str, Any]) -> Dict[str, Any]:
    """
    Вычисляет статистику по таблице
    
    Args:
        table: Валидированная таблица
    
    Returns:
        Словарь со статистикой
    """
    rows = table.get('rows', [])
    headers = table.get('headers', [])
    
    # Подсчет непустых ячеек
    non_empty_cells = 0
    numeric_cells = 0
    for row in rows:
        for cell in row:
            if cell and str(cell).strip():
                non_empty_cells += 1
                try:
                    float(str(cell).replace(',', '.').replace(' ', ''))
                    numeric_cells += 1
                except (ValueError, AttributeError):
                    pass
    
    total_cells = len(rows) * len(headers) if rows and headers else 0
    
    return {
        'row_count': len(rows),
        'col_count': len(headers) if headers else 0,
        'total_cells': total_cells,
        'non_empty_cells': non_empty_cells,
        'numeric_cells': numeric_cells,
        'fill_percentage': (non_empty_cells / total_cells * 100) if total_cells > 0 else 0,
        'numeric_percentage': (numeric_cells / non_empty_cells * 100) if non_empty_cells > 0 else 0
    }

