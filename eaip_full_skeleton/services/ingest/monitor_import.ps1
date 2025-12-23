# Скрипт для мониторинга процесса импорта в реальном времени
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  МОНИТОРИНГ ИМПОРТА В БД" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 Отслеживаю процесс импорта..." -ForegroundColor Yellow
Write-Host "💡 Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ключевые события для отслеживания:" -ForegroundColor White
Write-Host "  ✅ - Успешный импорт" -ForegroundColor Green
Write-Host "  ❌ - Ошибка импорта" -ForegroundColor Red
Write-Host "  📦 - Начало импорта ресурса" -ForegroundColor Cyan
Write-Host "  📥 - Импорт записи" -ForegroundColor Cyan
Write-Host ""

# Проверяем, запущен ли сервис
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Сервис запущен и доступен" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Сервис не запущен или недоступен!" -ForegroundColor Red
    Write-Host "   Запустите сервис: .\start_service.ps1" -ForegroundColor Yellow
    exit 1
}

# Мониторим логи через API или файлы
Write-Host "📊 Ожидаю загрузку файлов..." -ForegroundColor Cyan
Write-Host ""

# Простой мониторинг через проверку БД
$dbPath = Join-Path $PSScriptRoot "ingest_data.db"
$checkScript = @"
import sqlite3
import time
from pathlib import Path

db_path = Path(r'$dbPath')
if not db_path.exists():
    print('База данных не найдена')
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Получаем текущее количество записей
cursor.execute('SELECT COUNT(*) FROM aggregated_data')
count_before = cursor.fetchone()[0]
print(f'Текущее количество записей в aggregated_data: {count_before}')

# Мониторим изменения
print('Мониторинг изменений... (Ctrl+C для остановки)')
try:
    while True:
        time.sleep(2)
        cursor.execute('SELECT COUNT(*) FROM aggregated_data')
        count_now = cursor.fetchone()[0]
        
        if count_now > count_before:
            print(f'✅ НОВЫЕ ЗАПИСИ! Было: {count_before}, Стало: {count_now} (+{count_now - count_before})')
            count_before = count_now
            
            # Показываем последние записи
            cursor.execute('''
                SELECT resource_type, period, batch_id, created_at 
                FROM aggregated_data 
                ORDER BY created_at DESC 
                LIMIT 5
            ''')
            for row in cursor.fetchall():
                print(f'   → {row[0]} / {row[1]} (batch: {row[2][:8]}...)')
except KeyboardInterrupt:
    print('\nМониторинг остановлен')
finally:
    conn.close()
"@

# Сохраняем скрипт во временный файл
$tempScript = Join-Path $env:TEMP "monitor_import_temp.py"
$checkScript | Out-File -FilePath $tempScript -Encoding UTF8

# Запускаем мониторинг
python $tempScript

