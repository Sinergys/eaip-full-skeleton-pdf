# Task 6: Readiness-проверка для Word-отчёта

## Обзор

Реализована система проверки готовности данных для генерации Word-отчёта по ПКМ-690 с использованием требований из `pkm690_sections` и возможностью fallback на эталонные таблицы.

## Созданные файлы

1. **`eaip_full_skeleton/services/ingest/utils/word_readiness_validator.py`**
   - Функция `validate_word_report_readiness()` - основная проверка готовности
   - Функция `validate_section_data()` - проверка данных для конкретного раздела
   - Функция `get_missing_data_summary()` - формирование текстовой сводки
   - Проверка наличия эталонных таблиц для fallback

2. **Обновлён `eaip_full_skeleton/services/ingest/utils/word_report_generator.py`**
   - Добавлена проверка готовности перед генерацией
   - Блокировка генерации при отсутствии критических данных
   - Логирование причин блокировки
   - Параметр `skip_readiness_check` для обхода проверки (при необходимости)

3. **`scripts/test_word_readiness.py`**
   - Тестовый скрипт для проверки валидации

## Функциональность

### Основная проверка

```python
from eaip_full_skeleton.services.ingest.utils.word_readiness_validator import validate_word_report_readiness
from eaip_full_skeleton.services.ingest.domain.report_data import ReportData

# Создаем ReportData
report_data = ReportData.from_raw_data(
    aggregated_data=aggregated_data,
    equipment_data=equipment_data,
    enterprise_data=enterprise_data
)

# Проверяем готовность
readiness = validate_word_report_readiness(report_data)

if not readiness["ready"]:
    # Блокируем генерацию или используем fallback
    pass
```

### Результат проверки

```python
{
    "ready": bool,  # Можно ли генерировать отчёт
    "completeness_score": float,  # 0.0-1.0
    "sections_status": Dict[int, Dict],  # Статус каждого раздела
    "missing_sections": List[int],  # Разделы, которые нельзя сгенерировать
    "critical_missing_sections": List[int],  # Критические недостающие разделы
    "warnings": List[str],  # Предупреждения
    "errors": List[str],  # Ошибки
    "reference_tables_available": bool,  # Есть ли эталонные таблицы
    "ready_sections_count": int,
    "total_sections_count": int,
}
```

### Проверка по разделам

Для каждого раздела ПКМ-690 проверяется:
- Наличие обязательных КПИ (`required_kpis`)
- Наличие обязательных таблиц (`required_tables`)
- Возможность fallback на эталонные таблицы (для разделов с `allow_empty=True`)

### Блокировка генерации

Генерация блокируется, если:
- Отсутствуют данные для критических разделов (разделы без `allow_empty=True`)
- Нет возможности использовать fallback на эталонные таблицы

Генерация продолжается с предупреждениями, если:
- Отсутствуют данные для некритических разделов
- Есть возможность использовать fallback на эталонные таблицы

## Интеграция в Word-генератор

Проверка автоматически выполняется в `WordReportGenerator.generate_report()`:

```python
generator = WordReportGenerator()
doc = generator.generate_report(
    enterprise_data=enterprise_data,
    aggregated_data=aggregated_data,
    # ... другие параметры
    skip_readiness_check=False  # По умолчанию проверка включена
)
```

Если данные не готовы:
- Выбрасывается `ValueError` с описанием недостающих данных
- Логируется подробная информация о проблемах
- Генерация блокируется для критических случаев

## Fallback на эталонные таблицы

Для разделов, которые могут использовать эталонные таблицы (например, "Мероприятия"):
- Проверяется наличие эталонных таблиц через `reference_tables_loader`
- Если таблицы доступны, раздел считается готовым к генерации
- Генерируется предупреждение о использовании эталонных данных

## Примеры использования

### Проверка перед генерацией

```python
from eaip_full_skeleton.services.ingest.utils.word_readiness_validator import (
    validate_word_report_readiness,
    get_missing_data_summary
)

readiness = validate_word_report_readiness(report_data)

if not readiness["ready"]:
    summary = get_missing_data_summary(readiness)
    print(f"Данные не готовы:\n{summary}")
    # Принять решение: блокировать или использовать fallback
```

### Проверка конкретного раздела

```python
from eaip_full_skeleton.services.ingest.utils.word_readiness_validator import validate_section_data

is_valid, missing_kpis, warnings = validate_section_data(3, report_data)  # Раздел 3

if not is_valid:
    print(f"Недостающие КПИ: {missing_kpis}")
```

## Следующие шаги

1. Расширить проверку fallback для других типов разделов
2. Добавить проверку качества данных (не только наличие)
3. Интегрировать с API endpoints для возврата структурированных ошибок
4. Добавить метрики готовности в дашборд

