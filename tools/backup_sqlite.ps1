# Скрипт резервного копирования SQLite базы данных для Windows PowerShell
# Использование: .\backup_sqlite.ps1 [путь_к_базе]

param(
    [string]$DbPath = ""
)

# Определяем путь к БД
if ([string]::IsNullOrEmpty($DbPath)) {
    # Пробуем найти БД в стандартных местах
    $possiblePaths = @(
        "eaip_full_skeleton\services\ingest\ingest_data.db",
        "data\ingest_data.db",
        "ingest_data.db"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $DbPath = $path
            break
        }
    }
    
    if ([string]::IsNullOrEmpty($DbPath)) {
        Write-Host "❌ Ошибка: База данных не найдена" -ForegroundColor Red
        Write-Host "Использование: .\backup_sqlite.ps1 [путь_к_базе.db]"
        exit 1
    }
}

# Проверяем существование файла
if (-not (Test-Path $DbPath)) {
    Write-Host "❌ Ошибка: Файл не найден: $DbPath" -ForegroundColor Red
    exit 1
}

# Создаем директорию для бэкапов
$BackupDir = "backups"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

# Генерируем имя файла с датой и временем
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DbName = [System.IO.Path]::GetFileNameWithoutExtension($DbPath)
$BackupFile = Join-Path $BackupDir "${DbName}_${Timestamp}.db"

# Выполняем бэкап
Write-Host "📦 Создание резервной копии..." -ForegroundColor Cyan
Write-Host "   Источник: $DbPath"
Write-Host "   Назначение: $BackupFile"

# Используем Python для создания бэкапа (более надежно, чем sqlite3)
$pythonScript = @"
import sqlite3
import sys
from pathlib import Path

db_path = Path(r'$DbPath')
backup_file = Path(r'$BackupFile')

try:
    conn = sqlite3.connect(str(db_path))
    backup_conn = sqlite3.connect(str(backup_file))
    conn.backup(backup_conn)
    backup_conn.close()
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f'Ошибка: {e}', file=sys.stderr)
    sys.exit(1)
"@

$pythonScript | python
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при создании бэкапа" -ForegroundColor Red
    exit 1
}

# Проверяем размер файла
$OriginalSize = (Get-Item $DbPath).Length / 1MB
$BackupSize = (Get-Item $BackupFile).Length / 1MB

Write-Host "✅ Резервная копия создана успешно" -ForegroundColor Green
Write-Host "   Размер оригинала: $([math]::Round($OriginalSize, 2)) MB"
Write-Host "   Размер бэкапа: $([math]::Round($BackupSize, 2)) MB"
Write-Host "   Файл: $BackupFile"

# Опционально: удалить старые бэкапы (старше 30 дней)
if ($env:CLEANUP_OLD_BACKUPS) {
    Write-Host "🧹 Очистка старых бэкапов (старше 30 дней)..." -ForegroundColor Yellow
    $cutoffDate = (Get-Date).AddDays(-30)
    Get-ChildItem $BackupDir -Filter "*.db" | Where-Object { $_.LastWriteTime -lt $cutoffDate } | Remove-Item
    Write-Host "✅ Очистка завершена" -ForegroundColor Green
}

# Показываем список последних бэкапов
Write-Host ""
Write-Host "📋 Последние 5 бэкапов:" -ForegroundColor Cyan
Get-ChildItem $BackupDir -Filter "*.db" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object {
    Write-Host "   $($_.Name) - $($_.LastWriteTime) - $([math]::Round($_.Length / 1MB, 2)) MB"
}

