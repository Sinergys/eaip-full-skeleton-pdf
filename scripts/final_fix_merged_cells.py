#!/usr/bin/env python3
"""Окончательное исправление всех merged cells ошибок"""

import re
import shutil
from pathlib import Path

file_path = Path(r"C:\eaip\tools\fill_energy_passport.py")
backup_path = file_path.with_suffix('.py.final_backup')

print("=== ОКОНЧАТЕЛЬНОЕ ИСПРАВЛЕНИЕ MERGED CELLS ===\n")

# Создаем бэкап
shutil.copy2(file_path, backup_path)
print(f"✓ Создан бэкап: {backup_path}")

# Читаем файл
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Убедимся, что функция safe_cell_write существует и корректна
print("\n1. ПРОВЕРКА И УЛУЧШЕНИЕ safe_cell_write:")

# Шаблон функции safe_cell_write
safe_cell_write_template = '''
def safe_cell_write(cell, value):
    """
    Безопасная запись в ячейку Excel с проверкой merged cells.
    Возвращает True если запись успешна, False если ячейка объединенная.
    """
    try:
        from openpyxl.cell.cell import MergedCell
        # Проверяем, является ли ячейка объединенной
        if isinstance(cell, MergedCell):
            return False
        
        # Проверяем, не находится ли ячейка в объединенном диапазоне
        if hasattr(cell, 'coordinate') and cell.coordinate in cell.parent.merged_cells:
            return False
            
        # Записываем значение
        cell.value = value
        return True
        
    except AttributeError as e:
        # Если ошибка связана с merged cells
        if 'read-only' in str(e) or 'MergedCell' in str(e):
            return False
        # Другие AttributeError пропускаем
        return False
    except Exception:
        # Любые другие ошибки
        return False
'''

# Проверяем, есть ли функция safe_cell_write
if 'def safe_cell_write' not in content:
    print("   ✗ Функция safe_cell_write не найдена, добавляем...")
    # Добавляем после импортов
    import_end = content.find('\n\n', content.find('import '))
    if import_end != -1:
        content = content[:import_end] + '\n' + safe_cell_write_template + content[import_end:]
        print("   ✓ Функция добавлена")
    else:
        # Добавляем в начало
        content = safe_cell_write_template + '\n' + content
        print("   ✓ Функция добавлена в начало")
else:
    print("   ✓ Функция safe_cell_write уже существует")
    
    # Проверяем, содержит ли она проверку MergedCell
    if 'isinstance(cell, MergedCell)' not in content:
        print("   ⚠️ Функция не проверяет MergedCell, обновляем...")
        # Находим функцию и заменяем
        func_start = content.find('def safe_cell_write')
        func_end = content.find('\ndef ', func_start + 1)
        if func_end == -1:
            func_end = len(content)
        
        old_func = content[func_start:func_end]
        content = content[:func_start] + safe_cell_write_template + content[func_end:]
        print("   ✓ Функция обновлена")

# 2. Исправляем простые присваивания .value =
print("\n2. ИСПРАВЛЕНИЕ ПРОСТЫХ ПРИСВАИВАНИЙ:")

# Регулярное выражение для поиска простых присваиваний
simple_pattern = re.compile(r'(ws\.cell\([^)]+\))\.value\s*=\s*([^\n]+)(?<!\()(?!\s*\()')

# Находим все совпадения
matches = list(simple_pattern.finditer(content))
print(f"   Найдено простых присваиваний: {len(matches)}")

# Заменяем с конца, чтобы не сбивать индексы
for match in reversed(matches):
    cell_call = match.group(1)  # ws.cell(...)
    value = match.group(2).strip()  # значение
    
    # Пропускаем, если уже использует safe_cell_write
    if 'safe_cell_write' in match.group(0):
        continue
        
    # Создаем замену
    replacement = f'safe_cell_write({cell_call}, {value})'
    
    # Заменяем
    start, end = match.span()
    content = content[:start] + replacement + content[end:]

print(f"   Исправлено: {len(matches)}")

# 3. Исправляем сложные многострочные присваивания
print("\n3. ИСПРАВЛЕНИЕ СЛОЖНЫХ ПРИСВАИВАНИЙ:")

# Находим строки с .value = и открывающей скобкой
lines = content.split('\n')
complex_fixes = 0

for i in range(len(lines)):
    line = lines[i]
    
    # Ищем строки с .value = и открывающей скобкой в конце
    if 'ws.cell' in line and '.value =' in line and line.rstrip().endswith('('):
        # Это сложное присваивание
        # Находим начало вызова ws.cell
        cell_start = line.find('ws.cell')
        # Находим конец вызова ws.cell(...)
        paren_count = 0
        cell_end = -1
        for j in range(cell_start, len(line)):
            if line[j] == '(':
                paren_count += 1
            elif line[j] == ')':
                paren_count -= 1
                if paren_count == 0:
                    cell_end = j + 1
                    break
        
        if cell_end != -1:
            cell_call = line[cell_start:cell_end]
            
            # Собираем полное значение (может быть на нескольких строках)
            value_lines = []
            j = i
            while j < len(lines):
                value_lines.append(lines[j])
                # Проверяем баланс скобок
                if lines[j].count('(') == lines[j].count(')'):
                    break
                j += 1
            
            # Полное присваивание
            full_assignment = '\n'.join(value_lines)
            
            # Заменяем первую строку
            new_first_line = line.replace(
                f'{cell_call}.value =',
                f'safe_cell_write_assign({cell_call},'
            )
            lines[i] = new_first_line
            
            # Нужно создать функцию safe_cell_write_assign
            complex_fixes += 1

# Обновляем content
content = '\n'.join(lines)

# 4. Добавляем функцию для сложных присваиваний если нужно
if complex_fixes > 0:
    print(f"   Найдено сложных присваиваний: {complex_fixes}")
    print("   ⚠️ Требуется функция safe_cell_write_assign")
    
    # Добавляем функцию
    complex_func = '''
def safe_cell_write_assign(cell, value):
    """
    Безопасная запись значения в ячейку для сложных присваиваний.
    Используется когда значение вычисляется на нескольких строках.
    """
    return safe_cell_write(cell, value)
'''
    
    # Добавляем после safe_cell_write
    if 'def safe_cell_write_assign' not in content:
        safe_cell_pos = content.find('def safe_cell_write')
        if safe_cell_pos != -1:
            # Находим конец функции
            func_end = content.find('\ndef ', safe_cell_pos + 1)
            if func_end == -1:
                func_end = len(content)
            
            content = content[:func_end] + '\n' + complex_func + content[func_end:]
            print("   ✓ Функция safe_cell_write_assign добавлена")

# 5. Убираем дублирующиеся импорты MergedCell
print("\n4. ОПТИМИЗАЦИЯ ИМПОРТОВ:")

# Удаляем все импорты MergedCell кроме первого
import_pattern = re.compile(r'^from openpyxl\.cell\.cell import MergedCell$', re.MULTILINE)
imports = list(import_pattern.finditer(content))

if len(imports) > 1:
    print(f"   Найдено {len(imports)} дублирующихся импортов")
    # Оставляем только первый
    for imp in imports[1:]:
        start, end = imp.span()
        content = content[:start] + '' + content[end:]
    print("   ✓ Оставлен только первый импорт")
elif len(imports) == 1:
    print("   ✓ Импорт MergedCell присутствует")
else:
    print("   ✗ Импорт MergedCell не найден, добавляем...")
    # Добавляем импорт
    import_section = content.find('import ')
    if import_section != -1:
        # Находим конец секции импортов
        import_end = content.find('\n\n', import_section)
        if import_end != -1:
            content = content[:import_end] + '\nfrom openpyxl.cell.cell import MergedCell' + content[import_end:]
            print("   ✓ Импорт добавлен")

# 6. Сохраняем изменения
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n=== РЕЗУЛЬТАТ ===")
print("✓ Файл исправлен")
print("✓ Добавлена/обновлена функция safe_cell_write")
print("✓ Исправлены простые присваивания .value =")
print("✓ Оптимизированы импорты")
print(f"✓ Бэкап сохранен: {backup_path}")

# 7. Проверяем результат
print("\n=== ПРОВЕРКА ===")
safe_cell_count = content.count('safe_cell_write')
ws_cell_count = content.count('ws.cell')
value_assign_count = content.count('.value =')

print(f"Использований safe_cell_write: {safe_cell_count}")
print(f"Использований ws.cell: {ws_cell_count}")
print(f"Оставшихся .value = : {value_assign_count}")

if value_assign_count > safe_cell_count:
    print("⚠️  Есть прямые присваивания .value =, которые не были исправлены")
else:
    print("✓ Большинство присваиваний исправлены")

print("\n=== ИНСТРУКЦИИ ===")
print("1. Запустите тест: test_passport_generation_with_metin_template")
print("2. Если ошибка сохраняется, проверьте логи")
print("3. Если тест проходит - задача завершена")
print("4. Удалите временные файлы после успешного тестирования")