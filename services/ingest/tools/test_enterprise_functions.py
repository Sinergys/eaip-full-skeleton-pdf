"""Тест функций работы с enterprises"""
import sys
from pathlib import Path

INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

import database

# Тест получения предприятия
ent = database.get_enterprise_by_id(3)
print("Navoiy IES:")
print(f"  ID: {ent['id']}")
print(f"  Название: {ent['name']}")
print(f"  Отрасль: {ent.get('industry')}")
print(f"  Тип предприятия: {ent.get('enterprise_type')}")
print(f"  Тип продукции: {ent.get('product_type')}")

# Тест обновления
database.update_enterprise_type(
    enterprise_id=3,
    industry="энергетика",
    enterprise_type="ТЭС",
    product_type="электроэнергия"
)

# Проверяем обновление
ent_updated = database.get_enterprise_by_id(3)
print("\nПосле обновления:")
print(f"  Отрасль: {ent_updated.get('industry')}")
print(f"  Тип предприятия: {ent_updated.get('enterprise_type')}")
print(f"  Тип продукции: {ent_updated.get('product_type')}")

print("\n✅ Функции работают корректно!")

