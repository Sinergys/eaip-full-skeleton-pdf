#!/usr/bin/env python3
"""Анализ зависимостей fill_energy_passport.py"""

import re
from pathlib import Path

file_path = Path(r"C:\eaip\tools\fill_energy_passport.py")

print("=== АНАЛИЗ СТРУКТУРЫ ФАЙЛА ===\n")

# 1. Чтение файла
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
print(f"Общая статистика:")
print(f"  Всего строк: {total_lines}")

# 2. Поиск функций и классов
functions = []
classes = []

for i, line in enumerate(lines):
    line = line.strip()
    
    # Функции
    func_match = re.match(r'^def (\w+)', line)
    if func_match:
        functions.append({
            'name': func_match.group(1),
            'line': i + 1
        })
    
    # Классы
    class_match = re.match(r'^class (\w+)', line)
    if class_match:
        classes.append({
            'name': class_match.group(1),
            'line': i + 1
        })

print(f"  Функций: {len(functions)}")
print(f"  Классов: {len(classes)}")

# 3. Анализ импортов
print("\n=== ИМПОРТЫ ===")
imports = []
for i in range(min(100, len(lines))):
    line = lines[i].strip()
    if line.startswith(('import ', 'from ')):
        imports.append(line)

print(f"Всего импортов: {len(imports)}")
for imp in imports[:20]:  # Покажем первые 20
    print(f"  {imp}")
if len(imports) > 20:
    print(f"  ... и еще {len(imports) - 20} импортов")

# 4. Группировка функций по паттернам
print("\n=== ГРУППИРОВКА ФУНКЦИЙ ===")

patterns = {
    'Excel': ['excel', 'ws\\.', 'cell', 'workbook', 'sheet', 'openpyxl', 'xlsx', 'xls', 'write', 'read'],
    'Data': ['data', 'process', 'transform', 'convert', 'parse', 'extract', 'load', 'save'],
    'Validation': ['valid', 'check', 'verify', 'assert', 'is_', 'validate'],
    'Template': ['template', 'метин', 'шаблон', 'pattern'],
    'Utility': ['util', 'helper', 'get_', 'set_', 'find_', 'create_', 'make_', 'build_'],
}

function_groups = {}
for func in functions:
    name = func['name'].lower()
    group = 'Other'
    
    for group_name, group_patterns in patterns.items():
        for pattern in group_patterns:
            if re.search(pattern, name):
                group = group_name
                break
        if group != 'Other':
            break
    
    if group not in function_groups:
        function_groups[group] = []
    function_groups[group].append(func['name'])

# Вывод групп
for group in sorted(function_groups.keys()):
    funcs = function_groups[group]
    print(f"\n{group} ({len(funcs)} функций):")
    # Покажем первые 10 функций в группе
    for func in sorted(funcs)[:10]:
        print(f"  {func}")
    if len(funcs) > 10:
        print(f"  ... и еще {len(funcs) - 10} функций")

# 5. Поиск зависимостей между функциями
print("\n=== АНАЛИЗ ВЫЗОВОВ ФУНКЦИЙ ===")

# Создаем словарь вызовов
function_calls = {}
current_function = None

for i, line in enumerate(lines):
    line = line.strip()
    
    # Начало функции
    func_match = re.match(r'^def (\w+)', line)
    if func_match:
        current_function = func_match.group(1)
        function_calls[current_function] = []
        continue
    
    # Пропускаем пустые строки и комментарии
    if not line or line.startswith('#'):
        continue
    
    # Ищем вызовы функций (упрощенно)
    if current_function:
        # Ищем паттерны вызовов функций
        calls = re.findall(r'\b(\w+)\s*\(', line)
        for call in calls:
            # Исключаем ключевые слова и встроенные функции
            if call not in ['if', 'elif', 'while', 'for', 'def', 'class', 'return', 
                           'print', 'len', 'str', 'int', 'float', 'list', 'dict',
                           'set', 'tuple', 'range', 'enumerate', 'isinstance']:
                if call in [f['name'] for f in functions]:
                    if call not in function_calls[current_function]:
                        function_calls[current_function].append(call)

# Анализ графа вызовов
print("\nФункции с наибольшим количеством вызовов других функций:")
call_counts = []
for func, calls in function_calls.items():
    if calls:
        call_counts.append((func, len(calls)))

call_counts.sort(key=lambda x: x[1], reverse=True)
for func, count in call_counts[:10]:
    print(f"  {func}: вызывает {count} других функций")

# 6. Рекомендации
print("\n=== РЕКОМЕНДАЦИИ ПО РЕФАКТОРИНГУ ===")
print("\n1. ПРИОРИТЕТНЫЕ МОДУЛИ ДЛЯ ВЫДЕЛЕНИЯ:")

# Определяем наиболее независимые группы
module_priority = []
for group in ['Excel', 'Utility', 'Validation', 'Data', 'Template']:
    if group in function_groups:
        count = len(function_groups[group])
        if count > 0:
            module_priority.append((group, count))

module_priority.sort(key=lambda x: x[1], reverse=True)

for i, (group, count) in enumerate(module_priority, 1):
    print(f"   {i}. {group} модуль ({count} функций)")
    # Примеры функций
    examples = function_groups[group][:3]
    print(f"      Примеры: {', '.join(examples)}")

print("\n2. ПЛАН РЕФАКТОРИНГА:")
print("   Фаза 1: Выделить excel_operations.py")
print("   Фаза 2: Выделить utils.py (вспомогательные функции)")
print("   Фаза 3: Выделить validators.py")
print("   Фаза 4: Выделить data_processor.py")
print("   Фаза 5: Выделить template_manager.py")

print("\n3. ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:")
print("   - Уменьшение размера основного файла на 80-90%")
print("   - Улучшение читаемости кода")
print("   - Упрощение тестирования")
print("   - Ускорение разработки новых функций")

# 7. Оценка сложности
print("\n=== ОЦЕНКА СЛОЖНОСТИ ===")
print("Ориентировочное время: 3-5 дней")
print("Риски: низкие (поэтапный подход)")
print("Выгода: высокая (долгосрочное упрощение поддержки)")