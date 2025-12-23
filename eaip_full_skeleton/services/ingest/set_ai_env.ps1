# Скрипт для установки переменных окружения AI в PowerShell (Windows)
# Использование: .\set_ai_env.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Настройка AI для нормативных документов" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Запрос провайдера
Write-Host "Выберите провайдера AI:" -ForegroundColor Yellow
Write-Host "  1. DeepSeek (рекомендуется, дешевле)"
Write-Host "  2. OpenAI"
Write-Host "  3. Anthropic"
$providerChoice = Read-Host "Введите номер (1-3) [по умолчанию: 1]"

if ([string]::IsNullOrWhiteSpace($providerChoice)) {
    $providerChoice = "1"
}

switch ($providerChoice) {
    "1" { 
        $provider = "deepseek"
        $keyVar = "DEEPSEEK_API_KEY"
        Write-Host "Выбран провайдер: DeepSeek" -ForegroundColor Green
    }
    "2" { 
        $provider = "openai"
        $keyVar = "OPENAI_API_KEY"
        Write-Host "Выбран провайдер: OpenAI" -ForegroundColor Green
    }
    "3" { 
        $provider = "anthropic"
        $keyVar = "ANTHROPIC_API_KEY"
        Write-Host "Выбран провайдер: Anthropic" -ForegroundColor Green
    }
    default {
        $provider = "deepseek"
        $keyVar = "DEEPSEEK_API_KEY"
        Write-Host "Используется DeepSeek по умолчанию" -ForegroundColor Yellow
    }
}

Write-Host ""

# Запрос API ключа
$apiKey = Read-Host "Введите API ключ ($keyVar)"

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "❌ API ключ не может быть пустым!" -ForegroundColor Red
    exit 1
}

# Установка переменных окружения для текущей сессии
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
Write-Host "   Для постоянной установки используйте системные переменные (см. документацию)." -ForegroundColor Yellow

Write-Host ""
$launch = Read-Host "Запустить uvicorn сейчас? (y/n) [n]"

if ($launch -eq "y" -or $launch -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Запуск uvicorn..." -ForegroundColor Cyan
    Write-Host ""
    
    # Переход в директорию сервиса
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $scriptDir
    
    # Запуск uvicorn
    uvicorn main:app --reload --port 8001 --host 0.0.0.0
} else {
    Write-Host ""
    Write-Host "Для запуска uvicorn выполните:" -ForegroundColor Cyan
    Write-Host "   cd $scriptDir" -ForegroundColor Gray
    Write-Host "   uvicorn main:app --reload --port 8001 --host 0.0.0.0" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Или перезапустите этот скрипт с параметром запуска." -ForegroundColor Gray
}

