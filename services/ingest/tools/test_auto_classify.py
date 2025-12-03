"""Тест автоматического определения типа предприятия"""
import sys
from pathlib import Path

INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

import database

# Тест для Navoiy IES
print("Тест автоматического определения типа для Navoiy IES:")
print("-" * 70)

# Получаем текущее состояние
ent_before = database.get_enterprise_by_id(3)
print("До автоопределения:")
print(f"  Отрасль: {ent_before.get('industry')}")
print(f"  Тип предприятия: {ent_before.get('enterprise_type')}")
print(f"  Тип продукции: {ent_before.get('product_type')}")

# Запускаем автоопределение
database.auto_determine_enterprise_type(3)

# Проверяем результат
ent_after = database.get_enterprise_by_id(3)
print("\nПосле автоопределения:")
print(f"  Отрасль: {ent_after.get('industry')}")
print(f"  Тип предприятия: {ent_after.get('enterprise_type')}")
print(f"  Тип продукции: {ent_after.get('product_type')}")

if ent_after.get('industry'):
    print("\n✅ Автоопределение работает!")
else:
    print("\n⚠️ Автоопределение не сработало (возможно, нет подходящих файлов)")

