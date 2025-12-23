"""Скрипт для проверки следующих задач"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.unified_tasks_manager import load_tasks

if __name__ == "__main__":
    data = load_tasks()
    
    # Находим задачи со статусом not_started или in_progress
    tasks = [
        t for t in data['tasks'].values() 
        if t['status'] in ['not_started', 'in_progress']
    ]
    
    # Сортируем по приоритету
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    tasks_sorted = sorted(
        tasks, 
        key=lambda x: (
            priority_order.get(x.get('priority', 'P3'), 3),
            x['status'] == 'in_progress',  # in_progress сначала
            x['id']
        )
    )
    
    print("=" * 70)
    print("СЛЕДУЮЩИЕ ЗАДАЧИ ДЛЯ РАБОТЫ")
    print("=" * 70)
    print(f"\nВсего задач в работе: {len(tasks_sorted)}\n")
    
    # Группируем по приоритету
    by_priority = {}
    for task in tasks_sorted[:15]:  # Показываем первые 15
        priority = task.get('priority', 'P3')
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(task)
    
    for priority in ['P0', 'P1', 'P2', 'P3']:
        if priority in by_priority:
            print(f"\n{'='*70}")
            print(f"ПРИОРИТЕТ {priority}")
            print(f"{'='*70}")
            for task in by_priority[priority]:
                status_icon = "🔄" if task['status'] == 'in_progress' else "📋"
                print(f"\n{status_icon} {task['id']}: {task['name']}")
                print(f"   Статус: {task['status']}")
                print(f"   Категория: {task.get('category', 'N/A')}")
                print(f"   Область: {task.get('area', 'N/A')}")
                if task.get('expert_recommendations'):
                    print(f"   Рекомендации: {len(task['expert_recommendations'])} экспертов")
    
    # Проверяем CONTEXT_1 - есть ли следующие блоки
    context_1 = data['tasks'].get('CONTEXT_1')
    if context_1 and context_1['status'] == 'completed':
        print("\n" + "=" * 70)
        print("✅ CONTEXT_1 ЗАВЕРШЁН")
        print("=" * 70)
        print("Следующие блоки из TLDV отчёта:")
        print("  - БЛОК 2: Автоматическая проверка при старте агентов")
        print("  - БЛОК 3: Мониторинг и отчёты")
    
    print("\n" + "=" * 70)

