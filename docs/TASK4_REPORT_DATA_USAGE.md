# Task 4: Единый доменный объект ReportData

## Обзор

`ReportData` — единый доменный объект, который собирает все ключевые КПИ и агрегаты для использования в Excel-паспорте и Word-отчёте.

## Структура

### Основные компоненты

1. **ResourceTotals** — итоговые показатели по ресурсу:
   - `total_consumption` — общее потребление (кВт·ч, м³, т, Гкал)
   - `total_cost` — общие затраты, сум
   - `quarters_count` — количество кварталов с данными

2. **EquipmentSummary** — сводка по оборудованию:
   - `total_installed_power_kw` — установленная мощность, кВт
   - `total_used_power_kw` — используемая мощность, кВт
   - `total_items_count` — количество единиц оборудования
   - `vfd_count` — количество единиц с ЧРП

3. **MeasuresSummary** — сводка по мероприятиям:
   - `total_count` — количество мероприятий
   - `total_capex` — общая стоимость, сум
   - `total_saving_kwh` — общая экономия, кВт·ч/год
   - `total_saving_money` — общая экономия, сум/год
   - `average_payback_years` — средний срок окупаемости, лет
   - `items` — список мероприятий

4. **ReportData** — основной объект:
   - Содержит все исходные данные (aggregated_data, equipment_data, etc.)
   - Вычисляет все КПИ через централизованные функции
   - Предоставляет единый интерфейс для генераторов

## Использование

### Создание ReportData из сырых данных

```python
from eaip_full_skeleton.services.ingest.domain.report_data import ReportData

# Загружаем данные
with open("aggregated_energy.json", "r", encoding="utf-8") as f:
    aggregated_data = json.load(f)

with open("equipment.json", "r", encoding="utf-8") as f:
    equipment_data = json.load(f)

with open("measures.json", "r", encoding="utf-8") as f:
    measures_data = json.load(f)

# Создаем ReportData
report_data = ReportData.from_raw_data(
    aggregated_data=aggregated_data,
    equipment_data=equipment_data,
    measures_data=measures_data,
    enterprise_data={"name": "ООО Пример", "inn": "123456789"}
)

# Теперь все КПИ вычислены и доступны
print(f"Общее потребление электроэнергии: {report_data.electricity.total_consumption:,.0f} кВт·ч")
print(f"Общие затраты: {report_data.total_energy_cost:,.0f} сум")
print(f"Установленная мощность: {report_data.equipment.total_installed_power_kw:,.2f} кВт")
print(f"Количество мероприятий: {report_data.measures.total_count}")
```

### Использование в Excel-генераторе

```python
from tools.fill_energy_passport import fill_struktura_pr2, fill_equipment_sheet, fill_meropriyatiya_sheet
from eaip_full_skeleton.services.ingest.domain.report_data import ReportData

# Создаем ReportData
report_data = ReportData.from_raw_data(
    aggregated_data=agg_data,
    equipment_data=equipment_data,
    measures_data=measures_data
)

# Используем в функциях заполнения
fill_struktura_pr2(workbook["Struktura pr2"], report_data.aggregated_data)
fill_equipment_sheet(workbook, report_data.equipment_data, "Equipment")
fill_meropriyatiya_sheet(workbook["Meropriyatiya"], report_data.measures.items)
```

### Использование в Word-генераторе

```python
from eaip_full_skeleton.services.ingest.utils.word_report_generator import WordReportGenerator
from eaip_full_skeleton.services.ingest.domain.report_data import ReportData

# Создаем ReportData
report_data = ReportData.from_raw_data(
    aggregated_data=aggregated_data,
    equipment_data=equipment_data,
    measures_data=measures_data,
    enterprise_data=enterprise_data
)

# Генерируем Word-отчёт
generator = WordReportGenerator()
doc = generator.generate_report(
    enterprise_data=report_data.enterprise_data,
    aggregated_data=report_data.aggregated_data,
    equipment_data=report_data.equipment_data,
    measures_data=report_data.measures.items
)

# Или используем вычисленные КПИ напрямую
print(f"Общее потребление: {report_data.electricity.total_consumption:,.0f} кВт·ч")
print(f"Общие затраты: {report_data.total_energy_cost:,.0f} сум")
```

## Преимущества

1. **Единый источник правды**: Все КПИ вычисляются один раз через централизованные функции
2. **Консистентность**: Excel и Word используют одни и те же данные
3. **Удобство**: Не нужно передавать множество отдельных параметров
4. **Расширяемость**: Легко добавить новые КПИ в один объект

## Следующие шаги

1. Интегрировать `ReportData` в `fill_energy_passport.py`
2. Интегрировать `ReportData` в `word_report_generator.py`
3. Обновить тесты для использования `ReportData`
4. Добавить валидацию данных в `ReportData.from_raw_data()`

