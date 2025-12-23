# Скрипт запуска ingest сервиса с детальным логированием
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Запуск ingest сервиса" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Переходим в директорию сервиса
$serviceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $serviceDir

Write-Host "📂 Директория: $serviceDir" -ForegroundColor Yellow
Write-Host ""

# Проверяем виртуальное окружение
if (-not (Test-Path ".venv")) {
    Write-Host "🔧 Создаю виртуальное окружение..." -ForegroundColor Yellow
    python -m venv .venv
}

# Активируем виртуальное окружение
Write-Host "🔧 Активирую виртуальное окружение..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Устанавливаем зависимости
Write-Host "📦 Проверяю зависимости..." -ForegroundColor Yellow
pip install -q -r requirements.txt

Write-Host ""
Write-Host "🚀 Запускаю сервис на http://localhost:8001" -ForegroundColor Green
Write-Host "📊 Веб-интерфейс: http://localhost:8001/web/upload" -ForegroundColor Cyan
Write-Host "📚 API документация: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Устанавливаем уровень логирования
$env:LOG_LEVEL = "INFO"

# Запускаем сервис
uvicorn main:app --reload --port 8001 --log-level info

