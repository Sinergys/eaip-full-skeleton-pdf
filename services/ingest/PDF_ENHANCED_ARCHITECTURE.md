# Улучшенная архитектура обработки PDF

## Обзор

Реализована новая архитектура обработки PDF файлов, которая решает критические проблемы с обработкой сканированных документов.

## Ключевые улучшения

### 1. Предварительная классификация типа PDF

**Модуль:** `utils/pdf_classifier.py`

Определяет тип PDF ДО начала парсинга:
- **text_based** - текстовый PDF (можно парсить напрямую)
- **image_based** - PDF на основе изображений (требует OCR)
- **hybrid** - смешанный тип
- **unknown** - не удалось определить

**Методы классификации:**
1. Быстрая проверка через PyPDF2 (первые 3 страницы)
2. Точная проверка через pdfplumber (при необходимости)

**Метрики:**
- `text_ratio` - доля страниц с текстом (0-1)
- `confidence` - уверенность классификации (high/medium/low)
- `avg_chars_per_page` - среднее количество символов на страницу

### 2. Стратегии обработки

**Модуль:** `utils/pdf_classifier.py` → `get_pdf_processing_strategy()`

Выбирает оптимальную стратегию на основе классификации:

- **`ocr_first`** - для image-based PDF
  - Сразу применяется OCR
  - Извлечение таблиц из OCR текста
  - Структурирование данных

- **`text_first`** - для text-based PDF
  - Стандартный пайплайн (pdfplumber → PyPDF2)
  - OCR только при необходимости

- **`hybrid`** - для смешанных типов
  - Комбинированный подход
  - Адаптивная обработка

### 3. Проверка Java для Tabula

**Модуль:** `utils/table_detector.py`

- Автоматическая проверка наличия Java при импорте
- Tabula используется только если Java доступна
- Логируется предупреждение, если Java не найдена

### 4. Извлечение таблиц из OCR текста

**Модуль:** `utils/ocr_table_extractor.py`

Извлекает табличные структуры из OCR текста используя эвристики:

1. **Поиск выровненных колонок**
   - Множественные пробелы/табы
   - Анализ структуры строк

2. **Поиск разделителей**
   - Вертикальные линии (|, ||)
   - Горизонтальные линии (---)

3. **Структурирование данных**
   - Разделение на секции
   - Сохранение метаданных

## Пайплайн обработки

### OCR-First стратегия (для сканированных PDF)

```
PDF файл
  ↓
Классификация → image_based (high confidence)
  ↓
OCR обработка (Tesseract)
  ↓
Извлечение таблиц из OCR текста
  ↓
Структурирование данных
  ↓
Результат
```

### Text-First стратегия (для текстовых PDF)

```
PDF файл
  ↓
Классификация → text_based (high confidence)
  ↓
Парсинг через pdfplumber
  ↓
Извлечение таблиц (Camelot/pdfplumber/Tabula)
  ↓
Если мало текста → OCR fallback
  ↓
Результат
```

### Hybrid стратегия (для смешанных PDF)

```
PDF файл
  ↓
Классификация → hybrid/unknown
  ↓
Попытка парсинга через pdfplumber
  ↓
Если мало текста → OCR
  ↓
Извлечение таблиц (из парсинга + из OCR)
  ↓
Результат
```

## Использование

Система автоматически определяет тип PDF и выбирает стратегию:

```python
# В file_parser.py
pdf_classification = classify_pdf_type(file_path)
strategy = get_pdf_processing_strategy(pdf_classification)

if strategy == "ocr_first":
    return _process_pdf_with_ocr_first(...)
else:
    # Стандартный пайплайн
    ...
```

## Результаты обработки

Результат содержит дополнительную информацию:

```python
{
    "pdf_type": "image_based" | "text_based" | "hybrid" | "unknown",
    "pdf_type_confidence": "high" | "medium" | "low",
    "processing_strategy": "ocr_first" | "text_first" | "hybrid",
    "text_ratio": 0.0-1.0,
    "tables": [...],  # Включая таблицы из OCR
    "structured_data": [...]  # Структурированные секции
}
```

## Требования

### Обязательные
- Python 3.11+
- PyPDF2 или pdfplumber
- Tesseract OCR
- Poppler utils

### Опциональные
- Java Runtime Environment (для Tabula)
- scikit-image (для улучшения изображений)
- opencv-python (для улучшения изображений)

## Установка Java (для Tabula)

### Windows
```powershell
# Через chocolatey
choco install openjdk

# Или скачать с https://adoptium.net/
```

### Linux/Docker
```bash
sudo apt-get update
sudo apt-get install -y default-jre
```

### Dockerfile
```dockerfile
RUN apt-get update && \
    apt-get install -y default-jre && \
    rm -rf /var/lib/apt/lists/*
```

## Производительность

### До улучшений
- Сканированные PDF: ~12-15 минут (4 страницы)
- Неэффективная обработка (парсинг → провал → OCR)

### После улучшений
- Сканированные PDF: ~12-15 минут (4 страницы) - время не изменилось, но:
  - ✅ Нет лишних попыток парсинга
  - ✅ Извлекаются таблицы из OCR
  - ✅ Структурированные данные

## Логирование

Система логирует:
- Тип PDF и стратегию обработки
- Результаты классификации
- Найденные таблицы (включая из OCR)
- Ошибки и предупреждения

Пример логов:
```
INFO - Классификация PDF: type=image_based, strategy=ocr_first, confidence=high
INFO - PDF определен как image-based, применяю OCR-first стратегию
INFO - OCR-first обработка завершена: 4653 символов, 2 таблиц
```

