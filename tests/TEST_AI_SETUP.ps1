# Тестовый скрипт для проверки настройки AI
# Запуск: .\TEST_AI_SETUP.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Тест настройки AI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Установка переменных для теста
$env:AI_ENABLED = "true"
$env:AI_PROVIDER = "deepseek"

Write-Host "1. Проверка загрузки настроек..." -ForegroundColor Yellow
try {
    $result = python -c "import sys; sys.path.insert(0, 'eaip_full_skeleton/services/ingest'); from settings.ai_settings import get_ai_settings; s = get_ai_settings(); print(f'AI Enabled: {s.enabled}'); print(f'Provider: {s.provider}'); print(f'Has API Key: {bool(s.api_key)}'); print(f'Has Valid Config: {s.has_valid_config}')" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host $result
        Write-Host ""
        
        if ($result -match "Has Valid Config: True") {
            Write-Host "✅ Настройки загружены правильно!" -ForegroundColor Green
        } else {
            Write-Host "❌ Настройки неполные" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Ошибка загрузки настроек" -ForegroundColor Red
        Write-Host $result
    }
} catch {
    Write-Host "❌ Ошибка: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "2. Проверка статуса AI..." -ForegroundColor Yellow
try {
    $statusResult = python -c "import sys; sys.path.insert(0, 'eaip_full_skeleton/services/ingest'); from settings.ai_settings import get_ai_status; import json; print(json.dumps(get_ai_status(), indent=2, ensure_ascii=False))" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host $statusResult
        Write-Host ""
        
        if ($statusResult -match '"has_valid_config": true') {
            Write-Host "✅ Статус AI: готов к работе!" -ForegroundColor Green
        } else {
            Write-Host "❌ Статус AI: не готов" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Ошибка получения статуса" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Ошибка: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Проверка импортера нормативных документов..." -ForegroundColor Yellow
try {
    $importerResult = python -c "import sys; sys.path.insert(0, 'eaip_full_skeleton/services/ingest'); from domain.normative_importer import get_normative_importer; from settings.ai_settings import get_ai_settings; importer = get_normative_importer(); ai_settings = get_ai_settings(); print(f'Importer available: {importer is not None}'); print(f'AI Parser available: {importer and importer.ai_parser is not None if importer else False}'); print(f'AI Parser enabled: {importer and importer.ai_parser and importer.ai_parser.enabled if importer else False}')" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host $importerResult
        Write-Host ""
        
        if ($importerResult -match "AI Parser enabled: True") {
            Write-Host "✅ Импортер готов к работе!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Импортер доступен, но AI парсер не включен" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Ошибка проверки импортера" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Ошибка: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Итог:" -ForegroundColor Cyan
Write-Host "Если все проверки пройдены, запустите:" -ForegroundColor Yellow
Write-Host "  .\ENABLE_AI_SIMPLE.ps1" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

