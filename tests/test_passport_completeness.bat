@echo off
chcp 65001 >nul
echo ========================================
echo ТЕСТ ЗАПОЛНЕННОСТИ ЭНЕРГОПАСПОРТА
echo ========================================
echo.

cd /d "%~dp0"

python scripts\test_passport_completeness.py ^
    --template "templates\pcm690\energy_passport_template.xlsx" ^
    --aggregated "data\aggregated\aggregated_full_resources_2022_2024.json" ^
    --output "data\aggregated\EnergyPassport_PKM690_completeness_test.xlsx" ^
    --equipment-json "data\aggregated\oborudovanie_equipment.json" ^
    --envelope-json "data\aggregated\ograjdayuschie_envelope.json" ^
    --loss-active-month 3200 ^
    --loss-reactive-month 13600 ^
    --transformer-power 630

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ТЕСТ ЗАВЕРШЁН УСПЕШНО
    echo ========================================
    echo Откройте файл: data\aggregated\EnergyPassport_PKM690_completeness_test.xlsx
    echo Отчёт: data\aggregated\EnergyPassport_PKM690_completeness_test_completeness_report.json
) else (
    echo.
    echo ========================================
    echo ОШИБКА ПРИ ВЫПОЛНЕНИИ ТЕСТА
    echo ========================================
)

pause

