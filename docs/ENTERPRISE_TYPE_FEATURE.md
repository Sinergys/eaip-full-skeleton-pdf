# 🏭 Определение типа предприятия - Документация функциональности

**Дата реализации:** 2025-11-30  
**Статус:** ✅ Реализовано и протестировано

---

## 📋 Описание

Система автоматически определяет тип предприятия (отрасль, тип деятельности, тип продукции) на основе анализа загруженных файлов и названия предприятия.

---

## 🎯 Функциональность

### Автоматическое определение:
1. **Отрасль** (`industry`) — энергетика, химия, металлургия и т.д.
2. **Тип предприятия** (`enterprise_type`) — ТЭС, ГЭС, химический завод и т.д.
3. **Тип продукции** (`product_type`) — электроэнергия, химическая продукция и т.д.

### Логика классификации:

1. **Приоритет названию предприятия:**
   - Если в названии есть "ТЭС", "ГЭС", "АЭС" → энергетика
   - Если в названии есть "химическ", "азот" → химия

2. **Анализ файлов с учетом контекста:**
   - Файлы про само предприятие ("энергопаспорт", "реализация", "баланс") → вес 2.0
   - Файлы про потребителей ("ташкари", "внешний", "потребитель") → вес 0.5
   - Остальные файлы → вес 1.0

3. **Фильтрация отраслей потребителей:**
   - Если файл про потребителя и отрасль не совпадает с предприятием → вес × 0.3

---

## 📊 Структура данных

### Таблица `enterprises`:
```sql
CREATE TABLE enterprises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    industry TEXT,              -- Отрасль
    enterprise_type TEXT,      -- Тип предприятия
    product_type TEXT          -- Тип продукции
)
```

---

## 🔧 API и функции

### Функции в `database.py`:

1. **`get_or_create_enterprise(name, industry=None, enterprise_type=None, product_type=None)`**
   - Создает или получает предприятие с указанием типа

2. **`update_enterprise_type(enterprise_id, industry=None, enterprise_type=None, product_type=None)`**
   - Обновляет тип предприятия

3. **`auto_determine_enterprise_type(enterprise_id)`**
   - Автоматически определяет тип предприятия на основе загруженных файлов

### Модуль `utils/enterprise_classifier.py`:

1. **`classify_enterprise(enterprise_name, filenames)`**
   - Классифицирует предприятие: определяет отрасль, тип предприятия и тип продукции
   - Возвращает: `(industry, enterprise_type, product_type)`

---

## 📝 Примеры использования

### Автоматическое определение:
```python
import database

# Автоматически определить тип для предприятия
database.auto_determine_enterprise_type(enterprise_id=3)

# Получить результат
enterprise = database.get_enterprise_by_id(3)
print(f"Отрасль: {enterprise['industry']}")
print(f"Тип предприятия: {enterprise['enterprise_type']}")
print(f"Тип продукции: {enterprise['product_type']}")
```

### Ручное указание типа:
```python
database.update_enterprise_type(
    enterprise_id=3,
    industry="энергетика",
    enterprise_type="ТЭС",
    product_type="электроэнергия"
)
```

---

## ✅ Тестирование

Протестировано на Navoiy IES:
- ✅ Правильно определен как энергетическое предприятие (ТЭС)
- ✅ Тип продукции: электроэнергия
- ✅ Система корректно различает файлы про само предприятие и про потребителей

---

## 📚 Связанные документы

- `docs/ENTERPRISE_TYPE_CLASSIFICATION_COMPLETE.md` — отчет о реализации
- `docs/TZ_COMPLIANCE_CHECK.md` — проверка соответствия ТЗ
- `eaip_full_skeleton/services/ingest/utils/enterprise_classifier.py` — код классификатора

