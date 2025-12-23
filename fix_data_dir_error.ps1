# ============================================================
# Исправление ошибки: name 'DATA_DIR' is not defined
# ============================================================
# Этот скрипт добавляет определение DATA_DIR в main.py

$ErrorActionPreference = "Stop"

Write-Host "🔧 ИСПРАВЛЕНИЕ: Добавление DATA_DIR в main.py" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Gray

$mainPath = "C:\eaip\eaip_full_skeleton\services\ingest\main.py"

if (-not (Test-Path $mainPath)) {
    Write-Host "❌ Файл main.py не найден: $mainPath" -ForegroundColor Red
    exit 1
}

Write-Host "📄 Файл найден: $mainPath" -ForegroundColor Green

# Создаем резервную копию
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "$mainPath.backup_$timestamp"
Copy-Item $mainPath $backupPath -Force
Write-Host "✅ Создана резервная копия: $backupPath" -ForegroundColor Green

# Читаем содержимое файла
$content = Get-Content $mainPath -Raw -Encoding UTF8

# Проверяем, не добавлена ли уже DATA_DIR
if ($content -match "DATA_DIR\s*=") {
    Write-Host "ℹ️  DATA_DIR уже определена в файле" -ForegroundColor Yellow
    exit 0
}

# Ищем строку с AGGREGATED_DIR для вставки после неё
$searchPattern = "AGGREGATED_DIR\.mkdir\(parents=True, exist_ok=True\)"

if ($content -match $searchPattern) {
    Write-Host "✅ Найдена позиция для вставки (после AGGREGATED_DIR)" -ForegroundColor Green
    
    # Код для добавления
    $dataDirectoryCode = @"

# Временная директория для обработки файлов (для Word валидации и т.д.)
DATA_DIR = Path(os.getenv("DATA_DIR", os.path.join(INBOX_DIR, "temp")))
DATA_DIR.mkdir(parents=True, exist_ok=True)
"@

    # Вставляем код после строки с AGGREGATED_DIR.mkdir
    $content = $content -replace "($searchPattern)", "`$1$dataDirectoryCode"
    
    # Сохраняем изменения
    Set-Content -Path $mainPath -Value $content -Encoding UTF8 -NoNewline
    
    Write-Host ""
    Write-Host "✅ DATA_DIR успешно добавлена в main.py!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Добавленный код:" -ForegroundColor Cyan
    Write-Host $dataDirectoryCode -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  ВАЖНО: Перезапустите сервис для применения изменений!" -ForegroundColor Yellow
    Write-Host "    Нажмите Ctrl+C в терминале с uvicorn, затем:" -ForegroundColor Yellow
    Write-Host "    uvicorn main:app --host 0.0.0.0 --port 8001 --reload" -ForegroundColor Yellow
    
} else {
    Write-Host "❌ Не найдена позиция для вставки (строка с AGGREGATED_DIR.mkdir)" -ForegroundColor Red
    Write-Host "    Добавьте вручную после определения AGGREGATED_DIR:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "DATA_DIR = Path(os.getenv(`"DATA_DIR`", os.path.join(INBOX_DIR, `"temp`")))" -ForegroundColor White
    Write-Host "DATA_DIR.mkdir(parents=True, exist_ok=True)" -ForegroundColor White
    exit 1
}
