#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест модуля восстановления формул"""
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / 'services' / 'ingest'))

from utils.ai_formula_restorer import restore_formulas_in_file

file_path = r"C:\Users\DELL\Downloads\Telegram Desktop\ЭНЕРГО_ПАСПОРТ_23102025.xlsm"
output_path = file_path.replace('.xlsm', '_auto_restored.xlsm')

print("Testing formula restorer...")
print(f"Input: {file_path}")
print(f"Output: {output_path}")

result = restore_formulas_in_file(file_path, output_path)

print("\nResults:")
print(f"  Total #REF! errors found: {result['total_ref_errors_found']}")
print(f"  Total restored: {result['total_restored']}")

if result['restored_by_sheet']:
    print("\nRestored formulas by sheet:")
    for sheet_name, formulas in result['restored_by_sheet'].items():
        print(f"  {sheet_name}: {len(formulas)} formulas")
        for f in formulas[:3]:  # Показываем первые 3
            print(f"    {f['cell']}: {f['old_formula'][:50]} -> {f['new_formula'][:50]}")
else:
    print("  No formulas restored")

print(f"\n✅ Result saved to: {output_path}")

