"""Проверка переагрегированного файла"""

from pathlib import Path
import json

ingest_path = Path(__file__).resolve().parent.parent
AGGREGATED_DIR = ingest_path / "data" / "inbox" / "aggregated"
electr_file = AGGREGATED_DIR / "849e4240-52d1-4d43-ad1a-bfe771b45cbe_aggregated.json"

print(f"Файл электроэнергии: {electr_file}")
print(f"Существует: {electr_file.exists()}")

if electr_file.exists():
    data = json.loads(electr_file.read_text(encoding="utf-8"))
    print(f"Ресурсы: {list(data.get('resources', {}).keys())}")
    electricity = data.get("resources", {}).get("electricity", {})
    print(f"Кварталы электроэнергии: {len(electricity)}")
    for q, qd in list(electricity.items())[:3]:
        quarter_totals = qd.get("quarter_totals", {})
        print(
            f"  {q}: quarter_totals={list(quarter_totals.keys())}, active_kwh={quarter_totals.get('active_kwh')}"
        )
