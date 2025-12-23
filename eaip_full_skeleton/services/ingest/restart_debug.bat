@echo off
echo ========================================
echo   Перезапуск ingest сервиса с DEBUG
echo ========================================
echo.

echo [1/3] Останавливаю существующие процессы...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

echo [2/3] Устанавливаю переменные окружения...
set LOG_LEVEL=DEBUG
set PYTHONUNBUFFERED=1

echo [3/3] Запускаю сервис с DEBUG логированием...
echo.
echo Сервис будет доступен на:
echo   - API: http://localhost:8001/docs
echo   - Веб: http://localhost:8001/web/upload
echo.
echo Для остановки нажмите Ctrl+C
echo.

cd /d %~dp0
uvicorn main:app --reload --port 8001 --log-level debug

