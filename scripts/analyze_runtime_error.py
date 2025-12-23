#!/usr/bin/env python3
"""Анализ ошибки импорта MergedCell в рантайме"""

import re
from pathlib import Path

file_path = Path(r"C:\eaip\tools\fill_energy_passport.py")

print("=== АНАЛИЗ ОШИБКИ В РАНТАЙМЕ ===\n")

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Проверяем строку 1736 (ошибка name 'MergedCell' is not defined)
print("1. ОШИБКА В safe_cell_write (строка ~1736):")
print("   Сообщение: 'name \"MergedCell\" is not defined'")
print("   Контекст:")
for i in range(1730, 1745):
    if i < len(lines):
        print(f"   {i+1}: {lines[i].rstrip()}")

# 2. Проверяем строку 2049 (ошибка в fill_dinamika_sheet)
print("\n2. ОШИБКА В fill_dinamika_sheet (строка 2049):")
print("   Сообщение: 'MergedCell object attribute value is read-only'")
print("   Контекст:")
for i in range(2044, 2054):
    if i < len(lines):
        print(f"   {i+1}: {lines[i].rstrip()}")

# 3. Проверяем импорт MergedCell
print("\n3. ПРОВЕРКА ИМПОРТА MERGEDCELL:")
import_found = False
for i, line in enumerate(lines):
    if 'MergedCell' in line and 'import' in line:
        import_found = True
        print(f"   ✓ Импорт найден на строке {i+1}: {line.strip()}")
        
        # Проверяем синтаксис импорта
        if 'from openpyxl.cell.cell import MergedCell' in line:
            print("   ✓ Синтаксис импорта корректный")
        else:
            print("   ⚠️ Возможна проблема с синтаксисом импорта")

if not import_found:
    print("   ✗ Импорт MergedCell не найден")

# 4. Проверяем использование MergedCell в safe_cell_write
print("\n4. ИСПОЛЬЗОВАНИЕ MERGEDCELL В safe_cell_write:")
for i, line in enumerate(lines):
    if 'def safe_cell_write' in line:
        print(f"   Функция safe_cell_write начинается на строке {i+1}")
        # Ищем использование MergedCell в этой функции
        for j in range(i, min(i+50, len(lines))):
            if 'MergedCell' in lines[j]:
                print(f"   Использование MergedCell на строке {j+1}: {lines[j].strip()}")
        break

# 5. Проверяем, использует ли fill_dinamika_sheet safe_cell_write
print("\n5. ПРОВЕРКА fill_dinamika_sheet:")
in_dinamika = False
direct_assignments = []

for i, line in enumerate(lines):
    if 'def fill_dinamika_sheet' in line:
        in_dinamika = True
        print(f"   Функция начинается на строке {i+1}")
    
    if in_dinamika and 'ws.cell' in line and '.value =' in line:
        direct_assignments.append((i+1, line.strip()))
    
    if in_dinamika and 'safe_cell_write' in line:
        print(f"   ✓ Использует safe_cell_write на строке {i+1}")
        break

if direct_assignments:
    print(f"   ✗ Найдены прямые присваивания .value = ({len(direct_assignments)} шт.):")
    for line_num, line_text in direct_assignments[:5]:  # Покажем первые 5
        print(f"     Строка {line_num}: {line_text}")
    if len(direct_assignments) > 5:
        print(f"     ... и еще {len(direct_assignments) - 5} присваиваний")

# 6. Анализ проблемы
print("\n=== АНАЛИЗ ПРОБЛЕМЫ ===")
print("Проблема 1: Импорт MergedCell не работает в рантайме")
print("   Возможные причины:")
print("   1. Circular import (циклический импорт)")
print("   2. Проблема с путями Python")
print("   3. Импорт в условии или внутри функции")
print()
print("Проблема 2: Множественные места с прямой записью в ячейки")
print("   fill_dinamika_sheet и другие функции не используют safe_cell_write")
print()
print("Проблема 3: Нужно системное решение")
print("   Точечные исправления не работают, нужно исправить все места")

# 7. Рекомендации
print("\n=== РЕКОМЕНДАЦИИ ===")
print("1. Проверить импорт MergedCell в рантайме (запустить скрипт с импортом)")
print("2. Найти ВСЕ места с прямой записью .value =")
print("3. Создать декоратор или обертку для безопасной записи")
print("4. Применить ко всем функциям записи в Excel")
print("5. Протестировать системное решение")

# 8. Быстрое решение
print("\n=== БЫСТРОЕ РЕШЕНИЕ (временное) ===")
print("Добавить импорт прямо в safe_cell_write:")
print("def safe_cell_write(cell, value):")
print("    try:")
print("        from openpyxl.cell.cell import MergedCell")
print("        if isinstance(cell, MergedCell):")
print("            return False")
print("    except ImportError:")
print("        pass")
print("    # остальной код...")