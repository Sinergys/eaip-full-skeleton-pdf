# 📤 Инструкции по загрузке файлов в EAIP

## ✅ Статус сервиса

- **Ingest сервис**: http://localhost:8001
- **Health endpoint**: http://localhost:8001/health
- **Веб-интерфейс**: http://localhost:8001/web/upload

---

## 🎯 Способ 1: Веб-интерфейс (РЕКОМЕНДУЕТСЯ)

### Шаги:

1. **Откройте браузер** и перейдите по адресу:
   ```
   http://localhost:8001/web/upload
   ```

2. **Заполните форму**:
   - Выберите файл для загрузки (Excel, PDF, Word и т.д.)
   - Введите название предприятия (или выберите существующее)
   - При необходимости укажите тип ресурса (электричество, газ, вода и т.д.)

3. **Нажмите "Загрузить"**

4. **Проверьте результат**:
   - После загрузки вы получите `batch_id`
   - Проверьте статус обработки: http://localhost:8001/api/progress/{batch_id}
   - Просмотрите результаты: http://localhost:8001/web/results

---

## 🔧 Способ 2: API через PowerShell

### Простая загрузка (без привязки к предприятию):

```powershell
# Замените "путь\к\файлу.xlsx" на реальный путь к вашему файлу
$filePath = "C:\путь\к\файлу.xlsx"
$fileName = Split-Path $filePath -Leaf

$formData = @{
    file = Get-Item $filePath
}

$response = Invoke-RestMethod -Uri "http://localhost:8001/ingest/files" `
    -Method Post `
    -Form $formData `
    -ContentType "multipart/form-data"

Write-Host "Batch ID: $($response.batchId)"
Write-Host "Status: $($response.parsing_status)"
```

### Загрузка с привязкой к предприятию:

```powershell
# Замените значения на реальные
$filePath = "C:\путь\к\файлу.xlsx"
$enterpriseName = "Тестовое предприятие"
$resourceType = "electricity"  # Опционально: electricity, gas, water, other

$formData = @{
    file = Get-Item $filePath
    enterprise_name = $enterpriseName
    resource_type = $resourceType
}

$response = Invoke-RestMethod -Uri "http://localhost:8001/web/upload" `
    -Method Post `
    -Form $formData `
    -ContentType "multipart/form-data"

Write-Host "Batch ID: $($response.batch_id)"
Write-Host "Enterprise ID: $($response.enterprise_id)"
```

---

## 🔧 Способ 3: API через curl (для Linux/Mac/Git Bash)

### Простая загрузка:

```bash
curl -X POST "http://localhost:8001/ingest/files" \
  -F "file=@/путь/к/файлу.xlsx"
```

### Загрузка с предприятием:

```bash
curl -X POST "http://localhost:8001/web/upload" \
  -F "file=@/путь/к/файлу.xlsx" \
  -F "enterprise_name=Тестовое предприятие" \
  -F "resource_type=electricity"
```

---

## 📊 Проверка статуса обработки

После загрузки файла вы получите `batch_id`. Используйте его для проверки статуса:

### Через браузер:
```
http://localhost:8001/api/progress/{batch_id}
```

### Через PowerShell:
```powershell
$batchId = "ваш-batch-id"
$response = Invoke-RestMethod -Uri "http://localhost:8001/api/progress/$batchId"
$response | ConvertTo-Json -Depth 5
```

### Через curl:
```bash
curl "http://localhost:8001/api/progress/{batch_id}"
```

---

## 📋 Дополнительные эндпоинты

### Список предприятий:
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/enterprises"
```

### Загрузки предприятия:
```powershell
$enterpriseId = 1
Invoke-RestMethod -Uri "http://localhost:8001/api/enterprises/$enterpriseId/uploads"
```

### Чеклист готовности к генерации:
```powershell
$enterpriseId = 1
Invoke-RestMethod -Uri "http://localhost:8001/api/enterprises/$enterpriseId/upload-checklist"
```

### Готовность к генерации паспорта:
```powershell
$enterpriseId = 1
Invoke-RestMethod -Uri "http://localhost:8001/api/enterprises/$enterpriseId/generation-readiness"
```

---

## ⚠️ Поддерживаемые форматы

- **Excel**: `.xlsx`, `.xls`, `.xlsm`
- **PDF**: `.pdf`
- **Word**: `.docx`, `.doc`
- **Текст**: `.txt`

---

## 🐛 Отладка

### Проверка логов контейнера:
```powershell
docker compose logs ingest -f
```

### Проверка health:
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/health"
```

---

## 📝 Пример полного цикла

1. **Загрузите файл** через веб-интерфейс или API
2. **Получите batch_id** из ответа
3. **Проверьте прогресс** обработки
4. **Проверьте готовность** к генерации паспорта
5. **Сгенерируйте паспорт** (если готово):
   ```powershell
   $batchId = "ваш-batch-id"
   Invoke-RestMethod -Uri "http://localhost:8001/api/generate-passport/$batchId" -Method Post
   ```

