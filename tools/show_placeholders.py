"""Показать все placeholder'ы из экспортированной структуры."""

import json
from pathlib import Path

structure_path = Path("data/aggregated/new_template_structure.json")
data = json.loads(structure_path.read_text(encoding="utf-8"))

print("=" * 80)
print("PLACEHOLDER'Ы В НОВОМ ШАБЛОНЕ")
print("=" * 80)

for sheet_name, sheet_info in data["sheets"].items():
    if sheet_info["placeholder_cells"]:
        print(f"\n📄 Лист: {sheet_name}")
        print(
            f"   Найдено {len(sheet_info['placeholder_cells'])} ячеек с placeholder'ами"
        )
        for cell in sheet_info["placeholder_cells"]:
            print(f"   {cell['address']}: {cell['value'][:100]}")
            print(f"      Placeholder'ы: {', '.join(cell['placeholders'])}")

print("\n\n📊 Сводка:")
print(
    f"   Всего уникальных placeholder'ов: {len(data['summary']['unique_placeholders_all'])}"
)
print(f"   {', '.join(data['summary']['unique_placeholders_all'])}")
