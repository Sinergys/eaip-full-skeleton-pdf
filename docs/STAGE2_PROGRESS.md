# Stage 2 — PCM №690 Templates (Progress Log)

## 2025‑11‑09
- **Шаг 1. Инвентаризация** — собраны перечни исходных документов (`Audit in Sinergys`, `METIN`, `NORMATIV/690`), зафиксированы ключевые файлы для дальнейшей работы.
- **Шаг 2. Адаптация энергопаспорта METIN**
  - Подготовлены заметки по структуре (`docs/METIN_passport_notes.md`, `meta/energy_passport_layout.json`).
  - Из исходного файла `Эл энергия/2022-2024 потребление энергоресурсов.xlsx` сформирован агрегированный JSON с квартальными суммами (`C:\Users\DELL\Documents\AUDIT\METIN\aggregated_energy_2022_2024.json`).
  - На основе агрегированных данных обновлена копия энергопаспорта `энергопаспорт метин ирода3 безформул для ии_filled.xlsx` (восстановлены значения по кварталам для строки «Общее потребление по предприятию» на листе `Struktura pr2`).
  - В ingest-сервисе автоматизировано формирование таких агрегатов при загрузке файлов (см. `services/ingest/utils/energy_aggregator.py`).
- **Шаг 3. Шаблон ПКМ 690**
  - Скрипт `tools/fill_energy_passport.py` наполняет шаблон `EnergyPassport_PKM690_Template_v1.1.2.xlsx` (лист `Struktura pr2`, узлы учёта, страница расчёта потерь трансформатора).
  - Учтены потери трансформатора: активные 3200 кВт·ч/месяц, реактивные 13 600 кВАр·ч/месяц; добавлен лист `08_Потери_электроэнергии`.
  - Сформирован файл `EnergyPassport_PKM690_filled.xlsx` в `C:\Users\DELL\Documents\AUDIT\METIN\`.

### Внешние источники данных
Основные таблицы для расчётов Stage 2 лежат за пределами репозитория:
- `C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\pererashod.xlsx`
- `C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\otoplenie.xlsx`
- `C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\edenic na kvt.xlsx`
- `C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\gaz.xlsx`
- `C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\voda.xlsx`
- `C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\kotel.xlsx`
- `C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\ograjdayuschie_konstrukcii.xlsx`
- `C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\oborudovanie.xlsx`

При запуске скриптов необходимо использовать абсолютные пути или скопировать файлы в рабочую директорию.

#### Форматы команд (Windows PowerShell)
- Для чтения Excel через `python -c` используйте строку пути с `r'...'` или экранируйте обратные слэши:
  ```powershell
  python -c "import pandas as pd; path=r'C:\Users\DELL\Documents\AUDIT\Audit in Sinergys\pererashod.xlsx'; df=pd.read_excel(path); print(df.head())"
  ```
  либо
  ```powershell
  python -c "import pandas as pd; path='C:\\Users\\DELL\\Documents\\AUDIT\\Audit in Sinergys\\pererashod.xlsx'; df=pd.read_excel(path); print(df.head())"
  ```
- Команды запускайте из корня репозитория `C:\Users\DELL\Downloads\eaip_full_skeleton_cursor_ready`, без повторного `cd` внутрь `eaip_full_skeleton`.

## 2025-11-10 — Шаг 1: Распределение по категориям ✅

- ✅ Проанализированы файлы `pererashod.xlsx`, `otoplenie.xlsx`, `edenic na  kvt.xlsx`
- ✅ Определён mapping категорий: technological (тех-потери), household (хоз-бытовые), production (производственные), own_needs (0)
- ✅ Создана функция `aggregate_usage_categories()` в `services/ingest/utils/energy_aggregator.py`
- ✅ Создана функция `distribute_categories_by_quarter()` для распределения по кварталам
- ✅ Протестировано — корректно извлекает данные за 2022-2024
- ✅ Повторно проверено 2025-11-10 — структура листа `pererashod.xlsx` соответствует mapping, распределение по кварталам даёт итог, совпадающий с годовыми суммами (погрешность < 1%)

## 2025-11-10 — Организация проекта ✅

- ✅ Созданы директории `data/source_files/audit_sinergys/` и `data/source_files/metin/`
- ✅ Скопированы все исходные файлы из `C:\Users\DELL\Documents\AUDIT\` в проект
- ✅ Создан `data/README.md` с описанием структуры
- ✅ Создан `data/.gitignore` для исключения больших файлов данных
- ✅ Обновлена документация (`STAGE2_CONTEXT_PROMPT.md`) с новыми путями
- ✅ **Проект перенесён в `C:\eaip\`** — короткий путь для удобства работы (экономия 48 символов)

### Файлы в проекте (data/source_files/)
**audit_sinergys/** (9 файлов):
- pererashod.xlsx (11.12 KB)
- otoplenie.xlsx (11.90 KB)
- edenic na  kvt.xlsx (17.40 KB)
- gaz.xlsx, voda.xlsx, kotel.xlsx
- ograjdayuschie_konstrukcii.xlsx (12.63 KB)
- oborudovanie.xlsx (29.94 KB)
- EnergyPassport_PKM690_filled.xlsx (40.84 KB)

**metin/**:
- aggregated_energy_2022_2024.json (41.75 KB)

## 2025-11-10 — Интеграция компонентов из C:\PROJECT ✅

- ✅ Проанализирован проект `C:\PROJECT` (3 программы, 2612 строк полезного кода)
- ✅ Скопированы **2 генератора ПКМ 690**:
  - `tools/pkm690_excel_generator.py` (1027 строк) — Excel-паспорт
  - `tools/pkm690_document_generator.py` (732 строки) — Word-отчёт
- ✅ Скопирован **парсер паспортов**:
  - `services/ingest/parsers/excel_passport_parser.py` (458 строк)
- ✅ Скопирован **unified шаблон** энергоаудита
- ✅ Создан анализ использования: `docs/PROJECT_REUSE_ANALYSIS.md`

**Экономия времени:** 13-19 часов AI-работы (70%)! ⚡

## 2025-11-10 — Шаг 2: Расширение агрегатора (газ, вода, тепло) ✅

- ✅ Добавлена функция `aggregate_single_resource_file()` в `energy_aggregator.py`
- ✅ Реализован парсинг **gaz.xlsx** (газ) — поквартальные данные за 2022-2024
- ✅ Реализован парсинг **voda.xlsx** (вода) — объем потребления по месяцам
- ✅ Реализован парсинг **otoplenie.xlsx** (отопление) — данные о зданиях (площади, объемы)
- ✅ Реализован парсинг **kotel.xlsx** (котельная) — производство, нормы и факт
- ✅ Обновлен `TARGET_FILENAME_KEYWORDS` для автоматической агрегации новых файлов
- ✅ Создан `data/aggregated/aggregated_full_resources_2022_2024.json` (4 файла)

### Результаты парсинга

**Газ (gaz.xlsx):**
- Формат: Квартальные данные с месячной детализацией
- Поля: `cost_sum` (сум), `volume_m3` (м³)
- Периоды: 2022-Q1 до 2024-Q4
- Особенность: Данные по 3 годам в одном файле

**Вода (voda.xlsx):**
- Формат: Месячные данные, автогруппировка по кварталам
- Поля: `volume_m3` (м³)
- Периоды: 2022-Q1 до 2024-Q4
- Квартальные итоги: от 1238 до 2657 м³ на квартал

**Отопление (otoplenie.xlsx):**
- Формат: Инвентаризация зданий (не временные ряды)
- Поля: `name`, `width_m`, `length_m`, `height_m`, `area_m2`, `volume_m3`
- Здания: 13 объектов (офисы, производство, аренда)
- Общая площадь: 7934 м²

**Котельная (kotel.xlsx):**
- Формат: Производственные нормы и факт
- Поля: `name`, `norm_tons`, `actual_2022`, `actual_2023`, `actual_2024`
- Продукция: 5 видов труб и фитингов
- Нормы vs факт: отклонения от 4% до 25%

### Добавлено в `energy_aggregator.py`:

```python
def aggregate_single_resource_file(workbook_path) -> Optional[Dict]:
    """
    Aggregate data from single-resource files (gaz.xlsx, voda.xlsx, kotel.xlsx).
    Supports 4 resource types: gas, water, heating, boiler
    """
```

```python
def _compute_quarter_totals_single_resource(result, resource_type):
    """Compute quarterly totals for single-resource files"""
```

### Файлы обновлены:

- ✅ `eaip_full_skeleton/services/ingest/utils/energy_aggregator.py` (+176 строк)
- ✅ `data/aggregated/aggregated_full_resources_2022_2024.json` (новый)

## 2025-11-10 — Шаг 3: Endpoint генерации паспорта из БД ✅

- ✅ Создана функция `aggregate_from_db_json()` — агрегация из parsed_data.raw_json (164 строки)
- ✅ Адаптирован `pkm690_excel_generator.py` для работы с dict вместо SQLite
  - Изменён `__init__`: принимает `enterprise_data` и `energy_data` как dict
  - Изменён `create_energy_passport()`: работает без enterprise_id
  - Методы `get_*_data()` читают из self вместо SQL-запросов
- ✅ Создан endpoint `POST /api/generate-passport/{batch_id}`
  - Читает данные из БД (parsed_data.raw_json)
  - Агрегирует в памяти через `aggregate_from_db_json()`
  - Генерирует Excel паспорт через `PKM690ExcelGenerator`
  - Возвращает файл для скачивания (FileResponse)
- ✅ Добавлена кнопка "📊 Сгенерировать энергопаспорт" в results.html
  - JavaScript обработчик с индикацией прогресса
  - Автоматическое скачивание файла после генерации
  - Обработка ошибок с понятными сообщениями

### Полный поток работы:

```
1. Загрузка файла (upload.html)
   ↓
2. Парсинг и сохранение в БД (parsed_data.raw_json)
   ↓
3. Просмотр результатов (results.html)
   ↓
4. Клик "Сгенерировать энергопаспорт"
   ↓
5. POST /api/generate-passport/{batch_id}
   ↓ aggregate_from_db_json()
   ↓ PKM690ExcelGenerator
   ↓
6. Скачивание готового паспорта.xlsx
```

### Файлы изменены:

- ✅ `eaip_full_skeleton/services/ingest/utils/energy_aggregator.py` (+164 строки)
- ✅ `tools/pkm690_excel_generator.py` (адаптирован для dict)
- ✅ `eaip_full_skeleton/services/ingest/main.py` (+77 строк endpoint)
- ✅ `eaip_full_skeleton/services/ingest/web/results.html` (+кнопка +JS)

## 2025-11-10 — Шаг 3b: Тестирование генерации ✅

- ✅ Запущен ingest-сервис, выполнен полный цикл загрузки и генерации
- ✅ Excel-файл скачивается и открывается без предупреждений/циклических ссылок
- ✅ Исправлены формулы на листе `Measures` (итоги не ссылаются сами на себя)
- ✅ TODO `stage2_step3_test_flow` закрыт

## 2025-11-30 — CRIT_9: Расчёты балансов ✅

- ✅ Интегрированы централизованные формулы из `energy_passport_calculations.py`
- ✅ Добавлена валидация через `calculate_balance_total()` перед созданием формул Excel
- ✅ Создан тестовый скрипт `tools/test_balance_calculations.py` — все тесты пройдены (6/6)
- ✅ Улучшена функция `fill_balans_sheet()` в `tools/fill_energy_passport.py`
- ✅ Создан чеклист проверки листа "Баланс" (`docs/BALANCE_SHEET_CHECKLIST.md`)
- ✅ Создан скрипт автоматической проверки `tools/test_full_passport_cycle.py`
- ✅ Все рекомендации экспертного совета применены и проверены

**Файлы изменены:**
- `tools/fill_energy_passport.py` — добавлена валидация расчётов балансов
- `tools/test_balance_calculations.py` — тестовый скрипт для проверки формул
- `tools/test_full_passport_cycle.py` — автоматическая проверка листа "Баланс"
- `docs/CRIT_9_EXPERT_SOLUTION.md` — документ с применением рекомендаций экспертов
- `docs/BALANCE_SHEET_CHECKLIST.md` — чеклист для проверки расчётов

## 2025-11-30 — Документация и координация ✅

- ✅ Обновлён статус проекта в `PROJECT_STATUS_REPORT.md` (Stage 2: 85%)
- ✅ Создан отчёт о прогрессе `PROGRESS_REPORT_2025_11_30.md`
- ✅ Обновлён план следующих шагов `NEXT_STEPS_PLAN.md`
- ✅ Подготовлены рекомендации для Agent-2 (`docs/AGENT_2_RECOMMENDATIONS.md`)
- ✅ Обновлён единый файл задач и статус агентов
- ✅ Синхронизирована документация проекта

## 2025-11-10 — Шаблоны из C:\PROJECT ✅

- ✅ Скопированы подготовленные шаблоны энергопаспорта и отчёта:  
  `template_250314 Отчёт энергоаудит джурабек.xlsx`, `template_Отчёт бешафар.xlsx`,  
  `template_Структура_отчёта_по_разделам_программы_энергоаудита.xlsx`
- ✅ Добавлены в `templates/pcm690/` для дальнейшего анализа структуры листов и маппинга данных
- ✅ Проверено наличие `unified_energy_audit_template.xlsx` (ранее импортирован) — актуальная версия в проекте
- ✅ Черновик маппинга: создан файл `docs/PCM690_TEMPLATE_MAPPING.md` с описанием JSON-схем для листов `Оборудование`, `Мероприятия` и паспортной шапки

## 2025-11-10 — Парсер оборудования ✅

- ✅ Реализован `parse_equipment_workbook()` (`services/ingest/utils/equipment_parser.py`) — выделяет 11 участков, 95 позиций оборудования, считает суммарную мощность и количество частотных приводов
- ✅ Интегрирован в ingest: при загрузке `oborudovanie.xlsx` создаётся `{batch_id}_equipment.json` с агрегированной структурой
- ✅ JSON-структура задокументирована в `docs/PCM690_TEMPLATE_MAPPING.md`

## 2025-11-10 — Universal Excel Parser ✅

- ✅ Добавлен CLI-скрипт `excel_parser.py` — чтение `.xlsx / .xlsb / .csv` с автоопределением кодировки и экспортом в `csv/json/parquet`
- ✅ Поддерживает чанки (`--chunksize`) и передачу листа/колонок (`--sheet`, `--usecols`)
- ✅ Требуемые зависимости: `pandas`, `pyarrow`, `openpyxl`, `pyxlsb`, `chardet`
- ✅ Пример запуска: `python excel_parser.py --path data.xlsx --to parquet --out data.parquet`

## 2025-11-10 — Парсер ограждающих конструкций ✅

- ✅ Реализован `parse_building_envelope()` (`services/ingest/utils/building_envelope_parser.py`) — выделяет 6 секций, нормализует толщину, теплопроводность, площади и теплопотери
- ✅ Интегрирован в ingest: при загрузке `ograjdayuschie_konstrukcii.xlsx` создаётся `{batch_id}_envelope.json` и возвращается статистика в ответе API
- ✅ Структура JSON описана в `docs/PCM690_TEMPLATE_MAPPING.md`
- ✅ Добавлено заполнение листа `02_Исходные данные` в `fill_energy_passport.py` (`--envelope-json`) на основе данных ограждающих конструкций

## 2025-11-10 — Лист оборудования ✅

- ✅ `fill_energy_passport.py` принимает `--equipment-json` и формирует лист `Equipment` (при отсутствии — создаёт)
- ✅ В таблицу выводятся участок, раздел, перечень оборудования, количества, единичная и суммарная мощность, наличие ЧП, примечания
- ✅ Сводные показатели (кол-во разделов, суммарная мощность, число ЧП) берутся из `summary` JSON
- ✅ Обновлены `docs/PCM690_TEMPLATE_MAPPING.md` (раздел 7.1) и подготовлен пример `data/aggregated/oborudovanie_equipment.json`
- ✅ Endpoint `/api/generate-passport/{batch_id}` в ingest теперь использует `fill_energy_passport` (с автоподхватом `{batch_id}_equipment.json` и `{batch_id}_envelope.json`), fallback — старый `PKM690ExcelGenerator`

## 2025-11-11 — Загрузка и учёт файлов ✅

- ✅ Поле предприятия в веб-форме унифицировано (datalist): вводим название — выбираем из подсказок или создаём новое
- ✅ Выпадающий список «Вид энергоресурса» (электроэнергия, газ, тепло, вода, топливо, оборудование, ограждающие конструкции, узлы учёта, прочее) сохраняет тип загрузки и подсвечивает его в истории
- ✅ Добавлена дедупликация по имени, размеру и SHA-1: повторная загрузка возвращает существующий `batch_id`, файл не сохраняется повторно
- ✅ JSON узлов учёта (`schetchiki.xlsx`) разбирается на несколько таблиц, лист `01_Узлы учета` воспроизводит трёхстрочный заголовок, структура соответствует исходнику

## 2025-11-12 — Шаг 4: Расширение fill_energy_passport.py для всех листов ✅

- ✅ Создана функция `fill_balans_sheet()` — заполнение листа энергобаланса по категориям потребления (technological, own_needs, production, household)
  - Поддержка всех кварталов 2022-2024
  - Автоматические формулы итогов (=SUM)
  - Fallback на usage_data если by_usage отсутствует в agg_data
- ✅ Создана функция `fill_dinamika_sheet()` — заполнение листа динамики и удельных показателей
  - Таблица: год, квартал, потребление по ресурсам (электроэнергия, газ, вода, производство)
  - Автоматический расчёт удельного расхода: кВт·ч/кг производства (формула Excel)
- ✅ Создана функция `fill_meropriyatiya_sheet()` — заполнение листа мероприятий по энергосбережению
  - Поддержка внешних данных через `--measures-json`
  - Автоматический расчёт срока окупаемости
  - Дефолтные мероприятия если данные не предоставлены
- ✅ Интегрированы новые функции в `main()` скрипта
  - Добавлены аргументы `--usage-json` и `--measures-json`
  - Поддержка альтернативных названий листов (Balans/Баланс, Dinamika sr/Динамика, Meropriyatiya/Мероприятия)
- ✅ Все функции используют единый стиль кода и вспомогательные функции (_format_float, _auto_fit_columns)

**Файлы изменены:**
- ✅ `tools/fill_energy_passport.py` (+184 строки: 3 новые функции + интеграция)

## 2025-11-13 — Тестирование заполнения энергопаспорта ✅

- ✅ Создан тестовый скрипт `scripts/test_passport_completion.py` для проверки процента заполнения
  - Анализ всех листов энергопаспорта
  - Подсчёт заполненных ячеек и формул
  - Генерация JSON-отчёта с детальной статистикой
- ✅ Протестировано заполнение энергопаспорта:
  - **Общее заполнение:** 63.33% (1,107 из 1,748 ячеек)
  - **Листов:** 10 (включая 3 новых: Balans, Dinamika sr, Meropriyatiya)
  - **Топ-5 листов:** Dinamika sr (100%), Meropriyatiya (100%), Gas (94.29%), Electricity (94.29%), Analytics (90.48%)
- ✅ Исправлена логика создания листов: теперь листы создаются автоматически, если их нет в шаблоне
- ✅ Обновлена функция `fill_balans_sheet()`: построчное заполнение вместо матричного (более гибко)

**Файлы созданы:**
- ✅ `scripts/test_passport_completion.py` (тестовый скрипт)
- ✅ `data/aggregated/passport_completion_report.json` (JSON-отчёт)
- ✅ `EnergyPassport_PKM690_filled_test.xlsx` (тестовый заполненный паспорт)

## 2025-11-30 — Определение типа предприятия ✅

- ✅ Добавлены поля в БД: `industry`, `enterprise_type`, `product_type`
- ✅ Реализована автоматическая классификация типа предприятия на основе анализа файлов
- ✅ Учет контекста файлов (про само предприятие vs про потребителей)
- ✅ Протестировано на Navoiy IES: корректно определен как энергетическое предприятие (ТЭС)
- ✅ Документация обновлена: ТЗ, архитектура, README
- ✅ Интеграция всех парсеров в ingest-сервис

**Файлы изменены:**
- `eaip_full_skeleton/services/ingest/database.py` — добавлены поля и функции классификации
- `eaip_full_skeleton/services/ingest/utils/enterprise_classifier.py` — новый модуль классификации
- `docs/ENTERPRISE_TYPE_CLASSIFICATION_COMPLETE.md` — документация

---

## 2025-12-01 — Установка Java и тестирование Tabula ✅

- ✅ Установлен Microsoft OpenJDK 17.0.17 (LTS) через winget
- ✅ Установлен jpype1 для ускорения работы Tabula
- ✅ Настроена автоматическая установка JAVA_HOME в `table_detector.py`
- ✅ Протестировано извлечение таблиц из PDF с Tabula
- ✅ Создан тестовый скрипт `tools/test_tabula_extraction.py`
- ✅ Создан быстрый тест `tools/test_tabula_quick.py`
- ✅ Создано руководство по установке Java (`docs/JAVA_INSTALLATION_GUIDE.md`)
- ✅ Создан скрипт поиска Java (`tools/find_java.py`)

**Результаты:**
- Tabula работает с jpype (быстрее, чем через subprocess)
- Успешно извлечены таблицы из тестового PDF
- Java автоматически определяется системой

**Файлы изменены:**
- `eaip_full_skeleton/services/ingest/utils/table_detector.py` — улучшена диагностика Java
- `eaip_full_skeleton/services/ingest/tools/find_java.py` — новый скрипт поиска Java
- `eaip_full_skeleton/services/ingest/tools/test_tabula_extraction.py` — тест извлечения таблиц
- `docs/JAVA_INSTALLATION_GUIDE.md` — руководство по установке

---

## 2025-12-01 — Комплексное тестирование энергопаспорта ✅

- ✅ Создан комплексный тестовый скрипт `tools/comprehensive_passport_test.py`
- ✅ Протестирован файл "Метин Ирода" (`Энергопаспорт Метин Ирода 21112025.xlsx`)
- ✅ Проверены все блоки тестирования (1-4):
  - Блок 1: Общие проверки файла и структуры
  - Блок 2: Проверка основных листов
  - Блок 3: Проверка расчетных листов
  - Блок 4: Проверка формул и связей между листами

**Результаты тестирования:**
- ✅ **1527 формул** проверено — **0 ошибок**
- ✅ Все основные листы присутствуют (11 листов)
- ✅ Структура файла корректна
- ✅ Связи между листами работают
- ✅ Размер файла: 0.10 MB

**Найденные листы:**
- Структура пр 2 ✅
- Баланс ✅
- Динамика ср ✅
- Мероприятия ✅
- Узел учета ✅
- мазут,уголь 5
- Расход на ед.п
- и другие

**Файлы созданы:**
- `eaip_full_skeleton/services/ingest/tools/comprehensive_passport_test.py` — комплексный тест
- `docs/TESTING_REPORT_METIN_IRODA_2025_12_01.md` — детальный отчет о тестировании
- `docs/TESTING_REPORT_2025_12_01.md` — отчет о тестировании (предварительный)

**Статус:** Все проверки пройдены успешно. Файл готов к использованию.

---

- ✅ Добавлены поля в таблицу `enterprises`: `industry` (отрасль), `enterprise_type` (тип предприятия), `product_type` (тип продукции)
- ✅ Реализована миграция БД для добавления новых полей в существующие таблицы
- ✅ Создан модуль `utils/enterprise_classifier.py` для автоматического определения типа предприятия
- ✅ Реализована логика классификации с учетом:
  - Приоритета названия предприятия (если в названии есть "ТЭС" → энергетика)
  - Контекста файлов (файлы про само предприятие важнее файлов про потребителей)
  - Взвешенного анализа упоминаний отраслей в названиях файлов
- ✅ Добавлена функция `auto_determine_enterprise_type()` для автоматического определения типа
- ✅ Протестировано на Navoiy IES: правильно определен как энергетическое предприятие (ТЭС)
- ✅ Обновлена документация: ТЗ, архитектурная документация, README

**Файлы созданы/изменены:**
- ✅ `eaip_full_skeleton/services/ingest/database.py` — добавлены поля и функции
- ✅ `eaip_full_skeleton/services/ingest/utils/enterprise_classifier.py` — новый модуль классификации
- ✅ `docs/ENTERPRISE_TYPE_CLASSIFICATION_COMPLETE.md` — отчет о реализации
- ✅ `docs/ENTERPRISE_TYPE_FEATURE.md` — документация функциональности
- ✅ `docs/TZ_COMPLIANCE_CHECK.md` — проверка соответствия ТЗ

## Next
- Шаг 5: Автоматизировать заполнение Word-отчёта (`pkm690_document_generator.py`)
- Шаг 6: API интеграция (опционально) — endpoints для генерации паспорта и отчёта
- Шаг 7: Документация и финализация — обновить DEVELOPMENT_PLAN, создать тестовый чеклист
- AI-рекомендации по энергосбережению (интеграция с recommend service)

