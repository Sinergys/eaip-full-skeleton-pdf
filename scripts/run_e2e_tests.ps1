# ============================================================================
# EAIP Project: Run E2E Tests
# ============================================================================
# Назначение: Запуск E2E тестов для API endpoints
# Требования: Виртуальное окружение с установленными зависимостями
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
# Шаг 1: Проверка путей
# ============================================================================

Write-Step "Шаг 1: Проверка путей проекта"

$projectRoot = "C:\eaip"
$ingestService = "C:\eaip\eaip_full_skeleton\services\ingest"
$testsDir = "$ingestService\tests"
$venvPath = "C:\eaip\.venv"

Write-Info "Проверка существования папок..."

if (-not (Test-Path $projectRoot)) {
    Write-Error-Custom "Корневая папка не найдена: $projectRoot"
    exit 1
}

if (-not (Test-Path $ingestService)) {
    Write-Error-Custom "Папка ingest service не найдена: $ingestService"
    exit 1
}

if (-not (Test-Path $testsDir)) {
    Write-Error-Custom "Папка tests не найдена: $testsDir"
    exit 1
}

Write-Success "Все папки найдены"

# ============================================================================
# Шаг 2: Проверка виртуального окружения
# ============================================================================

Write-Step "Шаг 2: Проверка виртуального окружения"

if (-not (Test-Path $venvPath)) {
    Write-Error-Custom "Виртуальное окружение не найдено: $venvPath"
    Write-Info "Создайте виртуальное окружение:"
    Write-Info "  python -m venv .venv"
    exit 1
}

Write-Success "Виртуальное окружение найдено: $venvPath"

# Проверка активации venv
$pythonPath = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Error-Custom "Python не найден в venv: $pythonPath"
    exit 1
}

Write-Success "Python найден: $pythonPath"

# Получаем версию Python
$pythonVersion = & $pythonPath --version 2>&1
Write-Info "Версия Python: $pythonVersion"

# ============================================================================
# Шаг 3: Проверка зависимостей
# ============================================================================

Write-Step "Шаг 3: Проверка установленных зависимостей"

$pipPath = Join-Path $venvPath "Scripts\pip.exe"

Write-Info "Проверка pytest..."
$pytestInstalled = & $pipPath show pytest 2>$null
if (-not $pytestInstalled) {
    Write-Error-Custom "pytest не установлен"
    Write-Info "Установите зависимости:"
    Write-Info "  .\.venv\Scripts\pip.exe install pytest pytest-asyncio pytest-cov"
    exit 1
}
Write-Success "pytest установлен"

Write-Info "Проверка fastapi..."
$fastapiInstalled = & $pipPath show fastapi 2>$null
if (-not $fastapiInstalled) {
    Write-Error-Custom "fastapi не установлен"
    Write-Info "Установите зависимости из requirements.txt"
    exit 1
}
Write-Success "fastapi установлен"

Write-Info "Проверка openpyxl..."
$openpyxlInstalled = & $pipPath show openpyxl 2>$null
if (-not $openpyxlInstalled) {
    Write-Error-Custom "openpyxl не установлен"
    Write-Info "Установите зависимости из requirements.txt"
    exit 1
}
Write-Success "openpyxl установлен"

# ============================================================================
# Шаг 4: Переход в директорию ingest service
# ============================================================================

Write-Step "Шаг 4: Настройка окружения для тестов"

Set-Location $ingestService
Write-Info "Рабочая директория: $ingestService"

# Установка переменных окружения для тестов
$env:INGEST_DB_PATH = "$testsDir\.test_db\test_ingest.db"
$env:SYSTEM_MODE = "debug"
$env:PYTHONPATH = $ingestService

Write-Success "Переменные окружения настроены"
Write-Info "INGEST_DB_PATH: $env:INGEST_DB_PATH"
Write-Info "SYSTEM_MODE: $env:SYSTEM_MODE"

# ============================================================================
# Шаг 5: Запуск тестов
# ============================================================================

Write-Step "Шаг 5: Запуск E2E тестов"

$pytestPath = Join-Path $venvPath "Scripts\pytest.exe"

Write-Info "Запуск pytest..."
Write-Info "Файл тестов: tests\test_api_e2e.py"
Write-Host ""

# Параметры pytest:
# -v : verbose (детальный вывод)
# -s : показывать print() в тестах
# --tb=short : короткий traceback при ошибках
# tests/test_api_e2e.py : запустить только E2E тесты

try {
    & $pytestPath -v -s --tb=short tests/test_api_e2e.py
    $exitCode = $LASTEXITCODE
} catch {
    Write-Error-Custom "Ошибка при запуске pytest: $_"
    exit 1
}

# ============================================================================
# Шаг 6: Анализ результатов
# ============================================================================

Write-Host ""
Write-Step "Шаг 6: Анализ результатов"

if ($exitCode -eq 0) {
    Write-Success "Все тесты пройдены успешно! ✨"
    Write-Host ""
    Write-ColorOutput Green "🎯 Что дальше:"
    Write-Host "  1. Проверьте coverage: pytest --cov=. --cov-report=html tests/"
    Write-Host "  2. Запустите все тесты: pytest tests/"
    Write-Host "  3. Переходите к рефакторингу main.py"
} elseif ($exitCode -eq 5) {
    Write-Info "Тесты не найдены (exit code 5)"
    Write-Info "Проверьте что test_api_e2e.py существует в tests/"
} else {
    Write-Error-Custom "Некоторые тесты не прошли (exit code: $exitCode)"
    Write-Host ""
    Write-ColorOutput Yellow "🔍 Отладка:"
    Write-Host "  1. Проверьте ошибки выше"
    Write-Host "  2. Запустите конкретный тест:"
    Write-Host "     pytest tests/test_api_e2e.py::TestUploadEndpoint::test_upload_excel_file_success -v"
    Write-Host "  3. Включите детальный вывод:"
    Write-Host "     pytest tests/test_api_e2e.py -vv --tb=long"
}

Write-Host ""

# ============================================================================
# Шаг 7: Дополнительные команды
# ============================================================================

Write-Step "Шаг 7: Полезные команды"

Write-Info "Запуск конкретного теста:"
Write-Host "  pytest tests/test_api_e2e.py::TestUploadEndpoint::test_upload_excel_file_success -v"
Write-Host ""

Write-Info "Запуск тестов с coverage:"
Write-Host "  pytest --cov=. --cov-report=html --cov-report=term tests/test_api_e2e.py"
Write-Host ""

Write-Info "Запуск всех тестов:"
Write-Host "  pytest tests/ -v"
Write-Host ""

Write-Info "Запуск с остановкой на первой ошибке:"
Write-Host "  pytest tests/test_api_e2e.py -x"
Write-Host ""

# ============================================================================
# Конец скрипта
# ============================================================================

exit $exitCode
