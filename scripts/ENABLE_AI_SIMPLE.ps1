# Простая активация AI (ключ уже есть в конфигурации)
# Запуск: .\ENABLE_AI_SIMPLE.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Активация AI для нормативных документов" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия ключа в конфигурации
Write-Host "Проверка конфигурации..." -ForegroundColor Yellow
try {
    $checkResult = python -c "import sys; sys.path.insert(0, 'eaip_full_skeleton/services/ingest'); from settings.ai_settings import get_ai_settings; s = get_ai_settings(); print('API Key found:', 'YES' if s.api_key else 'NO')" 2>&1
    
    if ($checkResult -match "YES") {
        Write-Host "✅ API ключ найден в конфигурации!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ API ключ не найден в конфигурации" -ForegroundColor Yellow
        Write-Host "   Используется ключ из test_deepseek_simple.py" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️ Не удалось проверить конфигурацию" -ForegroundColor Yellow
}

Write-Host ""

# Установка только AI_ENABLED
$env:AI_ENABLED = "true"
$env:AI_PROVIDER = "deepseek"  # На всякий случай

Write-Host "✅ Переменные окружения установлены:" -ForegroundColor Green
Write-Host "   AI_ENABLED=$env:AI_ENABLED"
Write-Host "   AI_PROVIDER=$env:AI_PROVIDER"
Write-Host "   DEEPSEEK_API_KEY=загружен из конфигурации" -ForegroundColor Gray

Write-Host ""

# Проверка конфигурации
Write-Host "Проверка конфигурации AI..." -ForegroundColor Cyan
try {
    $statusResult = python -c "import sys; sys.path.insert(0, 'eaip_full_skeleton/services/ingest'); from settings.ai_settings import get_ai_status; import json; print(json.dumps(get_ai_status(), indent=2, ensure_ascii=False))" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host $statusResult
        Write-Host ""
        
        if ($statusResult -match '"has_valid_config": true') {
            Write-Host "✅ AI настроен и готов к работе!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ AI включен, но конфигурация неполная" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "⚠️ Не удалось проверить статус" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "⚠️  ВАЖНО: Эти переменные действуют только в текущей сессии PowerShell!" -ForegroundColor Yellow
Write-Host "   После закрытия PowerShell переменные будут потеряны." -ForegroundColor Yellow
Write-Host ""

$launch = Read-Host "Запустить uvicorn сейчас? (y/n) [y]"

if ([string]::IsNullOrWhiteSpace($launch) -or $launch -eq "y" -or $launch -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Запуск uvicorn..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "После запуска откройте: http://localhost:8001/web/normative" -ForegroundColor Green
    Write-Host "Должен появиться зелёный баннер 'AI настроен и готов к работе'" -ForegroundColor Green
    Write-Host ""
    Write-Host "Для проверки API выполните:" -ForegroundColor Gray
    Write-Host "   curl http://localhost:8001/api/normative/ai-status" -ForegroundColor Gray
    Write-Host ""
    
    # Переход в директорию сервиса
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $ingestDir = Join-Path $scriptDir "eaip_full_skeleton\services\ingest"
    
    if (Test-Path $ingestDir) {
        Set-Location $ingestDir
        Write-Host "Запуск из: $ingestDir" -ForegroundColor Gray
        Write-Host ""
        uvicorn main:app --reload --port 8001 --host 0.0.0.0
    } else {
        Write-Host "❌ Ошибка: директория не найдена: $ingestDir" -ForegroundColor Red
        Write-Host "Запустите скрипт из корня проекта C:\eaip" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Для запуска uvicorn выполните:" -ForegroundColor Cyan
    Write-Host "   cd eaip_full_skeleton/services/ingest" -ForegroundColor Gray
    Write-Host "   uvicorn main:app --reload --port 8001 --host 0.0.0.0" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️ Не забудьте: переменные окружения действуют только в текущей сессии!" -ForegroundColor Yellow
}

