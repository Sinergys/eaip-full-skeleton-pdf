# 🚀 БЫСТРАЯ СПРАВКА - ПРОЕКТ АТЛАС

## 📍 ГДЕ ЧТО НАХОДИТСЯ

### API Endpoints:
- `POST /web/upload` - загрузка файла
- `GET /api/progress/{batch_id}` - статус обработки
- `POST /api/generate-passport/{batch_id}?template_name={name}` - генерация паспорта
- `GET /api/enterprises/{id}/uploads` - история загрузок

### Основные файлы:
- `eaip_full_skeleton/services/ingest/main.py` - главный API сервис
- `eaip_full_skeleton/services/ingest/database.py` - работа с БД
- `tools/fill_energy_passport.py` - функции заполнения листов
- `eaip_full_skeleton/services/ingest/utils/energy_aggregator.py` - агрегация данных

### Шаблоны:
- `templates/pcm690/new_energy_passport.xlsx` - новый шаблон
- `templates/pcm690/template_metin.xlsx` - шаблон METIN

### Инструменты:
- `hybrid_analysis/debug/check_sheet_coverage.py` - проверка покрытия листов
- `hybrid_analysis/debug/check_data_availability.py` - проверка данных
- `hybrid_analysis/technical/ai_table_structure_analyzer.py` - анализ структуры

## 🔍 БЫСТРЫЙ ПОИСК

### Найти функцию заполнения:
```bash
grep "def fill_" tools/fill_energy_passport.py
```

### Найти API endpoint:
```bash
grep "@app\\.(get|post)" eaip_full_skeleton/services/ingest/main.py
```

### Найти проверку дубликатов:
```bash
grep "duplicate" eaip_full_skeleton/services/ingest/main.py -i
```

## ⚡ ЧАСТЫЕ ЗАДАЧИ

### Добавить функцию заполнения нового листа:
1. Создать функцию в `tools/fill_energy_passport.py`
2. Добавить вызов в `main()` функцию
3. Обновить `check_sheet_coverage.py` для проверки

### Добавить поддержку нового типа файла:
1. Обновить `TARGET_FILENAME_KEYWORDS` в `energy_aggregator.py`
2. Добавить логику парсинга в `aggregate_from_db_json()`
3. Обновить `should_aggregate_file()`

### Проверить структуру данных:
```bash
python hybrid_analysis/debug/check_data_availability.py --data path/to/data.json
```

