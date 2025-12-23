# Документация проекта EAIP

**Дата создания:** 2025-01-27  
**Дата последнего обновления:** 2025-12-01  
**Версия документа:** 1.1  
**Статус:** Актуальная версия

> 📋 **Последние обновления:** См. [PROJECT_UPDATE_2025_12_01.md](PROJECT_UPDATE_2025_12_01.md)

---

## 1. ОБЗОР ПРОЕКТА

### 1.1. Название и цель

**EAIP (Energy Audit Information Platform)** — универсальная платформа для проведения энергоаудита предприятий по требованиям Постановления Кабинета Министров Республики Узбекистан № 690 (ПКМ-690).

**Основная цель проекта:**
- Автоматизация процесса энергоаудита предприятий
- Обработка исходных данных в различных форматах (Excel, Word, PDF, изображения)
- Распознавание сканированных документов через OCR
- Формирование энергопаспортов и отчётов по энергоаудиту
- Структурирование данных в каноническую модель EAIP
- Валидация и расчёт показателей энергоэффективности

### 1.2. Структура директорий (дерево файлов)

```
eaip/
├── eaip_full_skeleton/          # Основной код проекта
│   ├── services/                # Микросервисы
│   │   ├── ingest/              # Сервис загрузки и обработки файлов
│   │   │   ├── main.py          # FastAPI приложение (точка входа)
│   │   │   ├── file_parser.py   # Универсальный парсер файлов
│   │   │   ├── ai_ocr_enhancer.py  # AI-усиление OCR
│   │   │   ├── ai_parser.py     # AI парсер (DeepSeek, OpenAI, Anthropic)
│   │   │   ├── utils/           # Утилиты
│   │   │   │   ├── image_enhancement.py      # Улучшение изображений для OCR
│   │   │   │   ├── ocr_table_extractor.py    # Извлечение таблиц из OCR
│   │   │   │   ├── pdf_classifier.py         # Классификация PDF (текст/изображение)
│   │   │   │   ├── ocr_memory_optimizer.py   # Оптимизация памяти для OCR
│   │   │   │   ├── table_detector.py         # Детектор таблиц в PDF
│   │   │   │   └── ...                       # Другие утилиты
│   │   │   ├── domain/          # Бизнес-логика
│   │   │   ├── config/          # Конфигурация
│   │   │   ├── tests/           # Тесты
│   │   │   └── requirements.txt # Зависимости
│   │   ├── validate/            # Сервис валидации данных
│   │   ├── analytics/           # Сервис аналитики
│   │   ├── reports/             # Сервис генерации отчётов
│   │   ├── recommend/           # Сервис рекомендаций
│   │   ├── management/          # Сервис управления
│   │   └── gateway-auth/        # API Gateway и аутентификация
│   ├── infra/                   # Docker и инфраструктура
│   └── tests/                   # Интеграционные тесты
├── docs/                        # Документация
│   ├── EAIP_TZ.md              # Техническое задание
│   ├── EAIP_ARCHITECTURE.md    # Архитектура системы
│   ├── EAIP_OCR_REQUIREMENTS_GAP.md  # Анализ требований OCR
│   └── ...
├── tools/                       # Инструменты разработки
├── templates/                   # Шаблоны энергопаспортов и отчётов
└── data/                        # Тестовые данные
```

### 1.3. Список всех модулей и их назначение

#### Микросервисы

| Модуль | Порт | Назначение |
|--------|------|------------|
| `ingest` | 8001 | Загрузка файлов, парсинг, OCR, структурирование данных |
| `validate` | 8002 | Валидация согласованности данных, проверка балансов |
| `analytics` | 8003 | Расчёты показателей энергоэффективности, аналитика |
| `reports` | 8004 | Генерация энергопаспортов (Excel) и отчётов (Word/PDF) |
| `recommend` | 8005 | Генерация рекомендаций по энергосбережению |
| `management` | 8006 | Управление пользователями, проектами, справочниками |
| `gateway-auth` | 8000 | API Gateway, аутентификация, маршрутизация запросов |

#### Основные модули в `services/ingest`

| Модуль | Файл | Назначение |
|--------|------|------------|
| **File Parser** | `file_parser.py` | Универсальный парсер Excel, Word, PDF, изображений |
| **OCR Engine** | `file_parser.py` (OCR функции) | Распознавание текста из PDF и изображений |
| **Image Enhancement** | `utils/image_enhancement.py` | Предобработка изображений для улучшения OCR |
| **OCR AI Enhancer** | `ai_ocr_enhancer.py` | AI-улучшение качества OCR распознавания |
| **PDF Classifier** | `utils/pdf_classifier.py` | Классификация PDF (текстовый/сканированный) |
| **Table Extractor** | `utils/ocr_table_extractor.py` | Извлечение таблиц из OCR текста |
| **Table Detector** | `utils/table_detector.py` | Детекция таблиц в PDF через Camelot/pdfplumber |
| **Memory Optimizer** | `utils/ocr_memory_optimizer.py` | Оптимизация памяти для больших изображений |
| **AI Parser** | `ai_parser.py` | AI-парсинг через DeepSeek/OpenAI/Anthropic |
| **Energy Aggregator** | `utils/energy_aggregator.py` | Агрегация энергетических данных |
| **Canonical Collector** | `utils/canonical_collector.py` | Сбор данных в каноническую модель EAIP |
| **Intelligent Router** | `utils/intelligent_router.py` | Автоматический анализ и маршрутизация файлов |
| **Resource Classifier** | `utils/resource_classifier.py` | Классификация типа энергоресурса |
| **AI Content Classifier** | `utils/ai_content_classifier.py` | AI-классификация содержимого файлов |

### 1.4. Используемые технологии и библиотеки

#### Backend Framework
- **FastAPI** 0.115.0 — современный веб-фреймворк для Python
- **Uvicorn** 0.30.0 — ASGI сервер
- **Pydantic** 2.9.2 — валидация данных и модели

#### OCR и обработка изображений
- **pytesseract** 0.3.10 — обёртка для Tesseract OCR
- **Tesseract OCR** (внешняя утилита) — движок распознавания текста
- **Pillow (PIL)** 10.2.0 — обработка изображений
- **opencv-python** ≥4.8.0 — улучшение изображений (deskew, бинаризация, шумоподавление)
- **scikit-image** ≥0.21.0 — дополнительные методы улучшения (Sauvola, Wiener)
- **pdf2image** 1.16.3 — конвертация PDF в изображения (требует Poppler)

#### Парсинг документов
- **openpyxl** 3.1.2 — парсинг Excel файлов
- **pandas** 2.2.0 — обработка табличных данных
- **python-docx** 1.1.0 — парсинг Word документов
- **pdfplumber** 0.10.3 — парсинг PDF (извлечение текста и таблиц)
- **PyPDF2** 3.0.1 — резервный парсер PDF

#### AI интеграция
- **openai** ≥1.0.0 — клиент для DeepSeek и OpenAI API
- Поддержка Anthropic Claude (через OpenAI-совместимый API)

#### База данных
- **SQLite** (встроенная) — локальная БД для разработки
- Поддержка PostgreSQL (в планах)

#### Инфраструктура
- **Docker** и **docker-compose** — контейнеризация сервисов
- **nginx** (в планах) — reverse proxy и load balancing

#### Внешние зависимости (системные)
- **Tesseract OCR** — движок OCR (Windows: через chocolatey или установщик)
- **Poppler** — конвертация PDF в изображения (Windows: через conda или chocolatey)
- **Java Runtime** (опционально) — для Camelot PDF (улучшенное извлечение таблиц)

---

## 2. ДЕТАЛЬНОЕ ОПИСАНИЕ OCR МОДУЛЯ

### 2.1. Какие OCR движки используются

#### Основной движок: Tesseract OCR

**Tesseract OCR** — основной движок для распознавания текста из PDF и изображений.

**Конфигурация:**
- Автоматическое определение пути к Tesseract в стандартных местах Windows:
  - `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
  - `C:\Tesseract-OCR\tesseract.exe`
- Поддержка языков: русский (`rus`) + английский (`eng`) по умолчанию
- Конфигурация через `pytesseract` библиотеку

**Код инициализации:**
```python
# file_parser.py, строки 122-150
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image, ImageEnhance
    
    # Автоматическое определение пути к Tesseract
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Tesseract-OCR\tesseract.exe",
    ]
    
    current_cmd = pytesseract.pytesseract.tesseract_cmd
    if not current_cmd or current_cmd == "tesseract" or not os.path.exists(current_cmd):
        for tesseract_path in tesseract_paths:
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                break
```

#### AI-усиление OCR

**AI-усиление** (опционально) — улучшение качества распознавания через AI (DeepSeek, OpenAI, Anthropic).

**Модуль:** `ai_ocr_enhancer.py`

**Функциональность:**
- Исправление типичных OCR ошибок (0/O, 1/l/I, 5/S, 8/B)
- Исправление пробелов в числах и единицах измерения
- Восстановление разрывов слов и строк
- Исправление неправильного распознавания русских букв
- Улучшение структурирования таблиц

**Использование:**
```python
# file_parser.py, строки 1043-1083
if HAS_OCR_AI_ENHANCER:
    ocr_enhancer = get_ocr_ai_enhancer()
    if ocr_enhancer:
        enhancement_result = ocr_enhancer.enhance_ocr_accuracy(
            initial_ocr_text=full_text,
            context="Энергетический документ с данными о потреблении энергии",
        )
```

### 2.2. Алгоритм предобработки изображений

**Модуль:** `utils/image_enhancement.py`

**Основная функция:** `enhance_image_for_ocr(image: PILImage) -> PILImage`

#### Порядок обработки изображения:

1. **Выравнивание (Deskew)** — устранение перекоса документа
   - Метод: определение угла наклона через OpenCV (контуры)
   - Поворот изображения на рассчитанный угол
   - Логирование угла наклона

2. **Нормализация освещения** — устранение неравномерного освещения
   - Метод: вычитание фона (Gaussian blur) и нормализация яркости
   - Решает проблему теней и отражений

3. **Удаление шума** — очистка изображения от артефактов
   - Методы:
     - Медианный фильтр (OpenCV) — для "соль-перец" шума
     - Гауссовский фильтр — для общего размытия шума
     - Билинейный фильтр — сохраняет края, удаляет шум

4. **Адаптивная бинаризация** — преобразование в чёрно-белое
   - Методы:
     - Метод Оцу (Otsu) — глобальная бинаризация через OpenCV
     - Адаптивная бинаризация — локальная бинаризация (лучше для неравномерного освещения)
     - Метод Sauvola (scikit-image) — адаптивная бинаризация (опционально)

5. **Улучшение резкости** — повышение чёткости текста
   - Метод: ImageEnhance.Sharpness (PIL)
   - Коэффициент усиления: 1.3x

**Пример использования:**
```python
# file_parser.py, строки 996-1002
enhanced_image = preprocess_image_for_ocr(image)

# Внутри preprocess_image_for_ocr используется:
from utils.image_enhancement import enhance_image_for_ocr
return enhance_image_for_ocr(image)
```

**Результат:** улучшение точности OCR на 20-30% для плохих сканов.

### 2.3. Как обрабатываются PDF файлы

**Модуль:** `file_parser.py`, функция `parse_pdf_file()`

#### Архитектура обработки PDF:

**Шаг 1: Предварительная классификация типа PDF**

```python
# file_parser.py, строки 348-363
from utils.pdf_classifier import classify_pdf_type, get_pdf_processing_strategy

pdf_classification = classify_pdf_type(file_path)
strategy = get_pdf_processing_strategy(pdf_classification)

result["pdf_type"] = pdf_classification.get("type", "unknown")
result["processing_strategy"] = strategy  # "text_first", "ocr_first", "hybrid"
```

**Типы PDF:**
- `text_based` — текстовый PDF (можно извлечь текст напрямую)
- `image_based` — сканированный PDF (требует OCR)
- `hybrid` — смешанный тип
- `unknown` — неопределённый тип

**Стратегии обработки:**
- `text_first` — сначала пытаемся извлечь текст, затем OCR при необходимости
- `ocr_first` — сразу применяем OCR (для явно сканированных документов)
- `hybrid` — комбинированный подход

**Шаг 2: Извлечение текста из текстовых PDF**

```python
# file_parser.py, строки 386-433
with pdfplumber.open(file_path) as pdf:
    for page_num, page in enumerate(pdf.pages, 1):
        page_text = page.extract_text() or ""
        page_tables = page.extract_tables()  # Извлечение таблиц
```

**Fallback:** Если `pdfplumber` не работает, используется `PyPDF2`.

**Шаг 3: Определение необходимости OCR**

```python
# file_parser.py, строки 472-500
avg_chars_per_page = result["total_characters"] / len(pdf.pages)
pages_with_text = sum(1 for p in result["pages"] if p.get("char_count", 0) > 0)
text_coverage = (pages_with_text / len(pdf.pages) * 100)

# PDF считается сканированным если:
is_likely_scanned = avg_chars_per_page < 50 or text_coverage < 30
is_definitely_scanned = avg_chars_per_page < 10 or text_coverage < 10
```

**Шаг 4: Применение OCR к сканированным PDF**

```python
# file_parser.py, строки 918-1086
def apply_ocr_to_pdf(file_path: str, languages: str = "rus+eng", batch_id: Optional[str] = None) -> str:
    # 1. Конвертация PDF в изображения через pdf2image
    images = convert_from_path(file_path, dpi=300, poppler_path=poppler_path)
    
    # 2. Обработка каждой страницы
    for i, image in enumerate(images[:max_pages_for_ocr], 1):
        # 3. Предобработка изображения
        enhanced_image = preprocess_image_for_ocr(image)
        
        # 4. OCR распознавание
        text = pytesseract.image_to_string(enhanced_image, lang=languages)
        
        # 5. AI-усиление (опционально)
        if HAS_OCR_AI_ENHANCER:
            enhanced_text = ocr_enhancer.enhance_ocr_accuracy(text)
```

**Ограничения:**
- Максимум 10 страниц для OCR (настраивается через `max_pages_for_ocr`)
- DPI для конвертации: 300 (оптимально для баланса качества/производительности)

### 2.4. Обработка таблиц (если реализована)

#### Извлечение таблиц из текстовых PDF

**Метод 1: pdfplumber (базовый)**

```python
# file_parser.py, строки 410-423
page_tables = page.extract_tables()
for table_idx, table in enumerate(page_tables):
    all_tables.append({
        "page": page_num,
        "table_index": table_idx,
        "method": "pdfplumber",
        "rows": table,
        "row_count": len(table),
        "col_count": len(table[0]) if table else 0,
    })
```

**Метод 2: Camelot PDF (улучшенный, опционально)**

```python
# file_parser.py, строки 435-461
from utils.table_detector import extract_tables_from_pdf

enhanced_tables = extract_tables_from_pdf(
    file_path, prefer_camelot=True
)
```

**Требования:** Java Runtime Environment (для Camelot).

#### Извлечение таблиц из OCR текста

**Модуль:** `utils/ocr_table_extractor.py`

**Функция:** `extract_tables_from_ocr_text(ocr_text: str, page_num: int = 1)`

**Алгоритм:**

1. **Поиск паттернов таблиц:**
   - Строки с множественными пробелами/табами (колонки)
   - Строки с разделителями (|, ||, ---)

2. **Парсинг строк таблицы:**
   - Разделение по пробелам/табам
   - Определение количества колонок
   - Формирование структурированных данных

**Пример:**
```python
# file_parser.py, строки 700-713
from utils.ocr_table_extractor import extract_tables_from_ocr_text

ocr_tables = extract_tables_from_ocr_text(ocr_text, page_num=1)
if ocr_tables:
    result["tables"].extend(ocr_tables)
```

#### AI-структурирование таблиц (опционально)

```python
# file_parser.py, строки 715-737
if HAS_AI_TABLE_PARSER and ocr_tables:
    table_parser = get_ai_table_parser()
    if table_parser:
        structured_tables = table_parser.structure_multiple_tables(ocr_tables)
        if structured_tables:
            result["tables"] = structured_tables
            result["ai_tables_structured"] = True
```

### 2.5. AI улучшение (если есть)

#### Модуль AI-усиления OCR

**Файл:** `ai_ocr_enhancer.py`

**Класс:** `OCRAIEnhancer`

**Функции:**

1. **`enhance_ocr_accuracy()`** — улучшение качества OCR текста
   - Вход: исходный OCR текст, контекст документа
   - Выход: улучшенный текст, список улучшений, оценка уверенности

2. **`enhance_page_by_page()`** — постраничное улучшение

**Промпт для AI:**
```
Улучши OCR распознавание этого энергетического документа.

Особое внимание удели:
- Числовым значениям (потребление энергии, показания счетчиков)
- Единицам измерения (кВт·ч, Гкал, м³, кВт, МВт)
- Названиям предприятий и приборов учета
- Датам и периодам (формат: ДД.ММ.ГГГГ или ГГГГ-ММ-ДД)
- Техническим терминам и аббревиатурам
- Табличным данным (сохрани структуру таблиц)

Исправь типичные OCR ошибки:
- Замены похожих символов (0/O, 1/l/I, 5/S, 8/B)
- Пробелы в числах и единицах измерения
- Разрывы слов и строк
- Неправильное распознавание русских букв
```

**Поддерживаемые AI провайдеры:**
- DeepSeek (через OpenAI API)
- OpenAI (GPT-4, GPT-3.5)
- Anthropic Claude

**Настройки:**
- Temperature: 0.3 (низкая для точных исправлений)
- Max tokens: 4000

**Использование:**
```python
# file_parser.py, строки 1044-1083
if HAS_OCR_AI_ENHANCER:
    ocr_enhancer = get_ocr_ai_enhancer()
    if ocr_enhancer:
        enhancement_result = ocr_enhancer.enhance_ocr_accuracy(
            initial_ocr_text=full_text,
            context="Энергетический документ с данными о потреблении энергии",
        )
```

### 2.6. Формат входных/выходных данных

#### Входные данные

**Поддерживаемые форматы:**
- **PDF:** `.pdf` (текстовые и сканированные)
- **Изображения:** `.jpg`, `.jpeg`, `.png`
- **Excel:** `.xlsx`, `.xlsm`, `.xls` (парсинг, не OCR)
- **Word:** `.docx` (парсинг, не OCR)

**Ограничения:**
- Максимальный размер файла: 50 МБ (настраивается)
- Максимальное количество страниц для OCR: 10 (настраивается)

#### Выходные данные

**Структура результата парсинга PDF:**

```python
{
    "file_path": str,
    "pages": [
        {
            "page_number": int,
            "text": str,
            "char_count": int,
            "table_count": int,
        }
    ],
    "text": str,  # Полный текст документа
    "tables": [
        {
            "page": int,
            "table_index": int,
            "method": str,  # "pdfplumber", "ocr_heuristic", "camelot"
            "rows": List[List[str]],
            "row_count": int,
            "col_count": int,
            "confidence": str,  # "high", "medium", "low"
        }
    ],
    "metadata": {
        "num_pages": int,
        "info": dict,  # Метаданные PDF
    },
    "pdf_type": str,  # "text_based", "image_based", "hybrid", "unknown"
    "processing_strategy": str,  # "text_first", "ocr_first", "hybrid"
    "is_scanned": bool,
    "scanned_confidence": str,  # "high", "medium", "low"
    "ocr_used": bool,
    "ocr_success": bool,
    "ocr_attempted": bool,
    "total_characters": int,
    "total_tables": int,
    "ai_validation": {  # Опционально
        "is_valid": bool,
        "confidence": float,
        "issues": List[str],
        "warnings": List[str],
        "suggestions": List[str],
        "ai_used": bool,
    },
    "ai_tables_structured": bool,  # Опционально
}
```

**Структура результата OCR изображения:**

```python
{
    "text": str,
    "char_count": int,
    "ocr_used": bool,
    "image_size": tuple,  # (width, height)
    "image_mode": str,  # "RGB", "L", etc.
    "error": str,  # Опционально
}
```

### 2.7. Ключевые функции с кратким описанием кода

#### Основные функции OCR

**1. `apply_ocr_to_pdf()` — OCR для PDF файлов**

```python
def apply_ocr_to_pdf(
    file_path: str, 
    languages: str = "rus+eng", 
    batch_id: Optional[str] = None
) -> str:
    """
    Применяет OCR к PDF файлу.
    
    Процесс:
    1. Конвертация PDF в изображения (pdf2image, DPI=300)
    2. Предобработка каждой страницы (enhance_image_for_ocr)
    3. OCR распознавание (pytesseract)
    4. AI-усиление (опционально)
    
    Возвращает: распознанный текст
    """
```

**Расположение:** `file_parser.py`, строки 918-1086

**2. `apply_ocr_to_image()` — OCR для изображений**

```python
def apply_ocr_to_image(
    image_path: str, 
    languages: str = "rus+eng"
) -> Dict[str, Any]:
    """
    Применяет OCR к изображению (JPG, PNG).
    
    Процесс:
    1. Загрузка изображения (PIL)
    2. Предобработка (preprocess_image_for_ocr)
    3. OCR распознавание (pytesseract)
    
    Возвращает: словарь с текстом и метаданными
    """
```

**Расположение:** `file_parser.py`, строки 1137-1186

**3. `preprocess_image_for_ocr()` — предобработка изображения**

```python
def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Предобработка изображения для улучшения качества OCR.
    
    Использует улучшенный модуль image_enhancement если доступен,
    иначе базовую предобработку (контраст + резкость).
    
    Возвращает: обработанное изображение
    """
```

**Расположение:** `file_parser.py`, строки 1100-1134

**4. `parse_pdf_file()` — универсальный парсер PDF**

```python
def parse_pdf_file(
    file_path: str, 
    batch_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Универсальный парсер PDF с автоматическим определением типа.
    
    Процесс:
    1. Классификация типа PDF (текстовый/сканированный)
    2. Выбор стратегии обработки
    3. Извлечение текста/таблиц или применение OCR
    4. AI-валидация и структурирование (опционально)
    
    Возвращает: полный результат парсинга
    """
```

**Расположение:** `file_parser.py`, строки 322-768

#### Утилиты улучшения изображений

**5. `enhance_image_for_ocr()` — комплексное улучшение изображения**

```python
def enhance_image_for_ocr(image: PILImage) -> PILImage:
    """
    Комплексное улучшение отсканированного изображения для OCR.
    
    Порядок обработки:
    1. Выравнивание (deskew)
    2. Нормализация освещения
    3. Удаление шума
    4. Адаптивная бинаризация
    5. Улучшение резкости
    
    Возвращает: улучшенное изображение
    """
```

**Расположение:** `utils/image_enhancement.py`, строки 422-479

**6. `deskew_image()` — выравнивание изображения**

```python
def deskew_image(image: PILImage, angle: Optional[float] = None) -> PILImage:
    """
    Выравнивает изображение (устраняет перекос).
    
    Если угол не указан, определяется автоматически через detect_skew_angle().
    Поворачивает изображение на рассчитанный угол.
    
    Возвращает: выровненное изображение
    """
```

**Расположение:** `utils/image_enhancement.py`, строки 98-126

**7. `adaptive_binarization()` — адаптивная бинаризация**

```python
def adaptive_binarization(
    image: PILImage, 
    method: str = "otsu"
) -> PILImage:
    """
    Адаптивная бинаризация (преобразование в черно-белое).
    
    Методы:
    - "otsu" - метод Оцу (глобальная бинаризация)
    - "adaptive" - адаптивная бинаризация (локальная)
    - "sauvola" - метод Sauvola (опционально, требует scikit-image)
    
    Возвращает: бинаризованное изображение
    """
```

**Расположение:** `utils/image_enhancement.py`, строки 129-181

#### AI-модули

**8. `OCRAIEnhancer.enhance_ocr_accuracy()` — AI-усиление OCR**

```python
def enhance_ocr_accuracy(
    self,
    initial_ocr_text: str,
    image_path: Optional[str] = None,
    context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    AI помогает улучшить качество OCR распознавания.
    
    Исправляет:
    - Типичные OCR ошибки (0/O, 1/l/I)
    - Пробелы в числах
    - Разрывы слов и строк
    - Неправильное распознавание русских букв
    
    Возвращает: словарь с улучшенным текстом и метаданными
    """
```

**Расположение:** `ai_ocr_enhancer.py`, строки 42-108

---

## 3. ТЕКУЩЕЕ СОСТОЯНИЕ

### 3.1. Что уже работает

#### ✅ Реализовано и работает

1. **Базовая OCR функциональность:**
   - ✅ OCR для PDF файлов (через pdf2image + Tesseract)
   - ✅ OCR для изображений (JPG, PNG)
   - ✅ Автоматическое определение необходимости OCR
   - ✅ Поддержка русского и английского языков

2. **Предобработка изображений:**
   - ✅ Выравнивание (deskew) через OpenCV
   - ✅ Адаптивная бинаризация (Otsu, адаптивная)
   - ✅ Удаление шума (медианный фильтр)
   - ✅ Улучшение контраста и резкости
   - ✅ Нормализация освещения

3. **Обработка PDF:**
   - ✅ Парсинг текстовых PDF (pdfplumber, PyPDF2)
   - ✅ Извлечение таблиц из текстовых PDF (pdfplumber)
   - ✅ Автоматическое определение сканированных PDF
   - ✅ Классификация типа PDF (текстовый/изображение)

4. **Извлечение таблиц:**
   - ✅ Извлечение таблиц из текстовых PDF (pdfplumber)
   - ✅ Извлечение таблиц из OCR текста (эвристики)
   - ✅ Опциональное улучшение через Camelot PDF

5. **AI интеграция (опционально):**
   - ✅ AI-усиление OCR текста (DeepSeek, OpenAI, Anthropic)
   - ✅ AI-валидация извлеченных данных
   - ✅ AI-структурирование таблиц

6. **Оптимизация:**
   - ✅ Оптимизация памяти для больших изображений
   - ✅ Ограничение количества страниц для OCR (10 страниц)
   - ✅ Проверка отмены обработки (через batch_id)

7. **Веб-интерфейс:**
   - ✅ Загрузка файлов через веб-интерфейс
   - ✅ Отображение результатов парсинга
   - ✅ Прогресс обработки файлов

### 3.2. Что в разработке

#### 🚧 В процессе разработки

1. **Улучшение качества OCR:**
   - 🚧 Поддержка дополнительных языков (узбекский)
   - 🚧 Улучшение распознавания таблиц из OCR
   - 🚧 Более точное определение структуры документа

2. **Производительность:**
   - 🚧 Асинхронная обработка больших файлов (Celery)
   - 🚧 Пакетная обработка файлов
   - 🚧 Кэширование результатов OCR

3. **Интеграция:**
   - 🚧 Сохранение метаданных OCR в базу данных
   - 🚧 История изменений распознанных данных
   - 🚧 Экспорт результатов OCR в различные форматы

### 3.3. Известные проблемы и ограничения

#### ⚠️ Известные проблемы

1. **Зависимости от внешних утилит:**
   - ⚠️ Требуется установка Tesseract OCR отдельно (не через pip)
   - ⚠️ Требуется установка Poppler для конвертации PDF (не через pip)
   - ⚠️ На Windows пути к утилитам могут не определяться автоматически

2. **Производительность:**
   - ⚠️ OCR обработка медленная для больших файлов (1-5 минут на страницу)
   - ⚠️ Ограничение на 10 страниц для OCR (настраивается, но влияет на время обработки)
   - ⚠️ Высокое потребление памяти для больших изображений (даже с оптимизацией)

3. **Качество OCR:**
   - ⚠️ Низкая точность для плохих сканов (размытые, с шумом)
   - ⚠️ Проблемы с распознаванием рукописного текста (не поддерживается)
   - ⚠️ Сложность с таблицами в OCR тексте (эвристики не всегда точны)

4. **Обработка ошибок:**
   - ⚠️ Нет явных требований к обработке критических ошибок OCR (полный отказ)
   - ⚠️ Нет fallback-стратегий при недоступности OCR-сервиса
   - ⚠️ Ограниченная валидация входных файлов перед OCR

5. **Мультиязычность:**
   - ⚠️ Нет явной поддержки узбекского языка (хотя Tesseract его поддерживает)
   - ⚠️ Нет автоматического определения языка документа

#### 🔴 Критичные ограничения

1. **Максимальный размер файла:** 50 МБ
2. **Максимальное количество страниц для OCR:** 10 страниц (настраивается)
3. **Поддерживаемые языки OCR:** только русский и английский (явно настроено)
4. **Требования к системе:** Windows/Linux с установленными Tesseract и Poppler

### 3.4. Что требует улучшения

#### 🔧 Рекомендации по улучшению (высокий приоритет)

1. **Обработка ошибок:**
   - Добавить обработку критических ошибок OCR (полный отказ)
   - Реализовать fallback-стратегии (резервные методы OCR)
   - Улучшить валидацию входных файлов перед OCR

2. **Мультиязычность:**
   - Добавить поддержку узбекского языка
   - Реализовать автоматическое определение языка документа
   - Поддержка смешанных языков в одном документе

3. **Производительность:**
   - Асинхронная обработка OCR через Celery
   - Пакетная обработка файлов
   - Улучшение оптимизации памяти для больших изображений

4. **Метаданные и трекинг:**
   - Сохранение метаданных OCR-обработки (время, методы, статистика)
   - История изменений распознанных данных
   - Метрики качества OCR (точность, процент ошибок)

5. **Качество OCR:**
   - Улучшение алгоритмов предобработки изображений
   - Более точное извлечение таблиц из OCR текста
   - Поддержка обработки фотографий документов (коррекция углов, освещения)

#### 📋 Рекомендации по улучшению (средний приоритет)

6. **API для внешних OCR:**
   - Интеграция с коммерческими OCR-сервисами (Google Cloud Vision, Azure)
   - Возможность подключения внешних OCR-API

7. **Безопасность:**
   - Шифрование данных во время OCR-обработки
   - Ограничение доступа к OCR-сервису (аутентификация)
   - Автоматическая очистка временных файлов

8. **Экспорт и интеграция:**
   - Экспорт результатов OCR в различные форматы (JSON, CSV, TXT)
   - Интеграция с другими системами через API

---

## Приложение A: Примеры использования

### Пример 1: Простая OCR обработка PDF

```python
from file_parser import apply_ocr_to_pdf

# OCR для PDF файла
text = apply_ocr_to_pdf(
    file_path="document.pdf",
    languages="rus+eng"
)
print(f"Распознано символов: {len(text)}")
```

### Пример 2: Предобработка изображения перед OCR

```python
from PIL import Image
from utils.image_enhancement import enhance_image_for_ocr
import pytesseract

# Загрузка изображения
image = Image.open("scan.jpg")

# Улучшение изображения
enhanced = enhance_image_for_ocr(image)

# OCR распознавание
text = pytesseract.image_to_string(enhanced, lang="rus+eng")
```

### Пример 3: Полный парсинг PDF с OCR

```python
from file_parser import parse_pdf_file

# Парсинг PDF (автоматически определит, нужен ли OCR)
result = parse_pdf_file("document.pdf", batch_id="batch-123")

# Проверка результата
if result["ocr_used"]:
    print(f"OCR применен: {result['total_characters']} символов")
    print(f"Найдено таблиц: {result['total_tables']}")
```

---

## Приложение B: Установка зависимостей

### Windows

```powershell
# 1. Установка Python пакетов
pip install -r requirements.txt

# 2. Установка Tesseract OCR
choco install tesseract
# Или скачать: https://github.com/UB-Mannheim/tesseract/wiki

# 3. Установка Poppler
choco install poppler
# Или скачать: https://github.com/oschwartz10612/poppler-windows/releases/

# 4. Установка языковых пакетов Tesseract (русский, английский)
# Обычно устанавливаются вместе с Tesseract
```

### Linux (Ubuntu/Debian)

```bash
# 1. Установка системных зависимостей
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
sudo apt-get install poppler-utils

# 2. Установка Python пакетов
pip install -r requirements.txt
```

---

**Дата последнего обновления:** 2025-12-01  
**Версия документа:** 1.1

---

## 🆕 Последние обновления (2025-12-01)

### 🧠 Intelligent Router
Автоматический анализ и маршрутизация файлов. Определяет тип документа, ресурса, данных и генерирует routing map.

**Документация:** `docs/INTELLIGENT_ROUTER_IMPLEMENTATION.md`

### 🔧 Переключатель режимов работы
Два режима обработки дубликатов: DEBUG (всегда переобрабатывать) и PRODUCTION (пропускать без изменений).

**Документация:** `docs/SYSTEM_MODE_SWITCH.md`

### 🖼️ Улучшенная обработка изображений
Правильное определение типа документа для JPG/PNG через OCR анализ.

**Документация:** `docs/IMAGE_PROCESSING_IMPROVEMENTS.md`

**Подробности:** См. [PROJECT_UPDATE_2025_12_01.md](PROJECT_UPDATE_2025_12_01.md) и [CHANGELOG.md](CHANGELOG.md)

