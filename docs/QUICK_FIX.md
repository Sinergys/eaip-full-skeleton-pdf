# ⚡ Быстрое решение: Активация AI

## ✅ Хорошие новости!

API ключ уже есть в конфигурации проекта (`test_deepseek_simple.py`).  
Модуль `ai_settings.py` автоматически загружает его.

## 🎯 Что нужно сделать

**Только установить одну переменную:** `AI_ENABLED=true`

---

## Способ 1: Использовать скрипт (самый простой) ✅

```powershell
cd C:\eaip
.\ENABLE_AI_SIMPLE.ps1
```

Скрипт:
- ✅ Проверит наличие ключа в конфигурации
- ✅ Установит `AI_ENABLED=true`
- ✅ Запустит uvicorn

---

## Способ 2: Вручную

1. **Остановите uvicorn** (если запущен): `Ctrl+C`

2. **В PowerShell выполните:**
   ```powershell
   $env:AI_ENABLED = "true"
   cd C:\eaip\eaip_full_skeleton\services\ingest
   uvicorn main:app --reload --port 8001 --host 0.0.0.0
   ```

3. **Проверьте:** откройте `http://localhost:8001/web/normative`

---

## Проверка

После запуска uvicorn проверьте:

```powershell
curl http://localhost:8001/api/normative/ai-status
```

Должно вернуть:
```json
{
  "ai_enabled": true,
  "has_valid_config": true,
  "ai_parser_available": true,
  "message": "✅ AI настроен и готов к работе"
}
```

---

## ⚠️ Важно

- Переменные окружения действуют только в текущей сессии PowerShell
- Uvicorn должен быть запущен ПОСЛЕ установки переменной
- Если закрыть PowerShell, переменная будет потеряна

---

**Готово!** После этого предупреждение исчезнет. 🎉

