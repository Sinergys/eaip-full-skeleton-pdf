# Шаг 4: Проверка исправления ошибки merged cells

Write-Host "=== ПРОВЕРКА ИСПРАВЛЕНИЯ MERGED CELLS ===" -ForegroundColor Yellow

# 1. Проверяем, что изменения применились
$filePath = "C:\eaip\tools\fill_energy_passport.py"
Write-Host "`n1. ПРОВЕРКА ИЗМЕНЕНИЙ В ФАЙЛЕ:" -ForegroundColor Cyan

# Проверяем строку 2175
$line2175 = Get-Content $filePath | Select-Object -Index 2174
if ($line2175 -match 'safe_cell_write') {
    Write-Host "   ✓ Строка 2175: Используется safe_cell_write" -ForegroundColor Green
} else {
    Write-Host "   ✗ Строка 2175: Не использует safe_cell_write" -ForegroundColor Red
    Write-Host "     Содержимое: $line2175"
}

# Проверяем строку 2180
$line2180 = Get-Content $filePath | Select-Object -Index 2179
if ($line2180 -match 'safe_cell_write') {
    Write-Host "   ✓ Строка 2180: Используется safe_cell_write" -ForegroundColor Green
} else {
    Write-Host "   ✗ Строка 2180: Не использует safe_cell_write" -ForegroundColor Red
    Write-Host "     Содержимое: $line2180"
}

# 2. Ищем тест
Write-Host "`n2. ПОИСК ТЕСТА:" -ForegroundColor Cyan
$testFile = "C:\eaip\eaip_full_skeleton\services\ingest\tests\test_passport_e2e_audit_sinergys.py"

if (Test-Path $testFile) {
    Write-Host "   ✓ Тестовый файл найден: $testFile" -ForegroundColor Green
    
    # Ищем конкретный тест
    $testContent = Get-Content $testFile -Raw
    if ($testContent -match 'test_passport_generation_with_metin_template') {
        Write-Host "   ✓ Тест найден в файле" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Тест не найден в файле" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✗ Тестовый файл не найден" -ForegroundColor Red
}

# 3. Инструкции по запуску теста
Write-Host "`n3. ИНСТРУКЦИИ ДЛЯ ЗАПУСКА ТЕСТА:" -ForegroundColor Cyan
Write-Host "   Перейдите в директорию проекта:"
Write-Host "   cd C:\eaip\eaip_full_skeleton"
Write-Host "`n   Запустите тест:"
Write-Host "   python -m pytest services/ingest/tests/test_passport_e2e_audit_sinergys.py::test_passport_generation_with_metin_template -v"
Write-Host "`n   Или все тесты в файле:"
Write-Host "   python -m pytest services/ingest/tests/test_passport_e2e_audit_sinergys.py -v"

# 4. Проверка наличия ошибки AttributeError
Write-Host "`n4. ЧТО ПРОВЕРИТЬ ПОСЛЕ ЗАПУСКА ТЕСТА:" -ForegroundColor Cyan
Write-Host "   - Ошибка 'AttributeError: 'MergedCell' object attribute 'value' is read-only' не возникает"
Write-Host "   - Тест проходит успешно"
Write-Host "   - Все данные записываются корректно"
Write-Host "   - Шаблон Excel не поврежден"

# 5. Действия при проблемах
Write-Host "`n5. ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ:" -ForegroundColor Yellow
Write-Host "   Проблема: Данные не записываются в merged cells"
Write-Host "   Решение: Реализовать функцию поиска свободных ячеек"
Write-Host "`n   Проблема: Тест не находит шаблон"
Write-Host "   Решение: Проверить путь к шаблону 'Метин'"
Write-Host "`n   Проблема: Другие ошибки"
Write-Host "   Решение: Проверить логи и стектрейс"

Write-Host "`n=== СЛЕДУЮЩИЕ ШАГИ ===" -ForegroundColor Green
Write-Host "1. Запустите тест по инструкциям выше"
Write-Host "2. Если тест проходит - исправление успешно"
Write-Host "3. Если есть проблемы - потребуется доработка"
Write-Host "4. Удалите временные файлы:"
Write-Host "   - step1_analysis.py"
Write-Host "   - step2_fix_merged_cells_fixed.ps1"
Write-Host "   - step4_run_test.ps1"
Write-Host "   - add_to_technical_debt.py"
Write-Host "   - simple_analysis.py"
Write-Host "   - analyze_dependencies.ps1"
Write-Host "   - analyze_error.ps1"