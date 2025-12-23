# План экологических мероприятий

## Обзор

План экологических мероприятий извлекается из экологических отчётов (ПДВ, ПДС и других документов) и используется для формирования рекомендаций по снижению воздействия на окружающую среду.

## Структура данных

### JSON структура

```json
{
  "source": "path/to/document.pdf",
  "generated_at": "2025-01-15T10:30:00Z",
  "measures": [
    {
      "order": 1,
      "name": "Установка пылеулавливающего оборудования",
      "description": "Установка циклонов для очистки выбросов от пыли",
      "type": "emission_reduction",
      "deadline": "2025-12-31",
      "cost": 5000000.0,
      "responsible": "Главный инженер",
      "status": "planned"
    },
    {
      "order": 2,
      "name": "Модернизация очистных сооружений",
      "description": "Реконструкция биологических очистных сооружений",
      "type": "discharge_reduction",
      "deadline": "2026-06-30",
      "cost": 15000000.0,
      "responsible": "Начальник цеха",
      "status": "planned"
    }
  ],
  "summary": {
    "total_measures": 2,
    "by_type": {
      "emission_reduction": 1,
      "discharge_reduction": 1
    }
  }
}
```

## Типы мероприятий

Парсер автоматически классифицирует мероприятия по следующим типам:

- **emission_reduction** - Снижение выбросов (очистка выбросов, фильтры, пылеулавливание)
- **discharge_reduction** - Снижение сбросов (очистка сточных вод, очистные сооружения)
- **monitoring** - Мониторинг и контроль (измерения, учёт, наблюдение)
- **equipment** - Оборудование (модернизация, замена, установка)
- **management** - Управление (организационные меры, документация)
- **other** - Прочие мероприятия

## Использование парсера

### Базовое использование

```python
from eaip_full_skeleton.services.ingest.utils.environmental_measures_parser import (
    parse_environmental_measures,
    is_environmental_document,
)

# Проверка типа документа
if is_environmental_document("ПДВ_2024.pdf"):
    # Извлечение текста из документа (например, через OCR)
    text = extract_text_from_pdf("ПДВ_2024.pdf")
    
    # Парсинг мероприятий
    measures_data = parse_environmental_measures(
        text=text,
        source_file="ПДВ_2024.pdf"
    )
    
    print(f"Найдено мероприятий: {measures_data['summary']['total_measures']}")
    for measure in measures_data['measures']:
        print(f"- {measure['name']} ({measure['type']})")
```

### Интеграция в пайплайн обработки файлов

```python
from eaip_full_skeleton.services.ingest.utils.environmental_measures_parser import (
    parse_environmental_measures,
    is_environmental_document,
    write_environmental_measures_json,
)
from eaip_full_skeleton.services.ingest import database

# В функции обработки файла
def process_environmental_document(batch_id: str, file_path: str, text: str):
    if is_environmental_document(file_path):
        # Парсинг мероприятий
        measures_data = parse_environmental_measures(
            text=text,
            source_file=file_path
        )
        
        # Сохранение в JSON
        json_path = write_environmental_measures_json(
            batch_id=batch_id,
            measures_data=measures_data,
            destination_dir="data/aggregated"
        )
        
        # Сохранение в БД
        enterprise_id = get_enterprise_id_from_batch(batch_id)
        if enterprise_id:
            database.save_environmental_measures(
                enterprise_id=enterprise_id,
                measures_data=measures_data
            )
        
        return measures_data
    return None
```

## Формат документов

Парсер ищет разделы с мероприятиями по следующим ключевым словам:

- "план мероприятий"
- "мероприятия"
- "рекомендации"
- "предложения"
- "меры"
- "экологические мероприятия"
- "мероприятия по снижению"
- "план работ"
- "программа мероприятий"

### Поддерживаемые форматы списков

1. **Нумерованный список:**
   ```
   1. Установка пылеулавливающего оборудования
   2. Модернизация очистных сооружений
   ```

2. **Маркированный список:**
   ```
   - Установка пылеулавливающего оборудования
   - Модернизация очистных сооружений
   ```

3. **Обычный текст:**
   ```
   Установка пылеулавливающего оборудования. 
   Модернизация очистных сооружений.
   ```

## Извлечение дополнительной информации

Парсер автоматически пытается извлечь:

- **Сроки выполнения** - из текста вида "срок до 31.12.2025" или "2025 год"
- **Стоимость** - из текста вида "стоимость 5 млн сум" или "5000000 сум"
- **Ответственный** - из текста вида "ответственный: Главный инженер"

## Использование в энергопаспорте

План экологических мероприятий может быть использован для:

1. **Заполнения раздела "Экологические мероприятия"** в энергопаспорте
2. **Формирования рекомендаций** по снижению воздействия на окружающую среду
3. **Расчёта экономической эффективности** мероприятий
4. **Планирования работ** по улучшению экологической ситуации

## Пример интеграции с генератором Excel

```python
from tools.pkm690_excel_generator import PKM690ExcelGenerator
from eaip_full_skeleton.services.ingest import database

# Получение мероприятий из БД
enterprise_id = 1
measures_data = database.get_environmental_measures(enterprise_id)

if measures_data:
    # Создание генератора
    generator = PKM690ExcelGenerator()
    
    # Добавление мероприятий в Excel
    for measure in measures_data['measures']:
        # Добавление в лист "Экологические мероприятия"
        # ...
```

## Ограничения

1. **Качество извлечения** зависит от качества исходного текста (OCR может давать ошибки)
2. **Структура документов** может различаться, парсер работает с наиболее распространёнными форматами
3. **Извлечение стоимости и сроков** работает только если они указаны в тексте в распознаваемом формате

## Улучшение точности

Для повышения точности извлечения рекомендуется:

1. **Использовать AI-парсер** для более точного извлечения структурированных данных
2. **Ручная проверка** извлечённых мероприятий
3. **Обучение модели** на примерах документов конкретного предприятия

## Связанные документы

- `docs/ENVIRONMENTAL_NORMATIVES.md` - экологические нормативы
- `eaip_full_skeleton/services/ingest/utils/environmental_measures_parser.py` - код парсера
- `eaip_full_skeleton/services/ingest/database.py` - функции работы с БД

