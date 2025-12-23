@echo off
REM Quick Start для проекта EAIP
REM Автоматически открывает нужные директории и файлы

echo ================================================
echo   EAIP - Energy Audit Integration Platform
echo   Quick Start Menu
echo ================================================
echo.
echo Текущая директория: C:\eaip
echo.
echo Выберите действие:
echo.
echo [1] Открыть проект в VS Code / Cursor
echo [2] Запустить ingest-сервис (локально)
echo [3] Открыть документацию Stage 2
echo [4] Открыть директорию данных
echo [5] Проверить пути к файлам данных
echo [0] Выход
echo.
set /p choice="Ваш выбор: "

if "%choice%"=="1" (
    echo Открываю проект в VS Code...
    code C:\eaip
    goto end
)

if "%choice%"=="2" (
    echo Запускаю ingest-сервис...
    cd C:\eaip\eaip_full_skeleton\services\ingest
    start cmd /k "python -m venv .venv 2>nul & .venv\Scripts\Activate.ps1 & pip install -q -r requirements.txt & uvicorn main:app --reload --port 8001"
    timeout /t 3 >nul
    start http://localhost:8001/docs
    goto end
)

if "%choice%"=="3" (
    echo Открываю документацию...
    start notepad C:\eaip\docs\STAGE2_CONTEXT_PROMPT.md
    start notepad C:\eaip\docs\STAGE2_PROGRESS.md
    goto end
)

if "%choice%"=="4" (
    echo Открываю директорию данных...
    explorer C:\eaip\data\source_files
    goto end
)

if "%choice%"=="5" (
    echo Проверяю доступность файлов данных...
    python C:\eaip\scripts\test_data_paths.py
    pause
    goto end
)

if "%choice%"=="0" (
    goto end
)

echo Неверный выбор!
pause

:end
echo.
echo Готово!

