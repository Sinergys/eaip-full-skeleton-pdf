# ============================================================
# Проверка наличия DATA_DIR в main.py
# ============================================================

$ErrorActionPreference = "Stop"

$mainPath = "C:\eaip\eaip_full_skeleton\services\ingest\main.py"

Write-Host "`n🔍 ПРОВЕРКА: DATA_DIR в main.py" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Gray

if (-not (Test-Path $mainPath)) {
    Write-Host "❌ Файл main.py не найден: $mainPath" -ForegroundColor Red
    exit 1
}

$content = Get-Content $mainPath -Raw -Encoding UTF8

if ($content -match "DATA_DIR\s*=\s*Path") {
    Write-Host "✅ DATA_DIR определена в файле!" -ForegroundColor Green
    
    # Извлекаем строку с определением
    $lines = $content -split "`n"
    foreach ($line in $lines) {
        if ($line -match "DATA_DIR") {
            Write-Host "    $($line.Trim())" -ForegroundColor White
        }
    }
} else {
    Write-Host "❌ DATA_DIR НЕ найдена в файле" -ForegroundColor Red
    Write-Host "    Запустите: .\fix_data_dir_error.ps1" -ForegroundColor Yellow
}

Write-Host ""
