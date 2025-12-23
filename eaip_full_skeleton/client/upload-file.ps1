# Скрипт для загрузки файла в EAIP через PowerShell
param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath
)

Write-Host "📤 Загрузка файла в EAIP..." -ForegroundColor Cyan
Write-Host ""

# Проверка существования файла
if (-not (Test-Path $FilePath)) {
    Write-Host "❌ Файл не найден: $FilePath" -ForegroundColor Red
    exit 1
}

$file = Get-Item $FilePath
Write-Host "Файл: $($file.Name)" -ForegroundColor Yellow
Write-Host "Размер: $([math]::Round($file.Length / 1MB, 2)) MB" -ForegroundColor Yellow
Write-Host ""

# Проверка доступности сервиса
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -TimeoutSec 3
    Write-Host "✅ Сервис ingest доступен" -ForegroundColor Green
} catch {
    Write-Host "❌ Сервис ingest недоступен на порту 8001" -ForegroundColor Red
    Write-Host "   Проверьте: docker ps | Select-String ingest" -ForegroundColor Yellow
    exit 1
}

Write-Host "Загрузка..." -ForegroundColor Cyan

try {
    # Загрузка файла
    $form = @{
        file = Get-Item $FilePath
    }
    
    $response = Invoke-RestMethod -Uri "http://localhost:8001/ingest/files" -Method Post -Form $form
    
    Write-Host ""
    Write-Host "✅ Файл успешно загружен!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Результат:" -ForegroundColor Cyan
    Write-Host "  Batch ID: $($response.batchId)" -ForegroundColor White
    Write-Host "  Файл: $($response.filename)" -ForegroundColor White
    
    if ($response.validate -and $response.validate.error) {
        Write-Host "  ⚠️  Валидация: $($response.validate.error)" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ Валидация: Запущена успешно" -ForegroundColor Green
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Ошибка загрузки:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Ответ сервера: $responseBody" -ForegroundColor Yellow
    }
    
    exit 1
}

