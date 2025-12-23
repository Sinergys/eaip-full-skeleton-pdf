# ============================================================================
# Update PDF Libraries: Remove PyPDF2, Install PyMuPDF
# ============================================================================
# Дата: 2025-12-05
# Цель: Замена устаревшей PyPDF2 на современную PyMuPDF
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Обновление PDF библиотек" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

$venvPath = "C:\eaip\.venv\Scripts"
$pipPath = Join-Path $venvPath "pip.exe"

if (-not (Test-Path $pipPath)) {
    Write-Host "❌ Виртуальное окружение не найдено: $venvPath" -ForegroundColor Red
    exit 1
}

Write-Host "1️⃣ Удаление PyPDF2..." -ForegroundColor Cyan
try {
    & $pipPath uninstall PyPDF2 -y 2>&1 | Out-Null
    Write-Host "   ✅ PyPDF2 удален" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  PyPDF2 не был установлен" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "2️⃣ Установка PyMuPDF..." -ForegroundColor Cyan
try {
    & $pipPath install PyMuPDF==1.24.0
    Write-Host "   ✅ PyMuPDF установлен" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Ошибка установки PyMuPDF: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3️⃣ Проверка установленных библиотек..." -ForegroundColor Cyan
Write-Host ""

$libraries = @("pdfplumber", "PyMuPDF")
foreach ($lib in $libraries) {
    $installed = & $pipPath show $lib 2>$null
    if ($installed) {
        $version = ($installed | Select-String "Version:").ToString().Split(":")[1].Trim()
        Write-Host "   ✅ $lib $version" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $lib НЕ установлен" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "✅ Обновление завершено!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Установленные PDF библиотеки:" -ForegroundColor Cyan
Write-Host "  • pdfplumber - для извлечения таблиц" -ForegroundColor White
Write-Host "  • PyMuPDF - для быстрой работы с PDF и OCR" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Примечание:" -ForegroundColor Yellow
Write-Host "  PyPDF2 fallback код остался в file_parser.py" -ForegroundColor White
Write-Host "  Будет заменен на PyMuPDF в будущем (см. TECHNICAL_DEBT.md)" -ForegroundColor White
Write-Host ""
