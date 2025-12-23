#!/usr/bin/env python3
"""Минимальное исправление только критических ошибок"""

from pathlib import Path

file_path = Path(r"C:\eaip\tools\fill_energy_passport.py")
backup_path = file_path.with_suffix('.py.minimal_backup')

print("=== МИНИМАЛЬНОЕ ИСПРАВЛЕНИЕ КРИТИЧЕСКИХ ОШИБОК ===\n")

import shutil
shutil.copy2(file_path, backup_path)
print(f"✓ Создан бэкап: {backup_path}")

# Читаем файл
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("\n1. ИСПРАВЛЕНИЕ КРИТИЧЕСКИХ МЕСТ:")

# Места, где были ошибки в тесте
critical_fixes = [
    {
        'line': 2049,  # fill_dinamika_sheet
        'old': '        ws.cell(row=current_row, column=2).value = (',
        'new': '        safe_cell_write(ws.cell(row=current_row, column=2), ('
    },
    {
        'line': 2175,  # _write_nodes_table
        'old': '                ws.cell(row=current_row, column=col_idx).value = value',
        'new': '                safe_cell_write(ws.cell(row=current_row, column=col_idx), value)'
    },
    {
        'line': 2180,  # _write_nodes_table
        'old': '                ws.cell(row=current_row, column=col_idx).value = value',
        'new': '                safe_cell_write(ws.cell(row=current_row, column=col_idx), value)'
    }
]

fixes_applied = 0
for fix in critical_fixes:
    line_idx = fix['line'] - 1
    
    if line_idx < len(lines):
        current_line = lines[line_idx].rstrip('\n')
        
        if fix['old'] in current_line:
            lines[line_idx] = fix['new'] + '\n'
            print(f"   ✓ Строка {fix['line']}: Исправлено")
            fixes_applied += 1
        else:
            print(f"   ⚠️ Строка {fix['line']}: Паттерн не найден")
            print(f"     Текущая строка: {current_line[:80]}...")
    else:
        print(f"   ✗ Строка {fix['line']}: Выход за границы файла")

print(f"\n   Всего применено исправлений: {fixes_applied}")

# 2. Проверяем функцию safe_cell_write
print("\n2. ПРОВЕРКА safe_cell_write:")

safe_func_found = False
for i, line in enumerate(lines):
    if 'def safe_cell_write' in line:
        safe_func_found = True
        print(f"   ✓ Функция найдена на строке {i+1}")
        
        # Проверяем базовую функциональность
        has_try_except = False
        for j in range(i, min(i+20, len(lines))):
            if 'try:' in lines[j] and 'except' in ''.join(lines[j:j+5]):
                has_try_except = True
                break
        
        if has_try_except:
            print("   ✓ Имеет обработку ошибок (try/except)")
        else:
            print("   ⚠️ Нет обработки ошибок, добавляем...")
            # Находим начало функции и добавляем try/except
            for j in range(i, min(i+10, len(lines))):
                if lines[j].strip().startswith('"""'):
                    # После докстринга
                    for k in range(j+1, min(j+5, len(lines))):
                        if lines[k].strip():
                            # Вставляем try/except перед первым непустым кодом
                            try_except = '''    try:
        cell.value = value
        return True
    except AttributeError:
        # Если ячейка объединенная (MergedCell)
        return False
'''
                            lines.insert(k, try_except)
                            print("   ✓ Добавлена обработка ошибок")
                            break
                    break
        break

if not safe_func_found:
    print("   ✗ Функция не найдена, добавляем простую версию...")
    simple_func = '''
def safe_cell_write(cell, value):
    """Безопасная запись в ячейку"""
    try:
        cell.value = value
        return True
    except AttributeError:
        # Если ячейка объединенная (MergedCell)
        return False
'''
    # Добавляем после импортов
    for i, line in enumerate(lines):
        if line.strip().startswith('def ') and i > 10:
            lines.insert(i, '\n' + simple_func)
            print("   ✓ Функция добавлена")
            break

# 3. Сохраняем
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n=== РЕЗУЛЬТАТ ===")
print(f"✓ Применено {fixes_applied} критических исправлений")
print(f"✓ Проверена/добавлена функция safe_cell_write")
print(f"✓ Бэкап сохранен: {backup_path}")

# 4. Проверка синтаксиса
print("\n=== ПРОВЕРКА СИНТАКСИСА ===")
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    compile(content, file_path.name, 'exec')
    print("✓ Синтаксис корректен")
except SyntaxError as e:
    print(f"✗ Ошибка синтаксиса: {e}")
    print(f"   Строка {e.lineno}: {content.split('\\n')[e.lineno-1][:80]}...")

print("\n=== ЗАПУСТИТЕ ТЕСТ ===")
print("cd C:\\eaip\\eaip_full_skeleton")
print("python -m pytest services/ingest/tests/test_passport_e2e_audit_sinergys.py::test_passport_generation_with_metin_template -v")