"""Проверка результатов ШАГА 7"""
import json
from pathlib import Path

report_file = Path("reports/ocr/step7_batch_test_results_20251130_005304.json")

if not report_file.exists():
    print(f"❌ Отчет не найден: {report_file}")
    exit(1)

with open(report_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("ПРОВЕРКА РЕЗУЛЬТАТОВ ШАГА 7")
print("=" * 80)
print()
print(f"✅ Файлов обработано: {data['total_files']}")
print(f"✅ Ошибок: {data['total_errors']}")
print(f"✅ Таблиц найдено: {data['total_tables']}")
print(f"✅ Постобработка чисел: {data['improvements_applied']['number_postprocessing']} файлов")
print(f"✅ Постобработка ID кодов: {data['improvements_applied']['id_code_postprocessing']} файлов")
print()
print("📋 Детали по файлам:")
for i, file_data in enumerate(data['files'], 1):
    status = "✅" if not file_data['errors'] else "❌"
    print(f"  {status} {i}. {file_data['file_name']}")
    print(f"     - Таблиц: {file_data['total_tables']}, Ошибок: {len(file_data['errors'])}")
    if file_data['errors']:
        for error in file_data['errors']:
            print(f"       ⚠️  {error}")

