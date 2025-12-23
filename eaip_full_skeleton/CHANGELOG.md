# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added - 2025-01-15

#### Индустриализация Word-отчётов по ПКМ-690

**Цель**: Полная индустриализация генерации Word-отчётов с использованием централизованных расчётов и единого источника данных.

**Выполнено**:

1. **Единый доменный объект ReportData**
   - Создан модуль `eaip_full_skeleton/services/ingest/domain/report_data.py`
   - Агрегация всех КПИ в едином объекте
   - Автоматическое вычисление всех показателей
   - Единый интерфейс для Excel и Word генераторов

2. **Структура разделов ПКМ-690**
   - Создан модуль `eaip_full_skeleton/services/ingest/domain/pkm690_sections.py`
   - Маппинг разделов ПКМ-690 на образцовый отчёт
   - Определены требования к данным для каждого раздела
   - Текстовые шаблоны для всех разделов

3. **Readiness-проверка для Word-отчётов**
   - Создан модуль `eaip_full_skeleton/services/ingest/utils/word_readiness_validator.py`
   - Проверка готовности данных перед генерацией
   - Блокировка генерации при отсутствии критических данных
   - Поддержка fallback на эталонные таблицы

4. **Заполнение шаблонов**
   - Создан модуль `eaip_full_skeleton/services/ingest/utils/section_template_filler.py`
   - Автоматическое заполнение текстовых шаблонов разделов
   - Динамическое извлечение данных из ReportData

5. **Интеграция Word-генератора с централизованными расчётами**
   - Все вычисления используют `energy_passport_calculations.py`
   - Все единицы измерения используют `energy_units.py`
   - Добавлены функции для агрегации данных по кварталам
   - Использование ReportData как единого источника данных

6. **Тестирование**
   - Создан `scripts/test_reference_word_reports.py` для параметризованных тестов
   - Создан `scripts/test_excel_word_consistency.py` для проверки согласованности
   - Все 4 эталонных предприятия протестированы (4/4 успешно)
   - Готовность данных: 100% для всех предприятий

7. **CI/CD интеграция**
   - Обновлён `.github/workflows/tests.yml`
   - Добавлены тесты Word-отчётов
   - Добавлен тест согласованности Excel/Word
   - Автоматическая проверка при изменениях в Word-генераторе

8. **Документация**
   - Создано 8 документов по задачам
   - Финальный чеклист и итоговый отчёт
   - Полная документация по использованию ReportData

**Результаты**:
- ✅ Все 9 задач индустриализации выполнены
- ✅ Word-отчёты генерируются для всех эталонных предприятий
- ✅ Все тесты проходят успешно
- ✅ Согласованность Excel/Word подтверждена
- ✅ Проект готов к промышленному использованию

---

### Added - 2025-01-15

#### Индустриализация формул и расчётов энергопаспорта

**Цель**: Довести все формулы, единицы измерения и расчётную логику до промышленного уровня.

**Выполнено**:

1. **Централизация единиц измерения**
   - Создан модуль `eaip_full_skeleton/services/ingest/domain/energy_units.py`
   - Определены все единицы проекта и константы преобразования
   - Функции-конвертеры: `to_kwh()`, `to_mwh()`, `to_gcal()`, `to_gj()`, и т.п.
   - Константы времени: `HOURS_PER_YEAR`, `HOURS_PER_QUARTER`, `MONTHS_PER_QUARTER`

2. **Централизация формул**
   - Создан модуль `eaip_full_skeleton/services/ingest/domain/energy_passport_calculations.py`
   - Все расчёты вынесены в централизованные функции:
     - Потери: `calculate_quarter_losses()`, `calculate_loss_percentage()`
     - Удельные показатели: `calculate_specific_consumption()`
     - Оборудование: `calculate_equipment_usage_coefficient()`, `calculate_annual_consumption_from_power()`
     - Баланс: `calculate_balance_total()`, `distribute_quarter_by_usage_categories()`
   - Все формулы защищены от edge-кейсов (деление на ноль, отрицательные значения)

3. **Рефакторинг fill_energy_passport.py**
   - Интегрированы централизованные формулы (12+ мест замены)
   - Сохранена обратная совместимость с fallback на старую логику

4. **Расширение эталонных объектов**
   - Создано 3 новых эталонных объекта:
     - `reference_enterprise_2_heat_intensive.json` (теплоёмкое предприятие)
     - `reference_enterprise_3_electric_intensive.json` (электроёмкое производство)
     - `reference_enterprise_4_services.json` (объект услуг/офис/ТЦ)
   - Всего 4 эталонных объекта для тестирования

5. **Параметризация тестов**
   - Обновлён `scripts/test_reference_enterprise.py` для всех эталонных объектов
   - Добавлен итоговый отчёт с таблицей результатов
   - Сохранение отчёта в JSON

6. **Обработка edge-кейсов**
   - Защита от деления на ноль во всех формулах
   - Обработка отрицательных и нереалистично больших значений
   - Логирование предупреждений при некорректных данных
   - Синхронизация с `passport_requirements.py` и `readiness_validator.py`

7. **Документация**
   - Создан справочник формул: `docs/energy_formulas_reference.md` (360+ строк)
   - Создан отчёт о индустриализации: `docs/ENERGY_FORMULAS_INDUSTRIALIZATION.md`

**Файлы**:
- `eaip_full_skeleton/services/ingest/domain/energy_units.py` (320+ строк)
- `eaip_full_skeleton/services/ingest/domain/energy_passport_calculations.py` (528 строк)
- `tools/fill_energy_passport.py` (обновлён)
- `scripts/test_reference_enterprise.py` (обновлён)
- `data/fixtures/reference_enterprise_2_heat_intensive.json` (создан)
- `data/fixtures/reference_enterprise_3_electric_intensive.json` (создан)
- `data/fixtures/reference_enterprise_4_services.json` (создан)
- `docs/energy_formulas_reference.md` (создан)
- `docs/ENERGY_FORMULAS_INDUSTRIALIZATION.md` (создан)

**Критерии готовности**: ✅ Все выполнены
- Формулы и единицы документированы и централизованы
- 4 эталонных объекта созданы и протестированы
- Параметризованные тесты работают
- Формулы устойчивы к edge-кейсам
- Обратная совместимость сохранена

### Fixed - 2025-11-05

#### PDF Generation with Cyrillic Support

**Issue**: PDF files generated by the reports service did not display Cyrillic characters correctly - they appeared as squares or were missing.

**Solution**:
- Added **DejaVuSans TTF font** with full Cyrillic support (`services/reports/assets/fonts/DejaVuSans.ttf`)
- Updated PDF generation code to use TTF fonts instead of UnicodeCIDFont
- Implemented font family registration for proper bold text rendering
- Added fallback mechanism if bold font variant is not available

**Technical Details**:
- Font registration happens at module import time in `services/reports/main.py`
- All PDF styles (`title_style`, `heading2_style`, `normal_style`) now use `DejaVuSans`
- Tables use Unicode font for all cells
- Font family registered for `<b>` tag support in Paragraph elements

**Files Changed**:
- `services/reports/main.py` - Added TTF font registration and Unicode font support
- `services/reports/assets/fonts/DejaVuSans.ttf` - Added font file
- `services/reports/requirements.txt` - Already includes `reportlab==4.2.5`

#### Startup Stability

**Issue**: The `audit_demo.ps1` script sometimes failed with "connection refused" errors because the reports service container wasn't ready yet.

**Solution**:
- Added port readiness check before generating PDF reports
- Script now waits for port 8005 to be available before making API calls

**Implementation**:
```powershell
Write-Host "Waiting for reports service..."
while (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 8005 -InformationLevel Quiet)) {
    Start-Sleep -Seconds 1
}
Write-Host "Reports service is ready."
```

**Files Changed**:
- `infra/audit_demo.ps1` - Added startup wait check

### Verification

After these changes:
- ✅ PDF files display Cyrillic text correctly
- ✅ PDF headers are valid (`%PDF-1.x`)
- ✅ Script runs reliably after `docker compose up`
- ✅ Font registration logs visible in container output

### Usage

To generate a PDF with Cyrillic support:

```powershell
cd infra
docker compose build reports
docker compose up -d reports
pwsh -ExecutionPolicy Bypass -File .\audit_demo.ps1
```

The generated PDF file `passport_demo1_full.pdf` will contain correctly rendered Cyrillic text.

