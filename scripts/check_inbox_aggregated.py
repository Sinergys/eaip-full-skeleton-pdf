#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка aggregated файлов в inbox"""

import json
from pathlib import Path

inbox_dir = Path("eaip_full_skeleton/services/ingest/data/inbox/aggregated")

if not inbox_dir.exists():
    print(f"❌ Директория не найдена: {inbox_dir}")
    exit(1)

files = list(inbox_dir.glob("*_aggregated.json"))
files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

print("=" * 80)
print(f"Проверка последних 5 файлов из {inbox_dir}")
print("=" * 80 + "\n")

for i, file_path in enumerate(files[:5], 1):
    print(f"{'='*80}")
    print(f"Файл {i}: {file_path.name}")
    print(f"{'='*80}\n")
    
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        
        resources = data.get("resources", {})
        electricity = resources.get("electricity", {})
        
        if not electricity:
            print("❌ resources.electricity отсутствует\n")
            continue
        
        print(f"✅ resources.electricity найден")
        print(f"   Кварталов: {len(electricity)}\n")
        
        # Проверяем by_usage
        quarters_with = []
        quarters_without = []
        
        for quarter, qdata in electricity.items():
            by_usage = qdata.get("by_usage")
            if by_usage:
                quarters_with.append(quarter)
                print(f"✅ {quarter}: by_usage = {by_usage}")
            else:
                quarters_without.append(quarter)
                print(f"❌ {quarter}: by_usage отсутствует")
        
        print(f"\nИтого: {len(quarters_with)} с by_usage, {len(quarters_without)} без\n")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}\n")

