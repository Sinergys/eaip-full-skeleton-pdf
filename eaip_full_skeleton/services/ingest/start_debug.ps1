# Скрипт для запуска ingest сервиса с DEBUG логированием
# Использование: .\start_debug.ps1

Write-Host "🔄 Останавливаю существующие процессы uvicorn..." -ForegroundColor Yellow

# Останавливаем процессы uvicorn на порту 8001
$processes = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $processes) {
    try {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ Остановлен процесс $pid" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠ Не удалось остановить процесс $pid" -ForegroundColor Yellow
    }
}

Start-Sleep -Seconds 2

Write-Host "`n🚀 Запускаю ingest сервис с DEBUG логированием..." -ForegroundColor Green
Write-Host "   Порт: 8001" -ForegroundColor Cyan
Write-Host "   Уровень логирования: DEBUG" -ForegroundColor Cyan
Write-Host "   API документация: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "   Веб-интерфейс: http://localhost:8001/web/upload" -ForegroundColor Cyan
Write-Host ""

# Устанавливаем переменные окружения
$env:LOG_LEVEL = "DEBUG"
$env:PYTHONUNBUFFERED = "1"

# Переходим в директорию сервиса
Set-Location $PSScriptRoot

# Запускаем сервис
uvicorn main:app --reload --port 8001 --log-level debug

