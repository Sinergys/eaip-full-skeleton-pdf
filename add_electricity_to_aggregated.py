"""Скрипт для добавления данных по электроэнергии в aggregated_full_resources_2022_2024.json"""
import json
from pathlib import Path

# Загружаем существующий агрегированный файл
aggregated_path = Path("data/aggregated/aggregated_full_resources_2022_2024.json")
metin_path = Path("data/source_files/metin/aggregated_energy_2022_2024.json")

print("=" * 80)
print("ДОБАВЛЕНИЕ ДАННЫХ ПО ЭЛЕКТРОЭНЕРГИИ В АГРЕГИРОВАННЫЙ JSON")
print("=" * 80)

# Загружаем существующие данные
if not aggregated_path.exists():
    print(f"❌ Файл не найден: {aggregated_path}")
    exit(1)

with open(aggregated_path, "r", encoding="utf-8") as f:
    aggregated_data = json.load(f)

print(f"✅ Загружен: {aggregated_path}")
print(f"   Ключи: {list(aggregated_data.keys())}")

# Загружаем данные из METIN
if not metin_path.exists():
    print(f"❌ Файл METIN не найден: {metin_path}")
    exit(1)

with open(metin_path, "r", encoding="utf-8") as f:
    metin_data = json.load(f)

print(f"✅ Загружен: {metin_path}")

# Извлекаем данные по электроэнергии из METIN
# Структура METIN: {"electricity": {...}, "gas": {...}, ...}
# Структура aggregated: {"gaz.xlsx": {"resources": {"gas": {...}}}, ...}

if "electricity" in metin_data:
    electricity_data = metin_data["electricity"]
    print(f"✅ Найдены данные по электроэнергии: {len(electricity_data)} кварталов")
    
    # Добавляем данные по электроэнергии в aggregated_data
    aggregated_data["electricity.xlsx"] = {
        "source": str(metin_path),
        "generated_at": metin_data.get("generated_at", ""),
        "resources": {
            "electricity": electricity_data
        }
    }
    
    print("✅ Данные по электроэнергии добавлены в aggregated_data")
    
    # Сохраняем обновленный файл
    backup_path = aggregated_path.with_suffix(".json.backup")
    if not backup_path.exists():
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(aggregated_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Создан бэкап: {backup_path}")
    
    with open(aggregated_path, "w", encoding="utf-8") as f:
        json.dump(aggregated_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Обновлен файл: {aggregated_path}")
    print("\n📊 Итоговая структура:")
    print(f"   Ключи: {list(aggregated_data.keys())}")
    print(f"   Electricity quarters: {list(electricity_data.keys())[:5]}")
    
else:
    print("❌ Данные по электроэнергии не найдены в METIN файле")
    print(f"   Структура METIN: {list(metin_data.keys())}")

print("\n" + "=" * 80)

