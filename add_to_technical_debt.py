#!/usr/bin/env python3
"""Добавление информации о исправлении merged cells в TECHNICAL_DEBT.md"""

import os
from pathlib import Path

file_path = Path(r"C:\eaip\TECHNICAL_DEBT.md")

print("=== ДОБАВЛЕНИЕ ИНФОРМАЦИИ В TECHNICAL_DEBT.md ===\n")

# Проверяем существование файла
if not file_path.exists():
    print(f"❌ Файл не найден: {file_path}")
    exit(1)

# Читаем содержимое
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Новая секция
new_section = '''

## 4. Исправление ошибки merged cells в fill_energy_passport.py

**Дата обнаружения:** 2025-12-06

**Суть проблемы:**
Ошибка `AttributeError: 'MergedCell' object attribute 'value' is read-only` в функции `_write_nodes_table` файла `fill_energy_passport.py` на строке 2175.

**Контекст:**
При записи данных в шаблон Excel "Метин" возникала ошибка при попытке записи в объединенные ячейки (merged cells). Функция `_write_nodes_table` использовала прямое присваивание:
```python
ws.cell(row=current_row, column=col_idx).value = value
```

**Выполненные действия (2025-12-06):**
1. ✅ Проанализирован существующий код проверки merged cells
2. ✅ Обнаружена функция `safe_cell_write` (строка 1693), которая уже содержит логику проверки
3. ✅ Изменены строки 2175 и 2180 в функции `_write_nodes_table`:
   - Было: `ws.cell(row=current_row, column=col_idx).value = value`
   - Стало: `safe_cell_write(ws.cell(row=current_row, column=col_idx), value)`

**Технический долг:**
1. **Пропуск данных:** Функция `safe_cell_write` возвращает `False` для merged cells, что означает пропуск записи данных. Если данные должны быть записаны, требуется дополнительная логика поиска свободных ячеек.
2. **Ограниченное решение:** Исправление решает проблему ошибки, но не гарантирует запись всех данных.
3. **Необходимость тестирования:** Требуется запуск теста `test_passport_generation_with_metin_template` для проверки корректности работы.

**Предлагаемые улучшения:**
1. **Функция поиска свободных ячеек:** Реализовать логику поиска альтернативных ячеек для записи данных.
2. **Расширенная проверка:** Добавить анализ структуры листа перед записью для определения безопасных зон.
3. **Рефакторинг файла:** Файл `fill_energy_passport.py` (2,246 строк) требует разделения на модули:
   - `excel_operations.py` (14 Excel-функций)
   - `utils.py` (вспомогательные функции)
   - `data_loaders.py` (функции загрузки данных)

**Приоритет:** Средний (ошибка исправлена, но требуется доработка для полного решения)

**Следующие шаги:**
1. Запустить тест `test_passport_generation_with_metin_template`
2. При необходимости реализовать функцию поиска свободных ячеек
3. Начать рефакторинг файла на модули
'''

# Добавляем новую секцию
new_content = content + new_section

# Сохраняем
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Информация добавлена в TECHNICAL_DEBT.md")
print("✅ Добавлен раздел 4: Исправление ошибки merged cells")
print("\n=== КРАТКОЕ СОДЕРЖАНИЕ ===")
print("1. Описана проблема с merged cells")
print("2. Задокументировано выполненное исправление")
print("3. Определен технический долг")
print("4. Предложены улучшения")
print("5. Определены следующие шаги")