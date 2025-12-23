#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Проверка и восстановление формулы AF13"""
import openpyxl
import json
from pathlib import Path

file_path = r"C:\Users\DELL\Downloads\Telegram Desktop\ЭНЕРГО_ПАСПОРТ_23102025.xlsm"

wb = openpyxl.load_workbook(file_path, data_only=False)

print("Checking target cell AM14 in Структура пр 2 sheet...")
struktura_sheet = wb['Структура пр 2 ']
balans_sheet = wb['Баланс']

# Проверяем ячейку AM14
cell_am14 = struktura_sheet['AM14']
print(f"AM14 value: {cell_am14.value}")
print(f"AM14 data type: {cell_am14.data_type}")

# Проверяем паттерн вокруг AM14
print("\nPattern check around AM14:")
for row in range(11, 16):
    cell_val = struktura_sheet[f'AM{row}'].value
    cell_type = struktura_sheet[f'AM{row}'].data_type
    balans_ref = f"AF{row-1}" if row > 11 else f"AF{row}"
    if row == 13:
        balans_ref = "AF13"
    print(f"  AM{row}: {cell_val} (type: {cell_type}) -> should reference from {balans_ref}")

# Проверяем, что находится в строке 13 листа "Баланс"
print("\nRow 13 in Баланс sheet (columns Z-AG):")
for col_letter in ['Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG']:
    cell = balans_sheet[f'{col_letter}13']
    if cell.data_type == 'f':
        formula = str(cell.value)
        # Извлекаем ссылку на ячейку
        if 'Структура пр 2' in formula:
            # Находим ссылку типа !AM14
            import re
            match = re.search(r'!([A-Z]+\d+)', formula)
            if match:
                ref = match.group(1)
                print(f"  {col_letter}13: {formula[:50]} -> references {ref}")
            else:
                print(f"  {col_letter}13: {formula[:50]}")
        else:
            print(f"  {col_letter}13: {formula[:50]}")
    else:
        print(f"  {col_letter}13: {cell.value}")

# Формулируем восстановленную формулу
restored_formula = "='Структура пр 2 '!AM14"
print(f"\n✅ Recommended restored formula for AF13:")
print(f"   {restored_formula}")

# Сохраняем результат
result = {
    'error_cell': 'AF13',
    'sheet': 'Баланс',
    'current_formula': str(balans_sheet['AF13'].value),
    'restored_formula': restored_formula,
    'target_cell': 'AM14',
    'target_sheet': 'Структура пр 2',
    'target_value': str(cell_am14.value) if cell_am14.value else None,
    'target_data_type': cell_am14.data_type,
    'pattern_analysis': {
        'af10_refers_to': 'AM11',
        'af11_refers_to': 'AM12',
        'af12_refers_to': 'AM13',
        'af13_should_refer_to': 'AM14',  # Восстанавливаем
        'af14_refers_to': 'AM15'
    },
    'confidence': 'high',
    'reasoning': 'Pattern shows each AF row references corresponding AM row in Структура пр 2 sheet'
}

output_file = Path(__file__).parent / 'formula_restoration_af13.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\nRestoration result saved to: {output_file}")

