# Скрипт для перезапуска uvicorn с включенным AI
# Использование: .\RESTART_WITH_AI.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Перезапуск uvicorn с включенным AI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка, запущен ли uvicorn
Write-Host "Проверка запущенных процессов uvicorn..." -ForegroundColor Yellow
$uvicornProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*main:app*"
}

if ($uvicornProcesses) {
    Write-Host "⚠️ Найдены запущенные процессы Python с uvicorn" -ForegroundColor Yellow
    Write-Host "   Рекомендуется остановить их вручную (Ctrl+C в окне, где запущен uvicorn)" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Продолжить? (y/n) [y]"
    if ($continue -eq "n" -or $continue -eq "N") {
        Write-Host "Отменено" -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""

# Установка переменных окружения
Write-Host "Установка переменных окружения..." -ForegroundColor Yellow
$env:AI_ENABLED = "true"
$env:AI_PROVIDER = "deepseek"

Write-Host "✅ Переменные установлены:" -ForegroundColor Green
Write-Host "   AI_ENABLED=$env:AI_ENABLED"
Write-Host "   AI_PROVIDER=$env:AI_PROVIDER"
Write-Host "   DEEPSEEK_API_KEY=загружен из конфигурации" -ForegroundColor Gray

Write-Host ""

# Проверка конфигурации
Write-Host "Проверка конфигурации AI..." -ForegroundColor Cyan
try {
    $statusResult = python -c "import sys; sys.path.insert(0, 'eaip_full_skeleton/services/ingest'); from settings.ai_settings import get_ai_status; import json; print(json.dumps(get_ai_status(), indent=2, ensure_ascii=False))" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        if ($statusResult -match '"has_valid_config": true') {
            Write-Host "✅ AI настроен и готов к работе!" -ForegroundColor Green
            Write-Host $statusResult
        } else {
            Write-Host "⚠️ AI включен, но конфигурация неполная" -ForegroundColor Yellow
            Write-Host $statusResult
        }
    } else {
        Write-Host "⚠️ Не удалось проверить статус" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Ошибка проверки: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "⚠️  ВАЖНО:" -ForegroundColor Yellow
Write-Host "   1. Убедитесь, что старый uvicorn остановлен (Ctrl+C)" -ForegroundColor Yellow
Write-Host "   2. Переменные действуют только в текущей сессии PowerShell" -ForegroundColor Yellow
Write-Host ""

# Запуск uvicorn
Write-Host "🚀 Запуск uvicorn..." -ForegroundColor Cyan
Write-Host ""
Write-Host "После запуска:" -ForegroundColor Green
Write-Host "  • Откройте: http://localhost:8001/web/normative" -ForegroundColor White
Write-Host "  • Должен появиться зелёный баннер 'AI настроен и готов к работе'" -ForegroundColor White
Write-Host "  • Проверка API: curl http://localhost:8001/api/normative/ai-status" -ForegroundColor Gray
Write-Host ""

# Переход в директорию сервиса
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ingestDir = Join-Path $scriptDir "eaip_full_skeleton\services\ingest"

if (Test-Path $ingestDir) {
    Set-Location $ingestDir
    Write-Host "Запуск из: $ingestDir" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Для остановки нажмите: Ctrl+C" -ForegroundColor Yellow
    Write-Host ""
    
    # Запуск uvicorn
    uvicorn main:app --reload --port 8001 --host 0.0.0.0
} else {
    Write-Host "❌ Ошибка: директория не найдена: $ingestDir" -ForegroundColor Red
    Write-Host "Запустите скрипт из корня проекта C:\eaip" -ForegroundColor Yellow
    exit 1
}

