"""Проверка состояния задач проекта"""
import json
import sys
from pathlib import Path

# Путь к файлу задач
project_root = Path(__file__).parent.parent.parent.parent.parent
tasks_file = project_root / "docs" / "AGENT_TASKS_UNIFIED.json"

if not tasks_file.exists():
    print(f"❌ Файл задач не найден: {tasks_file}")
    sys.exit(1)

with open(tasks_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

tasks = data['tasks']

# Группировка по статусам
completed = [t for t in tasks.values() if t['status'] == 'completed']
in_progress = [t for t in tasks.values() if t['status'] == 'in_progress']
not_started = [t for t in tasks.values() if t['status'] == 'not_started']
partial = [t for t in tasks.values() if t['status'] == 'partial']
pending = [t for t in tasks.values() if t['status'] == 'pending']

print("=" * 70)
print("📊 СТАТИСТИКА ЗАДАЧ ПРОЕКТА")
print("=" * 70)
print(f"\n✅ Завершено: {len(completed)}")
print(f"⏳ В работе: {len(in_progress)}")
print(f"⚠️ Частично: {len(partial)}")
print(f"📋 Не начато: {len(not_started)}")
print(f"⏸️ Ожидает: {len(pending)}")
print(f"\n📈 Всего задач: {len(tasks)}")
print(f"📊 Прогресс: {len(completed)}/{len(tasks)} ({len(completed)/len(tasks)*100:.1f}%)")

# Задачи в работе
if in_progress:
    print("\n" + "=" * 70)
    print("⏳ ЗАДАЧИ В РАБОТЕ")
    print("=" * 70)
    for t in in_progress:
        print(f"\n  {t['id']}: {t['name']}")
        print(f"    Приоритет: {t['priority']} | Категория: {t['category']}")
        if t.get('assigned_to'):
            print(f"    Назначено: {t['assigned_to']}")

# Критические не начатые
critical_not_started = [t for t in not_started if t['priority'] == 'P0']
if critical_not_started:
    print("\n" + "=" * 70)
    print("🔴 КРИТИЧЕСКИЕ ЗАДАЧИ НЕ НАЧАТЫ (P0)")
    print("=" * 70)
    for t in critical_not_started:
        print(f"  - {t['id']}: {t['name']}")

# Частично выполненные
if partial:
    print("\n" + "=" * 70)
    print("⚠️ ЧАСТИЧНО ВЫПОЛНЕННЫЕ ЗАДАЧИ")
    print("=" * 70)
    for t in partial[:5]:  # Первые 5
        print(f"  - {t['id']}: {t['name']} ({t['priority']})")
    if len(partial) > 5:
        print(f"  ... и еще {len(partial) - 5} задач")

print("\n" + "=" * 70)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 70)

