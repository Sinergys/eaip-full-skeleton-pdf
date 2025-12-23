# Генерация энергопаспорта

## Обзор

Модуль `services/reports/energy_passport` предоставляет функционал для автоматической генерации полного Excel-энергопаспорта на основе данных из БД/JSON и шаблона Excel.

## Выбор шаблона

Система поддерживает несколько шаблонов энергопаспортов через конфигурацию в `templates/pcm690/templates_config.py`:

- **`metin`** (по умолчанию) - шаблон с кириллическими названиями листов ("Структура пр 2", "Баланс", "Узел учета" и т.д.)
- **`new_energy_passport`** - новый шаблон
- **`default`** - дефолтный шаблон (используется как fallback)

### Использование через API

```bash
# Генерация с шаблоном metin (по умолчанию)
POST /api/generate-passport/{batch_id}

# Генерация с явным указанием шаблона
POST /api/generate-passport/{batch_id}?template_name=metin
POST /api/generate-passport/{batch_id}?template_name=new_energy_passport
```

**Важно:** При указании `template_name` всегда используется `fill_energy_passport` (который загружает шаблон из файла), а не `PKM690ExcelGenerator` (который создает файл с нуля).

## Основные компоненты

### 1. `generator.py` - Главная функция генерации

Функция `generate_energy_passport()` является единой точкой входа для создания энергопаспорта:

```python
from services.reports.energy_passport import generate_energy_passport
from pathlib import Path

result_path = generate_energy_passport(
    enterprise_id="metin-iroda",
    year=2023,
    template_path=Path("data/source_files/audit_sinergys/Энергопаспорт Метин Ирода_с_объемами_и_месяцами.xlsx"),
    output_path=Path("output/passport.xlsx"),
    aggregated_data=aggregated_data,
    enterprise_data=enterprise_data,
    building_data=building_data,
)
```

### 2. `data_collector.py` - Сбор данных

Модуль собирает и структурирует данные для заполнения паспорта:

- Электроэнергия по видам продукции (5 видов)
- Газ помесячно, квартально и годовые итоги
- Удельный расход газа на м² и на условную единицу
- Нормативы и фактические значения

### 3. Функции заполнения в `tools/fill_energy_passport.py`

- `fill_struktura_pr2()` - заполнение листа "Структура пр 2" (исправлен расчет газа из помесячных данных)
- `fill_electricity_by_product()` - заполнение электроэнергии по видам продукции
- `fill_gas_specific_consumption()` - заполнение удельного расхода газа
- `fill_gas_by_usage_categories()` - заполнение газа по категориям использования

## Ключевые исправления

### 1. Расчет газа из помесячных данных

**Проблема:** Значение E32 (2023 Q1 газ) было 14.0819 вместо 14.819

**Решение:** В функции `fill_struktura_pr2()` добавлен расчет газа из помесячных данных:

```python
# Суммируем помесячные данные по газу
gas_m3_from_months = 0.0
for month in gas_months:
    values = month.get("values", {})
    month_gas = values.get("volume_m3", 0) or values.get("gas_m3", 0) or 0
    if month_gas:
        gas_m3_from_months += float(month_gas)

# Используем данные из месячных, если они есть
if gas_m3_from_months > 0:
    gas_m3 = gas_m3_from_months
```

**Важно:** Газ в шаблоне должен быть в тысячах м³, поэтому значение делится на 1000:

```python
gas_m3_thousands = gas_m3 / 1000.0
_safe_set_cell_value(ws, row, col_gas, gas_m3_thousands)
```

### 2. Разбивка газа по категориям

- **Собственные нужды:** фиксировано 432 м³/месяц = 1296 м³/квартал = 5184 м³/год
- **Хозяйственно-бытовые нужды:** остаток (общее потребление - собственные нужды)

### 3. Электроэнергия по видам продукции

Заполняется таблица с 5 видами продукции:
1. Трубы ХВС
2. Фитинги ХВС (ХВС и ГВС)
3. Канализационные трубы
4. Канализационные фитинги
5. Трубы тёплого пола

Для каждого вида заполняются:
- Норма (кВт)
- Факт по годам (2022, 2023, 2024)
- Перерасход (%)

### 4. Удельный расход газа

Автоматически рассчитывается:
- Удельный расход на 1 м² здания: `Gas_year / Area_m2`
- Удельный расход на условную единицу: `Gas_year / Production_units`
- Отклонения от нормативов (абсолютные и в %)

## Структура данных

### Агрегированные данные (aggregated_data)

```python
{
    "resources": {
        "gas": {
            "2023-Q1": {
                "year": 2023,
                "quarter": 1,
                "months": [
                    {"month": "Январь", "values": {"volume_m3": 4800.0}},
                    {"month": "Февраль", "values": {"volume_m3": 5100.0}},
                    {"month": "Март", "values": {"volume_m3": 4919.0}},
                ],
                "quarter_totals": {"volume_m3": 14819.0},
            },
            # ... другие кварталы
        },
        "electricity": {
            "2023-Q1": {
                "quarter_totals": {"active_kwh": 100000.0, "reactive_kvarh": 50000.0},
            },
        },
        "production": {
            # Данные по производству
        },
    }
}
```

## Пример использования

См. `examples/generate_metin_passport.py` для полного примера.

## Тестирование

Запуск тестов:

```bash
pytest tests/test_energy_passport_generation.py -v
```

Тесты проверяют:
- Правильность расчета газа из помесячных данных (E32 = 14.819)
- Годовые итоги по газу
- Заполнение электроэнергии по видам продукции
- Расчет удельного расхода газа

## Требования

- Python 3.8+
- openpyxl
- pytest (для тестов)

## Примечания

- Шаблон Excel должен содержать листы: "Структура пр 2", "Баланс", "Расход  на ед.п"
- Формулы в шаблоне сохраняются и не перезаписываются
- Все значения газа записываются в тысячах м³
- Квартальные и годовые значения рассчитываются из помесячных данных

