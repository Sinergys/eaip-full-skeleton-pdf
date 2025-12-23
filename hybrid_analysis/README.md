# 🗺️ ПРОЕКТ "АТЛАС" - Гибридный анализ шаблонов энергетического паспорта

## 📋 Описание проекта

АТЛАС - это интеллектуальная система для автоматического анализа и заполнения шаблонов энергетических паспортов, объединяющая технический анализ, семантическое понимание, машинное обучение и сравнительный анализ.

## 🏗️ Архитектура

```
hybrid_analysis/
├── technical/          # Этап 1: Технический анализ
│   ├── cell_coordinates.json
│   ├── formulas_map.json
│   └── data_types.json
├── semantic/           # Этап 2: Семантический анализ
│   ├── cell_purpose.json
│   └── intelligent_mapping.json
├── ml/                 # Этап 3: Статистический анализ
│   ├── patterns_model.pkl
│   └── format_predictions.json
├── comparison/         # Этап 4: Сравнительный анализ
│   ├── template_differences.json
│   └── adapters.json
├── integrated_system/  # Этап 5: Интеграция
│   ├── universal_filler.py  # Универсальная система заполнения
│   ├── validator.py         # Валидация результатов
│   ├── run_integration.py   # Пайплайн полного цикла
│   └── README.md            # Документация
└── documentation/      # Документация
    └── system_docs.md
```

## 🚀 Этапы реализации

### Этап 1: Технический анализ (Python/Excel)
- ✅ Структурный парсинг шаблонов
- ✅ Анализ формул и ссылок
- ✅ Определение типов данных

### Этап 2: Семантический анализ (ИИ/LLM)
- ✅ Понимание бизнес-смысла
- ✅ Генерация семантического маппинга

### Этап 3: Статистический анализ (ML)
- ✅ Обучение на существующих данных
- ✅ Предсказание форматов

### Этап 4: Сравнительный анализ (Rule-based)
- ✅ Сопоставление шаблонов
- ✅ Генерация адаптеров

### Этап 5: Интеграция и валидация
- ✅ Универсальная система заполнения
- ✅ Автоматическая валидация

## 📦 Использование

```python
from hybrid_analysis.integrated_system.run_integration import run_integration_pipeline

results = run_integration_pipeline(
    template_path="templates/pcm690/new_energy_passport.xlsx",
    data_path="data/aggregated/aggregated_full_resources_2022_2024.json",
    output_dir="output",
    semantic_mapping_path="hybrid_analysis/semantic/semantic_mapping.json"
)
```

Или используйте универсальный заполнитель напрямую:

```python
from hybrid_analysis.integrated_system.universal_filler import UniversalFiller

filler = UniversalFiller(
    template_path="templates/pcm690/new_energy_passport.xlsx",
    data_path="data/aggregated/aggregated_full_resources_2022_2024.json",
    semantic_mapping_path="hybrid_analysis/semantic/semantic_mapping.json"
)

filler.load_all_data()
results = filler.fill()
filler.save("output/filled_template.xlsx")
```

## 🔧 Технологии

- **Python 3.8+**
- **openpyxl** - работа с Excel
- **pandas** - обработка данных
- **scikit-learn** - машинное обучение
- **LLM API** - семантический анализ (опционально)

## 📝 Лицензия

Внутренний проект EAIP

