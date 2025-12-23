"""Проверка пропущенного файла"""
import json
from pathlib import Path

# Файл из списка пропущенных
filename = "06d2ab5d-2bc2-46bf-909b-bb1b49fb3599_aggregated.json"
file_path = Path(__file__).resolve().parent.parent / "data" / "inbox" / "aggregated" / filename

print("=" * 70)
print(f"ПРОВЕРКА ФАЙЛА: {filename}")
print("=" * 70)

if not file_path.exists():
    print(f"❌ Файл не найден: {file_path}")
    exit(1)

# Читаем файл
content = file_path.read_text(encoding='utf-8')
data = json.loads(content)

print(f"\n📊 Размер файла: {len(content)} байт")
print(f"📋 Ключи в JSON: {list(data.keys())}")

print(f"\n📦 Структура resources:")
resources = data.get("resources", {})
for resource_type, resource_data in resources.items():
    if isinstance(resource_data, dict):
        periods = [k for k in resource_data.keys() if isinstance(resource_data[k], dict)]
        print(f"   {resource_type}: {len(periods)} периодов")
        if periods:
            # Показываем первый период
            first_period = periods[0]
            print(f"      Пример периода '{first_period}':")
            period_data = resource_data[first_period]
            for key, value in list(period_data.items())[:5]:
                print(f"         {key}: {value}")
    else:
        print(f"   {resource_type}: {resource_data}")

print(f"\n📄 Полное содержимое файла:")
print(json.dumps(data, ensure_ascii=False, indent=2))

print("\n" + "=" * 70)
print("ВЫВОД:")
if any(isinstance(v, dict) and len(v) > 0 for v in resources.values()):
    print("✅ Файл содержит данные для импорта")
else:
    print("⚠️ Файл имеет правильную структуру, но ресурсы пустые (нет периодов)")
    print("   Причина пропуска: нет данных для импорта")
print("=" * 70)

