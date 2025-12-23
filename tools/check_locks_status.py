"""Проверка статуса блокировок"""
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[0].parent
LOCKS_FILE = PROJECT_ROOT / "docs" / "AGENT_LOCKS.json"

def check_locks():
    """Проверяет статус блокировок"""
    if not LOCKS_FILE.exists():
        print("❌ Файл блокировок не найден")
        return
    
    with open(LOCKS_FILE, 'r', encoding='utf-8') as f:
        locks = json.load(f)
    
    now = datetime.now()
    print(f"Текущее время: {now.isoformat()}")
    print(f"Активные блокировки: {len(locks.get('locks', {}))}")
    
    for task_id, lock_info in locks.get('locks', {}).items():
        expires_at = datetime.fromisoformat(lock_info['expires_at'])
        locked_at = datetime.fromisoformat(lock_info['locked_at'])
        agent = lock_info['agent']
        
        if now < expires_at:
            remaining = expires_at - now
            print(f"  ✅ {task_id}: заблокирована агентом {agent}")
            print(f"     Заблокирована: {locked_at.isoformat()}")
            print(f"     Истекает: {expires_at.isoformat()}")
            print(f"     Осталось: {remaining.total_seconds() / 60:.1f} минут")
        else:
            print(f"  ⚠️ {task_id}: блокировка истекла (агент: {agent})")

if __name__ == "__main__":
    check_locks()

