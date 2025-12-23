# Скрипт для автоматической настройки AI из ключей проекта
# Использование: .\setup_ai_from_project.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Настройка AI из ключей проекта" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# API ключ из проекта
$DEEPSEEK_API_KEY = "sk-fa4d5adfd79d4307809a34b153fc0ab7"

# Путь к .env файлу
$envFile = Join-Path $PSScriptRoot ".env"

Write-Host "📝 Создаю .env файл..." -ForegroundColor Yellow
Write-Host "   Путь: $envFile" -ForegroundColor Gray

# Содержимое .env файла
$envContent = @"
# AI Configuration для нормативных документов
# Настроено автоматически из ключей проекта

# Включить AI
AI_ENABLED=true

# Провайдер AI (DeepSeek - дешевле и OpenAI-совместимый)
AI_PROVIDER=deepseek

# API ключ DeepSeek (из test_deepseek_simple.py)
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY

# Модель DeepSeek (опционально)
DEEPSEEK_MODEL=deepseek-chat

# Использовать AI для PDF вместо традиционного парсинга (опционально)
# AI_PREFER_FOR_PDF=true
"@

try {
    # Создаем .env файл
    $envContent | Out-File -FilePath $envFile -Encoding UTF8 -Force
    Write-Host "✅ .env файл создан успешно!" -ForegroundColor Green
    Write-Host ""
    
    # Устанавливаем переменные окружения для текущей сессии
    $env:AI_ENABLED = "true"
    $env:AI_PROVIDER = "deepseek"
    $env:DEEPSEEK_API_KEY = $DEEPSEEK_API_KEY
    
    Write-Host "✅ Переменные окружения установлены для текущей сессии:" -ForegroundColor Green
    Write-Host "   AI_ENABLED=$env:AI_ENABLED"
    Write-Host "   AI_PROVIDER=$env:AI_PROVIDER"
    Write-Host "   DEEPSEEK_API_KEY=$($DEEPSEEK_API_KEY.Substring(0, 15))..." -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "⚠️  ВАЖНО:" -ForegroundColor Yellow
    Write-Host "   - .env файл создан в: $envFile" -ForegroundColor Gray
    Write-Host "   - Переменные окружения установлены для текущей сессии PowerShell" -ForegroundColor Gray
    Write-Host "   - После перезапуска сервера переменные будут загружены из .env файла" -ForegroundColor Gray
    Write-Host ""
    
    $launch = Read-Host "Запустить uvicorn сейчас? (y/n) [y]"
    
    if ([string]::IsNullOrWhiteSpace($launch) -or $launch -eq "y" -or $launch -eq "Y") {
        Write-Host ""
        Write-Host "🚀 Запуск uvicorn..." -ForegroundColor Cyan
        Write-Host ""
        
        # Запуск uvicorn
        uvicorn main:app --reload --port 8001 --host 0.0.0.0
    } else {
        Write-Host ""
        Write-Host "Для запуска uvicorn выполните:" -ForegroundColor Cyan
        Write-Host "   cd $PSScriptRoot" -ForegroundColor Gray
        Write-Host "   uvicorn main:app --reload --port 8001" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Или перезапустите сервер, если он уже запущен." -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Ошибка при создании .env файла: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Попробуйте создать файл вручную:" -ForegroundColor Yellow
    Write-Host "   1. Создайте файл: $envFile" -ForegroundColor Gray
    Write-Host "   2. Добавьте содержимое:" -ForegroundColor Gray
    Write-Host "      AI_ENABLED=true" -ForegroundColor Gray
    Write-Host "      AI_PROVIDER=deepseek" -ForegroundColor Gray
    Write-Host "      DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY" -ForegroundColor Gray
    exit 1
}

