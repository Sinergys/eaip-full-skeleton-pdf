@echo off
REM Скрипт для переагрегации данных предприятия
REM Использование: reaggregate.bat [enterprise_id]

cd /d "%~dp0"
set PYTHONPATH=%CD%

if "%1"=="" (
    echo Использование: reaggregate.bat [enterprise_id]
    echo Пример: reaggregate.bat 1
    echo.
    echo Если enterprise_id не указан, будет переагрегировано для всех предприятий
    pause
    exit /b 1
)

python -m utils.reaggregate_all %1

pause

