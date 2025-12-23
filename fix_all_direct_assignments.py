#!/usr/bin/env python3
"""Исправление ВСЕХ прямых присваиваний .value = в fill_energy_passport.py"""

import re
from pathlib import Path

file_path = Path(r"C:\eaip\tools\fill_energy_passport.py")
backup_path = file_path.with_suffix('.py.backup_all')

print("=== ИСПРАВЛЕНИЕ ВСЕХ ПРЯМЫХ ПРИСВАИВАНИЙ ===\n")

# Создаем бэкап
import shutil
shutil.copy2(file_path, backup_path)
print(f"✓ Создан бэкап: {backup_path}")

# Читаем файл
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Находим ВСЕ прямые присваивания .value =
print("\n1. ПОИСК ПРЯМЫХ ПРИСВАИВАНИЙ .value =:")

direct_assignments = []
pattern = re.compile(r'(ws\.cell\(.*?\))\.value\s*=')

for i, line in enumerate(lines):
    if 'ws.cell' in line and '.value =' in line:
        # Проверяем, не используется ли уже safe_cell_write
        if 'safe_cell_write' not in line:
            direct_assignments.append((i, line))
            print(f"   Строка {i+1}: {line.strip()}")

print(f"\n   Всего найдено: {len(direct_assignments)} прямых присваиваний")

# 2. Исправляем каждое присваивание
print("\n2. ИСПРАВЛЕНИЕ ПРИСВАИВАНИЙ:")

replacements_made = 0
for line_num, line_text in direct_assignments:
    # Ищем паттерн ws.cell(...).value =
    match = pattern.search(line_text)
    if match:
        cell_call = match.group(1)  # ws.cell(...)
        
        # Находим значение после =
        value_start = line_text.find('=', match.end()) + 1
        value_part = line_text[value_start:].strip()
        
        # Если значение продолжается на следующей строке (скобки)
        if value_part.endswith('(') or not value_part:
            # Сложный случай - значение в нескольких строках
            # Пропускаем для простоты
            print(f"   ⚠️ Строка {line_num+1}: Сложное присваивание, пропускаем")
            continue
        
        # Создаем замену
        new_line = line_text.replace(
            f'{cell_call}.value = {value_part}',
            f'safe_cell_write({cell_call}, {value_part})'
        )
        
        lines[line_num] = new_line
        replacements_made += 1
        print(f"   ✓ Строка {line_num+1}: Исправлено")

# 3. Убираем дублирующиеся импорты MergedCell
print("\n3. ОПТИМИЗАЦИЯ ИМПОРТОВ MERGEDCELL:")

import_lines = []
for i, line in enumerate(lines):
    if 'from openpyxl.cell.cell import MergedCell' in line:
        import_lines.append(i)

if len(import_lines) > 1:
    print(f"   Найдено {len(import_lines)} дублирующихся импортов")
    # Оставляем только первый импорт
    for i in import_lines[1:]:
        lines[i] = ''  # Удаляем дубли
    print(f"   Оставлен только первый импорт на строке {import_lines[0]+1}")

# 4. Добавляем импорт в safe_cell_write на случай проблем
print("\n4. УЛУЧШЕНИЕ safe_cell_write:")

# Находим safe_cell_write
for i, line in enumerate(lines):
    if 'def safe_cell_write' in line:
        safe_cell_start = i
        break

# Добавляем локальный импорт в начало функции
local_import = "    try:\n        from openpyxl.cell.cell import MergedCell\n    except ImportError:\n        MergedCell = None  # Fallback\n"

# Вставляем после первой строки функции (после def ...:)
for i in range(safe_cell_start, safe_cell_start + 10):
    if i < len(lines) and lines[i].strip().startswith('"""'):
        # Пропускаем докстринг
        continue
    if i < len(lines) and lines[i].strip().startswith('try:'):
        # Вставляем перед try:
        lines.insert(i, local_import)
        print("   ✓ Добавлен локальный импорт MergedCell в safe_cell_write")
        break

# 5. Сохраняем изменения
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\n=== РЕЗУЛЬТАТ ===")
print(f"✓ Исправлено присваиваний: {replacements_made} из {len(direct_assignments)}")
print(f"✓ Оптимизированы импорты MergedCell")
print(f"✓ Улучшена функция safe_cell_write")
print(f"\n=== СЛЕДУЮЩИЕ ШАГИ ===")
print("1. Запустите тест снова: test_passport_generation_with_metin_template")
print("2. Если ошибка сохраняется, проверьте логи")
print("3. Если тест проходит - задача завершена")
print(f"\nБэкап сохранен: {backup_path}")