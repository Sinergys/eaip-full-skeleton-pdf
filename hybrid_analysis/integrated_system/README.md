# Этап 5: Интеграция и валидация

Универсальная система заполнения шаблонов энергетических паспортов с интеллектуальным анализом и валидацией.

## 🎯 Возможности

- ✅ **Универсальное заполнение** - автоматическое заполнение любых шаблонов
- ✅ **Интеграция всех анализов** - использование технического, семантического, ML и сравнительного анализа
- ✅ **Автоматическая валидация** - проверка корректности заполнения
- ✅ **Интеллектуальный маппинг** - семантическое сопоставление данных с ячейками
- ✅ **Поддержка адаптеров** - работа с разными форматами шаблонов

## 📦 Компоненты

### 1. UniversalFiller (`universal_filler.py`)

Универсальная система заполнения шаблонов.

```python
from hybrid_analysis.integrated_system.universal_filler import UniversalFiller

filler = UniversalFiller(
    template_path="templates/pcm690/new_energy_passport.xlsx",
    data_path="data/aggregated/aggregated_full_resources_2022_2024.json",
    structural_analysis_path="hybrid_analysis/technical/cell_coordinates.json",
    semantic_mapping_path="hybrid_analysis/semantic/semantic_mapping.json",
    ml_patterns_path="hybrid_analysis/ml/filling_patterns.json"
)

filler.load_all_data()
results = filler.fill()
filler.save("output/filled_template.xlsx")
```

### 2. FillValidator (`validator.py`)

Валидация результатов заполнения.

```python
from hybrid_analysis.integrated_system.validator import FillValidator

validator = FillValidator(
    filled_template_path="output/filled_template.xlsx",
    original_template_path="templates/pcm690/new_energy_passport.xlsx",
    semantic_mapping_path="hybrid_analysis/semantic/semantic_mapping.json"
)

validator.load_data()
report = validator.validate()
validator.save("output/validation_report.json")
```

### 3. IntegrationPipeline (`run_integration.py`)

Полный цикл интеграции и валидации.

```python
from hybrid_analysis.integrated_system.run_integration import run_integration_pipeline

results = run_integration_pipeline(
    template_path="templates/pcm690/new_energy_passport.xlsx",
    data_path="data/aggregated/aggregated_full_resources_2022_2024.json",
    output_dir="output",
    structural_analysis_path="hybrid_analysis/technical/cell_coordinates.json",
    semantic_mapping_path="hybrid_analysis/semantic/semantic_mapping.json"
)
```

## 🚀 Использование

### Командная строка

#### 1. Заполнение шаблона

```bash
python hybrid_analysis/integrated_system/universal_filler.py \
  --template templates/pcm690/new_energy_passport.xlsx \
  --data data/aggregated/aggregated_full_resources_2022_2024.json \
  --output output/filled_template.xlsx \
  --structural hybrid_analysis/technical/cell_coordinates.json \
  --semantic hybrid_analysis/semantic/semantic_mapping.json
```

#### 2. Валидация заполнения

```bash
python hybrid_analysis/integrated_system/validator.py \
  --filled output/filled_template.xlsx \
  --output output/validation_report.json \
  --original templates/pcm690/new_energy_passport.xlsx \
  --semantic hybrid_analysis/semantic/semantic_mapping.json
```

#### 3. Полный цикл интеграции

```bash
python hybrid_analysis/integrated_system/run_integration.py \
  --template templates/pcm690/new_energy_passport.xlsx \
  --data data/aggregated/aggregated_full_resources_2022_2024.json \
  --output output \
  --structural hybrid_analysis/technical/cell_coordinates.json \
  --semantic hybrid_analysis/semantic/semantic_mapping.json \
  --ml hybrid_analysis/ml/filling_patterns.json
```

## 📊 Результаты

### Структура результатов

```
output/
├── filled_template.xlsx          # Заполненный шаблон
├── filled_template.fill_report.json  # Отчет о заполнении
├── validation_report.json        # Отчет валидации
└── integration_summary.json      # Итоговая сводка
```

### Отчет о заполнении

```json
{
  "template_path": "templates/pcm690/new_energy_passport.xlsx",
  "data_path": "data/aggregated/aggregated_full_resources_2022_2024.json",
  "fill_date": "2025-11-15T...",
  "results": {
    "filled_cells": 150,
    "skipped_cells": 50,
    "errors": [],
    "warnings": [...],
    "filled_addresses": [...]
  }
}
```

### Отчет валидации

```json
{
  "validation_date": "2025-11-15T...",
  "status": "good",
  "score": 0.85,
  "validations": {
    "structural": {...},
    "filling": {...},
    "formats": {...},
    "semantic": {...}
  },
  "issues": [],
  "warnings": [...]
}
```

## 🔧 Интеграция с предыдущими этапами

### Этап 1: Технический анализ

Используется для:
- Определения структуры шаблона
- Поиска ячеек для заполнения
- Анализа типов данных

### Этап 2: Семантический анализ

Используется для:
- Интеллектуального маппинга данных
- Сопоставления ячеек с данными
- Определения уверенности заполнения

### Этап 3: ML анализ

Используется для:
- Предсказания форматов данных
- Определения паттернов заполнения
- Автоматического форматирования

### Этап 4: Сравнительный анализ

Используется для:
- Применения адаптеров между форматами
- Конвертации между шаблонами
- Маппинга ячеек между структурами

## 📝 Примеры

### Пример 1: Простое заполнение

```python
from pathlib import Path
from hybrid_analysis.integrated_system.universal_filler import fill_template

results = fill_template(
    template_path=Path("templates/pcm690/new_energy_passport.xlsx"),
    data_path=Path("data/aggregated/aggregated_full_resources_2022_2024.json"),
    output_path=Path("output/filled.xlsx")
)

print(f"Заполнено ячеек: {results['filled_cells']}")
```

### Пример 2: Заполнение с семантическим маппингом

```python
from hybrid_analysis.integrated_system.universal_filler import UniversalFiller

filler = UniversalFiller(
    template_path="templates/pcm690/new_energy_passport.xlsx",
    data_path="data/aggregated/aggregated_full_resources_2022_2024.json",
    semantic_mapping_path="hybrid_analysis/semantic/semantic_mapping.json"
)

filler.load_all_data()
results = filler.fill()

# Статистика заполнения
stats = filler.get_fill_statistics()
print(f"Успешность заполнения: {stats['success_rate']:.1f}%")
```

### Пример 3: Полный цикл с валидацией

```python
from hybrid_analysis.integrated_system.run_integration import run_integration_pipeline

results = run_integration_pipeline(
    template_path="templates/pcm690/new_energy_passport.xlsx",
    data_path="data/aggregated/aggregated_full_resources_2022_2024.json",
    output_dir="output",
    semantic_mapping_path="hybrid_analysis/semantic/semantic_mapping.json"
)

# Проверка готовности
if results["overall_summary"]["ready_for_use"]:
    print("✅ Шаблон готов к использованию!")
else:
    print("⚠️ Требуется проверка")
```

## 🐛 Отладка

### Проблемы с заполнением

1. **Низкий процент заполнения**
   - Проверьте наличие семантического маппинга
   - Убедитесь, что данные соответствуют ожидаемому формату
   - Проверьте уверенность маппинга (confidence)

2. **Ошибки валидации**
   - Проверьте формат данных в заполненных ячейках
   - Убедитесь в корректности единиц измерения
   - Проверьте структуру шаблона

### Логирование

Все модули выводят подробную информацию о процессе:
- Заполнение ячеек
- Пропущенные ячейки
- Ошибки и предупреждения

## 📚 Дополнительная документация

- [Технический анализ](../technical/README.md)
- [Семантический анализ](../semantic/README.md)
- [ML анализ](../ml/README.md)
- [Сравнительный анализ](../comparison/README.md)

## 🔄 Следующие шаги

1. Улучшение семантического маппинга
2. Расширение ML предсказаний
3. Добавление поддержки новых типов данных
4. Интеграция с другими системами

## 📝 Лицензия

Внутренний проект EAIP

