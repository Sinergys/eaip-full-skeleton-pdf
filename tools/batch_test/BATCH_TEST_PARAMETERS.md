# ПАРАМЕТРЫ БАТЧ-ТЕСТА OCR МОДУЛЯ

## Конфигурационный файл

Все параметры батч-теста хранятся в: `tools/batch_test/batch_test_config.yml`

---

## ОСНОВНЫЕ ПАРАМЕТРЫ

### 1. Размер батча
```yaml
batch:
  size: 5                    # Количество файлов для обработки
  pause_between_files: 10    # Пауза между файлами (секунды)
```

**Рекомендации:**
- Для быстрого теста: `size: 3-5`
- Для полного теста: `size: 10-20`
- Для production: `size: 50-100`

### 2. Директория с файлами
```yaml
batch:
  test_files_dir: "C:\\AUDIT\\OBJECTS\\Navoiy IES\\INBOX"
  max_file_size_mb: 5.0      # Максимальный размер файла (MB)
  min_file_size_mb: 0.0       # Минимальный размер файла (MB)
```

**Рекомендации:**
- Для быстрого теста: `max_file_size_mb: 1.0`
- Для полного теста: `max_file_size_mb: 5.0`
- Для production: `max_file_size_mb: 50.0`

### 3. DPI для конвертации PDF
```yaml
processing:
  pdf_dpi: 200               # 200 = быстро, 300 = качество
```

**Рекомендации:**
- Для быстрого теста: `pdf_dpi: 200` (ускорение 30-40%)
- Для качественного теста: `pdf_dpi: 300` (лучшее качество)
- Для production: `pdf_dpi: 200` (баланс скорости и качества)

### 4. Предобработка изображений
```yaml
preprocessing:
  use_preprocessing: true
  contrast_factor: 1.5       # +50% контраста
  sharpness_factor: 1.3      # +30% резкости
  normalize_illumination: true
  denoise: true
  binarize: true
```

**Рекомендации:**
- Для плохих сканов: все параметры `true`
- Для хороших сканов: можно отключить `denoise` и `binarize`
- Для быстрого теста: отключить `normalize_illumination`

### 5. Gemini Vision API
```yaml
gemini:
  model: "gemini-2.0-flash"
  timeout_seconds: 600        # 10 минут
  retry_attempts: 3
  backoff_base_seconds: 2
```

**Рекомендации:**
- Для быстрого теста: `timeout_seconds: 300` (5 минут)
- Для больших файлов: `timeout_seconds: 600` (10 минут)
- Для production: `retry_attempts: 3` (стабильность)

### 6. Пороги confidence
```yaml
validation:
  text_confidence_threshold: 0.30      # 30%
  table_confidence_threshold: 0.70     # 70%
  numbers_confidence_threshold: 0.60   # 60%
  dates_confidence_threshold: 0.80     # 80%
```

**Рекомендации:**
- Для строгой валидации: увеличить пороги на 0.10
- Для мягкой валидации: уменьшить пороги на 0.10
- Для production: использовать текущие значения

---

## ПРИМЕРЫ КОНФИГУРАЦИЙ

### Быстрый тест (3-5 файлов, < 1 MB)
```yaml
batch:
  size: 3
  max_file_size_mb: 1.0
  pause_between_files: 5

processing:
  pdf_dpi: 200
  use_preprocessing: true

preprocessing:
  normalize_illumination: false  # Отключить для ускорения
  denoise: true
  binarize: true
```

### Полный тест (10-20 файлов, < 5 MB)
```yaml
batch:
  size: 10
  max_file_size_mb: 5.0
  pause_between_files: 10

processing:
  pdf_dpi: 200
  use_preprocessing: true

preprocessing:
  normalize_illumination: true
  denoise: true
  binarize: true
```

### Production тест (50-100 файлов, любые размеры)
```yaml
batch:
  size: 50
  max_file_size_mb: 50.0
  pause_between_files: 5

processing:
  pdf_dpi: 200
  use_preprocessing: true

parallel:
  enabled: true
  max_workers: 3
```

---

## ИСПОЛЬЗОВАНИЕ

### Запуск с конфигурацией по умолчанию
```bash
python tools/batch_test/step4_batch_test.py
```

### Запуск с кастомной конфигурацией
```python
# В скрипте изменить путь к конфигу:
config_path = "tools/batch_test/custom_config.yml"
```

### Изменение параметров в коде
```python
# В step4_batch_test.py:
BATCH_SIZE = 10
PAUSE_BETWEEN_FILES = 5
PDF_DPI = 200
USE_PREPROCESSING = True
```

---

## МЕТРИКИ ДЛЯ ОТСЛЕЖИВАНИЯ

### Производительность
- Время обработки файла (сек)
- Время обработки страницы (сек)
- Время извлечения страниц (сек)
- Общее время батча (сек)

### Качество
- Confidence scores (среднее, минимум, максимум)
- Low confidence страниц (%)
- Ошибки парсинга JSON (%)
- Потеря таблиц (%)

### Надежность
- Успешных файлов (%)
- Ошибок обработки (%)
- Gemini retries (количество)
- Таймауты (количество)

---

## РЕКОМЕНДАЦИИ

1. **Начните с быстрого теста** (3-5 файлов) для проверки работоспособности
2. **Используйте полный тест** (10-20 файлов) для оценки качества
3. **Production тест** (50-100 файлов) только после подтверждения стабильности
4. **Мониторьте метрики** для выявления проблем
5. **Сохраняйте промежуточные результаты** для анализа

---

**Последнее обновление:** 2025-11-29

