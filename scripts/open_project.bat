@echo off
REM Быстрое открытие проекта EAIP в Cursor или VS Code
cd /d C:\eaip

REM Попробовать открыть в Cursor
where cursor >nul 2>&1
if %errorlevel% equ 0 (
    echo Открываю проект в Cursor...
    cursor .
    exit /b
)

REM Если Cursor не найден, открыть в VS Code
where code >nul 2>&1
if %errorlevel% equ 0 (
    echo Открываю проект в VS Code...
    code .
    exit /b
)

REM Если ничего не найдено, открыть в Explorer
echo Cursor и VS Code не найдены. Открываю в Explorer...
explorer .

