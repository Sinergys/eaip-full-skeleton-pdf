# Changelog

Все значимые изменения в проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/lang/ru/).

---

## [0.4.0] - 2025-01-15

### 🎉 Индустриализация Word-отчётов завершена

#### ✅ Добавлено

**Модули:**
- `eaip_full_skeleton/services/ingest/domain/report_data.py` - Единый доменный объект для агрегации всех КПИ
- `eaip_full_skeleton/services/ingest/domain/pkm690_sections.py` - Структура разделов ПКМ-690 с требованиями к данным
- `eaip_full_skeleton/services/ingest/utils/word_readiness_validator.py` - Валидация готовности данных для Word-отчётов
- `eaip_full_skeleton/services/ingest/utils/section_template_filler.py` - Заполнение текстовых шаблонов разделов

**Тесты:**
- `scripts/test_reference_word_reports.py` - Параметризованные тесты для генерации Word-отчётов
- `scripts/test_excel_word_consistency.py` - Тест согласованности Excel и Word отчётов
- `scripts/check_status.py` - Скрипт проверки статуса индустриализации

**Документация:**
- `docs/TASK4_REPORT_DATA_USAGE.md` - Документация по ReportData
- `docs/TASK5_PKM690_SECTIONS_SUMMARY.md` - Структура разделов ПКМ-690
- `docs/TASK6_WORD_READINESS_SUMMARY.md` - Readiness-проверка для Word
- `docs/TASK7_REFERENCE_WORD_TESTS_SUMMARY.md` - Тестирование Word-отчётов
- `docs/TASK8_SINGLE_SOURCE_OF_TRUTH_SUMMARY.md` - Единый источник правды
- `docs/WORD_REPORT_INDUSTRIALIZATION_COMPLETE.md` - Полный отчёт по индустриализации
- `docs/WORD_INDUSTRIALIZATION_FINAL_SUMMARY.md` - Финальный отчёт
- `docs/FINAL_CHECKLIST.md` - Финальный чеклист

#### 🔄 Изменено

**Word Report Generator:**
- Полная интеграция с `energy_passport_calculations.py` для всех вычислений
- Использование `ReportData` как единого источника данных
- Интеграция с `word_readiness_validator` для проверки готовности данных
- Использование эталонных таблиц как fallback источника данных

**CI/CD:**
- Обновлён `.github/workflows/tests.yml`:
  - Добавлены тесты Word-отчётов
  - Добавлен тест согласованности Excel/Word
  - Триггеры на изменения в Word-генераторе и ReportData

**Energy Passport Calculations:**
- Добавлены функции для агрегации данных по кварталам:
  - `calculate_total_consumption_by_resource()` - общее потребление по ресурсам
  - `calculate_total_cost_by_resource()` - общие затраты по ресурсам
  - `calculate_total_costs()` - все затраты
  - `calculate_average_payback_period()` - средний срок окупаемости мероприятий

#### 🐛 Исправлено

- Исправлена ошибка "cannot access local variable 'electricity_data'" в Word-генераторе
- Исправлена ошибка "unhashable type: 'slice'" при обработке nodes_data
- Улучшена проверка enterprise.name и enterprise.address в readiness validator

#### 📊 Результаты

- ✅ Все 9 задач индустриализации выполнены
- ✅ Word-отчёты генерируются для всех 4 эталонных предприятий
- ✅ Готовность данных: 100% для всех предприятий
- ✅ Все тесты проходят успешно (4/4)
- ✅ Согласованность Excel/Word подтверждена

---

## [0.3.0] - 2025-11-08

### Стабильный релиз с multi-arch образами

- Добавлена поддержка multi-arch Docker образов
- Улучшена безопасность с security scanning
- Обновлена документация

---

## [0.2.0] - 2025-11-08

### Стабильный релиз с Cyrillic PDF поддержкой

- Добавлены TTF шрифты (DejaVuSans/Arial) для генерации PDF с кириллицей
- Улучшен сервис отчётов с полной поддержкой Unicode
- Добавлена проверка готовности для отчётов (порт 8005)
- Обновлена модель analytics с опциональным meterId
- Обновлена документация (README, CHANGELOG, PDF_GENERATION.md)
- Очищены вложенные шрифты и предупреждения compose

---

[0.4.0]: https://github.com/Sinergys/eaip-full-skeleton-pdf/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Sinergys/eaip-full-skeleton-pdf/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Sinergys/eaip-full-skeleton-pdf/releases/tag/v0.2.0

