# Скрипт исправления кодировки Windows для миграции
# Запуск: .\tools\fix_windows_encoding.ps1

Write-Host "🔧 Исправление кодировки Windows для миграции PostgreSQL" -ForegroundColor Cyan

# 1. Устанавливаем UTF-8 для консоли
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 2. Устанавливаем кодовую страницу UTF-8
chcp 65001 | Out-Null

# 3. Переменные окружения для Python
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:LC_ALL = "C.UTF-8"
$env:LANG = "C.UTF-8"

# 4. Переменные окружения для PostgreSQL (ASCII только, избегаем проблем)
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_DB = "eaip_db"
$env:POSTGRES_USER = "eaip_user"
$env:POSTGRES_PASSWORD = "eaip_password"

Write-Host "✅ Кодировка установлена:" -ForegroundColor Green
Write-Host "   Консоль: UTF-8"
Write-Host "   Python: UTF-8"
Write-Host "   Кодовая страница: 65001"
Write-Host ""
Write-Host "📋 Переменные окружения PostgreSQL:" -ForegroundColor Yellow
Write-Host "   HOST: $env:POSTGRES_HOST"
Write-Host "   PORT: $env:POSTGRES_PORT"
Write-Host "   DB: $env:POSTGRES_DB"
Write-Host "   USER: $env:POSTGRES_USER"
Write-Host ""

# Проверка Python
Write-Host "🐍 Проверка Python..." -ForegroundColor Cyan
python -c "import sys; print(f'  Encoding: {sys.stdout.encoding}'); print(f'  Default: {sys.getdefaultencoding()}')"

# Проверка подключения к PostgreSQL
Write-Host "🗄️  Проверка подключения к PostgreSQL..." -ForegroundColor Cyan
python -c "import psycopg2; import os; conn = psycopg2.connect(host=os.getenv('POSTGRES_HOST'), port=int(os.getenv('POSTGRES_PORT', 5432)), database=os.getenv('POSTGRES_DB'), user=os.getenv('POSTGRES_USER'), password=os.getenv('POSTGRES_PASSWORD')); print('  ✅ Подключение успешно!'); conn.close()" 2>&1

Write-Host ""
Write-Host "✅ Готово! Можно запускать миграцию." -ForegroundColor Green
