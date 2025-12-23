#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Диагностика проблемы с отсутствием electricity.by_usage"""

import json
from pathlib import Path

print("=" * 80)
print("ДИАГНОСТИКА ПРОБЛЕМЫ: отсутствует electricity.by_usage")
print("=" * 80 + "\n")

# Проверяем структуру aggregated JSON файлов
aggregated_dir = Path("data/aggregated")
if not aggregated_dir.exists():
    print(f"❌ Директория {aggregated_dir} не найдена")
    exit(1)

print("Поиск aggregated JSON файлов...\n")
json_files = list(aggregated_dir.glob("*_aggregated.json"))

if not json_files:
    print("❌ Не найдено aggregated JSON файлов")
    exit(1)

# Анализируем последний файл
latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
print(f"Анализируем файл: {latest_file.name}\n")

try:
    data = json.loads(latest_file.read_text(encoding="utf-8"))
    
    print("=" * 80)
    print("СТРУКТУРА ДАННЫХ")
    print("=" * 80 + "\n")
    
    resources = data.get("resources", {})
    print(f"Ресурсы: {list(resources.keys())}\n")
    
    electricity = resources.get("electricity", {})
    if not electricity:
        print("❌ ПРОБЛЕМА: resources.electricity отсутствует!")
    else:
        print(f"✅ resources.electricity найден")
        print(f"   Кварталов: {len(electricity)}\n")
        
        # Проверяем наличие by_usage в каждом квартале
        quarters_with_by_usage = []
        quarters_without_by_usage = []
        
        for quarter, quarter_data in electricity.items():
            by_usage = quarter_data.get("by_usage")
            if by_usage:
                quarters_with_by_usage.append(quarter)
                print(f"✅ {quarter}: by_usage найден")
                print(f"   Категории: {list(by_usage.keys())}")
                print(f"   Значения: {by_usage}\n")
            else:
                quarters_without_by_usage.append(quarter)
                print(f"❌ {quarter}: by_usage ОТСУТСТВУЕТ")
                print(f"   Доступные ключи: {list(quarter_data.keys())}\n")
        
        print("=" * 80)
        print("ИТОГИ")
        print("=" * 80 + "\n")
        print(f"Кварталов с by_usage: {len(quarters_with_by_usage)}")
        print(f"Кварталов без by_usage: {len(quarters_without_by_usage)}")
        
        if quarters_without_by_usage:
            print(f"\n❌ ПРОБЛЕМА: Следующие кварталы не имеют by_usage:")
            for q in quarters_without_by_usage:
                print(f"   - {q}")
    
    # Проверяем наличие usage_categories.json
    print("\n" + "=" * 80)
    print("ПРОВЕРКА usage_categories.json")
    print("=" * 80 + "\n")
    
    usage_categories_file = aggregated_dir / "usage_categories.json"
    if usage_categories_file.exists():
        print(f"✅ Файл найден: {usage_categories_file}")
        try:
            usage_data = json.loads(usage_categories_file.read_text(encoding="utf-8"))
            print(f"   Структура: {list(usage_data.keys())}")
            if "years" in usage_data:
                print(f"   Годы: {list(usage_data['years'].keys())}")
                for year, categories in usage_data["years"].items():
                    print(f"   {year}: {categories}")
        except Exception as e:
            print(f"   ❌ Ошибка чтения: {e}")
    else:
        print(f"❌ Файл не найден: {usage_categories_file}")
        print("   Это означает, что aggregate_usage_categories() не вернул данные")
    
except Exception as e:
    print(f"❌ Ошибка при анализе файла: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("РЕКОМЕНДАЦИИ")
print("=" * 80 + "\n")
print("1. Проверьте, что файл pererashod.xlsx загружен и обработан")
print("2. Проверьте логи функции aggregate_usage_categories()")
print("3. Убедитесь, что функция distribute_categories_by_quarter() вызывается")
print("4. Проверьте, что данные оборудования (oborudovanie.xlsx) загружены")

