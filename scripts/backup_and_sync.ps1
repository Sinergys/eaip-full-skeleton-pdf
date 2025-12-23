# ============================================================================
# EAIP Project: Backup and Git Sync Script
# ============================================================================
# Назначение: Создание коммита, синхронизация с remote и локальный бэкап
# Дата создания: 2025-12-05
# Git репозиторий: C:\eaip\eaip_full_skeleton\.git
# ============================================================================

# Строгий режим PowerShell
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Цвета для вывода
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-ColorOutput Yellow "=========================================="
    Write-ColorOutput Yellow ">>> $Message"
    Write-ColorOutput Yellow "=========================================="
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput Green "✅ $Message"
}

function Write-Error-Custom {
    param([string]$Message)
    Write-ColorOutput Red "❌ $Message"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput Cyan "ℹ️  $Message"
}

# ============================================================================
# Шаг 0: Определение путей проекта
# ============================================================================

Write-Step "Шаг 0: Определение путей проекта"

$projectRoot = "C:\eaip"
$gitRoot = "C:\eaip\eaip_full_skeleton"

Write-Info "Корень проекта: $projectRoot"
Write-Info "Git репозиторий: $gitRoot"

# Проверяем существование папок
if (-not (Test-Path $projectRoot)) {
    Write-Error-Custom "Корневая папка проекта не найдена: $projectRoot"
    exit 1
}

if (-not (Test-Path $gitRoot)) {
    Write-Error-Custom "Папка Git репозитория не найдена: $gitRoot"
    exit 1
}

Set-Location $gitRoot
Write-Success "Рабочая директория установлена: $gitRoot"

# ============================================================================
# Шаг 1: Проверка Git репозитория
# ============================================================================

Write-Step "Шаг 1: Проверка Git репозитория"

if (-not (Test-Path ".git")) {
    Write-Error-Custom "Git репозиторий не инициализирован в $gitRoot"
    Write-Info "Выполните: git init"
    exit 1
}

Write-Success "Git репозиторий найден"

# ============================================================================
# Шаг 2: Проверка Git конфигурации
# ============================================================================

Write-Step "Шаг 2: Проверка Git конфигурации"

$gitUserName = git config user.name 2>$null
$gitUserEmail = git config user.email 2>$null

if ([string]::IsNullOrEmpty($gitUserName) -or [string]::IsNullOrEmpty($gitUserEmail)) {
    Write-Error-Custom "Git конфигурация не настроена"
    Write-Info "Выполните:"
    Write-Info '  git config user.name "Ваше Имя"'
    Write-Info '  git config user.email "your.email@example.com"'
    exit 1
}

Write-Success "Git user: $gitUserName <$gitUserEmail>"

# ============================================================================
# Шаг 3: Проверка remote репозитория
# ============================================================================

Write-Step "Шаг 3: Проверка remote репозитория"

$remoteUrl = git remote get-url origin 2>$null

if ([string]::IsNullOrEmpty($remoteUrl)) {
    Write-Info "Remote репозиторий не настроен"
    Write-Info "Если нужно добавить remote, выполните:"
    Write-Info '  git remote add origin https://github.com/username/repo.git'
    $hasRemote = $false
} else {
    Write-Success "Remote origin: $remoteUrl"
    $hasRemote = $true
}

# ============================================================================
# Шаг 4: Проверка статуса Git
# ============================================================================

Write-Step "Шаг 4: Проверка статуса изменений"

$gitStatus = git status --porcelain

if ([string]::IsNullOrEmpty($gitStatus)) {
    Write-Info "Нет изменений для коммита"
    $hasChanges = $false
} else {
    Write-Success "Найдены изменения:"
    git status --short | Select-Object -First 20
    $changesCount = ($gitStatus -split "`n").Count
    if ($changesCount -gt 20) {
        Write-Info "... и еще $($changesCount - 20) файлов"
    }
    $hasChanges = $true
}

# ============================================================================
# Шаг 5: Создание коммита (если есть изменения)
# ============================================================================

if ($hasChanges) {
    Write-Step "Шаг 5: Создание коммита"
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $commitMessage = "chore: backup before refactoring - $timestamp

Current state:
- main.py: 2100+ lines monolith
- database.py: SQLite with basic operations
- Tests: ~20 tests (utils, parsing)
- Status: Production ready, needs refactoring

Next steps:
- Write E2E tests for API endpoints
- Refactor main.py into modules
- Migrate to PostgreSQL"

    Write-Info "Добавляю все изменения..."
    git add -A
    
    Write-Info "Создаю коммит..."
    git commit -m $commitMessage
    
    Write-Success "Коммит создан успешно"
    
    # Показываем информацию о коммите
    $lastCommit = git log -1 --oneline
    Write-Info "Последний коммит: $lastCommit"
} else {
    Write-Info "Пропускаю создание коммита (нет изменений)"
}

# ============================================================================
# Шаг 6: Создание тэга версии
# ============================================================================

Write-Step "Шаг 6: Создание тэга версии"

$tagName = "v0.5.0-before-refactor"
$existingTag = git tag -l $tagName

if ($existingTag) {
    Write-Info "Тэг $tagName уже существует"
    Write-Info "Хотите удалить старый тэг и создать новый? (y/n)"
    $response = Read-Host
    if ($response -eq 'y') {
        git tag -d $tagName
        Write-Info "Старый тэг удален"
        $tagMessage = "State before refactoring: monolith main.py + SQLite (updated)"
        git tag -a $tagName -m $tagMessage
        Write-Success "Тэг $tagName создан заново"
    } else {
        Write-Info "Пропускаю создание тэга"
    }
} else {
    $tagMessage = "State before refactoring: monolith main.py + SQLite"
    git tag -a $tagName -m $tagMessage
    Write-Success "Тэг $tagName создан"
}

# ============================================================================
# Шаг 7: Синхронизация с remote (если настроен)
# ============================================================================

if ($hasRemote) {
    Write-Step "Шаг 7: Синхронизация с remote"
    
    Write-Info "Проверяю текущую ветку..."
    $currentBranch = git rev-parse --abbrev-ref HEAD
    Write-Info "Текущая ветка: $currentBranch"
    
    Write-Info "Отправляю коммиты в remote..."
    try {
        git push origin $currentBranch 2>&1 | Out-Null
        Write-Success "Коммиты отправлены в remote"
    } catch {
        Write-Error-Custom "Ошибка при push в remote"
        Write-Info "Возможные причины:"
        Write-Info "  - Нет доступа к интернету"
        Write-Info "  - Требуется аутентификация"
        Write-Info "  - Конфликты с remote"
        Write-Info "Выполните вручную: git push origin $currentBranch"
    }
    
    Write-Info "Отправляю тэги в remote..."
    try {
        git push origin --tags 2>&1 | Out-Null
        Write-Success "Тэги отправлены в remote"
    } catch {
        Write-Error-Custom "Ошибка при push тэгов"
        Write-Info "Выполните вручную: git push origin --tags"
    }
} else {
    Write-Info "Пропускаю синхронизацию с remote (не настроен)"
}

# ============================================================================
# Шаг 8: Создание локального бэкапа ВСЕГО проекта
# ============================================================================

Write-Step "Шаг 8: Создание локального бэкапа"

$backupDir = Join-Path $projectRoot "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Info "Создана папка backups: $backupDir"
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "eaip_backup_before_refactor_$timestamp.zip"
$backupPath = Join-Path $backupDir $backupName

Write-Info "Создаю ZIP архив ВСЕГО проекта (C:\eaip)..."
Write-Info "Это может занять 1-2 минуты..."

# Исключаем только виртуальные окружения и кеши
$excludeDirs = @(
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules"
)

# Создаем архив
try {
    # Используем PowerShell 5.0+ Compress-Archive
    # Получаем все файлы, исключая ненужные папки
    $filesToBackup = Get-ChildItem -Path $projectRoot -Recurse -File | 
        Where-Object { 
            $filePath = $_.FullName
            $shouldExclude = $false
            foreach ($excludeDir in $excludeDirs) {
                if ($filePath -like "*\$excludeDir\*") {
                    $shouldExclude = $true
                    break
                }
            }
            -not $shouldExclude
        }
    
    Write-Info "Найдено файлов для архивирования: $($filesToBackup.Count)"
    
    # Создаем архив порциями для больших проектов
    if ($filesToBackup.Count -gt 1000) {
        Write-Info "Большой проект, архивирование может занять время..."
    }
    
    # Используем встроенный Compress-Archive
    Compress-Archive -Path $filesToBackup.FullName -DestinationPath $backupPath -CompressionLevel Optimal -Force
    
    if (Test-Path $backupPath) {
        $backupSize = (Get-Item $backupPath).Length / 1MB
        Write-Success "Бэкап создан: $backupName"
        Write-Info "Размер: $([math]::Round($backupSize, 2)) MB"
        Write-Info "Путь: $backupPath"
    } else {
        Write-Error-Custom "Не удалось создать бэкап архив"
    }
} catch {
    Write-Error-Custom "Ошибка при создании архива: $_"
    Write-Info "Попробуйте создать архив вручную или освободите место на диске"
}

# ============================================================================
# Шаг 9: Итоговый отчёт
# ============================================================================

Write-Step "Шаг 9: Итоговый отчёт"

Write-Success "Все операции завершены!"
Write-Host ""
Write-ColorOutput Cyan "📊 Сводка:"
Write-Host "  ✅ Git репозиторий: $gitRoot"
Write-Host "  ✅ Git коммит: $(if ($hasChanges) { 'Создан' } else { 'Не требовался' })"
Write-Host "  ✅ Тэг: $tagName"
Write-Host "  ✅ Remote sync: $(if ($hasRemote) { 'Выполнена' } else { 'Не настроен' })"
Write-Host "  ✅ Локальный бэкап: $backupName"
Write-Host ""

Write-ColorOutput Green "🎯 Следующие шаги:"
Write-Host "  1. Проверьте бэкап: $backupPath"
if ($hasRemote) {
    Write-Host "  2. Проверьте remote: $remoteUrl"
} else {
    Write-Host "  2. Настройте remote (опционально):"
    Write-Host "     cd $gitRoot"
    Write-Host '     git remote add origin https://github.com/username/repo.git'
}
Write-Host "  3. Переходите к написанию E2E тестов"
Write-Host ""

Write-ColorOutput Yellow "📁 Структура проекта:"
Write-Host "  C:\eaip\                           # Корень проекта"
Write-Host "  ├── eaip_full_skeleton\.git\       # Git репозиторий"
Write-Host "  └── backups\                       # Бэкапы проекта"
Write-Host ""

# ============================================================================
# Конец скрипта
# ============================================================================
