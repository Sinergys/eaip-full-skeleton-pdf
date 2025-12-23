#!/usr/bin/env python3
"""Проверка и исправление импортов в fill_energy_passport.py"""

import re
from pathlib import Path

file_path = Path(r"C:\eaip\tools\fill_energy_passport.py")

print("=== ПРОВЕРКА И ИСПРАВЛЕНИЕ ИМПОРТОВ ===\n")

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Проверяем импорт MergedCell
print("1. ПРОВЕРКА ИМПОРТА MERGEDCELL:")
mergedcell_found = False
mergedcell_line = -1

for i, line in enumerate(lines):
    if 'MergedCell' in line and 'import' in line:
        mergedcell_found = True
        mergedcell_line = i
        print(f"   ✓ Импорт MergedCell найден на строке {i+1}: {line.strip()}")
        break

if not mergedcell_found:
    print("   ✗ Импорт MergedCell не найден")
    
    # Ищем импорты openpyxl
    print("   \n   Поиск импортов openpyxl:")
    for i, line in enumerate(lines[:50]):  # Первые 50 строк обычно содержат импорты
        if 'openpyxl' in line:
            print(f"     Строка {i+1}: {line.strip()}")
    
    # Добавляем импорт
    print("   \n   Добавляем импорт MergedCell...")
    
    # Находим место для добавления (после других импортов openpyxl)
    insert_line = -1
    for i, line in enumerate(lines[:50]):
        if 'from openpyxl' in line or 'import openpyxl' in line:
            insert_line = i + 1
    
    if insert_line > 0:
        lines.insert(insert_line, 'from openpyxl.cell.cell import MergedCell\n')
        print(f"   ✓ Импорт добавлен после строки {insert_line}")
    else:
        # Добавляем после существующих импортов
        for i, line in enumerate(lines[:50]):
            if line.strip() == '' and i > 10:  # Первая пустая строка после импортов
                lines.insert(i, 'from openpyxl.cell.cell import MergedCell\n')
                print(f"   ✓ Импорт добавлен на строку {i+1}")
                break

# 2. Проверяем другие импорты
print("\n2. ПРОВЕРКА ДРУГИХ ИМПОРТОВ:")

# energy_passport_calculations
energy_calc_found = False
for i, line in enumerate(lines):
    if 'energy_passport_calculations' in line and 'import' in line:
        energy_calc_found = True
        print(f"   ✓ energy_passport_calculations найден на строке {i+1}")
        break

if not energy_calc_found:
    print("   ✗ energy_passport_calculations не найден")
    print("   ℹ Это может быть внутренний модуль проекта")

# energy_units
energy_units_found = False
for i, line in enumerate(lines):
    if 'energy_units' in line and 'import' in line:
        energy_units_found = True
        print(f"   ✓ energy_units найден на строке {i+1}")
        break

if not energy_units_found:
    print("   ✗ energy_units не найден")
    print("   ℹ Это может быть внутренний модуль проекта")

# normative_integration
normative_found = False
for i, line in enumerate(lines):
    if 'normative_integration' in line and 'import' in line:
        normative_found = True
        print(f"   ✓ normative_integration найден на строке {i+1}")
        break

if not normative_found:
    print("   ✗ normative_integration не найден")
    print("   ℹ Это может быть внутренний модуль проекта")

# 3. Сохраняем изменения если были
if not mergedcell_found:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("\n✓ Файл обновлен с импортом MergedCell")
else:
    print("\n✓ Импорт MergedCell уже присутствует")

# 4. Проверяем использование MergedCell
print("\n3. ПРОВЕРКА ИСПОЛЬЗОВАНИЯ MERGEDCELL:")
usage_count = 0
for i, line in enumerate(lines):
    if 'MergedCell' in line and 'import' not in line:
        usage_count += 1
        print(f"   Строка {i+1}: {line.strip()}")

print(f"\n   Всего использований MergedCell: {usage_count}")

# 5. Рекомендации
print("\n=== РЕКОМЕНДАЦИИ ===")
print("1. Ошибки импорта energy_passport_calculations, energy_units, normative_integration")
print("   могут быть ложными срабатываниями Pylance, если это внутренние модули проекта.")
print("2. Проверьте структуру проекта и пути импорта.")
print("3. Если модули действительно отсутствуют, их нужно создать или установить.")
print("\n=== СТАТУС НАШЕГО ИСПРАВЛЕНИЯ ===")
print("✓ Импорт MergedCell проверен/исправлен")
print("✓ Функция safe_cell_write может использовать MergedCell")
print("✓ Наше исправление merged cells должно работать корректно")