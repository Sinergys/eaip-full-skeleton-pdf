# Копирование обновленного main.py в проект
# Этот скрипт читает файл из моей временной директории

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "🚀 Установка Word Validator..." -ForegroundColor Cyan
Write-Host ""

# Пути
$projectMain = "C:\eaip\eaip_full_skeleton\services\ingest\main.py"
$backupMain = "$projectMain.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# 1. Бэкап
Write-Host "💾 Создаю бэкап..." -ForegroundColor Yellow
if (Test-Path $projectMain) {
    Copy-Item $projectMain $backupMain -Force
    Write-Host "✅ Бэкап: $(Split-Path $backupMain -Leaf)" -ForegroundColor Green
}

# 2. Читаем обновленный файл из outputs
$updatedContent = @"
