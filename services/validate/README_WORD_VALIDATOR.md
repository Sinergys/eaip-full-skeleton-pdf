# Word Document Validator Service

Автоматизированная проверка текстовых отчётов энергоаудита на соответствие требованиям ПКМ №690.

## 🎯 Функциональность

- ✅ Валидация DOCX файлов (до 100MB)
- ✅ Кеширование результатов (SHA-256)
- ✅ Двухуровневая AI проверка (Ollama + DeepSeek)
- ✅ **Гибкий парсинг DeepSeek** - работает с различными форматами ответов
- ✅ Форматирование по ГОСТ стандартам
- ✅ Генерация рекомендаций по доработке

## 📋 Требования

### Обязательные переменные окружения:

```bash
DEEPSEEK_API_KEY=your_api_key_here
```

### Опциональные:

```bash
# Пути
TEMP_DIR=/tmp
GOST_TEMPLATE_PATH=path/to/template.docx

# AI конфигурация
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3-coder:480b-cloud
DEEPSEEK_MODEL=deepseek-chat
CHUNK_SIZE_TOKENS=20000

# Кеш
CACHE_ENABLED=true
CACHE_TTL_DAYS=30
```

## 🚀 Быстрый старт

### 1. Установка зависимостей:

```bash
pip install -r requirements.txt
```

### 2. Настройка окружения:

```bash
cp .env.example .env
# Отредактируйте .env, добавьте DEEPSEEK_API_KEY
```

### 3. Запуск сервиса:

```bash
uvicorn main:app --reload --port 8003
```

## 📡 API Endpoints

### POST `/api/v1/check-report/`

Загрузка и проверка Word документа.

**Request:**
```bash
curl -X POST "http://localhost:8003/api/v1/check-report/" \
  -F "file=@report.docx"
```

**Response:**
```json
{
  "message": "Обработка завершена",
  "file_path": "/path/to/report_Проверенный.docx",
  "from_cache": false,
  "processing_time_seconds": 245.3,
  "file_hash": "a1b2c3..."
}
```

## 🏗️ Архитектура

```
services/validate/
├── api/v1/endpoints/     # FastAPI endpoints
├── services/             # Business logic
│   ├── orchestrator.py   # Main coordinator
│   ├── docx_processor.py # Word document handling
│   ├── ai_processor.py   # Ollama + DeepSeek (flexible parsing)
│   └── assembler.py      # Final document creation
├── core/                 # Config, models, constants
├── db/                   # Cache management
└── utils/                # Helpers, prompts, exceptions
```

## 📊 Процесс обработки

1. **Валидация**: Проверка формата, размера, хеша
2. **Кеш**: Проверка наличия результата в кеше
3. **Извлечение**: Текст + объекты (картинки, таблицы)
4. **Чанкинг**: Разбивка на чанки (~20k токенов)
5. **AI Анализ**: 
   - Ollama → предварительный анализ
   - DeepSeek → семантическая корректировка с **гибким парсингом**
6. **Сборка**: Создание итогового DOCX с ГОСТ форматированием
7. **Кеширование**: Сохранение результата

### 🔄 Гибкий парсинг DeepSeek (NEW)

AI Processor использует 4-уровневую стратегию парсинга ответов DeepSeek:

1. **Точные маркеры** - ищет `[START_OF_CORRECTED_TEXT]` и `[END_OF_CORRECTED_TEXT]`
2. **Regex поиск** - гибкий поиск маркеров с вариациями
3. **Извлечение до рекомендаций** - берёт текст до секции рекомендаций
4. **Fallback** - использует весь ответ как последнее средство

Это обеспечивает стабильную работу даже если DeepSeek API возвращает ответы в разных форматах.

## 🔧 Конфигурация

См. `core/config.py` для полного списка настроек.

## 📝 Логирование

Логи записываются в:
- Console (INFO level)
- File: `logs/word_validator.log` (DEBUG level)

## 🧪 Тестирование

```bash
pytest tests/
```

## 📚 Документация API

После запуска доступна по адресу:
- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

## 🐛 Отладка

1. Включите DEBUG логирование в `.env`:
```bash
LOG_LEVEL=DEBUG
```

2. Проверьте доступность AI сервисов:
```bash
# Ollama
curl http://localhost:11434/api/tags

# DeepSeek
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

3. Проверьте логи парсинга DeepSeek:
```bash
# В логах будет видна какая стратегия парсинга сработала:
# "✅ Strategy 1: Found exact markers"
# "✅ Strategy 2: Found with regex"
# "✅ Strategy 3: Took text before recommendations"
# "⚠️ Strategy 4: Using entire response as last resort"
tail -f logs/word_validator.log | grep "Strategy"
```

## 📋 История изменений

### 2024-12-14 - DeepSeek Parsing Fix
- ✅ Добавлен гибкий парсинг ответов DeepSeek API
- ✅ Исправлена ошибка `DeepSeekFormatError: Missing [END_OF_CORRECTED_TEXT] marker`
- ✅ Реализованы 4 стратегии fallback парсинга
- ✅ Добавлены тесты для всех стратегий
- ✅ Обратная совместимость сохранена

## 📄 Лицензия

Проект EAIP - Internal Use Only
