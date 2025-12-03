#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Применение восстановленной формулы AF13"""
import openpyxl
import json
from pathlib import Path
from datetime import datetime

file_path = r"C:\Users\DELL\Downloads\Telegram Desktop\ЭНЕРГО_ПАСПОРТ_23102025.xlsm"
backup_path = file_path.replace('.xlsm', '_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.xlsm')

print("Creating backup...")
import shutil
shutil.copy2(file_path, backup_path)
print(f"Backup created: {backup_path}")

print("\nLoading workbook...")
wb = openpyxl.load_workbook(file_path, data_only=False)

print("Applying restored formula to AF13...")
sheet = wb['Баланс']
cell = sheet['AF13']

print(f"  Old formula: {cell.value}")
cell.value = "='Структура пр 2 '!AM14"
print(f"  New formula: {cell.value}")

# Сохраняем результат
output_path = file_path.replace('.xlsm', '_restored.xlsm')
wb.save(output_path)
print(f"\n✅ Saved restored file to: {output_path}")

# Сохраняем отчет
report = {
    'timestamp': datetime.now().isoformat(),
    'original_file': file_path,
    'backup_file': backup_path,
    'restored_file': output_path,
    'restored_formulas': [
        {
            'cell': 'AF13',
            'sheet': 'Баланс',
            'old_formula': "='Структура пр 2 '!#REF!",
            'new_formula': "='Структура пр 2 '!AM14",
            'confidence': 'high'
        }
    ]
}

report_file = Path(__file__).parent / 'formula_restoration_report.json'
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"Report saved to: {report_file}")

