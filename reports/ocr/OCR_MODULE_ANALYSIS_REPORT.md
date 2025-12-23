# ОТЧЕТ: АНАЛИЗ И УЛУЧШЕНИЕ OCR МОДУЛЯ EAIP

**Дата анализа:** 2025-11-29  
**Исполнитель:** Cursor AI (команда специалистов)  
**Статус:** ✅ Анализ завершен, решения предложены

---

## РОЛИ СПЕЦИАЛИСТОВ

Для комплексного анализа OCR модуля назначены следующие роли:

1. **Data Scientist** - анализ метрик, качества распознавания, статистики ошибок
2. **Software Engineer** - архитектура, алгоритмы, оптимизация кода
3. **ML Engineer** - OCR технологии, предобработка изображений, модели распознавания
4. **QA Engineer** - выявление проблем, тестирование, валидация

---

## 1. АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

### 1.1 Используемые технологии

#### Gemini Vision API
- **Модель:** `gemini-2.0-flash`
- **Использование:** Основной OCR движок для сканированных документов
- **Преимущества:**
  - Высокое качество распознавания (90% страниц с confidence ≥0.90)
  - Хорошее извлечение таблиц (5 таблиц из 5 файлов)
  - Поддержка многоязычности (русский, английский, узбекский)
- **Недостатки:**
  - Медленная обработка (среднее время 26 сек/страница)
  - Проблемы с парсингом JSON ответов (2 файла из 5)
  - Зависимость от внешнего API

#### Tesseract OCR
- **Использование:** Альтернативный OCR движок, автоопределение поворота (OSD)
- **Преимущества:**
  - Локальная обработка (нет зависимости от API)
  - Быстрая обработка
  - Хорошая поддержка языков
- **Недостатки:**
  - Низкое качество для сложных документов
  - Плохое извлечение таблиц
  - Требует предобработки изображений

### 1.2 Текущие алгоритмы обработки

#### Предобработка изображений
**Файл:** `eaip_full_skeleton/services/ingest/file_parser.py` (строки 1010-1038)

**Текущая реализация:**
1. `preprocess_image_for_ocr()` - базовая предобработка
2. Tesseract OSD - автоопределение поворота 90°/180°/270°
3. `deskew_image()` - исправление небольшого наклона (2-5°)

**Проблемы:**
- Нет улучшения контраста и резкости
- Нет удаления шумов
- Нет адаптивной бинаризации
- DPI=300 для Tesseract (можно оптимизировать до 200)

#### Парсинг JSON от Gemini
**Файл:** `eaip_full_skeleton/services/ingest/utils/gemini_vision_ocr.py` (строки 280-438)

**Текущая реализация:**
1. Удаление markdown обертки (```json ... ```)
2. Поиск JSON через regex `\{.*\}`
3. `fix_json_strings()` - посимвольный парсинг для исправления:
   - Вложенных кавычек
   - Unescaped control characters (\n, \r, \t)
4. Fallback парсинг при ошибках

**Проблемы:**
- Ошибки парсинга в 2 файлах из 5 (40%)
- Потеря таблиц при ошибках парсинга
- Нет обработки unterminated strings
- Нет обработки trailing commas в сложных структурах

#### Извлечение таблиц
**Файлы:**
- `eaip_full_skeleton/services/ingest/utils/ocr_table_extractor.py`
- `eaip_full_skeleton/services/ingest/utils/table_detector.py`

**Текущая реализация:**
1. Извлечение из OCR текста через паттерны:
   - Разделители: `|`, `[`, `]`
   - Числовые паттерны
   - Многострочные структуры
2. Извлечение из PDF через:
   - pdfplumber
   - Camelot
   - Tabula

**Проблемы:**
- Сложные таблицы (объединенные ячейки) не извлекаются
- Таблицы без четких границ теряются
- Нет валидации структуры таблиц

### 1.3 Выявленные проблемы

#### Критические проблемы (P0)

**1. Ошибки парсинга JSON от Gemini**
- **Частота:** 2 файла из 5 (40%)
- **Симптомы:**
  - "Unterminated string starting at position 16721"
  - "Invalid control character"
  - "Expecting ',' delimiter"
- **Влияние:**
  - Потеря таблиц (файл 3: 0 таблиц вместо ожидаемых)
  - Низкий confidence (0.50 вместо 0.90+)
  - Частичный парсинг (только текст, без таблиц)

**2. Потеря таблиц при ошибках парсинга**
- **Частота:** 1 файл из 5 (20%)
- **Симптомы:** Файл 3 имел таблицы, но они не были извлечены
- **Влияние:** Критическая потеря данных для закрытия по данным

#### Важные проблемы (P1)

**3. Медленная обработка**
- **Метрика:** Среднее время 26 сек/страница
- **Влияние:** Долгая обработка больших документов (5 страниц = 79 сек)
- **Причина:** Последовательная обработка страниц, нет параллелизации

**4. Низкий confidence на некоторых страницах**
- **Частота:** 1 страница из 10 (10%)
- **Симптомы:** Confidence=0.50 вместо ожидаемого ≥0.70
- **Влияние:** Требуется ручная проверка

#### Средние проблемы (P2)

**5. Отсутствие оптимизации предобработки**
- **Проблема:** Нет улучшения контраста, резкости, удаления шумов
- **Влияние:** Снижение качества OCR для плохих сканов

**6. Нет валидации структуры таблиц**
- **Проблема:** Таблицы могут быть некорректно структурированы
- **Влияние:** Ошибки в данных

### 1.4 Метрики производительности

#### Из батч-теста (ШАГ 4)

**Общие показатели:**
- Файлов обработано: 5/5 (100%)
- Успешных: 5
- Ошибок: 0 (но предупреждения о парсинге JSON)
- Всего символов: 32,849
- Всего таблиц: 5
- Общее время: 260.31 сек (4 мин 20 сек)
- Среднее время на страницу: 26.03 сек
- Low confidence: 10.0% (1 страница из 10)
- Gemini retries: 0

**Производительность по этапам:**
- Извлечение страниц: 0.4-1.4 сек/файл (в среднем 0.7 сек)
- OCR обработка: 3.3-49.5 сек/страница (в среднем 26.0 сек)
- Общее время на файл: 14.0-79.0 сек

**Качество OCR:**
- Высокий confidence (≥0.90): 9 страниц (90%)
- Средний confidence (0.70-0.89): 0 страниц
- Низкий confidence (<0.70): 1 страница (10%)

---

## 2. РЕШЕНИЯ ДЛЯ УЛУЧШЕНИЯ АЛГОРИТМОВ

### 2.1 Улучшение парсинга JSON от Gemini

#### Проблема
Текущая функция `fix_json_strings()` не обрабатывает:
- Unterminated strings (незакрытые строки)
- Trailing commas в сложных структурах
- Вложенные JSON объекты в строках

#### Решение 1: Улучшенный парсер JSON с восстановлением

```python
def fix_json_strings_advanced(text: str) -> str:
    """
    Улучшенный парсер JSON с восстановлением структуры
    Обрабатывает unterminated strings, trailing commas, вложенные объекты
    """
    result = []
    i = 0
    in_string = False
    escape_next = False
    string_start = -1
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
                string_start = i
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
                # Unterminated string - закрываем и открываем заново
                result.append('\\n"')
                result.append(', "')
                in_string = True
                string_start = i + 1
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
            elif char == '}':
                brace_depth -= 1
            elif char == '[':
                bracket_depth += 1
            elif char == ']':
                bracket_depth -= 1
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
```

#### Решение 2: Многоуровневый fallback парсинг

```python
def parse_gemini_json_robust(response_text: str) -> dict:
    """
    Многоуровневый парсинг JSON с fallback стратегиями
    """
    # Уровень 1: Стандартный парсинг
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Уровень 2: Удаление markdown обертки
    cleaned = remove_markdown_wrapper(response_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Уровень 3: Исправление через fix_json_strings_advanced
    fixed = fix_json_strings_advanced(cleaned)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass
    
    # Уровень 4: Частичный парсинг (извлечение текста и таблиц отдельно)
    return parse_partial_json(cleaned)
```

#### Решение 3: Улучшение промпта для Gemini

```python
prompt = """
Извлеки ВСЕ данные из этого документа.

ВАЖНО: В ответе используй ТОЛЬКО валидный JSON без управляющих символов.
Экранируй все кавычки внутри строк как \\".
Используй \\n для переносов строк.

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
```

**Приоритет:** P0 (критично)  
**Оценка времени:** 4-6 часов  
**Ожидаемый эффект:** Снижение ошибок парсинга с 40% до <5%

### 2.2 Оптимизация предобработки изображений

#### Проблема
Текущая предобработка не включает:
- Улучшение контраста
- Повышение резкости
- Удаление шумов
- Адаптивная бинаризация

#### Решение: Комплексная предобработка

```python
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

def enhance_image_for_ocr(image: Image.Image, dpi: int = 200) -> Image.Image:
    """
    Комплексная предобработка изображения для OCR
    """
    # Конвертируем в numpy array для OpenCV
    img_array = np.array(image)
    
    # 1. Конвертация в grayscale если нужно
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # 2. Улучшение контраста (CLAHE - Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 3. Удаление шумов (bilateral filter сохраняет края)
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # 4. Адаптивная бинаризация (Otsu's method)
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 5. Морфологическая обработка (удаление мелких артефактов)
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # 6. Повышение резкости (unsharp mask)
    gaussian = cv2.GaussianBlur(cleaned, (0, 0), 2.0)
    sharpened = cv2.addWeighted(cleaned, 1.5, gaussian, -0.5, 0)
    
    # Конвертируем обратно в PIL Image
    result = Image.fromarray(sharpened)
    
    return result
```

**Интеграция в file_parser.py:**

```python
# В функции apply_ocr_to_pdf, перед OCR:
enhanced_image = enhance_image_for_ocr(image, dpi=200)

# Затем применяем существующую логику:
# - Tesseract OSD для поворота
# - deskew_image для наклона
```

**Приоритет:** P1 (важно)  
**Оценка времени:** 2-3 часа  
**Ожидаемый эффект:** Повышение confidence на 5-10%, улучшение качества для плохих сканов

### 2.3 Улучшение извлечения таблиц

#### Проблема
- Сложные таблицы (объединенные ячейки) не извлекаются
- Таблицы без четких границ теряются
- Нет валидации структуры

#### Решение 1: Улучшенное извлечение через Gemini с детальным промптом

```python
table_extraction_prompt = """
Найди ВСЕ таблицы в этом документе, включая:
- Таблицы с объединенными ячейками
- Таблицы без четких границ
- Таблицы с повернутым текстом

Для каждой таблицы верни:
{
  "rows": [["ячейка1", "ячейка2"], ...],
  "headers": ["заголовок1", ...],
  "merged_cells": [[row, col, rowspan, colspan], ...],
  "location": "страница X, позиция Y",
  "confidence": 0.95
}

ВАЖНО: Сохраняй структуру таблицы точно, включая объединенные ячейки.
"""
```

#### Решение 2: Валидация структуры таблиц

```python
def validate_table_structure(table: dict) -> dict:
    """
    Валидирует структуру таблицы и исправляет ошибки
    """
    rows = table.get('rows', [])
    headers = table.get('headers', [])
    
    # Проверка 1: Все строки должны иметь одинаковое количество столбцов
    if rows:
        expected_cols = len(rows[0])
        for i, row in enumerate(rows):
            if len(row) != expected_cols:
                # Дополняем или обрезаем строку
                if len(row) < expected_cols:
                    row.extend([''] * (expected_cols - len(row)))
                else:
                    rows[i] = row[:expected_cols]
                logger.warning(f"Строка {i} исправлена: было {len(row)}, стало {expected_cols}")
    
    # Проверка 2: Headers должны соответствовать количеству столбцов
    if headers and rows:
        expected_cols = len(rows[0])
        if len(headers) != expected_cols:
            if len(headers) < expected_cols:
                headers.extend([''] * (expected_cols - len(headers)))
            else:
                headers = headers[:expected_cols]
    
    # Проверка 3: Удаление пустых строк
    rows = [row for row in rows if any(cell.strip() for cell in row)]
    
    return {
        'rows': rows,
        'headers': headers,
        'row_count': len(rows),
        'col_count': len(rows[0]) if rows else 0,
        'validated': True
    }
```

**Приоритет:** P1 (важно)  
**Оценка времени:** 3-4 часа  
**Ожидаемый эффект:** Улучшение извлечения таблиц на 15-20%

### 2.4 Повышение confidence scores

#### Проблема
- Некоторые страницы имеют низкий confidence (0.50)
- Нет механизма повышения confidence через повторную обработку

#### Решение: Адаптивная обработка с повторными попытками

```python
def extract_with_adaptive_confidence(image_path: str, page_num: int = 1, min_confidence: float = 0.70) -> dict:
    """
    Адаптивная обработка с повторными попытками при низком confidence
    """
    # Первая попытка
    result = extract_with_gemini_vision(image_path, page_num)
    confidence = result.get('confidence', 0.0)
    
    # Если confidence низкий, пробуем улучшить изображение и повторить
    if confidence < min_confidence:
        logger.warning(f"Низкий confidence ({confidence:.2f}) для {image_path}, пробуем улучшить...")
        
        # Улучшаем изображение
        image = Image.open(image_path)
        enhanced = enhance_image_for_ocr(image)
        
        # Сохраняем улучшенное изображение
        enhanced_path = str(Path(image_path).with_suffix('.enhanced.png'))
        enhanced.save(enhanced_path)
        
        # Повторная обработка
        result2 = extract_with_gemini_vision(enhanced_path, page_num)
        confidence2 = result2.get('confidence', 0.0)
        
        # Выбираем лучший результат
        if confidence2 > confidence:
            logger.info(f"Confidence улучшен с {confidence:.2f} до {confidence2:.2f}")
            result = result2
        
        # Удаляем временный файл
        try:
            os.unlink(enhanced_path)
        except:
            pass
    
    return result
```

**Приоритет:** P2 (средне)  
**Оценка времени:** 2 часа  
**Ожидаемый эффект:** Снижение low_confidence страниц с 10% до <5%

### 2.5 Оптимизация производительности

#### Проблема
- Последовательная обработка страниц (26 сек/страница)
- Нет параллелизации
- Нет кэширования

#### Решение 1: Параллельная обработка страниц

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def process_pdf_parallel(pdf_path: str, max_workers: int = 3) -> dict:
    """
    Параллельная обработка страниц PDF
    """
    # Извлекаем страницы
    images = convert_from_path(pdf_path, dpi=200)
    
    results = {}
    lock = threading.Lock()
    
    def process_page(page_num: int, image: Image.Image):
        # Сохраняем изображение во временный файл
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            image.save(tmp.name, 'PNG')
            tmp_path = tmp.name
        
        try:
            result = extract_with_gemini_vision(tmp_path, page_num)
            with lock:
                results[page_num] = result
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    # Параллельная обработка
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_page, i+1, img): (i+1, img)
            for i, img in enumerate(images)
        }
        
        for future in as_completed(futures):
            page_num, _ = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f"Ошибка обработки страницы {page_num}: {e}")
    
    # Сортируем результаты по номеру страницы
    sorted_results = [results[i] for i in sorted(results.keys())]
    
    return {
        'pages': sorted_results,
        'total_pages': len(images)
    }
```

**Оценка ускорения:** 3 страницы за 26 сек вместо 78 сек (3x ускорение)

#### Решение 2: Кэширование результатов

```python
import hashlib
import json
from pathlib import Path

def get_cache_key(image_path: str) -> str:
    """Генерирует ключ кэша на основе содержимого изображения"""
    with open(image_path, 'rb') as f:
        content = f.read()
    return hashlib.md5(content).hexdigest()

def get_cached_result(cache_key: str) -> Optional[dict]:
    """Получает результат из кэша"""
    cache_dir = Path("cache/ocr")
    cache_file = cache_dir / f"{cache_key}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def cache_result(cache_key: str, result: dict):
    """Сохраняет результат в кэш"""
    cache_dir = Path("cache/ocr")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_file = cache_dir / f"{cache_key}.json"
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
```

**Приоритет:** P1 (важно)  
**Оценка времени:** 3-4 часа  
**Ожидаемый эффект:** Ускорение обработки в 2-3 раза для повторяющихся документов

---

## 3. ПРИОРИТЕТЫ ВНЕДРЕНИЯ

### Критичные (P0) - Внедрить немедленно

1. **Улучшение парсинга JSON** (4-6 часов)
   - Влияние: Снижение ошибок с 40% до <5%
   - Риск: Низкий
   - Эффект: Высокий

### Важные (P1) - Внедрить в ближайшее время

2. **Оптимизация предобработки изображений** (2-3 часа)
   - Влияние: Повышение confidence на 5-10%
   - Риск: Низкий
   - Эффект: Средний

3. **Параллельная обработка страниц** (3-4 часа)
   - Влияние: Ускорение в 2-3 раза
   - Риск: Средний (нужно тестирование)
   - Эффект: Высокий

4. **Улучшение извлечения таблиц** (3-4 часа)
   - Влияние: Улучшение на 15-20%
   - Риск: Низкий
   - Эффект: Средний

### Средние (P2) - Внедрить по возможности

5. **Адаптивная обработка с повторными попытками** (2 часа)
   - Влияние: Снижение low_confidence с 10% до <5%
   - Риск: Низкий
   - Эффект: Низкий

6. **Кэширование результатов** (3-4 часа)
   - Влияние: Ускорение для повторяющихся документов
   - Риск: Низкий
   - Эффект: Средний

---

## 4. РЕКОМЕНДАЦИИ ПО ВНЕДРЕНИЮ

### Этап 1: Критичные исправления (1-2 дня)
1. Внедрить улучшенный парсинг JSON
2. Добавить unit-тесты для нового парсера
3. Провести батч-тест на 10-20 файлах

### Этап 2: Оптимизация (3-5 дней)
1. Внедрить комплексную предобработку изображений
2. Реализовать параллельную обработку страниц
3. Добавить валидацию структуры таблиц

### Этап 3: Улучшения (1-2 дня)
1. Внедрить адаптивную обработку с повторными попытками
2. Добавить кэширование результатов
3. Улучшить промпты для Gemini

### Мониторинг и метрики
1. Логировать все ошибки парсинга JSON
2. Отслеживать confidence scores по страницам
3. Измерять время обработки на каждом этапе
4. Собирать статистику по извлеченным таблицам

---

## 5. ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

После внедрения всех решений:

- **Ошибки парсинга JSON:** С 40% до <5%
- **Low confidence страниц:** С 10% до <5%
- **Время обработки:** С 26 сек/страница до 8-10 сек/страница (с параллелизацией)
- **Качество извлечения таблиц:** Улучшение на 15-20%
- **Общее качество OCR:** Повышение confidence на 5-10%

---

## АУДИТ ДЕЙСТВИЙ

**Время начала:** 2025-11-29 18:40:00  
**Время завершения:** 2025-11-29 19:00:00  
**Общее время:** ~20 минут

### Прочитанные файлы:
- `eaip_full_skeleton/services/ingest/utils/gemini_vision_ocr.py` (464 строки)
- `eaip_full_skeleton/services/ingest/file_parser.py` (1449 строк, секции OCR)
- `config/ocr.yml` (29 строк)
- `reports/ocr/STEP4_report.md` (288 строк)
- `reports/ocr/STEP1_report.md` (211 строк)
- `reports/ocr/STEP3_report.md` (222 строки)
- `eaip_full_skeleton/services/ingest/utils/ocr_table_extractor.py` (частично)
- `eaip_full_skeleton/services/ingest/utils/image_enhancement.py` (частично)

### Проанализированные компоненты:
- Gemini Vision API интеграция
- Tesseract OCR интеграция
- Предобработка изображений
- Парсинг JSON
- Извлечение таблиц
- Метрики производительности

---

**Конец отчёта**

