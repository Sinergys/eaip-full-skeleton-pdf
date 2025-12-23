# 📖 Как работает импорт и использование нормативов

**Дата:** 2025-12-01

---

## 🚀 БЫСТРАЯ ИНСТРУКЦИЯ: Как загрузить нормативный документ

### 1. Запустите сервер:
```bash
cd eaip_full_skeleton/services/ingest
uvicorn main:app --reload --port 8001
```

### 2. Откройте в браузере:
```
http://localhost:8001/docs
```

### 3. Найдите endpoint:
**`POST /api/normative/upload`**

### 4. Нажмите "Try it out" → выберите файл → "Execute"

**Поддерживаемые форматы:** PDF, Word (.docx), Excel (.xlsx)

**Опциональные параметры:**
- `title` - название документа
- `document_type` - тип (PKM690, GOST, SNiP и т.д.)

**Полная инструкция:** См. `docs/HOW_TO_UPLOAD_NORMATIVE.md`

---

## 📖 Детальное описание работы системы

---

## 🔄 Текущая процедура работы

### 1. **Импорт документа (один раз)**

#### Шаг 1: Загрузка файла
```
Пользователь → Загружает PDF/Word/Excel → /api/normative/upload
```

#### Шаг 2: Проверка на дубликаты (сейчас НЕ реализовано)
```python
# ТЕКУЩАЯ ПРОБЛЕМА: Дедупликация не работает для нормативов
file_hash = calculate_sha1(file_path)  # Вычисляется, но не проверяется
```

**Что нужно добавить:**
```python
# Проверка существующего документа по хешу
existing_doc = database.find_normative_document_by_hash(file_hash)
if existing_doc:
    return {
        "document_id": existing_doc["id"],
        "status": "duplicate",
        "message": "Документ уже импортирован ранее"
    }
```

#### Шаг 3: Парсинг документа
```python
parsed_result = parse_file(file_path)
# Результат: {"parsing": {"data": {"text": "..."}}}
```

**Проблема:** Полный текст НЕ сохраняется в БД, только извлеченные правила.

#### Шаг 4: AI-извлечение правил
```python
extracted_rules = ai_extract_rules(parsed_result)
# Результат: [
#   {"rule_type": "formula", "formula": "Q = A * B", ...},
#   {"rule_type": "normative", "numeric_value": 0.15, ...}
# ]
```

#### Шаг 5: Сохранение в БД
```python
# Сохраняется:
database.create_normative_document(...)  # Метаданные документа
database.create_normative_rule(...)      # Извлеченные правила
database.create_normative_reference(...) # Связи с полями паспорта

# НЕ сохраняется:
# - Полный текст документа ❌
# - Результат парсинга ❌
```

---

### 2. **Использование нормативов**

#### Вариант 1: Получение правил для поля
```python
# При заполнении энергопаспорта
rules = database.get_normative_rules_for_field(
    field_name="Удельный расход электроэнергии",
    sheet_name="Динамика ср"
)

# Результат: [
#   {
#     "rule_type": "normative",
#     "numeric_value": 0.15,
#     "unit": "кВт·ч/м²·год",
#     "document_title": "ПКМ №690",
#     ...
#   }
# ]
```

#### Вариант 2: Получение правил по типу
```python
# Получить все формулы
formulas = database.get_normative_rules_by_type("formula")

# Получить все нормативы
normatives = database.get_normative_rules_by_type("normative")
```

---

## ⚠️ Проблемы текущей реализации

### 1. **Нет дедупликации**
- Документ можно импортировать несколько раз
- Создаются дубликаты в БД
- Тратится время на повторный AI-анализ

### 2. **Не сохраняется полный текст**
- После импорта нельзя получить оригинальный текст
- Невозможно переизвлечь правила без повторной загрузки
- Нет возможности поиска по тексту документа

### 3. **Нет кэширования**
- Каждый раз парсится файл заново
- AI-анализ выполняется повторно

---

## ✅ Предлагаемое решение

### 1. **Добавить дедупликацию**

```python
# database.py
def find_normative_document_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    """Найти документ по хешу файла"""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM normative_documents
            WHERE file_hash = ?
            LIMIT 1
            """,
            (file_hash,)
        ).fetchone()
        return _row_to_dict(row) if row else None
```

```python
# normative_importer.py
def import_normative_document(self, file_path: str, ...):
    file_hash = self._calculate_file_hash(file_path)
    
    # ПРОВЕРКА НА ДУБЛИКАТ
    existing_doc = database.find_normative_document_by_hash(file_hash)
    if existing_doc:
        logger.info(f"Документ уже импортирован: ID={existing_doc['id']}")
        return {
            "document_id": existing_doc["id"],
            "status": "duplicate",
            "message": "Документ уже был импортирован ранее",
            "rules_count": database.count_rules_for_document(existing_doc["id"])
        }
    
    # Продолжаем импорт...
```

---

### 2. **Сохранить полный текст в БД**

#### Обновить схему БД:
```sql
ALTER TABLE normative_documents 
ADD COLUMN full_text TEXT;  -- Полный текст документа

ALTER TABLE normative_documents 
ADD COLUMN parsed_data_json TEXT;  -- Результат парсинга (JSON)
```

#### Сохранять при импорте:
```python
# normative_importer.py
parsed_result = self._parse_document(file_path)
full_text = self._extract_text_content(parsed_result)

# Сохраняем в БД
database.create_normative_document(
    ...,
    full_text=full_text,
    parsed_data_json=json.dumps(parsed_result)
)
```

#### Использовать при необходимости:
```python
# Получить полный текст документа
def get_normative_document_text(document_id: int) -> str:
    doc = database.get_normative_document(document_id)
    return doc.get("full_text", "")

# Переизвлечь правила (без повторной загрузки)
def re_extract_rules(document_id: int):
    doc = database.get_normative_document(document_id)
    parsed_result = json.loads(doc["parsed_data_json"])
    # Повторный AI-анализ с сохраненным текстом
    rules = ai_extract_rules(parsed_result)
    # Обновить правила в БД
```

---

### 3. **Оптимизировать использование**

#### Кэширование в памяти:
```python
# Кэш для часто используемых нормативов
_normative_cache = {}

def get_normative_value_cached(field_name: str, sheet_name: str):
    cache_key = f"{field_name}:{sheet_name}"
    if cache_key in _normative_cache:
        return _normative_cache[cache_key]
    
    rules = database.get_normative_rules_for_field(field_name, sheet_name)
    if rules:
        value = rules[0]["numeric_value"]  # Берем с наивысшей уверенностью
        _normative_cache[cache_key] = value
        return value
    return None
```

---

## 📊 Схема работы (улучшенная)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ИМПОРТ (один раз)                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Файл → Хеш → Проверка дубликата?                          │
│    │              │                                          │
│    │              ├─ ДА → Вернуть существующий ID          │
│    │              │                                          │
│    │              └─ НЕТ → Продолжить импорт               │
│    │                                                         │
│    ├─ Парсинг → Полный текст                                │
│    │                                                         │
│    ├─ AI-анализ → Правила (формулы, нормативы)             │
│    │                                                         │
│    └─ Сохранение в БД:                                      │
│       • Метаданные документа                                │
│       • Полный текст (NEW!)                                │
│       • Результат парсинга (NEW!)                           │
│       • Извлеченные правила                                 │
│       • Связи с полями паспорта                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. ИСПОЛЬЗОВАНИЕ (при необходимости)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Заполнение паспорта → Нужен норматив?                     │
│       │                                                      │
│       ├─ Получить правила для поля                         │
│       │   database.get_normative_rules_for_field(...)       │
│       │                                                      │
│       ├─ Применить норматив в расчетах                      │
│       │   if normative_value:                               │
│       │       validate_against_normative(actual, normative) │
│       │                                                      │
│       └─ Показать пользователю                             │
│          "Факт: 0.18 кВт·ч/м², Норматив: 0.15 кВт·ч/м²"    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3. ПОВТОРНОЕ ИСПОЛЬЗОВАНИЕ                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Нужен текст документа? → database.get_normative_document() │
│       │                                                      │
│       ├─ Получить полный текст                              │
│       │   doc["full_text"]                                  │
│       │                                                      │
│       ├─ Переизвлечь правила (без загрузки файла)          │
│       │   re_extract_rules(doc_id)                          │
│       │                                                      │
│       └─ Поиск по тексту                                    │
│          search_in_document_text(doc_id, query)             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Что нужно доработать

### Приоритет 1 (критично):
1. ✅ Добавить дедупликацию по `file_hash`
2. ✅ Сохранять полный текст в БД
3. ✅ Сохранять результат парсинга в БД

### Приоритет 2 (важно):
4. Кэширование нормативов
5. API для получения полного текста
6. API для переизвлечения правил

### Приоритет 3 (желательно):
7. Поиск по тексту документов
8. Версионирование правил (если документ обновлен)
9. Экспорт нормативов

---

## 💡 Пример использования

```python
# 1. Импорт (один раз)
result = importer.import_normative_document("pkm690.pdf")
# → {"document_id": 1, "status": "processed", "rules_extracted": 15}

# 2. Использование при заполнении паспорта
rules = database.get_normative_rules_for_field(
    "Удельный расход электроэнергии",
    "Динамика ср"
)
normative_value = rules[0]["numeric_value"]  # 0.15

# 3. Валидация данных
actual_value = 0.18
if actual_value > normative_value * 1.1:  # Превышение на 10%
    print(f"⚠️ Превышение норматива: {actual_value} > {normative_value}")

# 4. Получить полный текст (если нужно)
doc = database.get_normative_document(1)
full_text = doc["full_text"]
# Поиск в тексте, переизвлечение правил и т.д.
```

---

**Автор:** Agent-1 (Auto)  
**Дата:** 2025-12-01

