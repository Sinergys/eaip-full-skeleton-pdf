# Скрипт для анализа ошибки в fill_energy_passport.py

$filePath = "C:\eaip\tools\fill_energy_passport.py"

# 1. Находим строку 2175 и контекст
Write-Host "=== Анализ строки 2175 ===" -ForegroundColor Yellow
$lines = Get-Content $filePath

# Показываем строки 2170-2180
for ($i = 2169; $i -le 2179; $i++) {
    Write-Host ("{0}: {1}" -f ($i+1), $lines[$i])
}

Write-Host "`n=== Поиск функции _write_nodes_table ===" -ForegroundColor Yellow
# Ищем функцию
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match 'def _write_nodes_table') {
        Write-Host ("Функция найдена на строке {0}" -f ($i+1))
        # Показываем начало функции
        for ($j = $i; $j -lt $i+10; $j++) {
            Write-Host ("{0}: {1}" -f ($j+1), $lines[$j])
        }
        break
    }
}

Write-Host "`n=== Поиск merged cells в коде ===" -ForegroundColor Yellow
# Ищем использование merged cells
$mergedPatterns = @('merged_cells', 'MergedCell', 'ws.merge', 'merged_cells.ranges')
foreach ($pattern in $mergedPatterns) {
    $matches = Select-String -Path $filePath -Pattern $pattern
    if ($matches) {
        Write-Host ("Найдено '{0}':" -f $pattern) -ForegroundColor Cyan
        $matches | Select-Object -First 3 | ForEach-Object {
            Write-Host ("  Строка {0}: {1}" -f $_.LineNumber, $_.Line.Trim())
        }
    }
}

Write-Host "`n=== Поиск теста test_passport_generation_with_metin_template ===" -ForegroundColor Yellow
$testMatch = Select-String -Path $filePath -Pattern 'test_passport_generation_with_metin_template'
if ($testMatch) {
    Write-Host ("Тест найден на строке {0}" -f $testMatch.LineNumber) -ForegroundColor Green
} else {
    Write-Host "Тест не найден в этом файле" -ForegroundColor Red
    # Ищем в других файлах
    Write-Host "`nПоиск теста в проекте..." -ForegroundColor Yellow
    Get-ChildItem -Path "C:\eaip" -Filter "*.py" -Recurse | ForEach-Object {
        $test = Select-String -Path $_.FullName -Pattern 'test_passport_generation_with_metin_template'
        if ($test) {
            Write-Host ("Найден в: {0}" -f $_.FullName) -ForegroundColor Green
        }
    }
}