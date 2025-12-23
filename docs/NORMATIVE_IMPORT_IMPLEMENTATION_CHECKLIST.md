# ✅ Чеклист подготовки к реализации модуля импорта нормативов

**Дата:** 2025-12-01  
**Статус:** Готово к реализации

---

## 1. ✅ Интеграция AI-моделей

### Текущее состояние:

#### ✅ Настройки AI уже реализованы:
- **Модуль конфигурации:** `eaip_full_skeleton/services/ingest/settings/ai_settings.py`
- **Поддерживаемые провайдеры:** DeepSeek, OpenAI, Anthropic
- **Централизованное управление:** Единый класс `AISettings` для всех AI-модулей

#### Переменные окружения:

**Для DeepSeek (по умолчанию):**
```bash
AI_ENABLED=true
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat  # опционально
```

**Для OpenAI:**
```bash
AI_ENABLED=true
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL_TEXT=gpt-4  # опционально
OPENAI_MODEL_VISION=gpt-4-vision-preview  # опционально
```

**Для Anthropic:**
```bash
AI_ENABLED=true
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-3-opus-20240229  # опционально
```

#### ✅ Проверка конфигурации:
- Модуль `ai_settings.py` автоматически проверяет наличие API ключей
- Функция `has_ai_config()` возвращает статус готовности
- Fallback механизм: для разработки может загружать ключ из `test_deepseek_simple.py`

#### 📝 Рекомендация:
Создать файл `.env.example` в корне проекта с шаблоном переменных окружения (без реальных ключей).

---

## 2. ✅ Схема базы данных

### Структура таблиц уже реализована:

#### Таблица `normative_documents`:
```sql
CREATE TABLE IF NOT EXISTS normative_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                    -- Название документа
    document_type TEXT NOT NULL,             -- Тип: PKM690, GOST, SNiP, PUE, PTEEP, normative
    file_path TEXT NOT NULL,                 -- Путь к файлу
    file_hash TEXT,                          -- SHA1 хеш файла (для дедупликации)
    file_size INTEGER,                       -- Размер файла в байтах
    uploaded_at TEXT NOT NULL,                -- ISO формат даты загрузки
    ai_processed BOOLEAN DEFAULT FALSE,       -- Обработан ли AI
    processing_status TEXT DEFAULT 'pending' -- Статус: pending, processed, partial, error
)
```

#### Таблица `normative_rules`:
```sql
CREATE TABLE IF NOT EXISTS normative_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,             -- Связь с normative_documents
    rule_type TEXT NOT NULL,                  -- Тип: formula, normative, requirement
    description TEXT,                          -- Описание правила
    formula TEXT,                             -- Формула (если есть, например: "Q = A * ΔT / R")
    parameters TEXT,                          -- JSON с параметрами формулы
    numeric_value REAL,                       -- Числовое значение норматива (если есть)
    unit TEXT,                                -- Единица измерения (кВт·ч/м², Гкал и т.д.)
    ai_extracted BOOLEAN DEFAULT FALSE,       -- Извлечено ли AI
    extraction_confidence REAL,                -- Уверенность AI (0.0-1.0)
    created_at TEXT NOT NULL,                 -- ISO формат даты создания
    FOREIGN KEY (document_id) REFERENCES normative_documents(id) ON DELETE CASCADE
)
```

**Пример `parameters` (JSON):**
```json
{
    "A": "площадь, м²",
    "ΔT": "разница температур, °C",
    "R": "сопротивление, м²·°C/Вт"
}
```

#### Таблица `normative_references`:
```sql
CREATE TABLE IF NOT EXISTS normative_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,                -- Связь с normative_rules
    field_name TEXT NOT NULL,                -- Название поля (например: "Удельный расход электроэнергии")
    sheet_name TEXT,                          -- Имя листа Excel (например: "Динамика ср")
    cell_reference TEXT,                      -- Адрес ячейки (например: "C5")
    passport_field_path TEXT,                 -- Путь в структуре данных (например: "resources.electricity.specific_consumption")
    created_at TEXT NOT NULL,                 -- ISO формат даты создания
    FOREIGN KEY (rule_id) REFERENCES normative_rules(id) ON DELETE CASCADE
)
```

### Связи между таблицами:

```
normative_documents (1) ──< (N) normative_rules (1) ──< (N) normative_references
```

- Один документ → много правил
- Одно правило → много связей с полями паспорта (может применяться к разным полям)

### Функции работы с БД (уже реализованы):

```python
# Создание документа
database.create_normative_document(
    title="ПКМ №690",
    document_type="PKM690",
    file_path="/path/to/file.pdf",
    file_hash="sha1_hash",
    file_size=1024000
)

# Создание правила
database.create_normative_rule(
    document_id=1,
    rule_type="formula",
    description="Расчет теплопотерь",
    formula="Q = A * ΔT / R",
    parameters={"A": "площадь, м²", "ΔT": "разница температур, °C"},
    numeric_value=None,
    unit="кВт·ч",
    ai_extracted=True,
    extraction_confidence=0.9
)

# Создание связи с полем
database.create_normative_reference(
    rule_id=1,
    field_name="Удельный расход электроэнергии",
    sheet_name="Динамика ср",
    cell_reference="C5",
    passport_field_path="resources.electricity.specific_consumption"
)

# Получение правил для поля
database.get_normative_rules_for_field(
    field_name="Удельный расход электроэнергии",
    sheet_name="Динамика ср"
)
```

---

## 3. ✅ Тестирование и валидация

### Текущее состояние:

#### ✅ Существующие тесты:
- Папка: `eaip_full_skeleton/services/ingest/tests/`
- Тесты для парсинга, валидации, импорта данных
- **НО:** Специфических тестов для `normative_importer.py` пока нет

### 📋 План тестирования (рекомендуется добавить):

#### Тест 1: Базовый импорт документа
**Файл:** `tests/test_normative_importer_basic.py`

```python
def test_import_pdf_document():
    """Тест импорта PDF документа с AI-анализом"""
    # 1. Загрузить тестовый PDF (например, ПКМ 690)
    # 2. Вызвать import_normative_document()
    # 3. Проверить:
    #    - Документ создан в БД
    #    - Правила извлечены (rules_count > 0)
    #    - Связи с полями созданы
```

#### Тест 2: Извлечение формул
**Файл:** `tests/test_normative_importer_formulas.py`

```python
def test_extract_formulas():
    """Тест извлечения формул из документа"""
    # 1. Документ с формулами (например, СНиП)
    # 2. Проверить:
    #    - Формулы извлечены (rule_type="formula")
    #    - Параметры сохранены корректно (JSON)
    #    - Единицы измерения указаны
```

#### Тест 3: Извлечение нормативов
**Файл:** `tests/test_normative_importer_normatives.py`

```python
def test_extract_normatives():
    """Тест извлечения числовых нормативов"""
    # 1. Документ с нормативами (например, ГОСТ)
    # 2. Проверить:
    #    - Нормативы извлечены (rule_type="normative")
    #    - numeric_value заполнено
    #    - unit указан
```

#### Тест 4: Связи с полями паспорта
**Файл:** `tests/test_normative_importer_references.py`

```python
def test_field_references():
    """Тест автоматического связывания правил с полями"""
    # 1. Документ с упоминаниями полей паспорта
    # 2. Проверить:
    #    - Связи созданы (normative_references не пусто)
    #    - field_name соответствует реальным полям
    #    - sheet_name указан корректно
    #    - passport_field_path заполнен
```

#### Тест 5: Разные форматы файлов
**Файл:** `tests/test_normative_importer_formats.py`

```python
def test_import_word_document():
    """Тест импорта Word документа"""
    
def test_import_excel_document():
    """Тест импорта Excel документа"""
    
def test_import_scanned_pdf():
    """Тест импорта сканированного PDF (с OCR)"""
```

#### Тест 6: Обработка ошибок
**Файл:** `tests/test_normative_importer_errors.py`

```python
def test_ai_unavailable():
    """Тест поведения при недоступном AI"""
    # 1. Отключить AI (AI_ENABLED=false)
    # 2. Попытаться импортировать
    # 3. Проверить: возвращается ошибка или частичный результат
    
def test_invalid_document():
    """Тест обработки некорректного документа"""
    # 1. Поврежденный файл
    # 2. Проверить: обработка ошибки
    
def test_ai_extraction_failure():
    """Тест обработки ошибки AI-извлечения"""
    # 1. Документ, который AI не может обработать
    # 2. Проверить: статус "partial" или "error"
```

#### Тест 7: Валидация данных
**Файл:** `tests/test_normative_importer_validation.py`

```python
def test_validate_extracted_rules():
    """Тест валидации извлеченных правил"""
    # 1. Проверить:
    #    - Формулы валидны (синтаксис)
    #    - Единицы измерения корректны
    #    - Числовые значения в разумных пределах
    #    - Связи с полями существуют в passport_field_mapping
```

### 📝 Рекомендации по тестированию:

1. **Моки для AI:**
   - Создать моки для `ai_parser` чтобы не тратить токены на тесты
   - Использовать фиксированные ответы AI для предсказуемости

2. **Тестовые документы:**
   - Создать папку `tests/fixtures/normative_documents/`
   - Добавить небольшие тестовые PDF/Word/Excel файлы

3. **Интеграционные тесты:**
   - Тесты с реальным AI (опционально, помечать как `@pytest.mark.slow`)
   - Использовать реальные документы из `docs/normatives/`

4. **Покрытие кода:**
   - Цель: >80% покрытия для `normative_importer.py`
   - Проверка всех веток кода (AI доступен/недоступен, успех/ошибка)

---

## ✅ Итоговый статус

### Готово к реализации:
- ✅ AI-интеграция настроена и работает
- ✅ Схема БД реализована и протестирована
- ✅ Функции работы с БД готовы
- ✅ Модуль `normative_importer.py` уже существует и частично реализован

### Рекомендуется добавить:
- 📝 `.env.example` с шаблоном переменных окружения
- 📝 Автоматические тесты для `normative_importer.py`
- 📝 Документацию по использованию API импорта

### Можно начинать:
1. ✅ Проверить работу существующего кода
2. ✅ Добавить недостающие тесты
3. ✅ Улучшить обработку ошибок
4. ✅ Добавить валидацию извлеченных данных

---

**Автор:** Agent-1 (Auto)  
**Дата:** 2025-12-01

