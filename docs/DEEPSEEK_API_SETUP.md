# Настройка DeepSeek API для нормативных документов

## ✅ API ключ найден в проекте

API ключ DeepSeek уже находится в модуле проекта:
- **Файл:** `eaip_full_skeleton/test_deepseek_simple.py`
- **Ключ:** `sk-fa4d5adfd79d4307809a34b153fc0ab7`

## Автоматическая загрузка ключа

Система автоматически загружает ключ из тестового модуля, если он не установлен в переменных окружения.

### Порядок поиска ключа:
1. **Переменная окружения** `DEEPSEEK_API_KEY` (приоритет)
2. **Тестовый модуль** `test_deepseek_simple.py` (fallback для разработки)

## Быстрая настройка

### Вариант 1: Использовать ключ из модуля (уже работает!)

Просто установите переменные окружения:
```bash
# Windows (PowerShell)
$env:AI_ENABLED="true"
$env:AI_PROVIDER="deepseek"

# Linux/Mac
export AI_ENABLED=true
export AI_PROVIDER=deepseek
```

Ключ будет автоматически загружен из `test_deepseek_simple.py`.

### Вариант 2: Указать ключ явно в .env

Создайте или обновите `.env` файл:
```env
AI_ENABLED=true
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-fa4d5adfd79d4307809a34b153fc0ab7
DEEPSEEK_MODEL=deepseek-chat
```

### Вариант 3: Для Docker

В `docker-compose.yml` или `.env`:
```yaml
services:
  ingest:
    environment:
      - AI_ENABLED=true
      - AI_PROVIDER=deepseek
      - DEEPSEEK_API_KEY=sk-fa4d5adfd79d4307809a34b153fc0ab7
```

## Проверка работы

1. **Проверьте статус AI** через веб-интерфейс:
   ```
   http://localhost:8001/web/normative
   ```
   Должно показать: "✅ AI настроен и готов к работе"

2. **Или через API**:
   ```bash
   curl http://localhost:8001/api/normative/ai-status
   ```

3. **Проверьте логи** при загрузке документа:
   ```bash
   # Должно быть в логах:
   INFO: Используется API ключ из test_deepseek_simple.py (fallback для разработки)
   INFO: DeepSeek API настроен, модель: deepseek-chat
   ```

## Перезапуск приложения

После установки переменных окружения перезапустите приложение:

```bash
# Если используете Docker
docker compose restart ingest

# Если запускаете напрямую
# Остановите и запустите заново с новыми переменными окружения
```

## Результат

После настройки при загрузке нормативных документов:
- ✅ Документ будет распарсен
- ✅ AI извлечет формулы и нормативы
- ✅ Правила будут сохранены в БД
- ✅ Вы увидите количество извлеченных правил

## Важно

⚠️ **Для production**: Рекомендуется использовать переменные окружения или secrets вместо хранения ключа в коде.

Текущий fallback механизм удобен для разработки, но в production лучше использовать:
- Docker secrets
- Переменные окружения сервера
- Специализированные системы управления секретами (Vault, AWS Secrets Manager)

