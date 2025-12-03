"""Финальный тест определения типа для Navoiy IES с реальными данными"""
import sys
from pathlib import Path

INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

import database
from utils.enterprise_classifier import classify_enterprise

print("=" * 70)
print("ФИНАЛЬНЫЙ ТЕСТ ОПРЕДЕЛЕНИЯ ТИПА ДЛЯ NAVOIY IES")
print("=" * 70)

# Получаем предприятие
enterprise = database.get_enterprise_by_id(3)
if not enterprise:
    print("❌ Предприятие Navoiy IES не найдено!")
    sys.exit(1)

print(f"\n1. Предприятие: {enterprise['name']} (ID: {enterprise['id']})")

# Получаем все загруженные файлы
uploads = database.list_uploads_for_enterprise(3)
filenames = [upload.get("filename", "") for upload in uploads if upload.get("filename")]

print(f"\n2. Загружено файлов: {len(filenames)}")
print(f"   Примеры файлов (первые 10):")
for i, filename in enumerate(filenames[:10], 1):
    print(f"     {i}. {filename}")

# Классифицируем предприятие
print("\n3. Классификация предприятия:")
print("-" * 70)
industry, enterprise_type, product_type = classify_enterprise(
    enterprise["name"], filenames
)

print(f"   Отрасль: {industry}")
print(f"   Тип предприятия: {enterprise_type}")
print(f"   Тип продукции: {product_type}")

# Проверяем текущее состояние в БД
print("\n4. Текущее состояние в БД:")
print("-" * 70)
print(f"   Отрасль: {enterprise.get('industry')}")
print(f"   Тип предприятия: {enterprise.get('enterprise_type')}")
print(f"   Тип продукции: {enterprise.get('product_type')}")

# Обновляем данные в БД
print("\n5. Обновление данных в БД:")
print("-" * 70)
database.update_enterprise_type(
    enterprise_id=3,
    industry=industry,
    enterprise_type=enterprise_type,
    product_type=product_type,
)

# Проверяем результат
enterprise_updated = database.get_enterprise_by_id(3)
print("\n6. Результат после обновления:")
print("-" * 70)
print(f"   Отрасль: {enterprise_updated.get('industry')}")
print(f"   Тип предприятия: {enterprise_updated.get('enterprise_type')}")
print(f"   Тип продукции: {enterprise_updated.get('product_type')}")

# Проверка корректности
print("\n7. Проверка корректности:")
print("-" * 70)
is_correct = (
    enterprise_updated.get('industry') == 'энергетика' and
    enterprise_updated.get('enterprise_type') == 'ТЭС' and
    enterprise_updated.get('product_type') == 'электроэнергия'
)

if is_correct:
    print("   ✅ Определение типа КОРРЕКТНО!")
    print("   Navoiy IES правильно определен как энергетическое предприятие (ТЭС)")
else:
    print("   ⚠️ Определение типа требует проверки")
    if enterprise_updated.get('industry') != 'энергетика':
        print(f"   Ожидалась отрасль 'энергетика', получено '{enterprise_updated.get('industry')}'")
    if enterprise_updated.get('enterprise_type') != 'ТЭС':
        print(f"   Ожидался тип 'ТЭС', получено '{enterprise_updated.get('enterprise_type')}'")

print("\n" + "=" * 70)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 70)

