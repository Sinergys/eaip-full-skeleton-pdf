"""Скрипт для обновления статуса задачи CONTEXT_1"""
import sys
from pathlib import Path

# Добавляем путь к проекту
PROJECT_ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.unified_tasks_manager import update_task

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        new_status = sys.argv[1]
    else:
        new_status = 'completed'
    
    try:
        update_task('CONTEXT_1', {'status': new_status}, 'agent-1')
        print(f"✅ Статус задачи CONTEXT_1 обновлён на '{new_status}'")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

