# 🔄 Инструкция по перезапуску сервера

## ⚠️ Проблема: Endpoint `/debug/extensions` не найден

Это означает, что **сервер использует старую версию кода** и не перезагрузился с обновлениями.

## 🚀 Решение: Полный перезапуск

### Вариант 1: Через скрипт (рекомендуется)

```powershell
cd C:\eaip\eaip_full_skeleton\services\ingest
.\restart_clean.ps1
```

### Вариант 2: Вручную

```powershell
# 1. Остановите сервер
# В терминале, где запущен uvicorn, нажмите Ctrl+C
# Или убейте процесс:
Get-Process python | Where-Object {$_.Id -eq 2908} | Stop-Process -Force

# 2. Очистите кеш
cd C:\eaip\eaip_full_skeleton\services\ingest
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# 3. Перезапустите сервер
uvicorn main:app --reload --port 8001
```

## ✅ Проверка после перезапуска

### 1. Проверьте health endpoint:
```powershell
curl http://localhost:8001/health
```
Должен вернуть: `{"service":"ingest","status":"ok"}`

### 2. Проверьте debug endpoint:
```powershell
curl http://localhost:8001/debug/extensions
```
Должен вернуть JSON с `"xlsm_supported": true`

### 3. Проверьте в браузере:
Откройте: `http://localhost:8001/debug/extensions`

Должно показать:
```json
{
  "allowed_extensions": [".docx", ".jpeg", ".jpg", ".pdf", ".png", ".xlsm", ".xlsx"],
  "xlsm_supported": true,
  "code_version": "2025-01-16-xlsm-support"
}
```

## 🔍 Если endpoint все еще не найден

1. **Проверьте, что файл `main.py` содержит endpoint:**
   ```powershell
   Select-String -Path "main.py" -Pattern "debug/extensions"
   ```
   Должна быть строка: `@app.get("/debug/extensions")`

2. **Проверьте, что сервер запущен из правильной директории:**
   ```powershell
   cd C:\eaip\eaip_full_skeleton\services\ingest
   uvicorn main:app --reload --port 8001
   ```

3. **Проверьте логи сервера** - должны быть сообщения о загрузке модулей

## 📋 После успешного перезапуска

Попробуйте загрузить файл `energopasport.xlsm` - он должен загрузиться без ошибок!

