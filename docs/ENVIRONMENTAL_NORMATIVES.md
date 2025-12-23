# Экологические нормативы

## Обзор

Экологические нормативы используются для оценки соответствия предприятия требованиям экологического законодательства. В системе EAIP реализована поддержка следующих типов нормативов:

1. **ПДВ (Предельно допустимые выбросы)** - нормативы выбросов загрязняющих веществ в атмосферный воздух
2. **ПДС (Предельно допустимые сбросы)** - нормативы сбросов загрязняющих веществ в водные объекты
3. **Категории опасности предприятий** - классификация предприятий по уровню экологической опасности

## Структура данных

### В коде (PKM690ExcelGenerator)

Экологические нормативы хранятся в структуре `self.normatives["environmental"]`:

```python
"environmental": {
    # Предельно допустимые выбросы (ПДВ) в атмосферу
    "emissions": {
        "co": {"max_concentration": 3.0, "unit": "мг/м³"},  # Оксид углерода
        "nox": {"max_concentration": 0.4, "unit": "мг/м³"},  # Оксиды азота
        "so2": {"max_concentration": 0.5, "unit": "мг/м³"},  # Диоксид серы
        "dust": {"max_concentration": 0.5, "unit": "мг/м³"},  # Пыль
        "pm10": {"max_concentration": 0.06, "unit": "мг/м³"},  # PM10
        "pm2_5": {"max_concentration": 0.035, "unit": "мг/м³"},  # PM2.5
    },
    # Предельно допустимые сбросы (ПДС) в водные объекты
    "discharges": {
        "suspended_solids": {"max_concentration": 0.25, "unit": "мг/л"},  # Взвешенные вещества
        "bod5": {"max_concentration": 3.0, "unit": "мг/л"},  # БПК5
        "cod": {"max_concentration": 30.0, "unit": "мг/л"},  # ХПК
        "ammonium": {"max_concentration": 0.5, "unit": "мг/л"},  # Аммоний
        "nitrates": {"max_concentration": 40.0, "unit": "мг/л"},  # Нитраты
        "phosphates": {"max_concentration": 0.2, "unit": "мг/л"},  # Фосфаты
    },
    # Категории опасности предприятий
    "hazard_categories": {
        "category_1": {"description": "Чрезвычайно опасные", "criteria": "ПДВ > 1000 т/год"},
        "category_2": {"description": "Высокоопасные", "criteria": "ПДВ 100-1000 т/год"},
        "category_3": {"description": "Умеренно опасные", "criteria": "ПДВ 10-100 т/год"},
        "category_4": {"description": "Малоопасные", "criteria": "ПДВ < 10 т/год"},
    },
}
```

### В базе данных

Экологические нормативы хранятся в таблицах:

- `normative_documents` - нормативные документы (ПДВ, ПДС)
- `normative_rules` - правила/нормативы, извлечённые из документов
- `normative_references` - связи правил с полями энергопаспорта

## Функции работы с нормативами

### Получение нормативов из БД

```python
from eaip_full_skeleton.services.ingest import database

# Получить все экологические нормативы
normatives = database.get_environmental_normatives()
```

### Создание норматива в БД

```python
# Создать норматив ПДВ для CO
database.create_environmental_normative(
    document_id=1,
    substance_name="CO",
    norm_type="emission",
    max_concentration=3.0,
    unit="мг/м³",
    description="ПДВ для оксида углерода"
)

# Создать норматив ПДС для взвешенных веществ
database.create_environmental_normative(
    document_id=1,
    substance_name="suspended_solids",
    norm_type="discharge",
    max_concentration=0.25,
    unit="мг/л",
    description="ПДС для взвешенных веществ"
)
```

## Источники нормативов

Экологические нормативы могут быть получены из:

1. **Нормативных документов ПДВ/ПДС** - загружаются в систему и обрабатываются AI для извлечения нормативов
2. **Государственных нормативов** - стандартные значения по законодательству Узбекистана
3. **Ручной ввод** - администратор может вручную добавить нормативы через API

## Использование в энергопаспорте

Экологические нормативы используются для:

1. **Сравнения фактических выбросов с нормативами** - определение превышений ПДВ/ПДС
2. **Определения категории опасности предприятия** - на основе объемов выбросов
3. **Формирования рекомендаций** - мероприятия по снижению выбросов при превышении нормативов
4. **Заполнения разделов энергопаспорта** - экологические показатели и соответствие нормативам

## Примеры использования

### Проверка соответствия ПДВ

```python
# Фактический выброс CO
actual_co_emission = 2.5  # мг/м³

# Получить норматив
normatives = database.get_environmental_normatives()
co_limit = normatives["emissions"]["co"]["max_concentration"]  # 3.0 мг/м³

# Проверка
if actual_co_emission <= co_limit:
    print("✅ Соответствует ПДВ")
else:
    print(f"❌ Превышение ПДВ на {actual_co_emission - co_limit:.2f} мг/м³")
```

### Определение категории опасности

```python
# Годовой объем выбросов
annual_emissions = 500  # т/год

# Определить категорию
if annual_emissions > 1000:
    category = "category_1"  # Чрезвычайно опасные
elif annual_emissions >= 100:
    category = "category_2"  # Высокоопасные
elif annual_emissions >= 10:
    category = "category_3"  # Умеренно опасные
else:
    category = "category_4"  # Малоопасные

normatives = database.get_environmental_normatives()
category_info = normatives["hazard_categories"][category]
print(f"Категория: {category_info['description']}")
```

## Обновление нормативов

Нормативы могут быть обновлены:

1. **Через загрузку нормативных документов** - система автоматически извлечет нормативы из ПДВ/ПДС
2. **Через API** - администратор может обновить нормативы программно
3. **Вручную в БД** - прямое редактирование таблиц (не рекомендуется)

## Связанные документы

- `docs/PCM690_TEMPLATE_MAPPING.md` - маппинг полей энергопаспорта
- `eaip_full_skeleton/services/ingest/database.py` - функции работы с БД
- `tools/pkm690_excel_generator.py` - генератор Excel с нормативами

