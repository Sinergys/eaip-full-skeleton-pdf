# Скрипт для мониторинга логов в реальном времени
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Мониторинг логов ingest сервиса" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$serviceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logFile = Join-Path $serviceDir "logs" "ingest.log"

# Создаем директорию для логов если её нет
$logDir = Split-Path -Parent $logFile
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

Write-Host "📊 Отслеживаю логи импорта..." -ForegroundColor Yellow
Write-Host "💡 Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Фильтруем логи по ключевым словам импорта
Get-Content $logFile -Wait -ErrorAction SilentlyContinue | Where-Object {
    $_ -match "ИМПОРТ|import|aggregated_data|✅|❌|⚠️|📦|📥|📊"
} | ForEach-Object {
    if ($_ -match "✅") {
        Write-Host $_ -ForegroundColor Green
    } elseif ($_ -match "❌|ОШИБКА|ERROR") {
        Write-Host $_ -ForegroundColor Red
    } elseif ($_ -match "⚠️|WARNING") {
        Write-Host $_ -ForegroundColor Yellow
    } elseif ($_ -match "📦|📥|📊|ИМПОРТ") {
        Write-Host $_ -ForegroundColor Cyan
    } else {
        Write-Host $_
    }
}

