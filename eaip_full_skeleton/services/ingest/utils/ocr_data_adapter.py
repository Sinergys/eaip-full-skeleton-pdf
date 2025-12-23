"""
Адаптер для преобразования таблиц OCR в формат агрегатора
ЭТАП 2: Создание адаптера данных
"""
import logging
import re
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)

# Ключевые слова для поиска таблиц с данными энергоресурсов
ENERGY_KEYWORDS = {
    "electricity": [
        "электроэнергия", "электричество", "энергия", "квт·ч", "квтч", "квт", 
        "квар·ч", "кварч", "квар", "активная", "реактивная", "active", "reactive",
        "kwh", "kvarh", "электр", "electric"
    ],
    "gas": [
        "газ", "м³", "м3", "кубометр", "куб.м", "газоснабжение", "gas", "m3"
    ],
    "water": [
        "вода", "водоснабжение", "м³", "м3", "кубометр", "куб.м", "water"
    ],
    "heating": [
        "тепло", "теплоэнергия", "гкал", "гдж", "отопление", "heating", "heat"
    ]
}

# Ключевые слова для периодов
PERIOD_KEYWORDS = {
    "month": [
        "январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август",
        "сентябрь", "октябрь", "ноябрь", "декабрь",
        "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12",
        "янв", "фев", "мар", "апр", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"
    ],
    "quarter": [
        "q1", "q2", "q3", "q4", "квартал", "1 квартал", "2 квартал", "3 квартал", "4 квартал",
        "i квартал", "ii квартал", "iii квартал", "iv квартал"
    ],
    "year": [
        "год", "годовой", "annual", "2022", "2023", "2024", "2025"
    ]
}


def find_energy_tables_in_ocr(ocr_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Находит таблицы с данными энергоресурсов в результатах OCR.
    
    БЛОК 2.1: Поиск таблиц по ключевым словам
    
    Args:
        ocr_result: Результат OCR от extract_with_gemini_vision()
                   Структура: {
                       "text": str,
                       "tables": List[Dict],
                       "confidence": float,
                       "tables_count": int
                   }
    
    Returns:
        Список найденных таблиц с метаданными:
        [
            {
                "table": Dict,  # Исходная таблица из OCR
                "resource_type": Optional[str],  # "electricity", "gas", "water", "heating"
                "confidence_score": float,  # Оценка соответствия (0-1)
                "matched_keywords": List[str],  # Найденные ключевые слова
                "table_index": int  # Индекс таблицы в исходном списке
            }
        ]
    """
    if not ocr_result:
        logger.warning("OCR результат пуст")
        return []
    
    tables = ocr_result.get("tables", [])
    if not tables:
        logger.warning("Таблицы не найдены в OCR результате")
        return []
    
    text = ocr_result.get("text", "").lower()
    found_tables = []
    
    for table_idx, table in enumerate(tables):
        # Собираем весь текст таблицы для анализа
        table_text = ""
        
        # Добавляем заголовки
        headers = table.get("headers", [])
        if headers:
            table_text += " ".join(str(h).lower() for h in headers if h) + " "
        
        # Добавляем содержимое строк
        rows = table.get("rows", [])
        for row in rows[:10]:  # Анализируем первые 10 строк для производительности
            if row:
                table_text += " ".join(str(cell).lower() for cell in row if cell) + " "
        
        # Ищем совпадения по типам ресурсов
        matched_keywords = []
        resource_type = None
        max_confidence = 0.0
        
        for res_type, keywords in ENERGY_KEYWORDS.items():
            matches = []
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Проверяем в тексте таблицы
                if keyword_lower in table_text:
                    matches.append(keyword)
                # Проверяем в общем тексте OCR (контекст документа)
                if keyword_lower in text:
                    matches.append(keyword)
            
            if matches:
                # Оценка confidence: количество совпадений / общее количество ключевых слов
                confidence = min(len(matches) / max(len(keywords), 1), 1.0)
                if confidence > max_confidence:
                    max_confidence = confidence
                    resource_type = res_type
                    matched_keywords = matches
        
        # Если нашли таблицу с данными энергоресурсов
        if resource_type:
            found_tables.append({
                "table": table,
                "resource_type": resource_type,
                "confidence_score": max_confidence,
                "matched_keywords": matched_keywords,
                "table_index": table_idx
            })
            logger.info(
                f"✅ Найдена таблица {table_idx} с данными {resource_type} "
                f"(confidence: {max_confidence:.2f}, keywords: {matched_keywords[:3]})"
            )
    
    logger.info(f"📊 Всего найдено таблиц с данными энергоресурсов: {len(found_tables)}")
    return found_tables


def identify_resource_type(table: Dict[str, Any], initial_type: Optional[str] = None) -> Optional[str]:
    """
    Определяет тип ресурса на основе детального анализа таблицы.
    
    БЛОК 2.2: Определение типа ресурса
    
    Args:
        table: Таблица из OCR (с полями "headers", "rows")
        initial_type: Предварительно определённый тип из find_energy_tables_in_ocr()
    
    Returns:
        Тип ресурса: "electricity", "gas", "water", "heating" или None
    """
    if not table:
        return None
    
    # Собираем весь текст таблицы для анализа
    table_text = ""
    
    # Анализируем заголовки
    headers = table.get("headers", [])
    if headers:
        table_text += " ".join(str(h).lower() for h in headers if h) + " "
    
    # Анализируем первые 5 строк данных
    rows = table.get("rows", [])
    for row in rows[:5]:
        if row:
            table_text += " ".join(str(cell).lower() for cell in row if cell) + " "
    
    # Определяем тип ресурса по единицам измерения и ключевым словам
    resource_scores = {
        "electricity": 0,
        "gas": 0,
        "water": 0,
        "heating": 0
    }
    
    # Электроэнергия: кВт·ч, кВтч, кВАр·ч, активная, реактивная
    if any(unit in table_text for unit in ["квт·ч", "квтч", "квт", "kwh", "квар·ч", "кварч", "квар", "kvarh"]):
        resource_scores["electricity"] += 3
    if any(kw in table_text for kw in ["активная", "реактивная", "active", "reactive"]):
        resource_scores["electricity"] += 2
    
    # Газ: м³, м3, кубометр
    if any(unit in table_text for unit in ["м³", "м3", "кубометр", "куб.м", "m3"]):
        # Проверяем контекст - если есть "газ", то это газ, иначе может быть вода
        if "газ" in table_text or "gas" in table_text:
            resource_scores["gas"] += 3
        else:
            resource_scores["gas"] += 1
            resource_scores["water"] += 1
    
    # Вода: м³, м3, но с контекстом "вода", "водоснабжение"
    if any(kw in table_text for kw in ["вода", "водоснабжение", "water"]):
        resource_scores["water"] += 3
    if "м³" in table_text or "м3" in table_text:
        if "вода" in table_text or "водоснабжение" in table_text:
            resource_scores["water"] += 2
    
    # Тепло: Гкал, ГДж, отопление
    if any(unit in table_text for unit in ["гкал", "гдж", "gcal", "gj"]):
        resource_scores["heating"] += 3
    if any(kw in table_text for kw in ["тепло", "теплоэнергия", "отопление", "heating"]):
        resource_scores["heating"] += 2
    
    # Если был предварительный тип, увеличиваем его score
    if initial_type and initial_type in resource_scores:
        resource_scores[initial_type] += 1
    
    # Выбираем тип с максимальным score
    max_score = max(resource_scores.values())
    if max_score == 0:
        return initial_type  # Возвращаем предварительный тип, если ничего не найдено
    
    identified_type = max(resource_scores.items(), key=lambda x: x[1])[0]
    logger.info(f"✅ Определён тип ресурса: {identified_type} (score: {max_score})")
    return identified_type


def identify_period_type(table: Dict[str, Any]) -> Optional[str]:
    """
    Определяет тип периода (месяц, квартал, год) на основе структуры таблицы.
    
    БЛОК 2.2: Определение типа периода
    
    Args:
        table: Таблица из OCR (с полями "headers", "rows")
    
    Returns:
        Тип периода: "month", "quarter", "year" или None
    """
    if not table:
        return None
    
    # Анализируем заголовки
    headers = table.get("headers", [])
    headers_text = " ".join(str(h).lower() for h in headers if h) if headers else ""
    
    # Анализируем первую колонку (обычно там периоды)
    rows = table.get("rows", [])
    first_column_values = []
    for row in rows[:15]:  # Анализируем первые 15 строк
        if row and len(row) > 0:
            first_cell = str(row[0]).lower().strip()
            if first_cell:
                first_column_values.append(first_cell)
    
    first_column_text = " ".join(first_column_values)
    all_text = (headers_text + " " + first_column_text).lower()
    
    # Подсчитываем совпадения для каждого типа периода
    period_scores = {
        "month": 0,
        "quarter": 0,
        "year": 0
    }
    
    # Месяцы: ищем названия месяцев или номера 01-12
    month_keywords = PERIOD_KEYWORDS["month"]
    month_matches = sum(1 for kw in month_keywords if kw in all_text)
    if month_matches > 0:
        period_scores["month"] = min(month_matches, 12)  # Максимум 12 (все месяцы)
    
    # Кварталы: ищем "q1", "квартал", "1 квартал" и т.д.
    quarter_keywords = PERIOD_KEYWORDS["quarter"]
    quarter_matches = sum(1 for kw in quarter_keywords if kw in all_text)
    if quarter_matches > 0:
        period_scores["quarter"] = min(quarter_matches, 4)  # Максимум 4 (все кварталы)
    
    # Год: ищем "год", "годовой", "2022", "2023" и т.д.
    year_keywords = PERIOD_KEYWORDS["year"]
    year_matches = sum(1 for kw in year_keywords if kw in all_text)
    if year_matches > 0:
        period_scores["year"] = year_matches
    
    # Дополнительная эвристика: если в первой колонке много разных месяцев (>= 3), это месяцы
    unique_months = set()
    for val in first_column_values:
        for month_kw in month_keywords[:12]:  # Только полные названия месяцев
            if month_kw in val:
                unique_months.add(month_kw)
                break
    
    if len(unique_months) >= 3:
        period_scores["month"] += 5  # Сильный сигнал
    
    # Дополнительная эвристика: если в заголовках есть годы (2022, 2023, 2024, 2025)
    year_pattern = r'\b(202[2-5])\b'
    year_matches_in_headers = len(re.findall(year_pattern, headers_text))
    if year_matches_in_headers > 0:
        period_scores["year"] += year_matches_in_headers * 2
    
    # Выбираем тип с максимальным score
    max_score = max(period_scores.values())
    if max_score == 0:
        # Если ничего не найдено, пробуем определить по структуре
        # Если в первой колонке много строк с данными, вероятно это месяцы
        if len(first_column_values) >= 6:
            return "month"
        return None
    
    identified_period = max(period_scores.items(), key=lambda x: x[1])[0]
    logger.info(f"✅ Определён тип периода: {identified_period} (score: {max_score})")
    return identified_period


# Алиасы месяцев для нормализации
MONTH_ALIASES = {
    "январь": 1, "февраль": 2, "март": 3, "апрель": 4, "май": 5, "июнь": 6,
    "июль": 7, "август": 8, "сентябрь": 9, "октябрь": 10, "ноябрь": 11, "декабрь": 12,
    "янв": 1, "фев": 2, "мар": 3, "апр": 4, "июн": 6, "июл": 7,
    "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12
}


def _normalize_month_name(value: str) -> Optional[str]:
    """Нормализует название месяца"""
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    return normalized if normalized in MONTH_ALIASES else None


def extract_dates_from_table(table: Dict[str, Any], period_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Извлекает даты (месяцы, кварталы, годы) из таблицы.
    
    БЛОК 2.3: Извлечение дат из таблицы
    
    Args:
        table: Таблица из OCR (с полями "headers", "rows")
        period_type: Тип периода ("month", "quarter", "year") из identify_period_type()
    
    Returns:
        Словарь с извлечёнными датами:
        {
            "period_type": str,  # "month", "quarter", "year"
            "dates": List[Dict],  # [{ "month": 1, "year": 2024 }, ...]
            "years": List[int],  # [2022, 2023, 2024]
            "months": List[int],  # [1, 2, 3, ...]
            "quarters": List[int]  # [1, 2, 3, 4]
        }
    """
    if not table:
        return {"period_type": None, "dates": [], "years": [], "months": [], "quarters": []}
    
    # Определяем тип периода, если не указан
    if not period_type:
        period_type = identify_period_type(table)
    
    result: Dict[str, Any] = {
        "period_type": period_type,
        "dates": [],
        "years": [],
        "months": [],
        "quarters": []
    }
    
    # Анализируем заголовки для поиска годов
    headers = table.get("headers", [])
    years_found: Set[int] = set()
    for header in headers:
        if isinstance(header, (int, float)) and 2020 <= header <= 2030:
            years_found.add(int(header))
        elif isinstance(header, str):
            # Ищем годы в тексте заголовка
            year_matches = re.findall(r'\b(202[0-9]|203[0-9])\b', str(header))
            for year_str in year_matches:
                years_found.add(int(year_str))
    
    result["years"] = sorted(list(years_found))
    
    # Если не нашли годы в заголовках, пробуем найти в тексте таблицы
    if not result["years"]:
        rows = table.get("rows", [])
        for row in rows[:10]:
            for cell in row[:5]:
                if isinstance(cell, (int, float)) and 2020 <= cell <= 2030:
                    years_found.add(int(cell))
                elif isinstance(cell, str):
                    year_matches = re.findall(r'\b(202[0-9]|203[0-9])\b', str(cell))
                    for year_str in year_matches:
                        years_found.add(int(year_str))
        result["years"] = sorted(list(years_found))
    
    # Если годы не найдены, используем текущий год по умолчанию
    if not result["years"]:
        from datetime import datetime
        current_year = datetime.now().year
        result["years"] = [current_year]
    
    # Извлекаем месяцы/кварталы из первой колонки
    rows = table.get("rows", [])
    months_found: Set[int] = set()
    
    for row in rows:
        if not row or len(row) == 0:
            continue
        
        # Анализируем первую колонку
        first_cell = str(row[0]).strip() if row[0] else ""
        
        # Ищем месяц
        month_normalized = _normalize_month_name(first_cell)
        if month_normalized:
            month_num = MONTH_ALIASES[month_normalized]
            months_found.add(month_num)
        
        # Ищем номер месяца (01-12)
        month_match = re.search(r'\b(0?[1-9]|1[0-2])\b', first_cell)
        if month_match:
            month_num = int(month_match.group(1))
            months_found.add(month_num)
    
    result["months"] = sorted(list(months_found))
    
    # Вычисляем кварталы из месяцев
    if result["months"]:
        quarters_found: Set[int] = set()
        for month in result["months"]:
            month_int = int(month) if isinstance(month, (int, float, str)) else month
            quarter = (month_int - 1) // 3 + 1
            quarters_found.add(quarter)
        result["quarters"] = sorted(list(quarters_found))
    
    # Формируем список дат
    dates_list: List[Dict[str, Any]] = []
    for year in result["years"]:
        if period_type == "month" and result["months"]:
            for month in result["months"]:
                month_int = int(month) if isinstance(month, (int, float, str)) else month
                dates_list.append({
                    "year": year,
                    "month": month_int,
                    "quarter": (month_int - 1) // 3 + 1
                })
        elif period_type == "quarter" and result["quarters"]:
            for quarter in result["quarters"]:
                quarter_int = int(quarter) if isinstance(quarter, (int, float, str)) else quarter
                dates_list.append({
                    "year": year,
                    "quarter": quarter_int
                })
        elif period_type == "year":
            dates_list.append({
                "year": year
            })
    
    result["dates"] = dates_list
    logger.info(f"✅ Извлечено дат: {len(result['dates'])} ({result['period_type']})")
    return result


def extract_values_from_table(
    table: Dict[str, Any],
    resource_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Извлекает значения потребления и стоимости из таблицы.
    
    БЛОК 2.3: Извлечение значений из таблицы
    
    Args:
        table: Таблица из OCR (с полями "headers", "rows")
        resource_type: Тип ресурса ("electricity", "gas", "water", "heating")
    
    Returns:
        Словарь с извлечёнными значениями:
        {
            "values": List[Dict],  # [{ "row_index": 0, "consumption": 100.0, "cost": 5000.0 }, ...]
            "columns": Dict,  # {"consumption_col": 2, "cost_col": 3, ...}
            "total_consumption": float,
            "total_cost": float
        }
    """
    if not table:
        return {
            "values": [],
            "columns": {},
            "total_consumption": 0.0,
            "total_cost": 0.0
        }
    
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    
    # Определяем колонки с данными по заголовкам
    consumption_col = None
    cost_col = None
    active_kwh_col = None
    reactive_kvarh_col = None
    volume_m3_col = None
    
    headers_text = " ".join(str(h).lower() for h in headers if h)
    
    for col_idx, header in enumerate(headers):
        if not header:
            continue
        
        header_lower = str(header).lower()
        
        # Для электроэнергии
        if resource_type == "electricity":
            if any(kw in header_lower for kw in ["квт·ч", "квтч", "kwh", "активная"]):
                if "реакт" not in header_lower:
                    active_kwh_col = col_idx
            elif any(kw in header_lower for kw in ["квар·ч", "кварч", "kvarh", "реактивная"]):
                reactive_kvarh_col = col_idx
        
        # Для газа и воды
        elif resource_type in ("gas", "water"):
            if any(kw in header_lower for kw in ["м³", "м3", "кубометр", "объем", "volume"]):
                volume_m3_col = col_idx
        
        # Стоимость (для всех типов)
        if any(kw in header_lower for kw in ["стоимость", "сум", "cost", "цена", "price"]):
            cost_col = col_idx
    
    # Если не нашли колонки по заголовкам, пробуем найти по содержимому
    if not consumption_col and not active_kwh_col and not volume_m3_col:
        # Ищем числовые колонки (пропускаем первую - обычно это номер или месяц)
        for col_idx in range(1, min(10, len(headers) if headers else 5)):
            # Проверяем первые несколько строк на наличие чисел
            numeric_count = 0
            for row in rows[:5]:
                if col_idx < len(row):
                    cell = row[col_idx]
                    # Проверяем, является ли значение числом
                    try:
                        if cell and str(cell).strip():
                            # Убираем пробелы и запятые
                            cell_clean = str(cell).replace(" ", "").replace(",", ".")
                            float(cell_clean)
                            numeric_count += 1
                    except (ValueError, AttributeError):
                        pass
            
            # Если в колонке много чисел, это может быть колонка с потреблением
            if numeric_count >= 3:
                if consumption_col is None:
                    consumption_col = col_idx
    
    # Извлекаем значения из строк
    extracted_values = []
    total_consumption = 0.0
    total_cost = 0.0
    
    for row_idx, row in enumerate(rows):
        if not row or len(row) == 0:
            continue
        
        # Пропускаем строки с заголовками или итогами
        first_cell = str(row[0]).lower().strip() if row[0] else ""
        if any(skip_word in first_cell for skip_word in ["итого", "total", "всего", "№", "no", "номер"]):
            continue
        
        # Извлекаем значения
        consumption = None
        cost = None
        active_kwh = None
        reactive_kvarh = None
        volume_m3 = None
        
        # Пробуем извлечь по определённым колонкам
        if active_kwh_col is not None and active_kwh_col < len(row):
            try:
                cell_value = str(row[active_kwh_col]).replace(" ", "").replace(",", ".")
                active_kwh = float(cell_value)
                consumption = active_kwh
            except (ValueError, AttributeError, IndexError):
                pass
        
        if reactive_kvarh_col is not None and reactive_kvarh_col < len(row):
            try:
                cell_value = str(row[reactive_kvarh_col]).replace(" ", "").replace(",", ".")
                reactive_kvarh = float(cell_value)
            except (ValueError, AttributeError, IndexError):
                pass
        
        if volume_m3_col is not None and volume_m3_col < len(row):
            try:
                cell_value = str(row[volume_m3_col]).replace(" ", "").replace(",", ".")
                volume_m3 = float(cell_value)
                consumption = volume_m3
            except (ValueError, AttributeError, IndexError):
                pass
        
        if consumption_col is not None and consumption_col < len(row) and consumption is None:
            try:
                cell_value = str(row[consumption_col]).replace(" ", "").replace(",", ".")
                consumption = float(cell_value)
            except (ValueError, AttributeError, IndexError):
                pass
        
        if cost_col is not None and cost_col < len(row):
            try:
                cell_value = str(row[cost_col]).replace(" ", "").replace(",", ".")
                cost = float(cell_value)
            except (ValueError, AttributeError, IndexError):
                pass
        
        # Если нашли хотя бы одно значение, добавляем запись
        if consumption is not None or cost is not None:
            value_entry = {
                "row_index": row_idx,
                "consumption": consumption,
                "cost": cost,
                "active_kwh": active_kwh,
                "reactive_kvarh": reactive_kvarh,
                "volume_m3": volume_m3
            }
            extracted_values.append(value_entry)
            
            if consumption is not None:
                total_consumption += consumption
            if cost is not None:
                total_cost += cost
    
    result = {
        "values": extracted_values,
        "columns": {
            "consumption_col": consumption_col,
            "cost_col": cost_col,
            "active_kwh_col": active_kwh_col,
            "reactive_kvarh_col": reactive_kvarh_col,
            "volume_m3_col": volume_m3_col
        },
        "total_consumption": total_consumption,
        "total_cost": total_cost
    }
    
    logger.info(
        f"✅ Извлечено значений: {len(extracted_values)} "
        f"(потребление: {total_consumption:.2f}, стоимость: {total_cost:.2f})"
    )
    return result


def month_to_quarter(month_number: int) -> int:
    """Преобразует номер месяца в номер квартала"""
    return (month_number - 1) // 3 + 1


def _get_month_name(month_num: int) -> str:
    """Возвращает название месяца по номеру"""
    month_names = [
        "январь", "февраль", "март", "апрель", "май", "июнь",
        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"
    ]
    if 1 <= month_num <= 12:
        return month_names[month_num - 1]
    return ""


def convert_to_aggregator_format(
    dates_data: Dict[str, Any],
    values_data: Dict[str, Any],
    resource_type: str,
    period_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Преобразует извлечённые данные в формат агрегатора.
    
    БЛОК 2.4: Преобразование в формат агрегатора
    
    Args:
        dates_data: Результат extract_dates_from_table()
        values_data: Результат extract_values_from_table()
        resource_type: Тип ресурса ("electricity", "gas", "water", "heating")
        period_type: Тип периода ("month", "quarter", "year")
    
    Returns:
        Словарь в формате агрегатора:
        {
            "electricity": {
                "2024-Q1": {
                    "year": 2024,
                    "quarter": 1,
                    "months": [
                        {
                            "month": "январь",
                            "values": {
                                "cost_sum": 1000.0,
                                "active_kwh": 500.0,
                                "reactive_kvarh": 100.0
                            }
                        }
                    ]
                }
            }
        }
    """
    if not dates_data or not values_data:
        logger.warning("Недостаточно данных для преобразования в формат агрегатора")
        return {resource_type: {}}
    
    result: Dict[str, Any] = {resource_type: {}}
    
    # Определяем тип периода
    if not period_type:
        period_type = dates_data.get("period_type")
    
    # Получаем даты и значения
    dates = dates_data.get("dates", [])
    values = values_data.get("values", [])
    
    if not dates or not values:
        logger.warning("Нет дат или значений для преобразования")
        return result
    
    # Группируем значения по датам
    # Если у нас есть месяцы, группируем по месяцам
    if period_type == "month":
        # Создаём словарь для группировки значений по датам
        date_to_values: Dict[str, Any] = {}
        
        for date_info in dates:
            year = date_info.get("year")
            month = date_info.get("month")
            quarter = date_info.get("quarter")
            
            if not year or not month:
                continue
            
            quarter_key = f"{year}-Q{quarter}"
            month_name = _get_month_name(month)
            
            # Инициализируем структуру квартала
            if quarter_key not in result[resource_type]:
                result[resource_type][quarter_key] = {
                    "year": year,
                    "quarter": quarter,
                    "months": []
                }
            
            # Находим значения для этого месяца
            # Если значений больше, чем дат, распределяем пропорционально
            month_values = {}
            
            # Для электроэнергии
            if resource_type == "electricity":
                # Ищем значения active_kwh и reactive_kvarh
                for value_entry in values:
                    if value_entry.get("active_kwh") is not None:
                        month_values["active_kwh"] = value_entry.get("active_kwh")
                    if value_entry.get("reactive_kvarh") is not None:
                        month_values["reactive_kvarh"] = value_entry.get("reactive_kvarh")
                    if value_entry.get("cost") is not None:
                        month_values["cost_sum"] = value_entry.get("cost")
            
            # Для газа и воды
            elif resource_type in ("gas", "water"):
                for value_entry in values:
                    if value_entry.get("volume_m3") is not None:
                        month_values["volume_m3"] = value_entry.get("volume_m3")
                    if value_entry.get("cost") is not None:
                        month_values["cost_sum"] = value_entry.get("cost")
            
            # Для отопления
            elif resource_type == "heating":
                for value_entry in values:
                    if value_entry.get("consumption") is not None:
                        month_values["consumption"] = value_entry.get("consumption")
                    if value_entry.get("cost") is not None:
                        month_values["cost_sum"] = value_entry.get("cost")
            
            # Если не нашли специфичные значения, используем общее потребление
            if not month_values and values:
                # Берем первое доступное значение
                first_value = values[0] if values else {}
                if first_value.get("consumption") is not None:
                    month_values["consumption"] = first_value.get("consumption")
                if first_value.get("cost") is not None:
                    month_values["cost_sum"] = first_value.get("cost")
            
            # Добавляем месяц в квартал
            if month_values:
                month_entry = {
                    "month": month_name,
                    "values": month_values
                }
                result[resource_type][quarter_key]["months"].append(month_entry)
    
    # Если период - квартал
    elif period_type == "quarter":
        for date_info in dates:
            year = date_info.get("year")
            quarter = date_info.get("quarter")
            
            if not year or not quarter:
                continue
            
            quarter_key = f"{year}-Q{quarter}"
            
            # Инициализируем структуру квартала
            if quarter_key not in result[resource_type]:
                result[resource_type][quarter_key] = {
                    "year": year,
                    "quarter": quarter,
                    "months": []
                }
            
            # Для квартала создаём одну запись с суммарными значениями
            quarter_values: Dict[str, Any] = {}
            
            # Суммируем значения из всех записей
            for value_entry in values:
                if resource_type == "electricity":
                    if value_entry.get("active_kwh") is not None:
                        quarter_values["active_kwh"] = (quarter_values.get("active_kwh", 0) or 0) + value_entry.get("active_kwh", 0)
                    if value_entry.get("reactive_kvarh") is not None:
                        quarter_values["reactive_kvarh"] = (quarter_values.get("reactive_kvarh", 0) or 0) + value_entry.get("reactive_kvarh", 0)
                elif resource_type in ("gas", "water"):
                    if value_entry.get("volume_m3") is not None:
                        quarter_values["volume_m3"] = (quarter_values.get("volume_m3", 0) or 0) + value_entry.get("volume_m3", 0)
                
                if value_entry.get("cost") is not None:
                    quarter_values["cost_sum"] = (quarter_values.get("cost_sum", 0) or 0) + value_entry.get("cost", 0)
            
            if quarter_values:
                # Для квартала создаём одну запись "квартал"
                quarter_entry = {
                    "month": f"{quarter} квартал",
                    "values": quarter_values
                }
                result[resource_type][quarter_key]["months"].append(quarter_entry)
    
    # Если период - год
    elif period_type == "year":
        for date_info in dates:
            year = date_info.get("year")
            
            if not year:
                continue
            
            # Для года создаём 4 квартала
            for quarter in [1, 2, 3, 4]:
                quarter_key = f"{year}-Q{quarter}"
                
                if quarter_key not in result[resource_type]:
                    result[resource_type][quarter_key] = {
                        "year": year,
                        "quarter": quarter,
                        "months": []
                    }
                
                # Распределяем значения по кварталам (равномерно)
                year_values: Dict[str, Any] = {}
                for value_entry in values:
                    if resource_type == "electricity":
                        if value_entry.get("active_kwh") is not None:
                            year_values["active_kwh"] = (year_values.get("active_kwh", 0) or 0) + (value_entry.get("active_kwh", 0) / 4)
                        if value_entry.get("reactive_kvarh") is not None:
                            year_values["reactive_kvarh"] = (year_values.get("reactive_kvarh", 0) or 0) + (value_entry.get("reactive_kvarh", 0) / 4)
                    elif resource_type in ("gas", "water"):
                        if value_entry.get("volume_m3") is not None:
                            year_values["volume_m3"] = (year_values.get("volume_m3", 0) or 0) + (value_entry.get("volume_m3", 0) / 4)
                    
                    if value_entry.get("cost") is not None:
                        year_values["cost_sum"] = (year_values.get("cost_sum", 0) or 0) + (value_entry.get("cost", 0) / 4)
                
                if year_values:
                    quarter_entry = {
                        "month": f"{quarter} квартал",
                        "values": year_values
                    }
                    result[resource_type][quarter_key]["months"].append(quarter_entry)
    
    logger.info(f"✅ Преобразовано в формат агрегатора: {len(result[resource_type])} кварталов")
    return result


def validate_aggregator_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Валидирует данные в формате агрегатора.
    
    БЛОК 2.4: Валидация данных
    
    Args:
        data: Данные в формате агрегатора
    
    Returns:
        Словарь с результатами валидации:
        {
            "is_valid": bool,
            "errors": List[str],
            "warnings": List[str],
            "statistics": Dict
        }
    """
    errors: List[str] = []
    warnings: List[str] = []
    statistics = {
        "resources": 0,
        "quarters": 0,
        "months": 0,
        "total_values": 0
    }
    
    if not data:
        errors.append("Данные пусты")
        return {
            "is_valid": False,
            "errors": errors,
            "warnings": warnings,
            "statistics": statistics
        }
    
    # Проверяем структуру для каждого ресурса
    for resource_type, resource_data in data.items():
        if not isinstance(resource_data, dict):
            errors.append(f"Неверный формат данных для ресурса {resource_type}")
            continue
        
        statistics["resources"] += 1
        
        # Проверяем кварталы
        for quarter_key, quarter_data in resource_data.items():
            if not isinstance(quarter_data, dict):
                warnings.append(f"Неверный формат квартала {quarter_key}")
                continue
            
            # Проверяем обязательные поля
            if "year" not in quarter_data:
                errors.append(f"Отсутствует поле 'year' в квартале {quarter_key}")
            if "quarter" not in quarter_data:
                errors.append(f"Отсутствует поле 'quarter' в квартале {quarter_key}")
            if "months" not in quarter_data:
                errors.append(f"Отсутствует поле 'months' в квартале {quarter_key}")
            
            if "months" in quarter_data and isinstance(quarter_data["months"], list):
                statistics["quarters"] += 1
                statistics["months"] += len(quarter_data["months"])
                
                # Проверяем месяцы
                for month_entry in quarter_data["months"]:
                    if not isinstance(month_entry, dict):
                        warnings.append(f"Неверный формат месяца в квартале {quarter_key}")
                        continue
                    
                    if "month" not in month_entry:
                        warnings.append(f"Отсутствует поле 'month' в квартале {quarter_key}")
                    if "values" not in month_entry:
                        warnings.append(f"Отсутствует поле 'values' в квартале {quarter_key}")
                    elif isinstance(month_entry["values"], dict):
                        statistics["total_values"] += len(month_entry["values"])
    
    is_valid = len(errors) == 0
    
    result = {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "statistics": statistics
    }
    
    logger.info(
        f"✅ Валидация завершена: {'успешно' if is_valid else 'с ошибками'} "
        f"(ошибок: {len(errors)}, предупреждений: {len(warnings)})"
    )
    
    return result

