# Тестовый скрипт для проверки Word документов через API
# ИСПРАВЛЕНА совместимость с Windows PowerShell

param(
    [Parameter(Mandatory=$false)]
    [string]$FilePath = "C:\eaip\test_document.docx",
    
    [Parameter(Mandatory=$false)]
    [string]$ApiUrl = "http://localhost:8001/api/validate-word-document"
)

Write-Host ""
Write-Host "🧪 Тест проверки Word документа через AI" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Проверка файла
if (-not (Test-Path $FilePath)) {
    Write-Host "❌ Файл не найден: $FilePath" -ForegroundColor Red
    exit 1
}

$file = Get-Item $FilePath
Write-Host "📄 Файл: $($file.Name)" -ForegroundColor Green
Write-Host "📦 Размер: $([math]::Round($file.Length / 1KB, 1)) KB" -ForegroundColor Green
Write-Host ""

# Проверка API
Write-Host "🔍 Проверка API..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5
    Write-Host "✅ API доступен" -ForegroundColor Green
} catch {
    Write-Host "❌ API недоступен" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Отправляю на проверку..." -ForegroundColor Yellow
Write-Host ""

try {
    # Создаем boundary для multipart/form-data
    $boundary = [System.Guid]::NewGuid().ToString()
    
    # Читаем файл
    $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
    $fileEnc = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes)
    
    # Формируем тело запроса
    $LF = "`r`n"
    $bodyLines = (
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$($file.Name)`"",
        "Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document$LF",
        $fileEnc,
        "--$boundary--$LF"
    ) -join $LF
    
    # Отправляем запрос
    $response = Invoke-RestMethod -Uri $ApiUrl `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyLines `
        -TimeoutSec 300
    
    Write-Host "✅ Проверка завершена" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    
    $validation = $response.validation_result
    
    # Статус
    $statusColor = switch ($validation.overall_status) {
        "OK" { "Green" }
        "WARNINGS" { "Yellow" }
        "ERRORS" { "Red" }
        default { "White" }
    }
    Write-Host "📊 Статус: $($validation.overall_status)" -ForegroundColor $statusColor
    Write-Host "📝 Резюме: $($validation.summary)"
    Write-Host "🤖 AI: $($response.ai_provider)"
    Write-Host ""
    
    # Статистика
    if ($validation.statistics) {
        Write-Host "📈 Статистика:" -ForegroundColor Cyan
        Write-Host "   🔴 Критических: $($validation.statistics.critical_errors)"
        Write-Host "   🟡 Предупреждений: $($validation.statistics.warnings)"
        Write-Host ""
    }
    
    # Ошибки
    if ($validation.errors -and $validation.errors.Count -gt 0) {
        Write-Host "⚠️  Найдено проблем: $($validation.errors.Count)" -ForegroundColor Yellow
        Write-Host ""
        
        $count = [Math]::Min($validation.errors.Count, 5)
        for ($i = 0; $i -lt $count; $i++) {
            $error = $validation.errors[$i]
            Write-Host "$($i + 1). $($error.type.ToUpper())" -ForegroundColor Cyan
            Write-Host "   Серьезность: $($error.severity)"
            if ($error.location) {
                Write-Host "   Место: $($error.location)"
            }
            Write-Host "   Описание: $($error.description)"
            if ($error.suggestion) {
                Write-Host "   💡 Предложение: $($error.suggestion)" -ForegroundColor Yellow
            }
            Write-Host ""
        }
        
        if ($validation.errors.Count -gt 5) {
            Write-Host "... и еще $($validation.errors.Count - 5) проблем(ы)" -ForegroundColor Gray
            Write-Host ""
        }
    } else {
        Write-Host "✅ Проблем не найдено!" -ForegroundColor Green
        Write-Host ""
    }
    
    # Структура
    if ($validation.structure_check) {
        Write-Host "📋 Структура документа:" -ForegroundColor Cyan
        $structure = $validation.structure_check
        if ($structure.required_sections_found) {
            Write-Host "   ✅ Найдено разделов: $($structure.required_sections_found.Count)"
        }
        if ($structure.missing_sections -and $structure.missing_sections.Count -gt 0) {
            Write-Host "   ❌ Отсутствуют: $($structure.missing_sections -join ', ')" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    # Сохранение результата
    $outputFile = "word_validation_result.json"
    $response | ConvertTo-Json -Depth 10 | Set-Content $outputFile -Encoding UTF8
    Write-Host "💾 Полный результат: $outputFile" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Ошибка: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Статус: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Тест завершен" -ForegroundColor Green
Write-Host ""
