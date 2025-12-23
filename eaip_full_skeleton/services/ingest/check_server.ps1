# Скрипт проверки состояния сервера
Write-Host "🔍 Проверка состояния сервера ingest..." -ForegroundColor Cyan

# 1. Проверка доступности сервера
Write-Host "`n1. Проверка доступности сервера..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 2
    Write-Host "   ✅ Сервер доступен: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   📄 Ответ: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Сервер недоступен: $_" -ForegroundColor Red
    Write-Host "   💡 Убедитесь, что сервер запущен на порту 8001" -ForegroundColor Yellow
    exit
}

# 2. Проверка debug endpoint
Write-Host "`n2. Проверка debug endpoint..." -ForegroundColor Yellow
try {
    $debugResponse = Invoke-WebRequest -Uri "http://localhost:8001/debug/extensions" -UseBasicParsing -TimeoutSec 2
    Write-Host "   ✅ Debug endpoint доступен: $($debugResponse.StatusCode)" -ForegroundColor Green
    $data = $debugResponse.Content | ConvertFrom-Json
    Write-Host "   📊 Поддерживаемые форматы: $($data.allowed_extensions -join ', ')" -ForegroundColor Cyan
    Write-Host "   📊 .xlsm поддерживается: $($data.xlsm_supported)" -ForegroundColor $(if ($data.xlsm_supported) { "Green" } else { "Red" })
} catch {
    Write-Host "   ❌ Debug endpoint недоступен: $_" -ForegroundColor Red
    Write-Host "   ⚠️  Сервер использует СТАРУЮ версию кода!" -ForegroundColor Yellow
    Write-Host "   💡 Необходимо перезапустить сервер" -ForegroundColor Yellow
}

# 3. Проверка процессов Python
Write-Host "`n3. Проверка процессов Python..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "   📋 Найдено процессов Python: $($pythonProcesses.Count)" -ForegroundColor Cyan
    $pythonProcesses | ForEach-Object {
        Write-Host "      - PID: $($_.Id), Путь: $($_.Path)" -ForegroundColor Gray
    }
} else {
    Write-Host "   ℹ️  Процессы Python не найдены" -ForegroundColor Gray
}

# 4. Рекомендации
Write-Host "`n📋 Рекомендации:" -ForegroundColor Cyan
Write-Host "   1. Если debug endpoint недоступен - перезапустите сервер:" -ForegroundColor White
Write-Host "      cd C:\eaip\eaip_full_skeleton\services\ingest" -ForegroundColor Gray
Write-Host "      uvicorn main:app --reload --port 8001" -ForegroundColor Gray
Write-Host "`n   2. Проверьте, что файл main.py содержит endpoint /debug/extensions" -ForegroundColor White
Write-Host "`n   3. После перезапуска проверьте снова:" -ForegroundColor White
Write-Host "      curl http://localhost:8001/debug/extensions" -ForegroundColor Gray

