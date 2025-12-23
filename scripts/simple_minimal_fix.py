#!/usr/bin/env python3
"""Простое минимальное исправление критических ошибок"""

import shutil
from pathlib import Path

file_path = Path(r"C:\eaip\tools\fill_energy_passport.py")
backup_path = file_path.with_suffix('.py.simple_backup')

print("=== ПРОСТОЕ ИСПРАВЛЕНИЕ КРИТИЧЕСКИХ ОШИБОК ===\n")

# Создаем бэкап
shutil.copy2(file_path, backup_path)
print(f"Создан бэкап: {backup_path}")

# Читаем файл
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("\nИщем и исправляем критические строки...")

# Исправляем только самые критические места
fixes = 0

# Строка 2049 (fill_dinamika_sheet)
if len(lines) > 2048:
    line_2049 = lines[2048]
    if 'ws.cell(row=current_row, column=2).value = (' in line_2049:
        lines[2048] = line_2049.replace(
            'ws.cell(row=current_row, column=2).value = (',
            'safe_cell_write(ws.cell(row=current_row, column=2), ('
        )
        print("✓ Строка 2049 исправлена")
        fixes += 1

# Строка 2175 (_write_nodes_table)
if len(lines) > 2174:
    line_2175 = lines[2174]
    if 'ws.cell(row=current_row, column=col_idx).value = value' in line_2175:
        lines[2174] = line_2175.replace(
            'ws.cell(row=current_row, column=col_idx).value = value',
            'safe_cell_write(ws.cell(row=current_row, column=col_idx), value)'
        )
        print("✓ Строка 2175 исправлена")
        fixes += 1

# Строка 2180 (_write_nodes_table)
if len(lines) > 2179:
    line_2180 = lines[2179]
    if 'ws.cell(row=current_row, column=col_idx).value = value' in line_2180:
        lines[2179] = line_2180.replace(
            'ws.cell(row=current_row, column=col_idx).value = value',
            'safe_cell_write(ws.cell(row=current_row, column=col_idx), value)'
        )
        print("✓ Строка 2180 исправлена")
        fixes += 1

# Сохраняем
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\nВсего исправлений: {fixes}")
print(f"Бэкап: {backup_path}")

# Быстрая проверка
print("\nПроверяем наличие safe_cell_write...")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    
if 'def safe_cell_write' in content:
    print("✓ Функция safe_cell_write найдена")
else:
    print("✗ Функция safe_cell_write не найдена")
    
if 'safe_cell_write(' in content:
    safe_count = content.count('safe_cell_write(')
    print(f"✓ Используется {safe_count} раз")

print("\n=== ЗАПУСТИТЕ ТЕСТ ===")
print("cd C:\\eaip\\eaip_full_skeleton")
print("python -m pytest services/ingest/tests/test_passport_e2e_audit_sinergys.py::test_passport_generation_with_metin_template -v")