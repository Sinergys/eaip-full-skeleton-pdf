"""
Генерация таблицы placeholder'ов из JSON
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def main():
    # Загружаем данные
    data_file = PROJECT_ROOT / "data" / "aggregated" / "all_placeholders.json"
    with open(data_file, "r", encoding="utf-8") as f:
        all_placeholders = json.load(f)
    
    # Фильтруем только шаблоны
    template_placeholders = [
        p for p in all_placeholders 
        if ("templates" in p["file"] and "pcm690" in p["file"]) or "generate_pcm690" in p["file"]
    ]
    
    # Группируем по уникальным placeholder'ам
    unique_placeholders = {}
    for p in template_placeholders:
        key = p["placeholder"]
        if key not in unique_placeholders:
            unique_placeholders[key] = {
                "placeholder": key,
                "files": [],
                "locations": [],
                "data_type": p["data_type"],
                "source": p["source"]
            }
        unique_placeholders[key]["files"].append(p["file"])
        unique_placeholders[key]["locations"].append(p["line"])
    
    # Сортируем по файлу и placeholder'у
    sorted_placeholders = sorted(unique_placeholders.items(), key=lambda x: (x[1]["files"][0], x[0]))
    
    # Генерируем Markdown таблицу
    print("=" * 120)
    print("ТАБЛИЦА PLACEHOLDER'ОВ В ШАБЛОНАХ")
    print("=" * 120)
    print()
    print("| Файл | Строка/Ячейка | Placeholder | Тип данных | Источник для замены |")
    print("|------|---------------|-------------|------------|---------------------|")
    
    for key, info in sorted_placeholders:
        file = info["files"][0].replace("\\", "/")
        location = str(info["locations"][0])
        placeholder = info["placeholder"]
        data_type = info["data_type"]
        source = info["source"]
        
        # Ограничиваем длину для читаемости
        if len(file) > 50:
            file = "..." + file[-47:]
        if len(location) > 20:
            location = location[:17] + "..."
        if len(placeholder) > 30:
            placeholder = placeholder[:27] + "..."
        if len(source) > 40:
            source = source[:37] + "..."
        
        print(f"| {file} | {location} | {placeholder} | {data_type} | {source} |")
    
    print()
    print(f"**Всего уникальных placeholder'ов:** {len(unique_placeholders)}")
    print(f"**Всего вхождений:** {len(template_placeholders)}")
    
    # Сохраняем в файл
    output_file = PROJECT_ROOT / "docs" / "PLACEHOLDERS_TABLE.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 📋 Таблица Placeholder'ов в шаблонах\n\n")
        f.write("**Дата генерации:** 2025-11-13\n\n")
        f.write("## Общая статистика\n\n")
        f.write(f"- **Всего уникальных placeholder'ов:** {len(unique_placeholders)}\n")
        f.write(f"- **Всего вхождений:** {len(template_placeholders)}\n\n")
        f.write("## Таблица\n\n")
        f.write("| Файл | Строка/Ячейка | Placeholder | Тип данных | Источник для замены |\n")
        f.write("|------|---------------|-------------|------------|---------------------|\n")
        
        for key, info in sorted_placeholders:
            file = info["files"][0].replace("\\", "/")
            location = str(info["locations"][0])
            placeholder = info["placeholder"]
            data_type = info["data_type"]
            source = info["source"]
            
            f.write(f"| {file} | {location} | {placeholder} | {data_type} | {source} |\n")
    
    print(f"\n💾 Таблица сохранена в: {output_file}")

if __name__ == "__main__":
    main()

