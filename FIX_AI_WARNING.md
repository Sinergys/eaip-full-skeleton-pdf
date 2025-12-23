# 🔧 Как убрать предупреждение "AI не настроен"

## Проблема

На странице `http://localhost:8001/web/normative` отображается предупреждение:
> ⚠️ AI не настроен

## Причина

Переменные окружения `AI_ENABLED`, `AI_PROVIDER` и `DEEPSEEK_API_KEY` не установлены в сессии, где запущен uvicorn.

## Решение (выберите один способ)

### Способ 1: Использовать скрипт (самый простой) ✅

1. **Остановите uvicorn** (если запущен): нажмите `Ctrl+C` в окне, где он работает

2. **Запустите скрипт**:
   ```powershell
   cd C:\eaip
   .\SETUP_AI_NOW.ps1
   ```

3. Скрипт попросит:
   - Выбрать провайдера (1 - DeepSeek, 2 - OpenAI, 3 - Anthropic)
   - Ввести API ключ
   - Затем автоматически запустит uvicorn

4. **Проверьте**: откройте `http://localhost:8001/web/normative` - должно быть зелёное сообщение ✅

---

### Способ 2: Вручную (если скрипт не работает)

1. **Остановите uvicorn** (если запущен): `Ctrl+C`

2. **Откройте PowerShell** и выполните:
   ```powershell
   # Установить переменные окружения
   $env:AI_ENABLED = "true"
   $env:AI_PROVIDER = "deepseek"
   $env:DEEPSEEK_API_KEY = "sk-ваш-ключ-здесь"
   
   # Перейти в директорию сервиса
   cd C:\eaip\eaip_full_skeleton\services\ingest
   
   # Запустить uvicorn
   uvicorn main:app --reload --port 8001 --host 0.0.0.0
   ```

3. **Проверьте**: откройте `http://localhost:8001/web/normative`

---

### Способ 3: Через .env файл (для постоянной настройки)

1. **Создайте файл** `.env` в `C:\eaip\eaip_full_skeleton\services\ingest\`:
   ```env
   AI_ENABLED=true
   AI_PROVIDER=deepseek
   DEEPSEEK_API_KEY=sk-ваш-ключ-здесь
   ```

2. **Установите python-dotenv** (если ещё не установлен):
   ```powershell
   pip install python-dotenv
   ```

3. **Добавьте в начало `main.py`** (если ещё нет):
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Загружает .env файл
   ```

4. **Перезапустите uvicorn**

---

## ⚠️ Важно

- **Переменные окружения действуют только в текущей сессии PowerShell**
- Если вы закрыли PowerShell и открыли новый, переменные будут потеряны
- **Uvicorn должен быть запущен ПОСЛЕ установки переменных**
- Если uvicorn уже запущен, его нужно перезапустить

---

## Проверка

### 1. Проверить переменные в PowerShell:
```powershell
$env:AI_ENABLED
$env:AI_PROVIDER
$env:DEEPSEEK_API_KEY
```

### 2. Проверить через API:
```powershell
curl http://localhost:8001/api/normative/ai-status
```

Должен вернуть:
```json
{
  "ai_enabled": true,
  "ai_provider": "deepseek",
  "has_api_key": true,
  "has_valid_config": true,
  "ai_parser_available": true,
  "message": "✅ AI настроен и готов к работе (провайдер: deepseek)"
}
```

### 3. Проверить в браузере:
Откройте `http://localhost:8001/web/normative` - должно быть зелёное сообщение:
> ✅ AI настроен и готов к работе

---

## Если не работает

1. **Убедитесь, что uvicorn запущен ПОСЛЕ установки переменных**
2. **Проверьте, что переменные установлены в той же сессии PowerShell, где запущен uvicorn**
3. **Проверьте API ключ** - он должен начинаться с `sk-` для DeepSeek
4. **Посмотрите логи uvicorn** - там могут быть ошибки

---

## Где получить API ключ

- **DeepSeek**: https://platform.deepseek.com → API Keys
- **OpenAI**: https://platform.openai.com → API Keys  
- **Anthropic**: https://console.anthropic.com → API Keys

