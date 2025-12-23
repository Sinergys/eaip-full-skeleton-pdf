#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
try:
    from openpyxl import load_workbook
    wb = load_workbook('templates/pcm690/metin.xlsx')
    print('Листы в шаблоне metin:')
    for sheet in wb.worksheets:
        print(f'  - {sheet.title}')
    print(f'Всего: {len(wb.worksheets)}')
except Exception as e:
    print(f'Ошибка: {e}')
    import traceback
    traceback.print_exc()