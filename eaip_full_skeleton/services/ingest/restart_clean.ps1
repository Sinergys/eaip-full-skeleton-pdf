# Скрипт полной очистки и перезапуска сервиса ingest
Write-Host "🔄 Полная очистка и перезапуск сервиса ingest..." -ForegroundColor Cyan

# 1. Остановить все процессы Python
Write-Host "`n1. Остановка процессов Python..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*eaip*" -or $_.MainWindowTitle -like "*uvicorn*" -or $_.CommandLine -like "*ingest*"
}
if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Write-Host "   ✅ Остановлено процессов: $($pythonProcesses.Count)" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Процессы Python не найдены" -ForegroundColor Gray
}

# 2. Очистить кеш Python
Write-Host "`n2. Очистка кеша Python..." -ForegroundColor Yellow
$cacheDirs = Get-ChildItem -Path ".\" -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
if ($cacheDirs) {
    $cacheDirs | Remove-Item -Recurse -Force
    Write-Host "   ✅ Удалено директорий кеша: $($cacheDirs.Count)" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Кеш не найден" -ForegroundColor Gray
}

# Удалить .pyc файлы
$pycFiles = Get-ChildItem -Path ".\" -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
if ($pycFiles) {
    $pycFiles | Remove-Item -Force
    Write-Host "   ✅ Удалено .pyc файлов: $($pycFiles.Count)" -ForegroundColor Green
}

# 3. Проверка кода
Write-Host "`n3. Проверка кода..." -ForegroundColor Yellow
$mainFile = ".\main.py"
if (Test-Path $mainFile) {
    $content = Get-Content $mainFile -Raw
    if ($content -match '\.xlsm') {
        Write-Host "   ✅ .xlsm найден в коде" -ForegroundColor Green
    } else {
        Write-Host "   ❌ .xlsm НЕ найден в коде!" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ Файл main.py не найден!" -ForegroundColor Red
}

# 4. Готово к запуску
Write-Host "`n✅ Очистка завершена!" -ForegroundColor Green
Write-Host "`n📋 Для запуска сервера выполните:" -ForegroundColor Cyan
Write-Host "   uvicorn main:app --reload --port 8001" -ForegroundColor White
Write-Host "`n🔍 Для проверки выполните:" -ForegroundColor Cyan
Write-Host "   curl http://localhost:8001/debug/extensions" -ForegroundColor White

