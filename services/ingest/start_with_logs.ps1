# Комплексный скрипт: запуск сервиса + мониторинг логов
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Запуск ingest с мониторингом логов" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$serviceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $serviceDir

# Запускаем сервис в фоне
Write-Host "🚀 Запускаю сервис..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-File", (Join-Path $serviceDir "start_service.ps1")

# Ждем немного для запуска
Start-Sleep -Seconds 3

# Открываем браузер
Write-Host "🌐 Открываю веб-интерфейс..." -ForegroundColor Cyan
Start-Process "http://localhost:8001/web/upload"

Write-Host ""
Write-Host "✅ Сервис запущен!" -ForegroundColor Green
Write-Host "📊 Веб-интерфейс: http://localhost:8001/web/upload" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Для мониторинга логов запустите:" -ForegroundColor Yellow
Write-Host "   .\watch_logs.ps1" -ForegroundColor White
Write-Host ""

