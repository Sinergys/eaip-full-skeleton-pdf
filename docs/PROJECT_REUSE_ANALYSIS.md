# 📊 Анализ C:\PROJECT для использования в EAIP

**Дата анализа:** 2025-11-10  
**Проект-донор:** `C:\PROJECT` (3 программы)  
**Проект-получатель:** `C:\eaip` (EAIP Stage 2)

---

## 🎯 Цель

Идентифицировать готовые компоненты из `C:\PROJECT`, которые можно использовать для ускорения Stage 2 (генерация ПКМ №690 шаблонов).

---

## ✅ Найдено: 5 ключевых компонентов

### 1. 🏆 **PKM690 Excel Generator** (ВЫСОКИЙ ПРИОРИТЕТ)

**Файл:** `C:\PROJECT\pkm690_excel_generator.py` (1027 строк)

**Возможности:**
- ✅ Генерация Excel-таблиц энергетического паспорта по ПКМ 690
- ✅ Автоматические расчеты и формулы
- ✅ Нормативы Узбекистана (electricity, gas, water, building)
- ✅ Стилизация (шрифты, цвета, границы, выравнивание)
- ✅ Работа с SQLite БД (`energy_audit.db`)

**Нормативы включают:**
```python
'electricity': {
    'specific_consumption': 0.15,  # кВт·ч/м²·год
    'efficiency_min': 0.85,
    'cost_per_kwh': 150  # сум/кВт·ч
},
'gas': {...},
'water': {...},
'building': {...}
```

**Как использовать:**
- Скопировать в `C:\eaip\tools\pkm690_excel_generator.py`
- Адаптировать для работы с нашими JSON-данными вместо SQLite
- Интегрировать с `fill_energy_passport.py`

---

### 2. 📝 **PKM690 Document Generator** (ВЫСОКИЙ ПРИОРИТЕТ)

**Файл:** `C:\PROJECT\pkm690_document_generator.py` (732 строки)

**Возможности:**
- ✅ Генерация Word-документов по ПКМ 690
- ✅ Структура по стандарту ПКМ 690 Узбекистан
- ✅ Титульная страница, разделы, таблицы
- ✅ Форматирование (python-docx)
- ✅ Связка с БД для данных предприятия

**Разделы документа:**
- Титульная страница
- Общие сведения о предприятии
- Энергетический баланс
- Анализ потребления
- Мероприятия по энергосбережению
- Рекомендации

**Как использовать:**
- Перенести в `C:\eaip\tools\pkm690_word_generator.py`
- Использовать для Шага 5 Stage 2 (Word-отчёт)
- Заменить SQLite на JSON-данные

---

### 3. 🔍 **Excel Passport Parser** (СРЕДНИЙ ПРИОРИТЕТ)

**Файл:** `C:\PROJECT\parsers\excel_passport_parser.py` (458 строк)

**Возможности:**
- ✅ Интеллектуальный парсинг энергопаспортов Excel
- ✅ Автоопределение листов по ключевым словам
- ✅ Извлечение: enterprise info, resources, electricity, gas, water, fuel
- ✅ Парсинг оборудования, зданий, мероприятий
- ✅ Извлечение формул из ячеек Excel

**Примеры извлечения:**
```python
def _parse_electricity(self):
    """Детальные данные по электроэнергии"""
    return {
        "total_consumption": ...,
        "transformers": ...,
        "monthly_data": ...,
        "power_factor": ...,
        "losses": ...
    }
```

**Как использовать:**
- Дополнить существующий `energy_aggregator.py`
- Использовать для более гибкого парсинга различных форматов паспортов
- Интегрировать в ingest-сервис

---

### 4. 🌉 **PKM690 Calculator Bridge** (СРЕДНИЙ ПРИОРИТЕТ)

**Файл:** `C:\PROJECT\bridges\pkm690_bridge.py` (395 строк)

**Возможности:**
- ✅ FastAPI endpoints для расчётов ПКМ 690
- ✅ Pydantic модели для валидации
- ✅ 8 типов расчётов:
  - Energy balance (энергобаланс)
  - Specific consumption (удельный расход)
  - Energy efficiency (энергоэффективность)
  - Lighting consumption (освещение)
  - Heating consumption (отопление)
  - Energy savings (экономия)
  - Power factor (коэффициент мощности)
  - Dynamics (динамика)

**API endpoints:**
```python
POST /api/pkm690/energy-balance
POST /api/pkm690/specific-consumption
POST /api/pkm690/energy-efficiency
POST /api/pkm690/lighting-consumption
POST /api/pkm690/heating-consumption
POST /api/pkm690/energy-savings
POST /api/pkm690/power-factor
POST /api/pkm690/dynamics
GET  /api/pkm690/coefficients
GET  /api/pkm690/methods
```

**Как использовать:**
- Копировать в `C:\eaip\eaip_full_skeleton\services\reports\`
- Опциональная интеграция для Шага 6 Stage 2 (API endpoints)

---

### 5. 📥 **Metin Import Enhanced v2** (НИЗКИЙ ПРИОРИТЕТ)

**Файл:** `C:\PROJECT\import_metin_enhanced_v2.py` (346 строк)

**Возможности:**
- ✅ Специализированный импорт данных Metin Iroda
- ✅ Улучшенное извлечение информации о предприятии
- ✅ Парсинг энергетических данных из различных форматов
- ✅ Поиск данных по ключевым словам в ячейках
- ✅ Интеграция с SQLite

**Как использовать:**
- Использовать как справочный материал
- Заимствовать логику поиска данных по keywords
- Не копировать целиком (специфично для Metin Iroda)

---

## 📂 Шаблоны энергоаудита

**Директория:** `C:\PROJECT\templates\` (4 файла)

Найденные шаблоны:
1. `template_250314 Отчёт энергоаудит джурабек.xlsx`
2. `template_Отчёт бешафар.xlsx`
3. `template_Структура_отчёта_по_разделам_программы_энергоаудита.xlsx`
4. `unified_energy_audit_template.xlsx` ⭐

**Рекомендация:**
- Изучить `unified_energy_audit_template.xlsx` как альтернативный шаблон
- Сравнить с текущим `energy_passport_template.xlsx`
- Возможно, использовать как дополнительный шаблон

---

## 🎯 План интеграции (по приоритетам)

### Этап 1: Немедленно (Сейчас)

**1.1. Скопировать генераторы ПКМ 690:**
```powershell
Copy-Item "C:\PROJECT\pkm690_excel_generator.py" "C:\eaip\tools\"
Copy-Item "C:\PROJECT\pkm690_document_generator.py" "C:\eaip\tools\"
```

**1.2. Скопировать парсер:**
```powershell
New-Item -ItemType Directory "C:\eaip\eaip_full_skeleton\services\ingest\parsers" -Force
Copy-Item "C:\PROJECT\parsers\excel_passport_parser.py" "C:\eaip\eaip_full_skeleton\services\ingest\parsers\"
```

**1.3. Скопировать unified шаблон:**
```powershell
Copy-Item "C:\PROJECT\templates\unified_energy_audit_template.xlsx" "C:\eaip\templates\pcm690\"
```

### Этап 2: Адаптация (Шаг 2 Stage 2)

**2.1. Адаптировать `pkm690_excel_generator.py`:**
- Заменить `db_path` на `json_path`
- Изменить `get_enterprise_data()` для работы с JSON
- Интегрировать с `data/source_files/metin/aggregated_energy_2022_2024.json`

**2.2. Обновить `energy_aggregator.py`:**
- Добавить методы из `excel_passport_parser.py`
- Использовать интеллектуальный поиск по keywords
- Улучшить парсинг transformers, equipment, buildings

### Этап 3: Интеграция API (Шаг 6 Stage 2, опционально)

**3.1. Интегрировать PKM690 Bridge:**
```powershell
Copy-Item "C:\PROJECT\bridges\pkm690_bridge.py" "C:\eaip\eaip_full_skeleton\services\reports\"
```

**3.2. Добавить endpoints в reports service:**
- Регистрировать router в main.py
- Добавить зависимость `pkm690_calculator.py` (если есть)

---

## 🛠️ Необходимые изменения в скопированных файлах

### `pkm690_excel_generator.py`

**Было:**
```python
def __init__(self, db_path: str = "energy_audit.db"):
    self.db_path = db_path
```

**Стало:**
```python
def __init__(self, json_path: str = None):
    self.json_path = json_path
    self.data = None
    if json_path:
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
```

**Было:**
```python
def get_enterprise_data(self, enterprise_id: int) -> dict:
    conn = sqlite3.connect(self.db_path)
    ...
```

**Стало:**
```python
def get_enterprise_data(self) -> dict:
    return self.data.get("enterprise", {})
```

### `pkm690_document_generator.py`

Аналогичные изменения — замена SQLite на JSON.

---

## 📊 Оценка времени экономии

| Компонент | Строк кода | Написать с нуля | Адаптировать | Экономия |
|-----------|------------|-----------------|--------------|----------|
| Excel Generator | 1027 | ~8-10 ч | ~2-3 ч | **75%** |
| Word Generator | 732 | ~6-8 ч | ~2 ч | **70%** |
| Excel Parser | 458 | ~4-5 ч | ~1-2 ч | **60%** |
| PKM690 Bridge | 395 | ~3-4 ч | ~1 ч | **67%** |
| **ИТОГО** | **2612** | **21-27 ч** | **6-8 ч** | **70%** |

**Суммарная экономия: 13-19 часов AI-работы!** ⚡

---

## ⚠️ Важные замечания

### Зависимости
Убедитесь, что установлены:
```txt
openpyxl>=3.1.0
python-docx>=0.8.11
pandas>=2.0.0
```

### Лицензия
Проверьте LICENSE в `C:\PROJECT` перед копированием кода.

### Совместимость
- Все файлы используют Python 3.8+
- FastAPI bridge требует `pydantic`, `fastapi`
- Генераторы работают автономно

---

## 🚀 Быстрый старт

### Копирование ключевых файлов

```powershell
# Из C:\eaip выполнить:

# 1. Генераторы
Copy-Item "C:\PROJECT\pkm690_excel_generator.py" "tools\"
Copy-Item "C:\PROJECT\pkm690_document_generator.py" "tools\"

# 2. Парсер
New-Item -ItemType Directory "eaip_full_skeleton\services\ingest\parsers" -Force
Copy-Item "C:\PROJECT\parsers\excel_passport_parser.py" "eaip_full_skeleton\services\ingest\parsers\"

# 3. Шаблон
Copy-Item "C:\PROJECT\templates\unified_energy_audit_template.xlsx" "templates\pcm690\"

# 4. Bridge (опционально)
Copy-Item "C:\PROJECT\bridges\pkm690_bridge.py" "eaip_full_skeleton\services\reports\" -ErrorAction SilentlyContinue

Write-Host "✅ Файлы скопированы!"
```

### Проверка

```powershell
# Проверить скопированные файлы
Get-ChildItem "C:\eaip\tools" -Filter "*pkm690*"
Get-ChildItem "C:\eaip\eaip_full_skeleton\services\ingest\parsers"
Get-ChildItem "C:\eaip\templates\pcm690" -Filter "*unified*"
```

---

## 📝 Следующие шаги

1. ✅ Скопировать файлы (скрипт выше)
2. 🔄 Адаптировать `pkm690_excel_generator.py` для JSON
3. 🔄 Адаптировать `pkm690_document_generator.py` для JSON
4. 🔄 Интегрировать `excel_passport_parser.py` в `energy_aggregator.py`
5. ✅ Продолжить Stage 2, Шаг 2 (тепловая энергия)

---

## 🎯 Итоги

**Найдено:** 5 готовых компонентов (2612 строк)  
**Экономия времени:** 13-19 часов AI-работы (70%)  
**Рекомендация:** Немедленно скопировать генераторы и парсер

**Это значительно ускорит разработку Stage 2!** 🚀

---

**Дата создания:** 2025-11-10  
**Автор анализа:** Claude Sonnet 4.5

