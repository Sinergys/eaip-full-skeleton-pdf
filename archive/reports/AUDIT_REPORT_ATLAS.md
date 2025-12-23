# АУДИТ ТЕКУЩЕГО СОСТОЯНИЯ ПРОЕКТА "АТЛАС"

**Дата проведения:** 2025-01-XX  
**Версия проекта:** v0.3.0  
**Цель аудита:** Подготовка к реализации функционала контроля готовности данных к генерации паспорта

---

## 1. КОНФИГУРАЦИОННАЯ СТРУКТУРА

### Найденные файлы:

#### Основные конфигурационные модули:

1. **`eaip_full_skeleton/services/ingest/config/required_data_matrix.py`**
   - **Назначение:** Матрица обязательных данных для генерации энергетического паспорта
   - **Содержимое:**
     - `REQUIRED_DATA_MATRIX` - словарь с требованиями к ресурсам (energy_resources, infrastructure)
     - `MINIMAL_REQUIREMENTS` - минимальный набор для генерации паспорта
     - Функции: `get_required_resources()`, `get_optional_resources()`, `get_resource_config()`
   - **Структура:**
     ```python
     REQUIRED_DATA_MATRIX = {
         "energy_resources": {
             "electricity": {"required": True, "file_patterns": [...], "min_quarters": 4},
             "gas": {"required": True, ...},
             "water": {"required": False, ...},
             ...
         },
         "infrastructure": {
             "equipment": {"required": False, ...},
             "envelope": {"required": True, ...},
             "nodes": {"required": True, ...}
         }
     }
     ```

2. **`eaip_full_skeleton/services/ingest/settings/ai_settings.py`**
   - **Назначение:** Единый модуль конфигурации AI
   - **Содержимое:**
     - Класс `AISettings` для управления настройками AI
     - Проверка включения AI, выбор провайдера, API ключи
     - Функции: `is_ai_enabled()`, `get_ai_provider()`, `has_ai_config()`

3. **`eaip_full_skeleton/services/ingest/settings/excel_semantic_settings.py`**
   - **Назначение:** Настройки семантического анализа Excel
   - **Содержимое:**
     - Функция `get_excel_semantic_mode()` - режимы: "off", "assist", "strict"

4. **`eaip_full_skeleton/services/ingest/domain/passport_requirements.py`**
   - **Назначение:** Определение обязательных данных для заполнения каждого листа энергопаспорта
   - **Содержимое:**
     - `PASSPORT_SHEET_REQUIREMENTS` - словарь требований к каждому листу
     - Классы: `DataSource`, `FieldRequirement`, `SheetRequirement`
     - Функции: `get_sheet_requirement()`, `validate_sheet_data()`

### Существующие конфигурации:

1. **Матрица обязательных данных** (`config/required_data_matrix.py`):
   - Определяет обязательные и опциональные ресурсы
   - Указывает паттерны имен файлов для каждого ресурса
   - Задает минимальное количество кварталов данных
   - **Минимальные требования:**
     - Обязательные: `electricity`, `gas`, `nodes`, `envelope`
     - Минимум 4 квартала данных
     - Минимальный показатель готовности: 0.6 (60%)

2. **Требования к листам паспорта** (`domain/passport_requirements.py`):
   - Определяет требования для каждого листа Excel-паспорта
   - Указывает источники данных (DB, JSON файлы, default values)
   - Содержит правила валидации для каждого поля

3. **Настройки AI** (`settings/ai_settings.py`):
   - Централизованное управление AI функционалом
   - Поддержка провайдеров: deepseek, openai, anthropic
   - Проверка наличия API ключей

### Рекомендации по размещению:

- ✅ **Текущее размещение оптимально:**
  - `config/` - для матрицы требований к данным
  - `settings/` - для настроек приложения (AI, семантика)
  - `domain/` - для бизнес-логики (требования к паспорту)
- **Для нового функционала:**
  - Можно расширить `config/required_data_matrix.py` для добавления новых требований
  - Или создать `config/readiness_checklist.py` для детального чек-листа готовности

---

## 2. СИСТЕМА ВАЛИДАЦИИ

### Существующие функции валидации:

#### 1. **`utils/readiness_validator.py`** - Основной валидатор готовности

**Функции:**

- **`validate_generation_readiness(enterprise_id: int) -> Dict[str, Any]`** (строки 31-226)
  - Проверяет готовность данных для генерации энергетического паспорта
  - Возвращает:
    - `ready`: bool - готовность к генерации
    - `completeness_score`: float (0.0-1.0) - показатель готовности
    - `missing_resources`: List[str] - недостающие ресурсы
    - `missing_files`: List[str] - недостающие файлы
    - `available_resources`: List[str] - доступные ресурсы
    - `warnings`: List[str] - предупреждения
    - `progress_percentage`: int - процент готовности
    - `required_resources_status`: Dict - детальный статус обязательных ресурсов
    - `optional_resources_status`: Dict - детальный статус опциональных ресурсов
    - `sheet_validation`: Dict - валидация по листам (НОВОЕ)
    - `missing_sheet_data`: List[str] - недостающие данные для листов (НОВОЕ)

- **`get_upload_checklist(enterprise_id: int) -> Dict[str, Any]`** (строки 545-648)
  - Возвращает чек-лист требуемых файлов для предприятия
  - Возвращает:
    - `required_files`: List[Dict] - обязательные файлы с статусом загрузки
    - `optional_files`: List[Dict] - опциональные файлы
    - `uploaded_files`: List[str] - загруженные файлы
    - `missing_required`: List[str] - недостающие обязательные файлы

- **`_validate_sheets_data()`** (строки 651-778)
  - Валидирует данные для каждого листа паспорта
  - Использует `PASSPORT_SHEET_REQUIREMENTS` из `domain/passport_requirements.py`
  - Проверяет наличие критических полей для каждого листа

#### 2. **`utils/data_validator.py`** - Валидатор агрегированных данных

**Класс `DataValidator`:**

- **`validate() -> Tuple[bool, List[str], List[str]]`** (строки 81-104)
  - Выполняет полную валидацию данных
  - Возвращает: (is_valid, errors, warnings)
  - Проверяет:
    - Структуру данных
    - Каждый ресурс и квартал
    - Целостность данных между ресурсами

- **`validate_data_for_template()`** (строки 307-330)
  - Валидирует данные перед заполнением шаблона
  - Может выбрасывать исключение при ошибках

#### 3. **`domain/passport_requirements.py`** - Валидация по листам

**Функции:**

- **`validate_sheet_data(sheet_name: str, data: Dict[str, Any]) -> tuple[bool, List[str]]`** (строки 565-630)
  - Валидирует данные для заполнения конкретного листа
  - Проверяет наличие критических полей
  - Применяет правила валидации (min_count, min_value, min_quarters)

- **`evaluate_generation_readiness(canonical: Optional[CanonicalSourceData]) -> GenerationReadinessResult`** (строки 113-156)
  - Оценка готовности на основе CanonicalSourceData
  - Возвращает статус: "ready", "partially_ready", "blocked"

### Примеры использования:

```python
# Пример 1: Проверка готовности предприятия
from utils.readiness_validator import validate_generation_readiness

readiness = validate_generation_readiness(enterprise_id=1)
if readiness["ready"]:
    print(f"Готовность: {readiness['progress_percentage']}%")
else:
    print(f"Недостающие ресурсы: {readiness['missing_resources']}")

# Пример 2: Получение чек-листа
from utils.readiness_validator import get_upload_checklist

checklist = get_upload_checklist(enterprise_id=1)
for file in checklist["required_files"]:
    status = "✅" if file["uploaded"] else "❌"
    print(f"{status} {file['description']}")

# Пример 3: Валидация данных перед генерацией
from utils.data_validator import validate_data_for_template

is_valid, errors, warnings = validate_data_for_template(aggregated_data)
if not is_valid:
    print("Ошибки:", errors)
```

### Пробелы в валидации:

1. **Нет централизованной блокировки генерации:**
   - Endpoint `/api/generate-passport/{batch_id}` не проверяет готовность перед генерацией
   - Нужно добавить проверку `validate_generation_readiness()` перед генерацией

2. **Нет UI компонента для отображения чек-листа готовности:**
   - В `results.html` есть базовый чек-лист файлов, но нет детального чек-листа готовности
   - Нужна страница/секция с полным чек-листом готовности

3. **Валидация по листам не интегрирована в UI:**
   - `sheet_validation` возвращается в API, но не отображается в UI
   - Нужно добавить отображение статуса каждого листа

4. **Нет валидации перед генерацией на уровне API:**
   - Endpoint генерации не блокирует при недостаточных данных
   - Нужно добавить middleware или проверку в endpoint

---

## 3. API ENDPOINTS

### Существующие endpoints для загрузок:

#### Endpoints для работы с предприятиями:

1. **`GET /api/enterprises`** (строка 529)
   - Получить список предприятий

2. **`POST /api/enterprises`** (строка 534)
   - Создать новое предприятие

3. **`GET /api/enterprises/{enterprise_id}/uploads`** (строка 540)
   - Получить список загрузок предприятия

4. **`GET /api/enterprises/{enterprise_id}/upload-checklist`** (строка 549)
   - Получить чек-лист требуемых файлов для предприятия
   - **Возвращает:** `get_upload_checklist(enterprise_id)`

5. **`GET /api/enterprises/{enterprise_id}/generation-readiness`** (строка 569)
   - Получить статус готовности данных для генерации паспорта
   - **Возвращает:** `validate_generation_readiness(enterprise_id)`
   - **Структура ответа:**
     ```json
     {
       "enterprise_id": 1,
       "enterprise_name": "Предприятие",
       "ready": false,
       "completeness_score": 0.75,
       "missing_resources": ["water"],
       "missing_files": ["voda.xlsx"],
       "available_resources": ["electricity", "gas", "nodes", "envelope"],
       "warnings": ["..."],
       "progress_percentage": 75,
       "required_resources_status": {...},
       "optional_resources_status": {...},
       "sheet_validation": {...},
       "missing_sheet_data": [...]
     }
     ```

#### Endpoints для работы с загрузками:

6. **`GET /api/uploads/{batch_id}`** (строка 596)
   - Получить информацию о загрузке

7. **`GET /api/uploads/{batch_id}/editable`** (строка 604)
   - Получить редактируемый текст загрузки

8. **`POST /api/uploads/{batch_id}/editable`** (строка 616)
   - Обновить редактируемый текст загрузки

#### Endpoints для парсинга и валидации:

9. **`GET /ingest/parse/{batch_id}`** (строка 623)
   - Получить результаты парсинга загрузки

10. **`GET /ingest/parse/{batch_id}/summary`** (строка 748)
    - Получить краткую сводку парсинга

11. **`POST /ingest/validate`** (строка 777)
    - Валидация данных загрузки

#### Endpoints для генерации:

12. **`POST /api/generate-passport/{batch_id}`** (строка 1451)
    - Генерация энергетического паспорта
    - **⚠️ ПРОБЛЕМА:** Не проверяет готовность данных перед генерацией
    - **Нужно добавить:** Проверку `validate_generation_readiness()` перед генерацией

13. **`POST /api/generate-word-report/{batch_id}`** (строка 2180)
    - Генерация Word отчета

#### Endpoints для готовности (на основе CanonicalSourceData):

14. **`GET /api/batches/{batch_id}/generation-readiness`** (строка 168)
    - Оценка готовности на основе CanonicalSourceData
    - Использует `evaluate_generation_readiness()` из `domain/passport_requirements.py`
    - **Возвращает:**
      ```json
      {
        "batch_id": "...",
        "overall_status": "ready|partially_ready|blocked",
        "missing_required": [...],
        "missing_optional": [...],
        "notes": [...]
      }
      ```

15. **`GET /api/batches/{batch_id}/canonical-debug`** (строка 206)
    - Отладочный endpoint для просмотра CanonicalSourceData

#### Endpoints для загрузки файлов:

16. **`POST /web/upload`** (строка 860)
    - Веб-форма загрузки файла

17. **`POST /ingest/files`** (строка 2398)
    - API загрузка файлов

#### Endpoints для прогресса:

18. **`GET /api/progress/{batch_id}`** (строка 631)
    - Получить прогресс обработки файла

19. **`POST /web/upload/{batch_id}/cancel`** (строка 662)
    - Отмена обработки файла

#### Endpoints для нормативных документов:

20. **`POST /api/normative/upload`** (строка 2480)
    - Загрузка нормативного документа

21. **`GET /api/normative/documents`** (строка 2624)
    - Список нормативных документов

22. **`GET /api/normative/rules/{rule_type}`** (строка 2635)
    - Получить правила по типу

23. **`GET /api/normative/rules/for-field/{field_name}`** (строка 2646)
    - Получить правила для поля

#### Служебные endpoints:

24. **`GET /health`** (строка 399)
    - Проверка здоровья сервиса

25. **`GET /api/diagnose/pdf`** (строка 710)
    - Диагностика PDF файла

### Структура ответов:

#### Ответ `GET /api/enterprises/{enterprise_id}/generation-readiness`:
```json
{
  "enterprise_id": 1,
  "enterprise_name": "ООО Предприятие",
  "ready": false,
  "completeness_score": 0.75,
  "missing_resources": ["water"],
  "missing_files": ["voda.xlsx"],
  "available_resources": ["electricity", "gas", "nodes", "envelope"],
  "available_files": ["pererashod.xlsx", "gaz.xlsx", "uzly_ucheta.xlsx"],
  "warnings": [
    "Ресурс water: недостаточно кварталов (2 из 4)"
  ],
  "progress_percentage": 75,
  "required_resources_status": {
    "electricity": {
      "available": true,
      "quarters_count": 4,
      "min_quarters": 4,
      "has_enough_quarters": true,
      "description": "Электроэнергия - обязательный ресурс"
    },
    "water": {
      "available": false,
      "quarters_count": 0,
      "min_quarters": 4,
      "has_enough_quarters": false,
      "description": "Водоснабжение - опциональный ресурс"
    }
  },
  "optional_resources_status": {...},
  "sheet_validation": {
    "Struktura pr2": {
      "valid": true,
      "required": true,
      "errors": [],
      "description": "Структура потребления энергоресурсов по кварталам"
    },
    "Equipment": {
      "valid": false,
      "required": false,
      "errors": ["Отсутствует equipment.sections"],
      "description": "Перечень основного оборудования"
    }
  },
  "missing_sheet_data": ["Equipment: Отсутствует equipment.sections"]
}
```

### Возможности расширения:

1. **Добавить endpoint для детального чек-листа готовности:**
   - `GET /api/enterprises/{enterprise_id}/readiness-checklist`
   - Возвращает детальный чек-лист с разбивкой по листам паспорта

2. **Добавить endpoint для блокировки генерации:**
   - `GET /api/enterprises/{enterprise_id}/can-generate`
   - Простая проверка: можно ли генерировать паспорт

3. **Расширить endpoint генерации:**
   - Добавить проверку готовности в `POST /api/generate-passport/{batch_id}`
   - Возвращать ошибку 400 если данные не готовы

---

## 4. СТРУКТУРА ДАННЫХ

### Таблица uploads:

**Схема:** `eaip_full_skeleton/services/ingest/database.py` (строки 35-48)

```sql
CREATE TABLE uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL UNIQUE,
    enterprise_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT,
    file_size INTEGER,
    status TEXT NOT NULL,
    parsing_summary TEXT,  -- JSON строка
    created_at TEXT NOT NULL,
    FOREIGN KEY (enterprise_id) REFERENCES enterprises(id)
)
```

**Поля:**
- `id` - первичный ключ
- `batch_id` - уникальный идентификатор загрузки (UUID)
- `enterprise_id` - ссылка на предприятие
- `filename` - имя файла
- `file_type` - тип файла (xlsx, pdf, docx, jpg, png)
- `file_size` - размер файла в байтах
- `status` - статус обработки (см. ниже)
- `parsing_summary` - JSON строка с результатами парсинга
- `created_at` - дата создания (ISO format)

### Таблица parsed_data:

**Схема:** `database.py` (строки 51-58)

```sql
CREATE TABLE parsed_data (
    upload_id INTEGER PRIMARY KEY,
    raw_json TEXT,  -- JSON строка с распарсенными данными
    editable_text TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (upload_id) REFERENCES uploads(id)
)
```

**Поля:**
- `upload_id` - ссылка на uploads.id
- `raw_json` - JSON строка с полными распарсенными данными
  - Может содержать `canonical_source` (CanonicalSourceData)
  - Содержит структурированные данные из файла
- `editable_text` - редактируемый текст для пользователя
- `updated_at` - дата обновления

### Таблица enterprises:

**Схема:** `database.py` (строки 26-32)

```sql
CREATE TABLE enterprises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
)
```

### Таблица uploads_storage:

**Схема:** `database.py` (строки 62-68)

```sql
CREATE TABLE uploads_storage (
    upload_id INTEGER PRIMARY KEY,
    file_hash TEXT,
    file_mtime REAL,
    FOREIGN KEY (upload_id) REFERENCES uploads(id)
)
```

**Назначение:** Хранение метаданных файлов для дедупликации

### Статусы обработки:

**Используемые статусы** (из кода):
- `"pending"` - ожидает обработки
- `"processing"` - в процессе обработки
- `"success"` - успешно обработано
- `"error"` - ошибка обработки
- `"cancelled"` - отменено пользователем

### Хранение метаданных:

1. **`parsing_summary`** (в таблице `uploads`):
   - JSON строка с результатами парсинга
   - Содержит информацию о распознанных данных
   - Используется для быстрого доступа к метаданным

2. **`raw_json`** (в таблице `parsed_data`):
   - Полные распарсенные данные
   - Может содержать `canonical_source` (CanonicalSourceData)
   - Используется для генерации паспорта

3. **Агрегированные JSON файлы:**
   - Путь: `data/aggregated/` или `INBOX_DIR/aggregated/`
   - Формат: `{batch_id}_aggregated.json`
   - Содержит агрегированные данные по ресурсам и кварталам
   - Дополнительные файлы:
     - `{batch_id}_equipment.json` - данные об оборудовании
     - `{batch_id}_envelope.json` - расчет теплопотерь
     - `{batch_id}_nodes.json` - узлы учета
     - `usage_categories.json` - категории потребления

### Структура `raw_json`:

Пример структуры (из кода):
```json
{
  "canonical_source": {
    "resources": [...],
    "equipment": [...],
    "nodes": [...],
    "envelope": [...],
    "provenance": {...}
  },
  "parsed_data": {...},
  "aggregated": {...}
}
```

### Структура `parsing_summary`:

Пример (из кода):
```json
{
  "file_type": "xlsx",
  "sheets": [...],
  "resources_detected": ["electricity", "gas"],
  "status": "success"
}
```

---

## 5. UI КОМПОНЕНТЫ

### Существующие компоненты статуса:

#### 1. **`web/results.html`** - Страница результатов распознавания

**Компоненты:**

- **Чек-лист файлов** (строки 93-123, 286, 467-558):
  - Контейнер: `#checklistContainer`
  - Функция: `renderChecklist(checklistData)`
  - Отображает:
    - Обязательные файлы с иконками (✅/❌)
    - Опциональные файлы
    - Статус загрузки каждого файла
    - Паттерны имен файлов

- **Прогресс-бар готовности** (строки 74-92):
  - Класс: `.progress-bar`
  - Отображает процент готовности
  - Используется для визуализации `progress_percentage`

- **Предупреждения** (строки 127-143):
  - Класс: `.warnings`
  - Отображает список предупреждений из `warnings`

**JavaScript функции:**

- **`loadReadiness(enterpriseId)`** (строки 467-508):
  - Загружает данные готовности через API
  - Вызывает:
    - `GET /api/enterprises/{enterprise_id}/upload-checklist`
    - `GET /api/enterprises/{enterprise_id}/generation-readiness`
  - Рендерит чек-лист файлов

- **`renderChecklist(checklistData)`** (строки 510-558):
  - Рендерит чек-лист файлов
  - Показывает обязательные и опциональные файлы
  - Отображает статус загрузки

#### 2. **`web/upload.html`** - Страница загрузки файлов

**Компоненты:**

- **Прогресс обработки** (строки 110-150):
  - Контейнер: `.progress-container`
  - Отображает прогресс обработки файла
  - Использует `GET /api/progress/{batch_id}`

- **Статус загрузки** (строки 91-109):
  - Класс: `.status`
  - Отображает успех/ошибку загрузки

**JavaScript функции:**

- **`pollProgress(batchId)`** - опрос прогресса обработки
- **`handleUpload()`** - обработка загрузки файла

### Структура шаблонов:

1. **`web/upload.html`**:
   - Форма загрузки файла
   - Выбор предприятия
   - Прогресс обработки
   - Статус загрузки

2. **`web/results.html`**:
   - Метаданные загрузки
   - Чек-лист файлов
   - Прогресс готовности
   - Предупреждения
   - Кнопка генерации паспорта

3. **`web/normative_upload.html`**:
   - Загрузка нормативных документов

### JavaScript функции:

#### Из `results.html`:

```javascript
// Загрузка данных готовности
async function loadReadiness(enterpriseId) {
    const [checklistData, readinessData] = await Promise.all([
        fetchJSON(`/api/enterprises/${enterpriseId}/upload-checklist`),
        fetchJSON(`/api/enterprises/${enterpriseId}/generation-readiness`)
    ]);
    // Рендерит чек-лист и прогресс
}

// Рендеринг чек-листа
function renderChecklist(checklistData) {
    // Рендерит обязательные и опциональные файлы
    // Показывает статус загрузки каждого файла
}
```

#### Из `upload.html`:

```javascript
// Опрос прогресса
async function pollProgress(batchId) {
    const progress = await fetchJSON(`/api/progress/${batchId}`);
    // Обновляет прогресс-бар
}

// Обработка загрузки
async function handleUpload() {
    // Загружает файл через POST /web/upload
    // Начинает опрос прогресса
}
```

### Пробелы в UI:

1. **Нет детального чек-листа готовности:**
   - Текущий чек-лист показывает только файлы
   - Нет отображения статуса каждого листа паспорта
   - Нет детальной информации о недостающих данных

2. **Нет блокировки генерации в UI:**
   - Кнопка генерации не проверяет готовность
   - Нет визуальной индикации, почему генерация невозможна

3. **Нет отображения `sheet_validation`:**
   - API возвращает `sheet_validation`, но UI не использует
   - Нужно добавить секцию с валидацией каждого листа

4. **Нет индикации недостающих данных:**
   - `missing_sheet_data` не отображается в UI
   - Нужно показать, какие именно данные отсутствуют для каждого листа

---

## РЕКОМЕНДАЦИИ ПО ИНТЕГРАЦИИ

### Минимальные изменения:

1. **Добавить проверку готовности в endpoint генерации:**
   ```python
   @app.post("/api/generate-passport/{batch_id}")
   def api_generate_passport(batch_id: str, ...):
       # Получить enterprise_id из upload
       upload = database.get_upload_by_batch(batch_id)
       enterprise_id = upload["enterprise_id"]
       
       # Проверить готовность
       readiness = validate_generation_readiness(enterprise_id)
       if not readiness["ready"]:
           raise HTTPException(
               status_code=400,
               detail={
                   "message": "Данные не готовы к генерации",
                   "readiness": readiness
               }
           )
       
       # Продолжить генерацию...
   ```

2. **Добавить UI компонент для детального чек-листа:**
   - Расширить `results.html` секцией с валидацией листов
   - Отобразить `sheet_validation` для каждого листа
   - Показать `missing_sheet_data` с конкретными ошибками

3. **Добавить endpoint для быстрой проверки:**
   ```python
   @app.get("/api/enterprises/{enterprise_id}/can-generate")
   def api_can_generate(enterprise_id: int):
       readiness = validate_generation_readiness(enterprise_id)
       return {
           "can_generate": readiness["ready"],
           "reason": "..." if not readiness["ready"] else None
       }
   ```

### Оптимальный подход:

1. **Создать отдельную страницу/секцию "Готовность к генерации":**
   - URL: `/web/readiness/{enterprise_id}`
   - Показывает:
     - Общий статус готовности
     - Прогресс-бар
     - Чек-лист файлов
     - Валидацию по листам
     - Список недостающих данных
     - Кнопку генерации (заблокирована если не готово)

2. **Интегрировать проверку в существующие страницы:**
   - В `results.html` добавить секцию с детальным чек-листом
   - Показывать предупреждения о недостающих данных
   - Блокировать кнопку генерации если данные не готовы

3. **Добавить middleware для проверки готовности:**
   - Опционально: декоратор для endpoints генерации
   - Автоматическая проверка перед генерацией

### Потенциальные конфликты:

1. **Два разных подхода к оценке готовности:**
   - `validate_generation_readiness()` - на основе агрегированных данных
   - `evaluate_generation_readiness()` - на основе CanonicalSourceData
   - **Решение:** Использовать `validate_generation_readiness()` как основной, т.к. он более полный

2. **Разные источники данных:**
   - `validate_generation_readiness()` использует агрегированные JSON файлы
   - `evaluate_generation_readiness()` использует CanonicalSourceData из raw_json
   - **Решение:** Приоритет агрегированным данным, fallback на CanonicalSourceData

3. **Конфликт имен endpoints:**
   - `/api/batches/{batch_id}/generation-readiness` - для batch_id
   - `/api/enterprises/{enterprise_id}/generation-readiness` - для enterprise_id
   - **Решение:** Использовать enterprise_id как основной, т.к. готовность проверяется на уровне предприятия

---

## ВЫВОДЫ

### Текущее состояние:

✅ **Хорошо реализовано:**
- Матрица обязательных данных (`config/required_data_matrix.py`)
- Валидатор готовности (`utils/readiness_validator.py`)
- API endpoints для проверки готовности
- Базовая валидация данных (`utils/data_validator.py`)
- Требования к листам паспорта (`domain/passport_requirements.py`)

⚠️ **Требует доработки:**
- Нет блокировки генерации при недостаточных данных
- Нет детального UI для отображения готовности
- Нет интеграции валидации листов в UI
- Endpoint генерации не проверяет готовность

### Рекомендуемый план действий:

1. **Фаза 1: Блокировка генерации (критично)**
   - Добавить проверку готовности в `POST /api/generate-passport/{batch_id}`
   - Возвращать ошибку 400 если данные не готовы
   - Добавить проверку в UI перед отправкой запроса

2. **Фаза 2: Детальный UI (важно)**
   - Создать секцию в `results.html` с детальным чек-листом
   - Отобразить валидацию каждого листа
   - Показать недостающие данные с конкретными ошибками

3. **Фаза 3: Улучшения (желательно)**
   - Добавить endpoint `/api/enterprises/{id}/can-generate` для быстрой проверки
   - Создать отдельную страницу готовности
   - Добавить автоматическое обновление статуса готовности

---

**Конец отчета**

