"""
Модуль OCR через Google Gemini Vision API
"""
import google.generativeai as genai
from PIL import Image
import json
import logging
import re
import yaml
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Загрузка конфигурации
_config = None

def _load_config():
    """Загружает конфигурацию OCR из config/ocr.yml"""
    global _config
    if _config is None:
        config_path = Path(__file__).parent.parent.parent.parent.parent / "config" / "ocr.yml"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    _config = yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Не удалось загрузить config/ocr.yml: {e}, используются значения по умолчанию")
                _config = {}
        else:
            logger.warning("Файл config/ocr.yml не найден, используются значения по умолчанию")
            _config = {}
    
    # Значения по умолчанию
    defaults = {
        'confidence_thresholds': {
            'text': 0.30,
            'numbers': 0.60,
            'dates': 0.80,
            'tables': 0.70
        },
        'logging': {
            'low_confidence_log': 'reports/ocr/low_confidence.log',
            'enabled': True
        },
        'validation': {
            'add_validation_flag': True,
            'continue_on_low_confidence': True
        },
        'api': {
            'timeout_seconds': 600,
            'retry_attempts': 3,
            'backoff_base_seconds': 2,
            'errors_log': 'reports/ocr/gemini_errors.log'
        }
    }
    
    # Объединяем с дефолтными значениями
    for key, value in defaults.items():
        if key not in _config:
            _config[key] = value
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if sub_key not in _config[key]:
                    _config[key][sub_key] = sub_value
    
    return _config

def _log_low_confidence(doc_path: str, page: int, field: str, confidence: float, threshold: float):
    """Логирует запись с низким confidence"""
    config = _load_config()
    
    if not config.get('logging', {}).get('enabled', True):
        return
    
    log_path = Path(__file__).parent.parent.parent.parent.parent / config['logging']['low_confidence_log']
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().isoformat()
            f.write(f"{timestamp}|{doc_path}|page_{page}|{field}|confidence={confidence:.2f}|threshold={threshold:.2f}\n")
    except Exception as e:
        logger.warning(f"Не удалось записать в low_confidence.log: {e}")

def _check_confidence(result: dict, image_path: str, page_num: int = 1) -> dict:
    """Проверяет confidence и добавляет validation_flag при необходимости"""
    config = _load_config()
    thresholds = config.get('confidence_thresholds', {})
    
    validation_flags = []
    
    # Проверка общего confidence
    overall_confidence = result.get('confidence', 0.0)
    text_threshold = thresholds.get('text', 0.30)
    
    if overall_confidence < text_threshold:
        validation_flags.append('low_confidence')
        _log_low_confidence(str(image_path), page_num, 'overall', overall_confidence, text_threshold)
    
    # Проверка confidence таблиц
    tables = result.get('tables', [])
    tables_threshold = thresholds.get('tables', 0.70)
    
    for i, table in enumerate(tables):
        table_confidence = table.get('confidence', overall_confidence)
        if table_confidence < tables_threshold:
            validation_flags.append(f'low_confidence_table_{i}')
            _log_low_confidence(str(image_path), page_num, f'table_{i}', table_confidence, tables_threshold)
    
    # Добавляем validation_flag если включено
    if config.get('validation', {}).get('add_validation_flag', True) and validation_flags:
        result['validation_flag'] = validation_flags
    
    return result

def _parse_large_tables_robust(tables_content: str) -> list:
    """
    Специальный парсер для больших таблиц с обработкой ошибок JSON
    
    Обрабатывает:
    - Вложенные структуры (массивы в массивах)
    - Ошибки с запятыми и кавычками
    - Незакрытые скобки
    - Построчный парсинг таблиц
    
    Args:
        tables_content: Строка с содержимым таблиц из JSON
    
    Returns:
        Список таблиц
    """
    tables = []
    
    try:
        # Шаг 1: Находим все объекты таблиц
        # Ищем паттерн: { "rows": [...], "headers": [...], ... }
        table_pattern = r'\{\s*"rows"\s*:\s*\[(.*?)\]\s*,\s*"headers"\s*:\s*\[(.*?)\](?:[^}]*)\}'
        table_matches = re.finditer(table_pattern, tables_content, re.DOTALL)
        
        for match in table_matches:
            try:
                rows_str = match.group(1)
                headers_str = match.group(2)
                
                # Шаг 2: Парсим headers
                headers = []
                try:
                    # Извлекаем значения из массива headers
                    header_values = re.findall(r'"([^"]*(?:\\.[^"]*)*)"', headers_str)
                    headers = [h.replace('\\"', '"').replace('\\n', '\n') for h in header_values]
                except Exception as e:
                    logger.debug(f"Ошибка парсинга headers: {e}")
                    # Пробуем альтернативный метод
                    headers_match = re.search(r'\[(.*?)\]', headers_str, re.DOTALL)
                    if headers_match:
                        header_parts = re.split(r',\s*', headers_match.group(1))
                        headers = [h.strip('"').replace('\\"', '"') for h in header_parts if h.strip()]
                
                # Шаг 3: Парсим rows построчно
                rows = []
                # Находим все массивы строк: [[...], [...]]
                row_arrays = re.finditer(r'\[(.*?)\]', rows_str, re.DOTALL)
                
                for row_match in row_arrays:
                    try:
                        row_content = row_match.group(1)
                        # Извлекаем значения из строки
                        # Обрабатываем вложенные кавычки и экранирование
                        row_values = []
                        current_value = ""
                        in_quotes = False
                        escape_next = False
                        
                        i = 0
                        while i < len(row_content):
                            char = row_content[i]
                            
                            if escape_next:
                                current_value += char
                                escape_next = False
                            elif char == '\\':
                                escape_next = True
                                current_value += char
                            elif char == '"':
                                in_quotes = not in_quotes
                                if not in_quotes:
                                    # Закрыли значение
                                    row_values.append(current_value.replace('\\"', '"').replace('\\n', '\n'))
                                    current_value = ""
                                    # Пропускаем запятую и пробелы
                                    i += 1
                                    while i < len(row_content) and row_content[i] in ' ,\n\r\t':
                                        i += 1
                                    continue
                            elif in_quotes:
                                current_value += char
                            elif char == ',':
                                if current_value.strip():
                                    row_values.append(current_value.strip().strip('"').replace('\\"', '"'))
                                    current_value = ""
                            else:
                                if char not in ' \n\r\t':
                                    current_value += char
                            
                            i += 1
                        
                        # Добавляем последнее значение
                        if current_value.strip():
                            row_values.append(current_value.strip().strip('"').replace('\\"', '"'))
                        
                        if row_values:
                            rows.append(row_values)
                    except Exception as e:
                        logger.debug(f"Ошибка парсинга строки таблицы: {e}")
                        continue
                
                # Шаг 4: Создаем объект таблицы
                if rows or headers:
                    table = {
                        "rows": rows,
                        "headers": headers if headers else [f"Столбец {i+1}" for i in range(len(rows[0]) if rows else 0)],
                        "row_count": len(rows),
                        "col_count": len(headers) if headers else (len(rows[0]) if rows else 0),
                        "location": "page/table",
                        "confidence": 0.0
                    }
                    tables.append(table)
                    logger.debug(f"Извлечена таблица: {len(rows)} строк, {len(headers)} столбцов")
            except Exception as e:
                logger.debug(f"Ошибка парсинга таблицы: {e}")
                continue
        
        # Если не нашли таблицы через паттерн, пробуем альтернативный метод
        if not tables:
            # Ищем просто "rows": [[...], [...]]
            rows_match = re.search(r'"rows"\s*:\s*\[(.*?)\]', tables_content, re.DOTALL)
            if rows_match:
                rows_content = rows_match.group(1)
                # Парсим строки построчно
                row_arrays = re.finditer(r'\[(.*?)\]', rows_content, re.DOTALL)
                rows = []
                for row_match in row_arrays:
                    row_str = row_match.group(1)
                    # Простое разделение по запятым (упрощенный метод)
                    values = [v.strip().strip('"').replace('\\"', '"') 
                             for v in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', row_str)
                             if v.strip()]
                    if values:
                        rows.append(values)
                
                if rows:
                    # Определяем количество столбцов
                    max_cols = max(len(row) for row in rows) if rows else 0
                    table = {
                        "rows": rows,
                        "headers": [f"Столбец {i+1}" for i in range(max_cols)],
                        "row_count": len(rows),
                        "col_count": max_cols,
                        "location": "page/table",
                        "confidence": 0.0
                    }
                    tables.append(table)
                    logger.debug(f"Извлечена таблица альтернативным методом: {len(rows)} строк, {max_cols} столбцов")
    
    except Exception as e:
        logger.warning(f"Ошибка в специальном парсере таблиц: {e}")
    
    return tables


def _adaptive_confidence_retry(result: dict, image_path: str, page_num: int) -> dict:
    """
    Адаптивная обработка с повторными попытками при низком confidence
    
    Если confidence ниже порога:
    1. Улучшаем изображение
    2. Повторяем обработку
    3. Выбираем лучший результат
    """
    config = _load_config()
    adaptive_config = config.get('adaptive_processing', {})
    
    # Проверяем, включена ли адаптивная обработка
    if not adaptive_config.get('enabled', True):
        return result
    
    min_confidence = adaptive_config.get('min_confidence', 0.70)
    max_retry_attempts = adaptive_config.get('max_retry_attempts', 1)
    enhance_image = adaptive_config.get('enhance_image', True)
    save_enhanced = adaptive_config.get('save_enhanced_images', False)
    
    confidence = result.get('confidence', 0.0)
    
    # Если confidence достаточен, возвращаем результат
    if confidence >= min_confidence:
        return result
    
    logger.warning(f"Низкий confidence ({confidence:.2f}) для {image_path}, страница {page_num}. "
                   f"Пробуем улучшить изображение и повторить обработку...")
    
    enhanced_path = None
    
    try:
        # Улучшаем изображение
        if enhance_image:
            try:
                from PIL import Image as PILImage
                import sys
                import numpy as np
                from pathlib import Path
                # Импортируем функции улучшения
                utils_path = Path(__file__).parent
                ingest_path = utils_path.parent
                if str(ingest_path) not in sys.path:
                    sys.path.insert(0, str(ingest_path))
                
                # Импортируем функции улучшения изображений
                from utils.image_enhancement import enhance_light_image, enhance_image_for_ocr
                from file_parser import preprocess_image_for_ocr
                
                image = PILImage.open(image_path)
                
                # Определяем, является ли изображение светлым
                # Проверяем среднюю яркость
                gray = image.convert("L")
                img_array = np.array(gray)
                mean_brightness = np.mean(img_array)
                
                # Если средняя яркость > 180 (из 255), считаем изображение светлым
                is_light_image = mean_brightness > 180
                
                if is_light_image:
                    logger.info(f"Обнаружено светлое изображение (средняя яркость: {mean_brightness:.1f}), применяю специальное улучшение")
                    enhanced_image = enhance_light_image(image)
                else:
                    # Используем стандартное улучшение
                    enhanced_image = preprocess_image_for_ocr(image, dpi=200)
                
                # Сохраняем улучшенное изображение
                if save_enhanced:
                    from pathlib import Path
                    enhanced_path = str(Path(image_path).with_suffix('.enhanced.png'))
                    enhanced_image.save(enhanced_path, 'PNG')
                    logger.debug(f"Улучшенное изображение сохранено: {enhanced_path}")
                else:
                    # Используем временный файл
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        enhanced_image.save(tmp.name, 'PNG')
                        enhanced_path = tmp.name
                
                # Повторная обработка с улучшенным изображением
                # Пропускаем адаптивную обработку, чтобы избежать рекурсии
                logger.info(f"Повторная обработка с улучшенным изображением (попытка 1/{max_retry_attempts})")
                result2 = extract_with_gemini_vision(enhanced_path, page_num=page_num, skip_adaptive_retry=True)
                confidence2 = result2.get('confidence', 0.0)
                
                # Выбираем лучший результат
                if confidence2 > confidence:
                    improvement = confidence2 - confidence
                    logger.info(f"✅ Confidence улучшен с {confidence:.2f} до {confidence2:.2f} (+{improvement:.2f})")
                    result = result2
                    result['adaptive_retry_used'] = True
                    result['confidence_improvement'] = improvement
                    result['original_confidence'] = confidence
                else:
                    logger.warning(f"⚠️ Повторная попытка не улучшила confidence: {confidence2:.2f} <= {confidence:.2f}")
                    result['adaptive_retry_used'] = True
                    result['adaptive_retry_improved'] = False
                
            except Exception as e:
                logger.warning(f"Ошибка при адаптивной обработке: {e}, используем исходный результат")
                result['adaptive_retry_error'] = str(e)
        else:
            logger.debug("Улучшение изображения отключено в конфигурации")
    
    finally:
        # Удаляем временный файл (если не сохранен для отладки)
        if enhanced_path and not save_enhanced:
            try:
                import os
                os.unlink(enhanced_path)
            except Exception:
                pass
    
    return result


def _log_gemini_error(image_path: str, page_num: int, attempt: int, error: Exception, error_type: str = "unknown"):
    """Логирует ошибку Gemini API"""
    config = _load_config()
    
    log_path = Path(__file__).parent.parent.parent.parent.parent / config.get('api', {}).get('errors_log', 'reports/ocr/gemini_errors.log')
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().isoformat()
            error_msg = str(error)
            # Определяем тип ошибки
            if '504' in error_msg or 'Deadline Exceeded' in error_msg:
                error_type = 'timeout_504'
            elif 'timeout' in error_msg.lower():
                error_type = 'timeout'
            elif '429' in error_msg or 'quota' in error_msg.lower():
                error_type = 'rate_limit'
            elif '401' in error_msg or '403' in error_msg:
                error_type = 'auth_error'
            else:
                error_type = 'unknown'
            
            f.write(f"{timestamp}|{image_path}|page_{page_num}|attempt_{attempt}|{error_type}|{error_msg}\n")
    except Exception as e:
        logger.warning(f"Не удалось записать в gemini_errors.log: {e}")

def _is_retryable_error(error: Exception) -> bool:
    """Определяет, можно ли повторить запрос при данной ошибке"""
    error_msg = str(error).lower()
    
    # Повторяемые ошибки
    retryable_patterns = [
        '504',
        'deadline exceeded',
        'timeout',
        '503',  # Service Unavailable
        '500',  # Internal Server Error
        '502',  # Bad Gateway
    ]
    
    # Неповторяемые ошибки
    non_retryable_patterns = [
        '401',  # Unauthorized
        '403',  # Forbidden
        '400',  # Bad Request
        '404',  # Not Found
        '429',  # Rate Limit (может быть повторяемым, но с большей задержкой)
    ]
    
    # Проверяем неповторяемые ошибки
    for pattern in non_retryable_patterns:
        if pattern in error_msg:
            return False
    
    # Проверяем повторяемые ошибки
    for pattern in retryable_patterns:
        if pattern in error_msg:
            return True
    
    # По умолчанию не повторяем
    return False

# Настройка API ключа
genai.configure(api_key="AIzaSyAsULYwKTApWIppPOQHMCBJlZoOyBE6l10")


def extract_with_gemini_vision(image_path: str, page_num: int = 1, skip_adaptive_retry: bool = False) -> dict:
    """
    OCR через Gemini Vision с retry и backoff
    
    Args:
        image_path: Путь к изображению
        page_num: Номер страницы
        skip_adaptive_retry: Пропустить адаптивную обработку (для избежания рекурсии)
    """
    config = _load_config()
    api_config = config.get('api', {})
    retry_attempts = api_config.get('retry_attempts', 3)
    backoff_base = api_config.get('backoff_base_seconds', 2)
    timeout_seconds = api_config.get('timeout_seconds', 600)
    
    # Используем доступную модель
    model = genai.GenerativeModel('gemini-2.0-flash')
    image = Image.open(image_path)
    
    prompt = """
    Извлеки ВСЕ данные из этого документа.
    
    ВАЖНО: В ответе используй ТОЛЬКО валидный JSON без управляющих символов.
    Экранируй все кавычки внутри строк как \\".
    Используй \\n для переносов строк.
    НЕ используй markdown обертку (```json).
    
    ЗАДАЧА:
    1. Распознай весь текст (включая повернутый)
    2. Найди ВСЕ таблицы
    3. Структурируй таблицы (строки, столбцы, значения)
    
    ВЕРНИ JSON:
    {
      "text": "полный текст с экранированными \\n и \\"",
      "tables": [
        {
          "rows": [["ячейка1", "ячейка2"], ...],
          "headers": ["заголовок1", ...],
          "location": "страница/позиция"
        }
      ],
      "confidence": 0.95
    }
    
    ТОЛЬКО JSON, БЕЗ ПОЯСНЕНИЙ, БЕЗ MARKDOWN ОБЕРТКИ!
    """
    
    last_error = None
    
    # Retry loop с экспоненциальным backoff
    for attempt in range(1, retry_attempts + 1):
        try:
            logger.info(f"Отправка запроса в Gemini Vision для {image_path} (попытка {attempt}/{retry_attempts})")
            start_time = time.time()
            
            response = model.generate_content([prompt, image])
            
            elapsed_time = time.time() - start_time
            logger.info(f"Запрос успешно выполнен за {elapsed_time:.2f} сек")
            
            # Успешный запрос - выходим из цикла
            break
            
        except Exception as e:
            last_error = e
            error_msg = str(e)
            
            # Логируем ошибку
            _log_gemini_error(image_path, page_num, attempt, e)
            
            # Проверяем, можно ли повторить
            if not _is_retryable_error(e):
                logger.error(f"Неповторяемая ошибка: {error_msg}")
                raise e
            
            # Если это последняя попытка - выбрасываем исключение
            if attempt >= retry_attempts:
                logger.error(f"Все {retry_attempts} попыток исчерпаны. Последняя ошибка: {error_msg}")
                raise e
            
            # Вычисляем задержку (экспоненциальный backoff)
            backoff_time = backoff_base * (2 ** (attempt - 1))
            logger.warning(f"Ошибка на попытке {attempt}/{retry_attempts}: {error_msg}. Повтор через {backoff_time} сек...")
            time.sleep(backoff_time)
    
    # Если дошли сюда, значит запрос успешен
    if 'response' not in locals():
        # Это не должно произойти, но на всякий случай
        raise last_error if last_error else Exception("Неизвестная ошибка")
    
    # Обработка успешного ответа
    try:
        
        # Извлекаем JSON из ответа
        response_text = response.text.strip()
        
        # Сохраняем сырой ответ для отладки (опционально)
        if logger.isEnabledFor(logging.DEBUG):
            debug_path = Path(image_path).parent / "gemini_raw_response.txt"
            try:
                with open(debug_path, 'w', encoding='utf-8') as f:
                    f.write(response_text)
            except:
                pass
        
        # Убираем markdown обертку если есть
        if response_text.startswith('```'):
            # Убираем ```json или ``` в начале
            parts = response_text.split('```')
            if len(parts) >= 3:
                # Есть открывающий и закрывающий ```
                response_text = parts[1]  # Берем содержимое между ```
                if response_text.startswith('json'):
                    response_text = response_text[4:].strip()
            elif len(parts) == 2:
                # Только открывающий ```
                response_text = parts[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:].strip()
            else:
                # Убираем первую строку с ```
                lines = response_text.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                response_text = '\n'.join(lines).strip()
        
        # Пробуем найти JSON в ответе (может быть несколько JSON блоков)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response_text
        
        # Улучшенное исправление JSON с обработкой unterminated strings и trailing commas
        def fix_json_strings_advanced(text: str) -> str:
            """
            Улучшенный парсер JSON с восстановлением структуры
            Обрабатывает unterminated strings, trailing commas, вложенные объекты
            """
            result = []
            i = 0
            in_string = False
            escape_next = False
            bracket_depth = 0
            brace_depth = 0
            
            while i < len(text):
                char = text[i]
                
                if escape_next:
                    result.append(char)
                    escape_next = False
                elif char == '\\':
                    result.append(char)
                    escape_next = True
                elif char == '"' and not escape_next:
                    if not in_string:
                        # Открывающая кавычка
                        in_string = True
                        result.append(char)
                    else:
                        # Проверяем, закрывающая ли это кавычка
                        j = i + 1
                        while j < len(text) and text[j] in ' \t\n\r':
                            j += 1
                        
                        if j >= len(text) or text[j] in ':,\\]\\}':
                            # Закрывающая кавычка
                            in_string = False
                            result.append(char)
                        else:
                            # Вложенная кавычка - экранируем
                            result.append('\\"')
                elif in_string:
                    # Внутри строки
                    if char == '\n':
                        # Unterminated string - закрываем и экранируем перенос
                        result.append('\\n')
                        # НЕ закрываем строку здесь, продолжаем внутри строки
                    elif char == '\r':
                        result.append('\\r')
                    elif char == '\t':
                        result.append('\\t')
                    elif ord(char) < 32:
                        # Удаляем управляющие символы
                        pass
                    else:
                        result.append(char)
                else:
                    # Вне строки
                    if char == '{':
                        brace_depth += 1
                        result.append(char)
                    elif char == '}':
                        brace_depth -= 1
                        result.append(char)
                    elif char == '[':
                        bracket_depth += 1
                        result.append(char)
                    elif char == ']':
                        bracket_depth -= 1
                        result.append(char)
                    elif char == ',':
                        # Проверяем trailing comma
                        j = i + 1
                        while j < len(text) and text[j] in ' \t\n\r':
                            j += 1
                        if j >= len(text) or text[j] in '}]':
                            # Trailing comma - удаляем
                            pass
                        else:
                            result.append(char)
                    else:
                        result.append(char)
                
                i += 1
            
            # Закрываем незакрытые строки
            if in_string:
                result.append('"')
            
            return ''.join(result)
        
        # Применяем улучшенное исправление ко всему JSON
        json_str = fix_json_strings_advanced(json_str)
        
        # Многоуровневый парсинг JSON с fallback стратегиями
        result = None
        parse_error = None
        
        # Уровень 1: Стандартный парсинг
        try:
            result = json.loads(json_str)
            logger.debug("JSON успешно распарсен на уровне 1 (стандартный)")
        except json.JSONDecodeError as e:
            parse_error = e
            logger.debug(f"Уровень 1 не прошел: {e.msg}")
            
            # Уровень 2: Парсинг после fix_json_strings_advanced
            try:
                fixed_str = fix_json_strings_advanced(json_str)
                result = json.loads(fixed_str)
                logger.info("JSON успешно распарсен на уровне 2 (после fix_json_strings_advanced)")
            except json.JSONDecodeError as e2:
                parse_error = e2
                logger.debug(f"Уровень 2 не прошел: {e2.msg}")
                
                # Уровень 3: Дополнительные исправления
                try:
                    # Исправление 1: Убираем trailing запятые
                    fixed_str = re.sub(r',\s*}', '}', fixed_str)
                    fixed_str = re.sub(r',\s*]', ']', fixed_str)
                    
                    # Исправление 2: Исправляем неправильные закрывающие скобки
                    fixed_str = re.sub(r'"location"\s*:\s*"[^"]*"\s*\]', lambda m: m.group(0).replace(']', '}'), fixed_str)
                    
                    # Исправление 3: Убираем комментарии
                    fixed_str = re.sub(r'//.*?\n', '\n', fixed_str)
                    
                    # Исправление 4: Закрываем незакрытые скобки
                    open_braces = fixed_str.count('{') - fixed_str.count('}')
                    open_brackets = fixed_str.count('[') - fixed_str.count(']')
                    if open_braces > 0:
                        fixed_str += '}' * open_braces
                    if open_brackets > 0:
                        fixed_str += ']' * open_brackets
                    
                    result = json.loads(fixed_str)
                    logger.info("JSON успешно распарсен на уровне 3 (после дополнительных исправлений)")
                except json.JSONDecodeError as e3:
                    parse_error = e3
                    logger.warning(f"Уровень 3 не прошел: {e3.msg}")
                    
                    # Уровень 4: Частичный парсинг (извлечение текста и таблиц отдельно)
                    logger.warning("Переход к частичному парсингу JSON")
                    try:
                        # Извлекаем текст (улучшенный паттерн)
                        text_match = re.search(r'"text"\s*:\s*"((?:[^"\\]|\\.|\\n|\\r|\\t)*)"', json_str, re.DOTALL)
                        if not text_match:
                            # Пробуем без экранирования
                            text_match = re.search(r'"text"\s*:\s*"([^"]*)"', json_str, re.DOTALL)
                        text = text_match.group(1).replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t').replace('\\"', '"') if text_match else ""
                        
                        # Извлекаем таблицы (улучшенный паттерн)
                        tables_match = re.search(r'"tables"\s*:\s*\[(.*?)\]', json_str, re.DOTALL)
                        tables = []
                        if tables_match:
                            # Пробуем распарсить таблицы отдельно
                            try:
                                tables_content = tables_match.group(1)
                                # Исправляем основные ошибки в таблицах
                                tables_content = re.sub(r',\s*}', '}', tables_content)
                                tables_content = re.sub(r',\s*]', ']', tables_content)
                                tables_json = '[' + tables_content + ']'
                                tables = json.loads(tables_json)
                            except Exception as table_error:
                                logger.warning(f"Не удалось распарсить таблицы: {table_error}")
                                # Уровень 5: Специальный парсер для больших таблиц
                                try:
                                    tables = _parse_large_tables_robust(tables_content)
                                    if tables:
                                        logger.info(f"✅ Таблицы успешно извлечены через специальный парсер (уровень 5): {len(tables)} таблиц")
                                        # Обновляем parse_level в результате
                                        if 'parse_level' not in result or result.get('parse_level', 0) < 5:
                                            result['parse_level'] = 5
                                except Exception as e5:
                                    logger.warning(f"Специальный парсер таблиц не сработал: {e5}")
                                    # Пробуем извлечь хотя бы структуру таблиц
                                    table_objects = re.findall(r'\{[^{}]*"rows"[^{}]*\}', tables_content, re.DOTALL)
                                    for table_obj in table_objects:
                                        try:
                                            table = json.loads(table_obj)
                                            tables.append(table)
                                        except:
                                            pass
                        
                        # Извлекаем confidence
                        conf_match = re.search(r'"confidence"\s*:\s*([\d.]+)', json_str)
                        confidence = float(conf_match.group(1)) if conf_match else 0.5
                        
                        # Определяем уровень парсинга (5 если использован специальный парсер)
                        parse_level = 5 if any(t.get('parse_level') == 5 for t in tables if isinstance(t, dict)) else 4
                        if tables and len(tables) > 0:
                            # Проверяем, использован ли специальный парсер (по наличию структурированных данных)
                            if all(isinstance(t, dict) and 'rows' in t and 'headers' in t for t in tables):
                                parse_level = 5
                        
                        result = {
                            "text": text,
                            "tables": tables,
                            "confidence": confidence,
                            "error": "JSON partially parsed",
                            "parse_level": parse_level
                        }
                        level_name = "специальный парсер (уровень 5)" if parse_level == 5 else "частичный (уровень 4)"
                        logger.info(f"Частично распарсен JSON ({level_name}): текст ({len(text)} символов), таблиц ({len(tables)})")
                    except Exception as e4:
                        logger.error(f"Не удалось выполнить частичный парсинг JSON: {e4}")
                        result = {
                            "text": response_text[:5000] if len(response_text) > 5000 else response_text,
                            "tables": [],
                            "confidence": 0.0,
                            "error": f"JSON parse failed at all levels: {str(parse_error)}",
                            "parse_level": 0
                        }
        
        # Если result все еще None, это ошибка
        if result is None:
            logger.error("Критическая ошибка: result остался None после всех попыток парсинга")
            result = {
                "text": response_text[:5000] if len(response_text) > 5000 else response_text,
                "tables": [],
                "confidence": 0.0,
                "error": "Critical JSON parse failure",
                "parse_level": 0
            }
        
        logger.info(f"Gemini Vision успешно обработал {image_path}")
        
        # Валидируем структуру таблиц
        if result.get('tables'):
            try:
                from .table_validator import validate_tables_list
                validated_tables = validate_tables_list(result['tables'])
                result['tables'] = validated_tables
                result['tables_validated'] = True
                result['tables_count'] = len(validated_tables)
                
                # Логируем статистику валидации
                invalid_count = len(result.get('tables', [])) - len(validated_tables)
                if invalid_count > 0:
                    logger.warning(f"Валидация таблиц: {invalid_count} таблиц не прошли валидацию")
                if validated_tables:
                    logger.info(f"Валидация таблиц: {len(validated_tables)} таблиц успешно валидированы")
            except Exception as e:
                logger.warning(f"Ошибка валидации таблиц: {e}, используем исходные таблицы")
                result['tables_validated'] = False
        
        # Постобработка числовых значений в таблицах
        if result.get('tables'):
            try:
                from .number_postprocessor import postprocess_tables_numbers
                processed_tables = postprocess_tables_numbers(result['tables'])
                result['tables'] = processed_tables
                result['numbers_postprocessed'] = True
                logger.info(f"Постобработка чисел: обработано {len(processed_tables)} таблиц")
            except Exception as e:
                logger.warning(f"Ошибка постобработки чисел: {e}, используем исходные таблицы")
                result['numbers_postprocessed'] = False
        
        # Постобработка идентификационных кодов в таблицах
        if result.get('tables'):
            try:
                from .id_code_validator import postprocess_tables_id_codes
                processed_tables = postprocess_tables_id_codes(result['tables'])
                result['tables'] = processed_tables
                result['id_codes_postprocessed'] = True
                logger.info(f"Постобработка идентификационных кодов: обработано {len(processed_tables)} таблиц")
            except Exception as e:
                logger.warning(f"Ошибка постобработки идентификационных кодов: {e}, используем исходные таблицы")
                result['id_codes_postprocessed'] = False
        
        # Проверяем confidence и добавляем validation_flag при необходимости
        result = _check_confidence(result, image_path, page_num=page_num)
        
        # Адаптивная обработка: повторная попытка при низком confidence (только если не пропущена)
        if not skip_adaptive_retry:
            result = _adaptive_confidence_retry(result, image_path, page_num)
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON от Gemini: {e}")
        logger.debug(f"Ответ Gemini: {response_text[:500]}")
        return {
            "text": response_text if 'response_text' in locals() else "",
            "tables": [],
            "confidence": 0.0,
            "error": f"JSON decode error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Ошибка при работе с Gemini Vision: {e}")
        return {
            "text": "",
            "tables": [],
            "confidence": 0.0,
            "error": str(e)
        }

