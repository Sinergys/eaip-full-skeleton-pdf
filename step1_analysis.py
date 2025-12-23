#!/usr/bin/env python3
"""Шаг 1: Анализ существующего кода merged cells"""

import re
from pathlib import Path

file_path = Path(r"C:\eaip\tools\fill_energy_passport.py")

print("=== ШАГ 1: АНАЛИЗ СУЩЕСТВУЮЩЕГО КОДА ===\n")

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Ищем импорт MergedCell
print("1. ИМПОРТ MERGEDCELL:")
for i, line in enumerate(lines[:100]):
    if 'MergedCell' in line:
        print(f"   Строка {i+1}: {line.strip()}")

# 2. Ищем проверки MergedCell
print("\n2. ПРОВЕРКИ MERGEDCELL:")
for i, line in enumerate(lines):
    if 'MergedCell' in line and 'import' not in line:
        print(f"   Строка {i+1}: {line.strip()}")

# 3. Ищем функцию safe_cell_write
print("\n3. ФУНКЦИЯ safe_cell_write:")
for i, line in enumerate(lines):
    if 'def safe_cell_write' in line:
        print(f"   Найдена на строке {i+1}")
        # Покажем функцию
        for j in range(i, min(i+20, len(lines))):
            print(f"   {j+1}: {lines[j].rstrip()}")
        break

# 4. Ищем использование merged_cells
print("\n4. ИСПОЛЬЗОВАНИЕ merged_cells:")
for i, line in enumerate(lines):
    if 'merged_cells' in line.lower():
        print(f"   Строка {i+1}: {line.strip()}")

# 5. Анализ строки 2175 и контекста
print("\n5. КОНТЕКСТ СТРОКИ 2175:")
for i in range(2170, 2181):
    if i-1 < len(lines):
        print(f"   {i}: {lines[i-1].rstrip()}")

print("\n=== ВЫВОДЫ ===")
print("1. В файле уже есть импорт: from openpyxl.cell.cell import MergedCell")
print("2. Есть проверки: isinstance(cell, MergedCell)")
print("3. Есть функция safe_cell_write с логикой проверки")
print("4. Нужно использовать существующую логику для _write_nodes_table")

print("\n=== СЛЕДУЮЩИЙ ШАГ ===")
print("Создать функции is_merged_cell и find_free_cell на основе существующего кода")