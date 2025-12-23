# 📋 ПЛАН: B4 - Импорт электроэнергии в БД

**Задача:** B4 - Импорт электроэнергии  
**Приоритет:** P0  
**Статус:** in_progress  
**Агент:** Agent-1

---

## 🔍 ТЕКУЩАЯ СИТУАЦИЯ

### Что есть:
- ✅ Функция `aggregate_energy_data()` - агрегирует данные электроэнергии из Excel
- ✅ Функция `write_aggregation_json()` - сохраняет агрегированные данные в JSON файлы
- ✅ Парсер электроэнергии в `energy_aggregator.py`
- ✅ Таблицы БД: `enterprises`, `uploads`, `parsed_data`

### Чего нет:
- ❌ Таблица `aggregated_data` в БД
- ❌ Функция импорта агрегированных данных электроэнергии в БД
- ❌ Интеграция импорта в процесс обработки файлов

---

## 🎯 ЦЕЛЬ

Создать функционал для импорта агрегированных данных электроэнергии в БД, чтобы:
1. Данные были доступны для генерации паспортов
2. Данные можно было запрашивать через API
3. Данные были связаны с предприятиями и загрузками

---

## 📝 ПЛАН РЕАЛИЗАЦИИ

### Блок 1: Создание таблицы aggregated_data (10 минут)
- [ ] Добавить таблицу `aggregated_data` в `init_db()`
- [ ] Структура таблицы:
  - `id` (PRIMARY KEY)
  - `enterprise_id` (FOREIGN KEY)
  - `batch_id` (TEXT, для связи с uploads)
  - `resource_type` (TEXT: 'electricity', 'gas', 'water', etc.)
  - `period` (TEXT: '2022-Q1', '2022-Q2', etc.)
  - `data_json` (TEXT: JSON с данными за период)
  - `created_at` (TEXT)
  - `updated_at` (TEXT)

### Блок 2: Функция импорта электроэнергии (10 минут)
- [ ] Создать функцию `import_electricity_to_db()` в `database.py`
- [ ] Параметры: `enterprise_id`, `batch_id`, `electricity_data` (из aggregated JSON)
- [ ] Логика:
  - Извлечь данные по кварталам из `electricity_data`
  - Для каждого квартала создать запись в `aggregated_data`
  - Обновить существующие записи, если они есть

### Блок 3: Интеграция в процесс обработки (10 минут)
- [ ] Модифицировать `main.py` или обработчик файлов
- [ ] После агрегации данных вызывать `import_electricity_to_db()`
- [ ] Добавить обработку ошибок

### Блок 4: Тестирование и валидация (10 минут)
- [ ] Протестировать импорт на реальных данных
- [ ] Проверить целостность данных
- [ ] Обновить документацию

---

## 🔧 ТЕХНИЧЕСКИЕ ДЕТАЛИ

### Структура данных электроэнергии:
```json
{
  "electricity": {
    "2022-Q1": {
      "year": 2022,
      "quarter": 1,
      "months": [...],
      "quarter_totals": {
        "active_kwh": 12345,
        "reactive_kvarh": 6789,
        "cost_sum": 1234567
      }
    }
  }
}
```

### SQL для создания таблицы:
```sql
CREATE TABLE IF NOT EXISTS aggregated_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enterprise_id INTEGER NOT NULL,
    batch_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    period TEXT NOT NULL,
    data_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (enterprise_id) REFERENCES enterprises(id),
    UNIQUE(enterprise_id, resource_type, period)
)
```

---

## ✅ КРИТЕРИИ УСПЕХА

- [ ] Таблица `aggregated_data` создана в БД
- [ ] Функция импорта электроэнергии работает
- [ ] Данные корректно импортируются из JSON
- [ ] Данные доступны через API или функции БД
- [ ] Интеграция в процесс обработки файлов

---

**Следующий шаг:** Начать с Блока 1 - создание таблицы в БД

