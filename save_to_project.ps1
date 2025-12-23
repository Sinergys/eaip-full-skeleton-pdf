# Скрипт сохранения файлов в проект

Write-Host "🚀 Сохранение файлов в проект EAIP..." -ForegroundColor Cyan

# 1. Копируем обновленный main.py
$mainSource = "C:\Users\DELL\Documents\AUDIT\CLAUDE\main.py"
$mainDest = "C:\eaip\eaip_full_skeleton\services\ingest\main.py"

if (Test-Path $mainSource) {
    Copy-Item $mainSource $mainDest -Force
    Write-Host "✅ main.py скопирован" -ForegroundColor Green
} else {
    Write-Host "❌ main.py не найден в outputs" -ForegroundColor Red
}

# 2. Копируем документацию в docs
$docsFiles = @(
    "WORD_VALIDATION_GUIDE.md",
    "TASK_SUMMARY.md"
)

foreach ($file in $docsFiles) {
    $source = "C:\Users\DELL\Documents\AUDIT\CLAUDE\$file"
    $dest = "C:\eaip\docs\$file"
    
    if (Test-Path $source) {
        Copy-Item $source $dest -Force
        Write-Host "✅ $file скопирован в docs" -ForegroundColor Green
    }
}

# 3. Копируем тестовый скрипт
$testSource = "C:\Users\DELL\Documents\AUDIT\CLAUDE\test_word_validation.py"
$testDest = "C:\eaip\scripts\test_word_validation.py"

if (Test-Path $testSource) {
    Copy-Item $testSource $testDest -Force
    Write-Host "✅ test_word_validation.py скопирован в scripts" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Все файлы сохранены в проект!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Следующие шаги:" -ForegroundColor Yellow
Write-Host "  1. pip install python-docx"
Write-Host "  2. Перезапустить сервис"
Write-Host "  3. Проверить: curl http://localhost:8001/api/validate-word-document"
