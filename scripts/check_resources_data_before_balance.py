#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка resources_data перед вызовом fill_balans_sheet()"""

import json
from pathlib import Path

print("=" * 80)
print("ПРОВЕРКА: resources_data перед fill_balans_sheet()")
print("=" * 80 + "\n")

# Читаем код main.py чтобы понять откуда берется resources_data
main_py = Path("eaip_full_skeleton/services/ingest/main.py")
content = main_py.read_text(encoding="utf-8")

# Ищем где resources_data формируется
print("1. АНАЛИЗ КОДА: Откуда берется resources_data?\n")

# Строка 1691: resources_data = aggregated.get("resources") or aggregated
if "resources_data = aggregated.get" in content:
    print("✅ resources_data берется из aggregated.get('resources')")
    print("   Строка ~1691: resources_data = aggregated.get('resources') or aggregated\n")

# Проверяем, есть ли логирование resources_data
if "logger.info.*resources_data" in content or "logger.info.*ресурсов" in content:
    print("✅ Есть логирование resources_data")
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "resources_data" in line and "logger" in line:
            print(f"   Строка {i+1}: {line.strip()[:80]}")
else:
    print("⚠️ Логирование resources_data не найдено\n")

# Проверяем, есть ли проверка by_usage перед fill_balans_sheet
print("\n2. ПРОВЕРКА: Есть ли проверка by_usage перед fill_balans_sheet()?\n")

fill_balans_line = None
lines = content.split("\n")
for i, line in enumerate(lines):
    if "fill_balans_sheet(" in line:
        fill_balans_line = i + 1
        print(f"✅ Вызов fill_balans_sheet() найден на строке {fill_balans_line}")
        print(f"   {line.strip()}\n")
        
        # Показываем контекст (10 строк до и после)
        print("   Контекст (10 строк до вызова):")
        for j in range(max(0, i-10), i):
            print(f"   {j+1:4d}: {lines[j]}")
        
        print(f"\n   >>> СТРОКА {i+1}: {lines[i]}")
        
        print("\n   Контекст (5 строк после вызова):")
        for j in range(i+1, min(len(lines), i+6)):
            print(f"   {j+1:4d}: {lines[j]}")
        break

# Проверяем, есть ли диагностика by_usage
print("\n3. ПРОВЕРКА: Есть ли диагностика by_usage в коде?\n")

has_diagnostic = False
for i, line in enumerate(lines):
    if "by_usage" in line.lower() and ("logger" in line or "print" in line or "debug" in line):
        has_diagnostic = True
        print(f"   Строка {i+1}: {line.strip()[:100]}")

if not has_diagnostic:
    print("   ❌ Диагностика by_usage не найдена перед fill_balans_sheet()")

print("\n" + "=" * 80)
print("РЕКОМЕНДАЦИИ")
print("=" * 80 + "\n")

print("Нужно добавить диагностику перед вызовом fill_balans_sheet():")
print("""
# Перед строкой 1960 (fill_balans_sheet)
if balans_sheet:
    # ДИАГНОСТИКА: Проверяем наличие by_usage
    electricity = resources_data.get("electricity", {})
    quarters_with_by_usage = []
    quarters_without_by_usage = []
    
    for quarter, quarter_data in electricity.items():
        by_usage = quarter_data.get("by_usage")
        if by_usage:
            quarters_with_by_usage.append(quarter)
        else:
            quarters_without_by_usage.append(quarter)
    
    logger.info(f"Перед fill_balans_sheet(): кварталов с by_usage: {len(quarters_with_by_usage)}, без: {len(quarters_without_by_usage)}")
    
    if quarters_without_by_usage:
        logger.warning(f"Кварталы без by_usage: {quarters_without_by_usage}")
    
    logger.info(f"Заполнение листа '{balans_sheet.title}'")
    fill_balans_sheet(balans_sheet, resources_data)
""")

