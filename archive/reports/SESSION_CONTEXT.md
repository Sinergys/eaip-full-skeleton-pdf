# 📋 КОНТЕКСТ СЕАНСА - ПРОЕКТ АТЛАС

**Последнее обновление:** 2025-01-15  
**Версия:** 1.0

---

## 🎯 ТЕКУЩИЙ СТАТУС ПРОЕКТА

### ✅ Выполнено в текущем сеансе:

1. **Полный анализ всех листов нового шаблона**
   - Проанализированы все 8 листов шаблона `new_energy_passport.xlsx`
   - Создан инструмент `ai_table_structure_analyzer.py` для ИИ-анализа структуры таблиц
   - Создан полный семантический профиль с онтологией

2. **Улучшение покрытия листов**
   - Добавлены функции заполнения для недостающих листов:
     - `fill_fuel_dynamics_sheet()` - для "мазут,уголь 5"
     - `fill_specific_consumption_sheet()` - для "Расход на ед.п"
   - Покрытие функциями: 7/8 листов (87.5%)

3. **Исправление проблем с данными**
   - Добавлен выбор шаблона в UI
   - Расширена поддержка всех типов ресурсов (fuel, coal, heat)
   - Исправлена агрегация файлов одного ресурса (`gaz.xlsx`, `voda.xlsx`)

4. **Аудит функционала**
   - Проведен полный аудит системы управления загрузкой данных
   - Выявлены недостающие компоненты
   - Составлен план доработки

---

## 📁 СТРУКТУРА ПРОЕКТА

### Основные директории:

- `eaip_full_skeleton/` - основной проект (FastAPI сервисы)
  - `services/ingest/` - сервис загрузки и обработки файлов
  - `services/reports/` - сервис генерации отчетов
  - `services/validate/` - сервис валидации
- `tools/` - утилиты для заполнения паспортов
- `hybrid_analysis/` - модули анализа шаблонов
  - `technical/` - технический анализ структуры
  - `semantic/` - семантический анализ
  - `debug/` - инструменты отладки
- `templates/pcm690/` - шаблоны энергетических паспортов
- `data/aggregated/` - агрегированные данные

---

## 🔧 КЛЮЧЕВЫЕ КОМПОНЕНТЫ

### 1. Система загрузки файлов

**Endpoint:** `POST /web/upload`  
**Файл:** `eaip_full_skeleton/services/ingest/main.py:529`

**Функционал:**
- Загрузка файлов (Excel, PDF, Word, изображения)
- Проверка дубликатов по хешу (`find_duplicate_upload()`)
- Регистрация в БД (`create_upload()`)
- Автоматический парсинг и агрегация

**База данных:**
- `uploads` - информация о загрузках
- `uploads_storage` - хеши файлов
- `parsed_data` - распарсенные данные

### 2. Генерация энергопаспорта

**Endpoint:** `POST /api/generate-passport/{batch_id}?template_name={name}`  
**Файл:** `eaip_full_skeleton/services/ingest/main.py:989`

**Поддерживаемые шаблоны:**
- `new_energy_passport` - новый шаблон (по умолчанию)
- `metin` - шаблон METIN
- `default` - шаблон по умолчанию

**Функции заполнения:**
- `fill_struktura_pr2()` - структура потребления
- `fill_balans_sheet()` - баланс
- `fill_dinamika_sheet()` - динамика
- `fill_fuel_dynamics_sheet()` - динамика топлива (НОВОЕ)
- `fill_specific_consumption_sheet()` - удельные расходы (НОВОЕ)
- `fill_meropriyatiya_sheet()` - мероприятия
- `fill_nodes_sheet()` - узлы учета

### 3. Агрегация данных

**Файл:** `eaip_full_skeleton/services/ingest/utils/energy_aggregator.py`

**Типы файлов:**
- Многоресурсные: `pererashod.xlsx` (листы "ЭЛЕКТР", "ГАЗ", "СУВ")
- Одноресурсные: `gaz.xlsx`, `voda.xlsx`, `otoplenie.xlsx`, `kotel.xlsx`

**Функции:**
- `aggregate_energy_data()` - агрегация многоресурсных файлов
- `aggregate_single_resource_file()` - агрегация одноресурсных файлов
- `aggregate_from_db_json()` - агрегация из БД (поддержка обоих типов)

---

## 📊 ШАБЛОН NEW_ENERGY_PASSPORT.XLSX

### Листы (8):

1. **Sheet1** - Нормативно-правовая документация (не требует заполнения данными)
2. **Узел учета** - Узлы учета энергоресурсов ✅
3. **Структура пр 2** - Структура потребления энергоресурсов ✅
4. **Баланс** - Баланс энергоресурсов ✅
5. **Динамика ср** - Динамика потребления ✅
6. **мазут,уголь 5** - Динамика потребления топлива ✅
7. **Расход на ед.п** - Расход на единицу продукции ✅
8. **Мериаприятия 1** - Энергосберегающие мероприятия ✅

### Результаты анализа:

- **Полный семантический профиль:** `hybrid_analysis/technical/full_semantic_profile_v2.json`
- **Индивидуальные анализы:** `hybrid_analysis/technical/sheet_analyses_v2/`
- **Покрытие функциями:** 7/8 листов (87.5%)

---

## ⚠️ ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ

### Критические:

1. **Нет валидации готовности данных** перед генерацией
   - Генерация может быть запущена при неполных данных
   - Нет проверки наличия всех требуемых ресурсов

2. **Нет матрицы обязательных данных**
   - Нет централизованного определения требуемых файлов
   - Нет минимального набора для генерации

3. **Нет чек-листа в UI**
   - Пользователь не видит, какие файлы еще нужны
   - Нет индикации готовности данных

### Известные ограничения:

- Агрегация файлов одного ресурса требует точного соответствия структуры
- Некоторые ресурсы (fuel, coal, heat) могут отсутствовать в данных
- Нет автоматической валидации структуры загружаемых файлов

---

## 🛠️ ИНСТРУМЕНТЫ ОТЛАДКИ

### 1. Проверка покрытия листов
```bash
python hybrid_analysis/debug/check_sheet_coverage.py \
  --template templates/pcm690/new_energy_passport.xlsx \
  --mapping hybrid_analysis/semantic/extended_semantic_mapping.json
```

### 2. Проверка доступности данных
```bash
python hybrid_analysis/debug/check_data_availability.py \
  --data data/aggregated/aggregated_full_resources_2022_2024.json \
  --required-resources "electricity,gas,water,fuel,coal,heat"
```

### 3. Анализ одного листа
```bash
python hybrid_analysis/technical/ai_table_structure_analyzer.py \
  --template templates/pcm690/new_energy_passport.xlsx \
  --sheet "Динамика ср" \
  --output output/analysis.json
```

---

## 📋 ПРИОРИТЕТНЫЕ ЗАДАЧИ

### Высокий приоритет:

1. **Создать матрицу обязательных данных**
   - Конфиг с определением требуемых файлов
   - Привязка ресурсов к именам файлов

2. **Добавить валидацию готовности**
   - Функция `validate_generation_readiness()`
   - API endpoint для проверки
   - Блокировка генерации при неполных данных

3. **Создать чек-лист в UI**
   - Отображение требуемых файлов
   - Статус загрузки каждого файла
   - Индикатор готовности

### Средний приоритет:

4. Улучшить агрегацию одноресурсных файлов
5. Добавить валидацию структуры файлов
6. Расширить логирование

---

## 🔗 ВАЖНЫЕ ССЫЛКИ

### Документация:
- `PROJECT_FUNCTIONALITY_AUDIT_REPORT.md` - отчет об аудите
- `docs/COMPLETE_SHEET_ANALYSIS_REPORT.md` - анализ листов
- `docs/DATA_COVERAGE_FIX_REPORT.md` - исправления данных
- `docs/SHEET_COVERAGE_IMPROVEMENT_REPORT.md` - улучшение покрытия

### Результаты анализа:
- `hybrid_analysis/technical/full_semantic_profile_v2.json` - семантический профиль
- `hybrid_analysis/technical/sheet_analyses_v2/` - анализы листов
- `hybrid_analysis/debug/coverage_report.json` - отчет о покрытии

---

## 🎯 БЫСТРЫЙ СТАРТ

### Запуск сервиса:
```bash
cd eaip_full_skeleton/services/ingest
python -m uvicorn main:app --reload --port 8001
```

### Генерация паспорта:
```bash
python tools/fill_energy_passport.py \
  --template templates/pcm690/new_energy_passport.xlsx \
  --aggregated data/aggregated/aggregated_full_resources_2022_2024.json \
  --output output/passport.xlsx
```

### API endpoints:
- `GET /web/upload` - страница загрузки
- `POST /web/upload` - загрузка файла
- `GET /web/results?batchId={id}` - результаты
- `GET /api/progress/{batch_id}` - статус обработки
- `POST /api/generate-passport/{batch_id}?template_name={name}` - генерация паспорта

---

## 💡 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Файлы одного ресурса** (`gaz.xlsx`, `voda.xlsx`) обрабатываются отдельной логикой
2. **Выбор шаблона** добавлен в UI - передается через `template_name` параметр
3. **Все ресурсы инициализируются** в коде, но могут быть пустыми если файлы не загружены
4. **Покрытие листов** можно проверить через `check_sheet_coverage.py`

---

**Версия контекста:** 1.0  
**Дата:** 2025-01-15

