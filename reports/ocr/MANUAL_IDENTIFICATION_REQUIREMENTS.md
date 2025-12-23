# ТРЕБОВАНИЯ: РУЧНАЯ ИДЕНТИФИКАЦИЯ ДОКУМЕНТОВ

**Дата:** 2025-11-29  
**Статус:** Требования к разработке

---

## ЦЕЛЬ

Добавить процедуру ручной идентификации для документов, которые не прошли автоматическое распознавание OCR.

---

## ПРОБЛЕМА

При автоматическом распознавании некоторые документы:
- Имеют низкий confidence (< порога)
- Не извлекаются таблицы (ошибки парсинга JSON)
- Имеют частичное распознавание
- Требуют ручной проверки и корректировки

---

## РЕШЕНИЕ: РУЧНАЯ ИДЕНТИФИКАЦИЯ

### Процесс работы

1. **Автоматическое распознавание** → OCR модуль обрабатывает документ
2. **Проверка качества** → Если confidence < порога ИЛИ таблицы не извлечены → флаг `requires_manual_review`
3. **Ручная идентификация** → Пользователь просматривает документ и вводит данные
4. **Сохранение результатов** → Результаты сохраняются и используются для улучшения алгоритмов

---

## ФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ

### 1. Определение необходимости ручной проверки

**Условия для флага `requires_manual_review = true`:**

- Confidence < порога (из `config/ocr.yml`)
- Таблицы не извлечены (0 таблиц, но документ содержит таблицы)
- Частичный парсинг JSON (уровень 4)
- Ошибки обработки (критические)

**Критерии:**
```yaml
manual_review:
  enabled: true
  triggers:
    - low_confidence: true  # confidence < min_confidence
    - no_tables: true       # 0 таблиц при ожидании таблиц
    - partial_parse: true    # частичный парсинг JSON
    - critical_error: true  # критические ошибки
```

---

### 2. Веб-интерфейс для ручной идентификации

#### 2.1. Список документов, требующих проверки

**Endpoint:** `GET /api/ocr/manual-review/list`

**Ответ:**
```json
{
  "total": 5,
  "files": [
    {
      "batch_id": "abc123",
      "file_name": "акт выполненых работ май.PDF",
      "file_path": "/path/to/file",
      "review_reason": "low_confidence",
      "confidence": 0.50,
      "extracted_text": "...",
      "extracted_tables": [],
      "status": "pending",  // pending, in_progress, completed
      "reviewed_by": null,
      "reviewed_at": null
    }
  ]
}
```

#### 2.2. Просмотр документа для проверки

**Endpoint:** `GET /api/ocr/manual-review/{batch_id}/view`

**Ответ:**
```json
{
  "file_info": {
    "batch_id": "abc123",
    "file_name": "акт выполненых работ май.PDF",
    "file_size_kb": 211.9,
    "pages_count": 1
  },
  "ocr_result": {
    "confidence": 0.50,
    "text": "извлеченный текст...",
    "tables": [],
    "warnings": ["Частичный парсинг JSON", "Низкий confidence"]
  },
  "document_preview": {
    "pages": [
      {
        "page_number": 1,
        "image_url": "/api/files/preview/abc123/page1.png",
        "thumbnail_url": "/api/files/preview/abc123/page1_thumb.png"
      }
    ]
  }
}
```

#### 2.3. Сохранение результатов ручной проверки

**Endpoint:** `POST /api/ocr/manual-review/{batch_id}/submit`

**Тело запроса:**
```json
{
  "reviewer_notes": "Документ содержит таблицу с данными о выполненных работах",
  "corrected_text": "исправленный текст...",
  "corrected_tables": [
    {
      "rows": [["...", "..."], ...],
      "headers": ["...", "..."]
    }
  ],
  "document_type": "акт выполненных работ",
  "issues_found": [
    "Таблица не была извлечена из-за ошибки парсинга JSON",
    "Низкое качество скана"
  ],
  "suggestions": [
    "Улучшить парсинг JSON для вложенных структур",
    "Добавить более агрессивную предобработку"
  ]
}
```

**Ответ:**
```json
{
  "success": true,
  "batch_id": "abc123",
  "status": "completed",
  "reviewed_at": "2025-11-29T21:30:00Z"
}
```

---

### 3. UI компоненты

#### 3.1. Страница списка документов для проверки

**Путь:** `/ocr/manual-review`

**Элементы:**
- Таблица с документами, требующими проверки
- Фильтры: по статусу, по причине проверки, по дате
- Поиск по имени файла
- Кнопка "Начать проверку" для каждого документа

#### 3.2. Страница ручной проверки документа

**Путь:** `/ocr/manual-review/{batch_id}`

**Элементы:**
- **Левая панель:**
  - Превью документа (изображения страниц)
  - Навигация по страницам
  - Zoom in/out
  
- **Центральная панель:**
  - Извлеченный текст (редактируемый)
  - Извлеченные таблицы (редактируемые)
  - Поля для ввода:
    - Тип документа
    - Заметки проверяющего
    - Найденные проблемы
    - Предложения по улучшению
  
- **Правая панель:**
  - Информация о документе
  - Статистика OCR (confidence, количество символов, таблиц)
  - Предупреждения и ошибки
  - История проверок (если есть)

- **Нижняя панель:**
  - Кнопка "Сохранить и продолжить"
  - Кнопка "Отправить на проверку"
  - Кнопка "Пропустить" (если не требует проверки)

---

### 4. Backend API

#### 4.1. Модель данных

**Таблица:** `ocr_manual_reviews`

```sql
CREATE TABLE IF NOT EXISTS ocr_manual_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id VARCHAR(255) NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    review_reason VARCHAR(50) NOT NULL,  -- low_confidence, no_tables, partial_parse, critical_error
    confidence FLOAT,
    extracted_text TEXT,
    extracted_tables JSONB,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, in_progress, completed, skipped
    reviewer_notes TEXT,
    corrected_text TEXT,
    corrected_tables JSONB,
    document_type VARCHAR(100),
    issues_found TEXT[],
    suggestions TEXT[],
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ocr_manual_reviews_batch_id ON ocr_manual_reviews(batch_id);
CREATE INDEX idx_ocr_manual_reviews_status ON ocr_manual_reviews(status);
CREATE INDEX idx_ocr_manual_reviews_review_reason ON ocr_manual_reviews(review_reason);
```

#### 4.2. Интеграция в OCR модуль

**Файл:** `eaip_full_skeleton/services/ingest/utils/gemini_vision_ocr.py`

**Изменения:**
```python
def extract_with_gemini_vision(...) -> dict:
    result = {...}
    
    # Проверка необходимости ручной проверки
    requires_manual_review = False
    review_reasons = []
    
    if result.get("confidence", 0) < config.get("manual_review", {}).get("min_confidence", 0.70):
        requires_manual_review = True
        review_reasons.append("low_confidence")
    
    if result.get("parse_level", 0) == 4:  # Частичный парсинг
        requires_manual_review = True
        review_reasons.append("partial_parse")
    
    if result.get("tables_count", 0) == 0 and document_has_tables:  # Нужна эвристика
        requires_manual_review = True
        review_reasons.append("no_tables")
    
    result["requires_manual_review"] = requires_manual_review
    result["review_reasons"] = review_reasons
    
    # Сохранение в БД для ручной проверки
    if requires_manual_review:
        save_for_manual_review(batch_id, file_path, result)
    
    return result
```

---

### 5. Интеграция в веб-интерфейс

#### 5.1. Добавление в главное меню

**Файл:** `eaip_full_skeleton/services/ingest/web/templates/base.html`

```html
<li>
  <a href="/ocr/manual-review">
    Ручная проверка OCR
    <span class="badge" id="manual-review-count">0</span>
  </a>
</li>
```

#### 5.2. Уведомления

**Показывать уведомление:**
- При загрузке нового файла, требующего проверки
- В реальном времени (WebSocket или polling)

---

### 6. Работа в Cursor (чат)

#### 6.1. Процесс

1. **AI определяет проблемный файл:**
   ```
   📋 Файл требует ручной проверки: акт выполненых работ май.PDF
   Причина: low_confidence (0.50), partial_parse (таблицы не извлечены)
   ```

2. **Пользователь просматривает файл вручную:**
   - Открывает файл
   - Просматривает содержимое
   - Определяет проблемы

3. **Пользователь сообщает в чат:**
   ```
   Файл содержит:
   - Таблицу с данными о выполненных работах
   - 5 столбцов: №, Наименование, Количество, Цена, Сумма
   - Проблема: таблица не извлечена из-за ошибки парсинга JSON
   ```

4. **AI анализирует и предлагает решение:**
   ```
   Анализ:
   - Таблица должна быть извлечена
   - Проблема: вложенные структуры в JSON не обрабатываются
   - Решение: улучшить парсер JSON для вложенных структур
   ```

5. **Совместное утверждение:**
   - Пользователь подтверждает решение
   - AI реализует улучшение
   - Тестирование на проблемном файле

---

## ТЕХНИЧЕСКИЕ ДЕТАЛИ

### Конфигурация

**Файл:** `config/ocr.yml`

```yaml
# Настройки ручной проверки
manual_review:
  enabled: true
  min_confidence: 0.70  # Минимальный confidence для автоматического прохождения
  triggers:
    low_confidence: true
    no_tables: true
    partial_parse: true
    critical_error: true
  auto_save: true  # Автоматически сохранять для проверки
  notification: true  # Уведомления о новых файлах
```

### API Endpoints

1. `GET /api/ocr/manual-review/list` - Список файлов для проверки
2. `GET /api/ocr/manual-review/{batch_id}/view` - Просмотр документа
3. `POST /api/ocr/manual-review/{batch_id}/submit` - Сохранение результатов
4. `GET /api/ocr/manual-review/stats` - Статистика проверок
5. `POST /api/ocr/manual-review/{batch_id}/skip` - Пропустить проверку

---

## ПРИОРИТЕТЫ РЕАЛИЗАЦИИ

### Этап 1: Backend (1-2 дня)
1. Добавить модель данных `ocr_manual_reviews`
2. Интегрировать проверку в OCR модуль
3. Создать API endpoints
4. Добавить конфигурацию

### Этап 2: Веб-интерфейс (2-3 дня)
1. Создать страницу списка документов
2. Создать страницу ручной проверки
3. Добавить редакторы текста и таблиц
4. Интегрировать в главное меню

### Этап 3: Интеграция в Cursor (1 день)
1. Создать команды для работы в чате
2. Добавить анализ проблемных файлов
3. Реализовать процесс совместной работы

---

## КРИТЕРИИ ПРИЕМКИ

- ✅ Документы с низким confidence автоматически помечаются для проверки
- ✅ Веб-интерфейс позволяет просматривать и редактировать результаты OCR
- ✅ Результаты ручной проверки сохраняются в БД
- ✅ Работа в Cursor чате позволяет совместно анализировать проблемы
- ✅ Уведомления о новых файлах для проверки
- ✅ Статистика по проверкам доступна

---

**Статус:** Требования определены, готово к реализации

