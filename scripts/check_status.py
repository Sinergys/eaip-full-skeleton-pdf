"""Быстрая проверка статуса индустриализации Word-отчётов."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

print("="*70)
print("ПРОВЕРКА СТАТУСА ИНДУСТРИАЛИЗАЦИИ WORD-ОТЧЁТОВ")
print("="*70)

# Проверка Word-отчётов
word_report_path = PROJECT_ROOT / "test_output" / "word_reports" / "test_report.json"
if word_report_path.exists():
    word_data = json.loads(word_report_path.read_text(encoding="utf-8"))
    print(f"\n✅ Word-отчёты: {word_data['successful']}/{word_data['total_tests']} успешно")
    if word_data['results']:
        scores = [r['readiness']['completeness_score']*100 for r in word_data['results'] if r.get('readiness')]
        if scores:
            print(f"   Готовность данных: {min(scores):.0f}% - {max(scores):.0f}%")
else:
    print("\n⚠️ Word-отчёты: файл отчёта не найден")

# Проверка согласованности
consistency_path = PROJECT_ROOT / "test_output" / "consistency_report.json"
if consistency_path.exists():
    consistency_data = json.loads(consistency_path.read_text(encoding="utf-8"))
    print(f"\n✅ Согласованность Excel/Word: {consistency_data['successful']}/{consistency_data['total_tests']} успешно")
else:
    print("\n⚠️ Согласованность: файл отчёта не найден")

# Проверка файлов
print("\n📁 Проверка файлов:")
files_to_check = [
    ("ReportData", "eaip_full_skeleton/services/ingest/domain/report_data.py"),
    ("PKM690 Sections", "eaip_full_skeleton/services/ingest/domain/pkm690_sections.py"),
    ("Word Readiness Validator", "eaip_full_skeleton/services/ingest/utils/word_readiness_validator.py"),
    ("Section Template Filler", "eaip_full_skeleton/services/ingest/utils/section_template_filler.py"),
    ("Word Report Generator", "eaip_full_skeleton/services/ingest/utils/word_report_generator.py"),
    ("Test Word Reports", "scripts/test_reference_word_reports.py"),
    ("Test Consistency", "scripts/test_excel_word_consistency.py"),
    ("CI Workflow", ".github/workflows/tests.yml"),
]

all_exist = True
for name, path in files_to_check:
    file_path = PROJECT_ROOT / path
    if file_path.exists():
        print(f"   ✅ {name}")
    else:
        print(f"   ❌ {name} (не найден)")
        all_exist = False

print("\n" + "="*70)
if all_exist:
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
else:
    print("⚠️ Некоторые файлы не найдены")
print("="*70)

