# ✅ Реализация модуля проверки соответствия нормативу

**Дата:** 2025-12-01  
**Статус:** Завершено

---

## 🎯 Что реализовано

### 1. Модуль `normative_validator.py`

**Файл:** `eaip_full_skeleton/services/ingest/domain/normative_validator.py`

**Функции:**
- ✅ `validate_against_normative()` - проверка соответствия фактического значения нормативу
- ✅ `check_critical_fields()` - проверка всех критических полей для предприятия
- ✅ `get_top_fields_with_normatives()` - получение топ полей с наибольшим количеством нормативов
- ✅ `get_normative_statistics()` - получение статистики по нормативным документам

**Возможности:**
- Определение статуса: `compliant` (соответствует), `violation` (нарушение), `below_norm` (ниже нормы), `unknown` (неизвестно)
- Вычисление отклонения в процентах
- Поддержка допустимого отклонения (tolerance_percent)
- Интеграция с базой данных через `database.get_normative_rules_for_field()`

---

### 2. API Endpoints

**Файл:** `eaip_full_skeleton/services/ingest/main.py`

**Новые endpoints:**
- ✅ `POST /api/normative/validate-field` - проверка соответствия поля нормативу
- ✅ `GET /api/normative/statistics` - статистика по нормативным документам
- ✅ `GET /api/normative/critical-fields/{enterprise_id}` - проверка критических полей для предприятия

**Пример использования:**
```python
# Проверка соответствия
POST /api/normative/validate-field?field_name=Удельный расход&actual_value=0.18&sheet_name=Динамика ср

# Ответ:
{
    "field_name": "Удельный расход",
    "sheet_name": "Динамика ср",
    "validation": {
        "status": "violation",
        "actual": 0.18,
        "normative": 0.15,
        "deviation_percent": 20.0,
        "message": "⚠️ Превышение норматива на 20.0%. Факт: 0.18, Норматив: 0.15",
        "rule": {...},
        "unit": "кВт·ч/м²"
    }
}
```

---

### 3. Тесты

**Файл:** `eaip_full_skeleton/services/ingest/tests/test_normative_validator.py`

**Покрытие:**
- ✅ Тесты для `validate_against_normative()`:
  - Соответствие нормативу
  - Превышение норматива
  - Норматив не найден
  - Норматив без числового значения
  - Значение ниже нормы
- ✅ Тесты для `check_critical_fields()`
- ✅ Тесты для `get_top_fields_with_normatives()`
- ✅ Тесты для `get_normative_statistics()`

**Результаты:** 8 тестов, все проходят ✅

---

## 📋 Использование

### Проверка одного поля

```python
from domain.normative_validator import validate_against_normative

result = validate_against_normative(
    actual_value=0.18,
    field_name="Удельный расход",
    sheet_name="Динамика ср",
    tolerance_percent=10.0
)

if result["status"] == "violation":
    print(f"⚠️ {result['message']}")
elif result["status"] == "compliant":
    print(f"✅ {result['message']}")
```

### Проверка критических полей

```python
from domain.normative_validator import check_critical_fields

result = check_critical_fields(enterprise_id=1)
print(f"Нарушений: {result['violations_count']}")
print(f"Соответствует: {result['compliant_count']}")
```

### Получение статистики

```python
from domain.normative_validator import get_normative_statistics

stats = get_normative_statistics()
print(f"Документов: {stats['total_documents']}")
print(f"Правил: {stats['total_rules']}")
print(f"Топ полей: {stats['top_fields']}")
```

---

## 🔗 Интеграция с базой данных

Модуль использует функцию `database.get_normative_rules_for_field()`, которая:
- Ищет правила в таблице `normative_rules`
- Связывает с документами через `normative_documents`
- Фильтрует по полям через `normative_references`
- Сортирует по уверенности извлечения (`extraction_confidence`)

---

## 📊 Статусы проверки

| Статус | Описание | Условие |
|--------|----------|---------|
| `compliant` | Соответствует нормативу | Значение в пределах допустимого отклонения |
| `violation` | Превышение норматива | Значение выше норматива + tolerance |
| `below_norm` | Ниже норматива | Значение ниже норматива - tolerance |
| `unknown` | Неизвестно | Норматив не найден или не имеет числового значения |

---

## 🎯 Следующие шаги

1. **Интеграция с заполнением паспорта:**
   - Добавить автоматическую проверку при заполнении полей
   - Логирование нарушений

2. **Уведомления:**
   - Email уведомления при нарушении
   - Telegram бот (опционально)

3. **Визуализация:**
   - Дашборд со статистикой
   - Цветовая индикация (красный/зеленый)

4. **Экспорт отчетов:**
   - Excel с результатами проверок
   - PDF отчеты

---

**Автор:** Agent-1 (Auto)  
**Дата:** 2025-12-01

