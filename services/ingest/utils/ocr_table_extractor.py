"""
Модуль извлечения таблиц из OCR текста
Обрабатывает структурированные данные после OCR распознавания
"""

import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def extract_tables_from_ocr_text(
    ocr_text: str, page_num: int = 1
) -> List[Dict[str, Any]]:
    """
    Извлекает табличные структуры из OCR текста

    Использует эвристики для поиска таблиц:
    - Поиск выровненных колонок (пробелы/табы)
    - Поиск повторяющихся паттернов разделителей
    - Анализ структуры строк

    Args:
        ocr_text: Текст, полученный из OCR
        page_num: Номер страницы

    Returns:
        Список найденных таблиц
    """
    if not ocr_text or len(ocr_text.strip()) < 20:
        return []

    tables = []
    lines = ocr_text.split("\n")

    # Фильтруем пустые строки
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    if len(non_empty_lines) < 3:  # Минимум 3 строки для таблицы
        return []

    # Ищем паттерны таблиц
    # Паттерн 1: Строки с множественными пробелами/табами (колонки)
    potential_table_rows = []
    for line in non_empty_lines:
        # Подсчитываем количество последовательных пробелов/табов
        spaces = len(re.findall(r"\s{2,}", line))
        tabs = line.count("\t")
        # Также ищем разделители таблиц: |, [, вертикальные линии
        has_table_separators = bool(re.search(r"[|\[\]]{2,}|[|\[\]]\s*[|\[\]]", line))
        if spaces >= 2 or tabs >= 2 or has_table_separators:
            potential_table_rows.append(line)

    if len(potential_table_rows) >= 3:
        # Пытаемся извлечь таблицу
        table_data = _parse_table_rows(potential_table_rows)
        if table_data and len(table_data) >= 2:
            tables.append(
                {
                    "page": page_num,
                    "table_index": 0,
                    "method": "ocr_heuristic",
                    "rows": table_data,
                    "row_count": len(table_data),
                    "col_count": max(len(row) for row in table_data)
                    if table_data
                    else 0,
                    "confidence": "medium",
                }
            )

    # Паттерн 2: Строки с разделителями (|, ||, ---, [, ])
    separator_lines = []
    for line in non_empty_lines:
        if re.search(r"[|\[\]]{2,}|[-]{3,}", line):
            separator_lines.append(line)

    if len(separator_lines) >= 2:
        # Находим строки между разделителями
        table_data = _parse_separator_table(non_empty_lines)
        if table_data and len(table_data) >= 2:
            tables.append(
                {
                    "page": page_num,
                    "table_index": len(tables),
                    "method": "ocr_separator",
                    "rows": table_data,
                    "row_count": len(table_data),
                    "col_count": max(len(row) for row in table_data)
                    if table_data
                    else 0,
                    "confidence": "medium",
                }
            )

    # Паттерн 3: Строки с числами, разделенными пробелами или символами [|]
    # Ищем последовательности строк с числами и разделителями
    numeric_table_rows = []
    for line in non_empty_lines:
        # Ищем строки с числами и разделителями [|]
        if re.search(r"[\d\s\[\|\.]+", line):
            # Подсчитываем количество чисел в строке
            numbers = re.findall(r"\d+[\.\s]*\d*", line)
            separators = len(re.findall(r"[\[\|]", line))
            # Если есть хотя бы 2 числа или есть разделители - это потенциальная строка таблицы
            if len(numbers) >= 2 or separators >= 1:
                numeric_table_rows.append(line)

    # Если нашли последовательные строки с числами (минимум 2)
    if len(numeric_table_rows) >= 2:
        table_data = _parse_numeric_table(numeric_table_rows)
        if table_data and len(table_data) >= 2:
            tables.append(
                {
                    "page": page_num,
                    "table_index": len(tables),
                    "method": "ocr_numeric",
                    "rows": table_data,
                    "row_count": len(table_data),
                    "col_count": max(len(row) for row in table_data)
                    if table_data
                    else 0,
                    "confidence": "medium",
                }
            )

    return tables


def _parse_table_rows(rows: List[str]) -> List[List[str]]:
    """
    Парсит строки таблицы, разделенные пробелами/табами

    Args:
        rows: Список строк таблицы

    Returns:
        Список списков ячеек
    """
    if not rows:
        return []

    # Определяем позиции колонок на основе первой строки
    first_line = rows[0]
    # Ищем последовательности пробелов длиной >= 2
    space_patterns = list(re.finditer(r"\s{2,}", first_line))

    if not space_patterns:
        # Пробуем табы
        if "\t" in first_line:
            return [line.split("\t") for line in rows]
        return []

    # Определяем позиции разделения
    split_positions = [0]
    for match in space_patterns:
        split_positions.append(match.end())
    split_positions.append(len(first_line))

    # Парсим каждую строку
    table_data = []
    for row in rows:
        cells = []
        for i in range(len(split_positions) - 1):
            start = split_positions[i]
            end = split_positions[i + 1] if i + 1 < len(split_positions) else len(row)
            cell = row[start:end].strip()
            cells.append(cell)
        if any(cells):  # Пропускаем полностью пустые строки
            table_data.append(cells)

    return table_data


def _parse_separator_table(lines: List[str]) -> List[List[str]]:
    """
    Парсит таблицу с разделителями (|, ||, ---)

    Args:
        lines: Список строк

    Returns:
        Список списков ячеек
    """
    table_data: List[List[str]] = []
    in_table = False

    for line in lines:
        # Проверяем, является ли строка разделителем
        if re.search(r"[-|]{3,}", line):
            in_table = True
            continue

        if in_table:
            # Разделяем по |, [, или комбинациям
            if "|" in line or "[" in line or "]" in line:
                # Пробуем разные разделители
                if "|" in line:
                    cells = [cell.strip() for cell in line.split("|")]
                elif "[" in line or "]" in line:
                    # Разделяем по [ или ]
                    cells = re.split(r"[\[\]]+", line)
                    cells = [cell.strip() for cell in cells if cell.strip()]
                else:
                    cells = []
                
                # Убираем пустые ячейки по краям
                while cells and not cells[0]:
                    cells.pop(0)
                while cells and not cells[-1]:
                    cells.pop()
                if cells:
                    table_data.append(cells)
            else:
                # Если строка без разделителя, возможно таблица закончилась
                if table_data:
                    break

    return table_data


def _parse_numeric_table(rows: List[str]) -> List[List[str]]:
    """
    Парсит таблицу с числами, разделенными пробелами или символами [|]

    Args:
        rows: Список строк таблицы

    Returns:
        Список списков ячеек
    """
    if not rows:
        return []

    table_data = []
    for row in rows:
        # Пробуем разные разделители
        if "|" in row:
            # Разделяем по |
            cells = [cell.strip() for cell in row.split("|")]
        elif "[" in row or "]" in row:
            # Разделяем по [ или ]
            cells = re.split(r"[\[\]]+", row)
            cells = [cell.strip() for cell in cells if cell.strip()]
        else:
            # Разделяем по множественным пробелам (>=2)
            cells = re.split(r"\s{2,}", row)
            cells = [cell.strip() for cell in cells if cell.strip()]

        # Убираем пустые ячейки по краям
        while cells and not cells[0]:
            cells.pop(0)
        while cells and not cells[-1]:
            cells.pop()

        if cells and len(cells) >= 2:  # Минимум 2 колонки
            table_data.append(cells)

    return table_data


def structure_ocr_data(ocr_text: str, tables: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Структурирует данные после OCR с учетом найденных таблиц

    Args:
        ocr_text: Текст из OCR
        tables: Найденные таблицы

    Returns:
        Структурированные данные
    """
    result = {"text": ocr_text, "tables": tables, "structured_sections": []}

    # Разделяем текст на секции (до/после таблиц)
    if tables:
        # Сортируем таблицы по позиции в тексте
        # (упрощенная версия - в реальности нужно определять позиции)
        result["structured_sections"] = [
            {"type": "table", "table_index": i, "data": table}
            for i, table in enumerate(tables)
        ]

    return result
