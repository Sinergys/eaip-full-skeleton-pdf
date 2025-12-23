# 🤖 Руководство по настройке AI для нормативных документов

## Обзор

Это руководство описывает единый подход к настройке AI для извлечения формул и нормативов из документов (ПКМ 690, ГОСТ, СНиП и др.).

---

## 📋 Текущее состояние

### ✅ Что сделано

1. **Создан единый модуль конфигурации** (`settings/ai_settings.py`)
   - Централизованная загрузка всех настроек AI
   - Валидация провайдеров и API ключей
   - Безопасная загрузка без хардкода

2. **Обновлены модули для использования единой конфигурации**
   - `main.py` - endpoint `/api/normative/ai-status`
   - `ai_parser.py` - инициализация AI парсера
   - Все проверки теперь через `settings.ai_settings`

3. **Создан `.env.example`** с полным описанием переменных

4. **Обновлены docker-compose файлы** для всех провайдеров

---

## 🔧 Переменные окружения

### Основные переменные

| Переменная | Описание | Значение по умолчанию | Обязательная |
|-----------|----------|----------------------|--------------|
| `AI_ENABLED` | Включить/выключить AI | `false` | Да (для работы AI) |
| `AI_PROVIDER` | Провайдер AI | `deepseek` | Да |
| `DEEPSEEK_API_KEY` | API ключ DeepSeek | - | Да (если `AI_PROVIDER=deepseek`) |
| `OPENAI_API_KEY` | API ключ OpenAI | - | Да (если `AI_PROVIDER=openai`) |
| `ANTHROPIC_API_KEY` | API ключ Anthropic | - | Да (если `AI_PROVIDER=anthropic`) |

### Дополнительные переменные (опционально)

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `DEEPSEEK_MODEL` | Модель DeepSeek | `deepseek-chat` |
| `OPENAI_MODEL_TEXT` | Модель OpenAI для текста | `gpt-4` |
| `OPENAI_MODEL_VISION` | Модель OpenAI для изображений | `gpt-4-vision-preview` |
| `ANTHROPIC_MODEL` | Модель Anthropic | `claude-3-opus-20240229` |
| `AI_PREFER_FOR_PDF` | Использовать AI для PDF вместо OCR | `false` |
| `AI_MAX_TOKENS` | Максимальное количество токенов | `2000` |
| `AI_TEMPERATURE` | Температура модели (0.0-1.0) | `0.2` |
| `AI_TIMEOUT` | Таймаут запросов (секунды) | `60` |

---

## 🪟 Настройка для Windows (локальная разработка)

### Способ 1: PowerShell (рекомендуется)

Создайте файл `set_ai_env.ps1` в корне проекта:

```powershell
# Установка переменных окружения для текущей сессии PowerShell
$env:AI_ENABLED = "true"
$env:AI_PROVIDER = "deepseek"
$env:DEEPSEEK_API_KEY = "sk-ваш-ключ-здесь"

# Проверка
Write-Host "✅ Переменные установлены:"
Write-Host "   AI_ENABLED=$env:AI_ENABLED"
Write-Host "   AI_PROVIDER=$env:AI_PROVIDER"
Write-Host "   DEEPSEEK_API_KEY=$($env:DEEPSEEK_API_KEY.Substring(0,10))..."

# Запуск приложения
Write-Host "`n🚀 Запуск uvicorn..."
cd eaip_full_skeleton/services/ingest
uvicorn main:app --reload --port 8001 --host 0.0.0.0
```

Запуск:
```powershell
.\set_ai_env.ps1
```

### Способ 2: Через .env файл (для python-dotenv)

Если используете `python-dotenv`, создайте файл `.env` в `eaip_full_skeleton/services/ingest/`:

```env
AI_ENABLED=true
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-ваш-ключ-здесь
```

И обновите `main.py` для загрузки `.env`:
```python
from dotenv import load_dotenv
load_dotenv()  # Загружает .env файл
```

### Способ 3: Через системные переменные (постоянно)

**⚠️ Внимание:** Это устанавливает переменные для всей системы.

```powershell
# Установка для текущего пользователя
[System.Environment]::SetEnvironmentVariable("AI_ENABLED", "true", "User")
[System.Environment]::SetEnvironmentVariable("AI_PROVIDER", "deepseek", "User")
[System.Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-ваш-ключ", "User")

# Перезапустите PowerShell/IDE чтобы переменные вступили в силу
```

### Проверка переменных

```powershell
# Проверить переменные в текущей сессии
$env:AI_ENABLED
$env:AI_PROVIDER
$env:DEEPSEEK_API_KEY

# Или через Python
python -c "import os; print('AI_ENABLED:', os.getenv('AI_ENABLED')); print('AI_PROVIDER:', os.getenv('AI_PROVIDER'))"
```

---

## 🐳 Настройка для Docker/Docker Compose

### 1. Создайте файл `.env` в `eaip_full_skeleton/infra/`

```env
# AI Configuration
AI_ENABLED=true
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-ваш-ключ-здесь
DEEPSEEK_MODEL=deepseek-chat

# Или для OpenAI:
# AI_PROVIDER=openai
# OPENAI_API_KEY=sk-ваш-ключ-здесь
# OPENAI_MODEL_TEXT=gpt-4
# OPENAI_MODEL_VISION=gpt-4-vision-preview

# Или для Anthropic:
# AI_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-ваш-ключ-здесь
# ANTHROPIC_MODEL=claude-3-opus-20240229
```

### 2. Обновите docker-compose файл

Переменные уже добавлены в `docker-compose.local.yml`:

```yaml
ingest:
  environment:
    AI_PROVIDER: ${AI_PROVIDER:-deepseek}
    AI_ENABLED: ${AI_ENABLED:-false}
    DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:-}
    OPENAI_API_KEY: ${OPENAI_API_KEY:-}
    ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
    # ... другие переменные
```

### 3. Пересоберите и перезапустите

```bash
cd eaip_full_skeleton/infra
docker compose -f docker-compose.local.yml build ingest
docker compose -f docker-compose.local.yml up -d ingest

# Проверить логи
docker compose -f docker-compose.local.yml logs ingest | grep -i "ai\|deepseek"
```

---

## ✅ Проверка работы

### 1. Проверка через API

```bash
# Проверить статус AI
curl http://localhost:8001/api/normative/ai-status

# Ожидаемый ответ при правильной настройке:
{
  "ai_enabled": true,
  "ai_provider": "deepseek",
  "has_api_key": true,
  "has_valid_config": true,
  "importer_available": true,
  "ai_parser_available": true,
  "message": "✅ AI настроен и готов к работе (провайдер: deepseek)"
}
```

### 2. Проверка через веб-интерфейс

Откройте `http://localhost:8001/web/normative`

- ✅ Если AI настроен: зелёный баннер "AI настроен и готов к работе"
- ⚠️ Если AI не настроен: жёлтый баннер с инструкциями

### 3. Проверка через Python

```python
from settings.ai_settings import get_ai_status, is_ai_enabled, has_ai_config

print("AI включен:", is_ai_enabled())
print("Есть валидная конфигурация:", has_ai_config())
print("Полный статус:", get_ai_status())
```

---

## 🔍 Устранение проблем

### Проблема: "AI не настроен" даже после установки переменных

**Решение:**
1. Убедитесь, что переменные установлены в той же сессии, где запущен uvicorn
2. Перезапустите uvicorn после установки переменных
3. Проверьте, что переменные видны: `python -c "import os; print(os.getenv('AI_ENABLED'))"`

### Проблема: "API ключ не найден"

**Решение:**
1. Проверьте правильность названия переменной (зависит от провайдера)
2. Убедитесь, что ключ не содержит пробелов или кавычек
3. Для Windows: используйте PowerShell, не cmd

### Проблема: Docker не видит переменные

**Решение:**
1. Убедитесь, что `.env` файл находится в `infra/` (рядом с docker-compose.yml)
2. Проверьте синтаксис `.env` файла (без пробелов вокруг `=`)
3. Пересоберите контейнер: `docker compose build ingest`

---

## 📚 Дополнительная документация

- `eaip_full_skeleton/services/ingest/AI_SETUP.md` - Детальная настройка AI
- `eaip_full_skeleton/services/ingest/settings/ai_settings.py` - Исходный код модуля настроек
- `docs/normative_import_guide.md` - Руководство по импорту нормативных документов

---

## 🎯 Быстрый старт (чеклист)

- [ ] Получить API ключ от выбранного провайдера
- [ ] Установить переменные окружения (PowerShell или .env)
- [ ] Перезапустить uvicorn/контейнер
- [ ] Проверить статус через `/api/normative/ai-status`
- [ ] Проверить веб-интерфейс `/web/normative`
- [ ] Загрузить тестовый нормативный документ

---

**Готово!** Теперь AI будет автоматически извлекать формулы и нормативы из загруженных документов.

