# 📤 Как загрузить нормативный документ

## 🚀 Быстрый старт

### Шаг 1: Запустить сервер

Откройте терминал в директории проекта и выполните:

```bash
cd eaip_full_skeleton/services/ingest
uvicorn main:app --reload --port 8001
```

Или используйте готовый скрипт:
```bash
quick_start.bat
```
(Выберите пункт [2] - Запустить ingest-сервис)

### Шаг 2: Открыть интерфейс

После запуска сервера откройте в браузере:

**Swagger UI (рекомендуется):**
```
http://localhost:8001/docs
```

**Или прямой адрес API:**
```
http://localhost:8001/api/normative/upload
```

---

## 📋 Способы загрузки

### Способ 1: Через Swagger UI (самый простой)

1. Откройте `http://localhost:8001/docs`
2. Найдите endpoint `POST /api/normative/upload`
3. Нажмите **"Try it out"**
4. Нажмите **"Choose File"** и выберите файл (PDF, Word, Excel)
5. Опционально заполните:
   - `title` - название документа (если не указано, берется из имени файла)
   - `document_type` - тип документа (например: "PKM690", "GOST", "SNiP")
6. Нажмите **"Execute"**
7. Посмотрите результат в ответе сервера

### Способ 2: Через curl (командная строка)

```bash
curl -X POST "http://localhost:8001/api/normative/upload" \
  -F "file=@путь/к/файлу.pdf" \
  -F "title=ПКМ №690" \
  -F "document_type=PKM690"
```

**Пример:**
```bash
curl -X POST "http://localhost:8001/api/normative/upload" \
  -F "file=@C:\eaip\data\normative\pkm690.pdf" \
  -F "title=ПКМ №690" \
  -F "document_type=PKM690"
```

### Способ 3: Через Python (скрипт)

```python
import requests

url = "http://localhost:8001/api/normative/upload"

with open("путь/к/файлу.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "title": "ПКМ №690",
        "document_type": "PKM690"
    }
    response = requests.post(url, files=files, data=data)
    print(response.json())
```

### Способ 4: Через Postman

1. Метод: **POST**
2. URL: `http://localhost:8001/api/normative/upload`
3. Body → form-data:
   - `file` (тип: File) - выберите файл
   - `title` (тип: Text, опционально) - название документа
   - `document_type` (тип: Text, опционально) - тип документа
4. Нажмите **Send**

---

## ✅ Что происходит при загрузке

1. **Проверка дубликата** - система проверяет, не загружался ли этот файл ранее (по хешу)
2. **Парсинг документа** - извлечение текста из PDF/Word/Excel
3. **AI-анализ** - извлечение нормативов и формул с помощью AI
4. **Сохранение в БД**:
   - Метаданные документа
   - Полный текст документа
   - Извлеченные правила (нормативы, формулы)
   - Связи с полями энергопаспорта

---

## 📊 Ответ сервера

### Успешная загрузка:
```json
{
  "document_id": 1,
  "title": "ПКМ №690",
  "document_type": "PKM690",
  "status": "processed",
  "rules_extracted": 15,
  "file_path": "C:\\eaip\\data\\inbox\\normative\\pkm690.pdf",
  "filename": "pkm690.pdf"
}
```

### Документ уже загружен (дубликат):
```json
{
  "document_id": 1,
  "title": "ПКМ №690",
  "document_type": "PKM690",
  "status": "duplicate",
  "message": "Документ уже был импортирован ранее (ID=1)",
  "rules_extracted": 15
}
```

### Ошибка:
```json
{
  "detail": "Описание ошибки"
}
```

---

## 🔍 Проверка загруженных документов

### Веб-дашборд:
```
http://localhost:8001/web/normative/dashboard
```

### API для получения списка документов:
```
GET http://localhost:8001/api/normative/documents
```

### API для получения правил:
```
GET http://localhost:8001/api/normative/rules?field_name=Удельный расход
```

---

## ⚠️ Важные замечания

1. **Форматы файлов**: Поддерживаются PDF, Word (.docx), Excel (.xlsx, .xls)
2. **Размер файла**: Максимальный размер ограничен настройками сервера
3. **AI-обработка**: Требуются переменные окружения для AI (DEEPSEEK_API_KEY или OPENAI_API_KEY)
4. **Дубликаты**: Если файл уже загружен, повторная загрузка не создаст дубликат, вернется существующий документ
5. **Время обработки**: Зависит от размера файла и сложности документа (обычно 10-60 секунд)

---

## 🛠️ Устранение проблем

### Сервер не запускается
- Проверьте, что порт 8001 свободен
- Убедитесь, что установлены все зависимости: `pip install -r requirements.txt`

### Ошибка "AI недоступен"
- Проверьте переменные окружения: `DEEPSEEK_API_KEY` или `OPENAI_API_KEY`
- Создайте файл `.env` в директории `eaip_full_skeleton/services/ingest/`

### Файл не загружается
- Проверьте формат файла (должен быть PDF, DOCX, XLSX)
- Проверьте размер файла (не должен превышать лимит)
- Проверьте логи сервера в терминале

---

## 📚 Дополнительная информация

- **Документация API**: `http://localhost:8001/docs`
- **Описание работы импорта**: `docs/NORMATIVE_IMPORT_WORKFLOW.md`
- **Проверка нарушений**: `http://localhost:8001/api/normative/violations`

---

**Дата создания:** 2025-01-16  
**Версия:** 1.0

