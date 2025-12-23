# 🚀 Быстрый старт: Настройка AI для нормативных документов

## Проблема

В веб-интерфейсе `/web/normative` отображается предупреждение "AI не настроен": документы загружаются, но формулы/нормативы не извлекаются.

## Решение (3 шага)

### Шаг 1: Получить API ключ

Выберите провайдера и получите ключ:
- **DeepSeek** (рекомендуется): https://platform.deepseek.com → API Keys
- **OpenAI**: https://platform.openai.com → API Keys
- **Anthropic**: https://console.anthropic.com → API Keys

### Шаг 2: Установить переменные окружения

#### Windows (PowerShell) - самый простой способ:

```powershell
cd eaip_full_skeleton/services/ingest
.\set_ai_env.ps1
```

Скрипт попросит выбрать провайдера и ввести API ключ, затем запустит uvicorn.

#### Или вручную:

```powershell
$env:AI_ENABLED = "true"
$env:AI_PROVIDER = "deepseek"
$env:DEEPSEEK_API_KEY = "sk-ваш-ключ-здесь"
```

### Шаг 3: Перезапустить приложение

```powershell
# Если uvicorn уже запущен, остановите его (Ctrl+C)
# Затем запустите заново:
uvicorn main:app --reload --port 8001 --host 0.0.0.0
```

## Проверка

1. Откройте `http://localhost:8001/web/normative`
2. Должен появиться зелёный баннер: "✅ AI настроен и готов к работе"
3. Или проверьте через API:
   ```powershell
   curl http://localhost:8001/api/normative/ai-status
   ```

## Для Docker

1. Создайте файл `eaip_full_skeleton/infra/.env`:
   ```env
   AI_ENABLED=true
   AI_PROVIDER=deepseek
   DEEPSEEK_API_KEY=sk-ваш-ключ
   ```

2. Перезапустите контейнер:
   ```bash
   docker compose -f docker-compose.local.yml restart ingest
   ```

## Подробная документация

- Полное руководство: `docs/AI_CONFIGURATION_GUIDE.md`
- Резюме изменений: `docs/AI_CONFIGURATION_REVIEW_SUMMARY.md`

---

**Готово!** Теперь AI будет автоматически извлекать формулы и нормативы из загруженных документов.

