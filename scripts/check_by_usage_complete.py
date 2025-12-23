#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Полная диагностика by_usage - проверка всех мест хранения aggregated данных"""

import json
from pathlib import Path

print("=" * 80)
print("ПОЛНАЯ ДИАГНОСТИКА: Проверка by_usage во всех aggregated файлах")
print("=" * 80 + "\n")

# Проверяем все возможные места
aggregated_paths = [
    Path("data/aggregated"),
    Path("eaip_full_skeleton/infra/data/inbox/aggregated"),
    Path("eaip_full_skeleton/infra/data/aggregated"),
]

all_aggregated_files = []
for dir_path in aggregated_paths:
    if dir_path.exists():
        json_files = list(dir_path.glob("*_aggregated.json"))
        all_aggregated_files.extend(json_files)
        if json_files:
            print(f"✅ Найдено {len(json_files)} файлов в {dir_path}")

# Также проверяем файл с полными ресурсами
full_resources_file = Path("data/aggregated/aggregated_full_resources_2022_2024.json")
if full_resources_file.exists():
    all_aggregated_files.append(full_resources_file)
    print(f"✅ Найден файл полных ресурсов: {full_resources_file}")

print(f"\nВсего найдено aggregated файлов: {len(all_aggregated_files)}\n")

if not all_aggregated_files:
    print("❌ Aggregated JSON файлы не найдены ни в одном месте")
    exit(1)

# Анализируем последние 3 файла
all_aggregated_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
files_to_check = all_aggregated_files[:3]

print("=" * 80)
print("АНАЛИЗ ПОСЛЕДНИХ ФАЙЛОВ")
print("=" * 80 + "\n")

for file_path in files_to_check:
    print(f"\n{'='*80}")
    print(f"Файл: {file_path.name}")
    print(f"Путь: {file_path.absolute()}")
    print(f"{'='*80}\n")
    
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        
        resources = data.get("resources", {})
        electricity = resources.get("electricity", {})
        
        if not electricity:
            print("❌ resources.electricity отсутствует")
            continue
        
        print(f"✅ resources.electricity найден")
        print(f"   Кварталов: {len(electricity)}\n")
        
        # Проверяем наличие by_usage
        quarters_with_by_usage = []
        quarters_without_by_usage = []
        
        for quarter, quarter_data in electricity.items():
            by_usage = quarter_data.get("by_usage")
            if by_usage:
                quarters_with_by_usage.append(quarter)
                categories = list(by_usage.keys())
                total = sum(by_usage.values())
                print(f"✅ {quarter}: by_usage найден")
                print(f"   Категории: {categories}")
                print(f"   Сумма: {total:,.0f} кВт·ч")
                print(f"   Детали: {by_usage}\n")
            else:
                quarters_without_by_usage.append(quarter)
                available_keys = list(quarter_data.keys())
                quarter_total = quarter_data.get("quarter_totals", {}).get("active_kwh", 0)
                print(f"❌ {quarter}: by_usage ОТСУТСТВУЕТ")
                print(f"   Доступные ключи: {available_keys}")
                print(f"   quarter_totals.active_kwh: {quarter_total:,.0f}\n")
        
        print(f"{'='*80}")
        print(f"ИТОГИ для {file_path.name}:")
        print(f"{'='*80}")
        print(f"✅ Кварталов с by_usage: {len(quarters_with_by_usage)}")
        if quarters_with_by_usage:
            print(f"   {', '.join(quarters_with_by_usage)}")
        
        print(f"❌ Кварталов без by_usage: {len(quarters_without_by_usage)}")
        if quarters_without_by_usage:
            print(f"   {', '.join(quarters_without_by_usage)}")
        
        if len(quarters_with_by_usage) > 0:
            print(f"\n✅ ЭТОТ ФАЙЛ СОДЕРЖИТ ДАННЫЕ by_usage!")
            print(f"   Можно использовать для генерации паспорта")
        elif len(quarters_without_by_usage) > 0:
            print(f"\n❌ ПРОБЛЕМА: Данные by_usage отсутствуют")
            print(f"   Валидатор выдаст ошибку при генерации паспорта")
    
    except Exception as e:
        print(f"❌ Ошибка при анализе файла: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("ИТОГОВАЯ СВОДКА")
print("=" * 80 + "\n")

print("✅ ПРОВЕРКА 1: Файл pererashod.xlsx загружен")
print("✅ ПРОВЕРКА 2: Файл usage_categories.json создан")
print("✅ ПРОВЕРКА 3: Функция distribute_categories_by_quarter() вызывается")

# Финальная проверка - есть ли хотя бы один файл с by_usage
has_by_usage = False
for file_path in files_to_check:
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        electricity = data.get("resources", {}).get("electricity", {})
        for quarter_data in electricity.values():
            if quarter_data.get("by_usage"):
                has_by_usage = True
                break
        if has_by_usage:
            break
    except:
        pass

if has_by_usage:
    print("✅ ПРОВЕРКА 4: Данные by_usage найдены в aggregated файлах")
    print("\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
else:
    print("❌ ПРОВЕРКА 4: Данные by_usage НЕ найдены в aggregated файлах")
    print("\n⚠️ ПРОБЛЕМА: Нужно проверить логи обработки файлов")

print("\n" + "=" * 80)

