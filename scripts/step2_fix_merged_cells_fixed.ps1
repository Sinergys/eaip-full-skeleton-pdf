# Шаг 2: Исправление ошибки merged cells в _write_nodes_table

$filePath = "C:\eaip\tools\fill_energy_passport.py"

# Создаем бэкап
$backupPath = "$filePath.backup_step2"
Copy-Item $filePath $backupPath -Force
Write-Host "Создан бэкап: $backupPath" -ForegroundColor Green

# Читаем файл
$lines = Get-Content $filePath

# Заменяем строку 2175 (индекс 2174)
if ($lines.Count -gt 2174) {
    $oldLine2175 = $lines[2174]
    $lines[2174] = $lines[2174] -replace 'ws\.cell\(row=current_row, column=col_idx\)\.value = value', 'safe_cell_write(ws.cell(row=current_row, column=col_idx), value)'
}

# Заменяем строку 2180 (индекс 2179)
if ($lines.Count -gt 2179) {
    $oldLine2180 = $lines[2179]
    $lines[2179] = $lines[2179] -replace 'ws\.cell\(row=current_row, column=col_idx\)\.value = value', 'safe_cell_write(ws.cell(row=current_row, column=col_idx), value)'
}

# Сохраняем изменения
Set-Content $filePath $lines -Encoding UTF8

# Показываем изменения
Write-Host "`n=== ИЗМЕНЕНИЯ ===" -ForegroundColor Green

if ($oldLine2175) {
    Write-Host "Строка 2175:" -ForegroundColor Cyan
    Write-Host "  Было: $oldLine2175"
    Write-Host "  Стало: $($lines[2174])"
}

if ($oldLine2180) {
    Write-Host "`nСтрока 2180:" -ForegroundColor Cyan
    Write-Host "  Было: $oldLine2180"
    Write-Host "  Стало: $($lines[2179])"
}

# Проверяем, что изменения применились
Write-Host "`n=== ПРОВЕРКА ===" -ForegroundColor Yellow

$check2175 = Select-String -Path $filePath -Pattern 'safe_cell_write.*2175' -SimpleMatch
$check2180 = Select-String -Path $filePath -Pattern 'safe_cell_write.*2180' -SimpleMatch

if ($check2175 -or $check2180) {
    Write-Host "✓ Изменения применены успешно" -ForegroundColor Green
} else {
    # Проверяем по содержимому строк
    $newLines = Get-Content $filePath
    $hasSafeCell2175 = $newLines[2174] -match 'safe_cell_write'
    $hasSafeCell2180 = $newLines[2179] -match 'safe_cell_write'
    
    if ($hasSafeCell2175 -and $hasSafeCell2180) {
        Write-Host "✓ Изменения применены успешно" -ForegroundColor Green
    } else {
        Write-Host "✗ Возможна проблема с применением изменений" -ForegroundColor Red
    }
}

Write-Host "`n=== ИНСТРУКЦИИ ===" -ForegroundColor Yellow
Write-Host "1. Запустите тест: test_passport_generation_with_metin_template"
Write-Host "2. Проверьте, что ошибка AttributeError больше не возникает"
Write-Host "3. Если все работает, удалите бэкап: Remove-Item '$backupPath'"

Write-Host "`n=== ПРИМЕЧАНИЕ ===" -ForegroundColor Gray
Write-Host "Функция safe_cell_write возвращает False для merged cells"
Write-Host "Это означает, что данные в объединенные ячейки записаны не будут"
Write-Host "Если это проблема, потребуется дополнительная логика поиска свободных ячеек"