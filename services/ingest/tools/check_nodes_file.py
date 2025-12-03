"""Проверка файла узлов учёта"""
import json
from pathlib import Path

batch_id = "06d2ab5d-2bc2-46bf-909b-bb1b49fb3599"
aggregated_dir = Path(__file__).resolve().parent.parent / "data" / "inbox" / "aggregated"

# Проверяем файл aggregated
aggregated_file = aggregated_dir / f"{batch_id}_aggregated.json"
print("=" * 70)
print(f"ПРОВЕРКА ФАЙЛА: {batch_id}")
print("=" * 70)

print(f"\n1. Файл aggregated: {aggregated_file.name}")
if aggregated_file.exists():
    data = json.loads(aggregated_file.read_text(encoding='utf-8'))
    resources = data.get("resources", {})
    print(f"   Ресурсы: {list(resources.keys())}")
    print(f"   Периоды с данными:")
    for res_type, res_data in resources.items():
        if isinstance(res_data, dict) and res_data:
            periods = list(res_data.keys())
            print(f"     {res_type}: {len(periods)} периодов - {periods[:3]}...")
        else:
            print(f"     {res_type}: 0 периодов (ПУСТО)")
else:
    print("   ❌ Файл не найден")

# Проверяем файл nodes
nodes_file = aggregated_dir / f"{batch_id}_nodes.json"
print(f"\n2. Файл nodes: {nodes_file.name}")
if nodes_file.exists():
    data = json.loads(nodes_file.read_text(encoding='utf-8'))
    total_nodes = data.get("summary", {}).get("total_nodes", 0)
    nodes = data.get("nodes", [])
    print(f"   ✅ Файл найден!")
    print(f"   Узлов учёта: {total_nodes}")
    if nodes:
        print(f"   Пример первого узла:")
        node = nodes[0]
        print(f"     Название: {node.get('name')}")
        print(f"     P (кВт·ч): {node.get('active_energy_p')}")
        print(f"     Q (кВАр·ч): {node.get('reactive_energy_q')}")
        print(f"     ТТ: {node.get('tt')}")
else:
    print("   ❌ Файл не найден")

print("\n" + "=" * 70)
print("ВЫВОД:")
print("Файл schetchiki.xlsx - это файл УЗЛОВ УЧЁТА (nodes),")
print("а не файл с данными потребления по периодам.")
print("Он обрабатывается отдельно и сохраняется в *_nodes.json")
print("Batch-импорт ищет только *_aggregated.json с данными по кварталам.")
print("=" * 70)

