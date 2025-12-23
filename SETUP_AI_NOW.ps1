# Быстрая настройка AI для нормативных документов
# Запуск: .\SETUP_AI_NOW.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Настройка AI для нормативных документов" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка текущих переменных
Write-Host "Текущие переменные окружения:" -ForegroundColor Yellow
$currentEnabled = $env:AI_ENABLED
$currentProvider = $env:AI_PROVIDER
$currentKey = $env:DEEPSEEK_API_KEY

Write-Host "  AI_ENABLED: $([string]::IsNullOrWhiteSpace($currentEnabled) ? 'НЕ УСТАНОВЛЕНО' : $currentEnabled)" -ForegroundColor $(if ($currentEnabled -eq 'true') { 'Green' } else { 'Red' })
Write-Host "  AI_PROVIDER: $([string]::IsNullOrWhiteSpace($currentProvider) ? 'НЕ УСТАНОВЛЕНО' : $currentProvider)" -ForegroundColor $(if ($currentProvider) { 'Green' } else { 'Red' })
Write-Host "  DEEPSEEK_API_KEY: $(if ($currentKey) { 'УСТАНОВЛЕНО (' + $currentKey.Substring(0, [Math]::Min(10, $currentKey.Length)) + '...)' } else { 'НЕ УСТАНОВЛЕНО' })" -ForegroundColor $(if ($currentKey) { 'Green' } else { 'Red' })
Write-Host ""

# Если уже настроено, спрашиваем что делать
if ($currentEnabled -eq 'true' -and $currentProvider -and $currentKey) {
    Write-Host "✅ AI уже настроен!" -ForegroundColor Green
    Write-Host ""
    $action = Read-Host "Что делать? (1 - перезапустить uvicorn, 2 - изменить настройки, 3 - выйти) [1]"
    
    if ([string]::IsNullOrWhiteSpace($action)) { $action = "1" }
    
    if ($action -eq "1") {
        Write-Host ""
        Write-Host "🚀 Запуск uvicorn..." -ForegroundColor Cyan
        Write-Host ""
        cd eaip_full_skeleton/services/ingest
        uvicorn main:app --reload --port 8001 --host 0.0.0.0
        exit 0
    } elseif ($action -eq "3") {
        exit 0
    }
}

# Настройка
Write-Host "Настройка AI:" -ForegroundColor Yellow
Write-Host ""

# Выбор провайдера
Write-Host "Выберите провайдера AI:" -ForegroundColor Yellow
Write-Host "  1. DeepSeek (рекомендуется, дешевле)"
Write-Host "  2. OpenAI"
Write-Host "  3. Anthropic"
$providerChoice = Read-Host "Введите номер (1-3) [1]"

if ([string]::IsNullOrWhiteSpace($providerChoice)) { $providerChoice = "1" }

switch ($providerChoice) {
    "1" { 
        $provider = "deepseek"
        $keyVar = "DEEPSEEK_API_KEY"
    }
    "2" { 
        $provider = "openai"
        $keyVar = "OPENAI_API_KEY"
    }
    "3" { 
        $provider = "anthropic"
        $keyVar = "ANTHROPIC_API_KEY"
    }
    default {
        $provider = "deepseek"
        $keyVar = "DEEPSEEK_API_KEY"
    }
}

Write-Host "Выбран провайдер: $provider" -ForegroundColor Green
Write-Host ""

# Запрос API ключа
$apiKey = Read-Host "Введите API ключ ($keyVar)"

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "❌ API ключ не может быть пустым!" -ForegroundColor Red
    exit 1
}

# Установка переменных
$env:AI_ENABLED = "true"
$env:AI_PROVIDER = $provider
Set-Item -Path "env:$keyVar" -Value $apiKey

Write-Host ""
Write-Host "✅ Переменные окружения установлены:" -ForegroundColor Green
Write-Host "   AI_ENABLED=$env:AI_ENABLED"
Write-Host "   AI_PROVIDER=$env:AI_PROVIDER"
Write-Host "   $keyVar=$($apiKey.Substring(0, [Math]::Min(10, $apiKey.Length)))..." -ForegroundColor Gray

Write-Host ""
Write-Host "⚠️  ВАЖНО: Эти переменные действуют только в текущей сессии PowerShell!" -ForegroundColor Yellow
Write-Host "   После закрытия PowerShell переменные будут потеряны." -ForegroundColor Yellow
Write-Host ""

# Проверка через Python
Write-Host "Проверка конфигурации..." -ForegroundColor Cyan
try {
    $checkResult = python -c "import sys; sys.path.insert(0, 'eaip_full_skeleton/services/ingest'); from settings.ai_settings import get_ai_status; import json; print(json.dumps(get_ai_status(), indent=2, ensure_ascii=False))" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Конфигурация проверена:" -ForegroundColor Green
        Write-Host $checkResult
    } else {
        Write-Host "⚠️ Не удалось проверить конфигурацию через Python" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Python недоступен для проверки" -ForegroundColor Yellow
}

Write-Host ""
$launch = Read-Host "Запустить uvicorn сейчас? (y/n) [y]"

if ([string]::IsNullOrWhiteSpace($launch) -or $launch -eq "y" -or $launch -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Запуск uvicorn..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "После запуска откройте: http://localhost:8001/web/normative" -ForegroundColor Green
    Write-Host "Должен появиться зелёный баннер 'AI настроен и готов к работе'" -ForegroundColor Green
    Write-Host ""
    
    cd eaip_full_skeleton/services/ingest
    uvicorn main:app --reload --port 8001 --host 0.0.0.0
} else {
    Write-Host ""
    Write-Host "Для запуска uvicorn выполните:" -ForegroundColor Cyan
    Write-Host "   cd eaip_full_skeleton/services/ingest" -ForegroundColor Gray
    Write-Host "   uvicorn main:app --reload --port 8001 --host 0.0.0.0" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️ Не забудьте: переменные окружения действуют только в текущей сессии!" -ForegroundColor Yellow
}

