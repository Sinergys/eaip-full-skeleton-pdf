# 📊 Извлечение и нормализация таблиц из образцового отчёта

**Дата:** 2025-01-15  
**Статус:** ✅ Завершено  
**Версия:** 1.0

---

## 📋 Резюме

Создан модуль для парсинга и нормализации таблиц из образцового Word-отчёта "МЕТИН ИРОДА ОТЧЕТ 1107.docx". Таблицы приведены к машинно-удобному виду для использования как эталон и источник данных.

---

## ✅ Выполненные задачи

### 1. Модуль парсинга таблиц ✅

**Создан:** `scripts/extract_reference_tables.py`

**Функциональность:**
- Извлечение всех таблиц из Word-документа (29 таблиц)
- Классификация таблиц по типам:
  - `equipment` - оборудование
  - `specific_consumption` - удельный расход
  - `consumption_structure` - структура потребления
  - `losses` - потери
  - `measures` - мероприятия
  - `other` - прочие
- Нормализация данных для каждого типа таблиц
- Сохранение в JSON-файлы

**Результаты:**
- `data/reference_analysis/tables/tables_equipment.json` (9 таблиц, 266 записей)
- `data/reference_analysis/tables/tables_specific_consumption.json` (1 таблица, 4 записи)
- `data/reference_analysis/tables/tables_consumption_structure.json` (0 таблиц)
- `data/reference_analysis/tables/tables_losses.json` (2 таблицы, 37 записей)
- `data/reference_analysis/tables/tables_measures.json` (3 таблицы, 3 записи)
- `data/reference_analysis/tables/tables_other.json` (14 таблиц, 14 записей)

---

### 2. Классификация и нормализация ✅

**Реализовано для каждого типа:**

1. **Equipment (Оборудование)**
   - Поля: `name`, `section`, `power_kw`, `count`, `vfd`, `group`
   - Автоматическое определение колонок по ключевым словам

2. **Measures (Мероприятия)**
   - Поля: `id`, `name`, `essence`, `capex`, `saving_kwh`, `saving_money`, `payback_years`, `priority`
   - Поддержка двух форматов:
     - Стандартный формат с колонками
     - Формат "Показатель" / "Значение" (key-value)
   - Сохранение сырых данных в `raw_data` для ручной обработки

3. **Specific Consumption (Удельный расход)**
   - Поля: `product`, `period`, `energy_type`, `value`, `unit`

4. **Consumption Structure (Структура потребления)**
   - Поля: `period`, `technological`, `own_needs`, `production`, `household`, `total`

5. **Losses (Потери)**
   - Поля: `transformer`, `power_kva`, `loss_active`, `loss_reactive`, `percentage`

---

### 3. Особый фокус: таблицы «Мероприятия» ✅

**Создан маппинг-конфиг:** `data/reference_analysis/tables/measures_mapping.json`

**Структура маппинга:**
- Описание каждого поля (id, name, essence, capex, saving_kwh, saving_money, payback_years, priority)
- Возможные названия колонок для каждого поля
- Конфигурация для Excel-листа "Мероприятия":
  - Номера колонок (A-H)
  - Ширина колонок
  - Строка заголовков
- Конфигурация для Word-раздела:
  - Название раздела
  - Стиль таблицы
  - Поля для итоговой сводки

**Использование:**
- Для генерации Excel-листа "Мероприятия"
- Для генерации текстового раздела "Мероприятия" в Word-отчёте
- Для будущего доменного объекта `ReportData.meropriyatiya`

---

### 4. API-доступ к таблицам ✅

**Создан модуль:** `eaip_full_skeleton/services/ingest/utils/reference_tables_loader.py`

**Функции:**

1. **`load_reference_table(table_type: str)`**
   - Загружает все таблицы указанного типа
   - Возвращает список нормализованных таблиц

2. **`load_single_table(table_type: str, table_index: int)`**
   - Загружает одну конкретную таблицу по индексу

3. **`get_all_measures()`**
   - Получает все мероприятия из всех таблиц типа "measures"

4. **`get_equipment_by_section(section: str = None)`**
   - Получает оборудование, опционально фильтруя по разделу/цеху

5. **`get_specific_consumption_by_period(period: str = None)`**
   - Получает данные удельного расхода, опционально фильтруя по периоду

6. **`get_losses_data()`**
   - Получает все данные о потерях

7. **`get_consumption_structure_by_period(period: str = None)`**
   - Получает структуру потребления, опционально фильтруя по периоду

8. **`get_table_statistics()`**
   - Получает статистику по всем таблицам

9. **`get_measures_mapping()`**
   - Возвращает маппинг колонок таблицы мероприятий

---

### 5. Не трогать оригинальный DOCX ✅

- Весь парсинг только чтение
- Никаких изменений/удалений таблиц, графиков, рисунков
- Все изменения только в производных JSON/структурах

---

## 📁 Структура файлов

```
data/reference_analysis/tables/
├── tables_equipment.json              # 9 таблиц, 266 записей
├── tables_specific_consumption.json    # 1 таблица, 4 записи
├── tables_consumption_structure.json  # 0 таблиц
├── tables_losses.json                 # 2 таблицы, 37 записей
├── tables_measures.json               # 3 таблицы, 3 записи
├── tables_other.json                  # 14 таблиц, 14 записей
└── measures_mapping.json             # Маппинг для мероприятий

scripts/
├── extract_reference_tables.py        # Скрипт извлечения таблиц
└── test_reference_tables_loader.py   # Тест API

eaip_full_skeleton/services/ingest/utils/
└── reference_tables_loader.py        # API для загрузки таблиц
```

---

## 🎯 Критерии готовности

### ✅ Все критерии выполнены

1. **Нормализованные JSON для основных типов таблиц** ✅
   - Все типы таблиц сохранены в `data/reference_analysis/tables/`
   - Особое внимание уделено таблицам "Мероприятия"

2. **Удобные функции load_reference_table(...)** ✅
   - API-модуль создан и протестирован
   - Функции пригодны для тестов и логики Excel/Word

3. **Таблицы «Мероприятия» пригодны для генерации** ✅
   - Структура нормализована
   - Маппинг-конфиг создан
   - Готовы для использования в Excel и Word

4. **Оригинальный DOCX не изменяется** ✅
   - Весь парсинг только чтение
   - Никаких изменений в исходном файле

---

## 📝 Примеры использования

### Загрузка всех мероприятий

```python
from eaip_full_skeleton.services.ingest.utils.reference_tables_loader import get_all_measures

measures = get_all_measures()
for measure in measures:
    print(f"{measure['name']}: {measure['capex']} сум, окупаемость {measure['payback_years']} лет")
```

### Загрузка оборудования по цеху

```python
from eaip_full_skeleton.services.ingest.utils.reference_tables_loader import get_equipment_by_section

equipment = get_equipment_by_section(section="Цех 1")
for item in equipment:
    print(f"{item['name']}: {item['power_kw']} кВт")
```

### Использование маппинга мероприятий

```python
from eaip_full_skeleton.services.ingest.utils.reference_tables_loader import get_measures_mapping

mapping = get_measures_mapping()
# Использовать для генерации Excel/Word
```

---

## 🔄 Следующие шаги

1. **Интеграция с Excel-листом "Мероприятия"**
   - Использовать `get_all_measures()` для заполнения листа
   - Применить `measures_mapping.json` для структуры колонок

2. **Интеграция с Word-разделом "Мероприятия"**
   - Использовать нормализованные данные для генерации текста
   - Применить конфигурацию из `measures_mapping.json`

3. **Улучшение нормализации**
   - Ручная обработка таблиц в формате "Показатель/Значение"
   - Дополнительная валидация данных

---

**Статус:** ✅ Задача 2 выполнена, готово к интеграции с Excel и Word.

