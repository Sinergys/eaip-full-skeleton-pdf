"""Менеджер единого файла задач - работа с AGENT_TASKS_UNIFIED.json"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent
TASKS_FILE = PROJECT_ROOT / "docs" / "AGENT_TASKS_UNIFIED.json"
TASKS_MD_FILE = PROJECT_ROOT / "docs" / "AGENT_TASKS_UNIFIED.md"


def load_tasks() -> Dict[str, Any]:
    """Загружает единый файл задач"""
    if not TASKS_FILE.exists():
        raise FileNotFoundError(f"Файл задач не найден: {TASKS_FILE}")
    
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_tasks(data: Dict[str, Any]):
    """Сохраняет единый файл задач с проверкой размера"""
    # Проверяем размер перед записью
    try:
        import sys
        from pathlib import Path
        project_root = Path(__file__).resolve().parents[0].parent
        sys.path.insert(0, str(project_root))
        from tools.file_size_manager import check_file_size, optimize_file_if_needed
        
        file_info = check_file_size(TASKS_FILE)
        if file_info["exceeds_limit"]:
            # Оптимизируем файл перед записью
            optimize_file_if_needed(TASKS_FILE, force=False)
    except (ImportError, Exception):
        # Если file_size_manager недоступен, продолжаем без проверки
        pass
    
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """Получает задачу по ID"""
    data = load_tasks()
    return data["tasks"].get(task_id)


def update_task(task_id: str, updates: Dict[str, Any], agent: str):
    """Обновляет задачу и добавляет запись в историю"""
    data = load_tasks()
    
    if task_id not in data["tasks"]:
        raise ValueError(f"Задача {task_id} не найдена")
    
    task = data["tasks"][task_id]
    
    # Обновляем поля
    for key, value in updates.items():
        if key != "history":  # История обновляется отдельно
            task[key] = value
    
    # Добавляем в историю
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "action": "update",
        "changes": updates,
        "previous_status": task.get("status"),
        "new_status": updates.get("status", task.get("status"))
    }
    
    if "history" not in task:
        task["history"] = []
    
    task["history"].append(history_entry)
    
    # Ограничиваем историю последними 50 записями
    if len(task["history"]) > 50:
        task["history"] = task["history"][-50:]
    
    save_tasks(data)
    return task


def add_solution(task_id: str, solution: Dict[str, Any], agent: str):
    """Добавляет решение к задаче"""
    solution_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "type": solution.get("type", "implementation"),
        "approach": solution.get("approach", ""),
        "details": solution.get("details", ""),
        "files": solution.get("files", []),
        "code_snippets": solution.get("code_snippets", []),
        "testing_required": solution.get("testing_required", False),
        "risks": solution.get("risks", [])
    }
    
    data = load_tasks()
    if task_id not in data["tasks"]:
        raise ValueError(f"Задача {task_id} не найдена")
    
    task = data["tasks"][task_id]
    if "solutions" not in task:
        task["solutions"] = []
    
    task["solutions"].append(solution_entry)
    
    # Добавляем в историю
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "action": "solution_added",
        "solution_type": solution.get("type")
    }
    task["history"].append(history_entry)
    
    save_tasks(data)
    return solution_entry


def add_execution(task_id: str, execution: Dict[str, Any], agent: str):
    """Добавляет запись о выполнении к задаче"""
    execution_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "block_number": execution.get("block_number", 1),
        "status": execution.get("status", "in_progress"),
        "completed": execution.get("completed", []),
        "next_step": execution.get("next_step", ""),
        "files_changed": execution.get("files_changed", []),
        "time_spent_minutes": execution.get("time_spent_minutes", 0)
    }
    
    data = load_tasks()
    if task_id not in data["tasks"]:
        raise ValueError(f"Задача {task_id} не найдена")
    
    task = data["tasks"][task_id]
    if "execution" not in task:
        task["execution"] = []
    
    task["execution"].append(execution_entry)
    
    # Обновляем статус задачи
    if execution_entry["status"] == "completed":
        task["status"] = "completed"
    elif execution_entry["status"] == "in_progress":
        task["status"] = "in_progress"
    
    # Добавляем в историю
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "action": "execution_added",
        "block_number": execution.get("block_number"),
        "status": execution.get("status")
    }
    task["history"].append(history_entry)
    
    save_tasks(data)
    return execution_entry


def lock_task_unified(task_id: str, agent: str, duration_minutes: int = 15) -> bool:
    """Блокирует задачу в едином файле"""
    data = load_tasks()
    if task_id not in data["tasks"]:
        return False
    
    task = data["tasks"][task_id]
    
    # Проверяем, не заблокирована ли уже
    if task.get("locked_by") and task.get("locked_until"):
        locked_until = datetime.fromisoformat(task["locked_until"])
        if datetime.now() < locked_until:
            return False  # Заблокирована другим агентом
    
    # Блокируем
    task["locked_by"] = agent
    task["locked_until"] = (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
    task["assigned_to"] = agent
    
    # Добавляем в историю
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "action": "locked",
        "duration_minutes": duration_minutes
    }
    task["history"].append(history_entry)
    
    save_tasks(data)
    return True


def unlock_task_unified(task_id: str, agent: str):
    """Снимает блокировку задачи"""
    data = load_tasks()
    if task_id not in data["tasks"]:
        return
    
    task = data["tasks"][task_id]
    
    if task.get("locked_by") == agent:
        task["locked_by"] = None
        task["locked_until"] = None
        
        # Добавляем в историю
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": "unlocked"
        }
        task["history"].append(history_entry)
        
        save_tasks(data)


def get_available_tasks_unified(priority: Optional[str] = None, exclude: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Возвращает список доступных задач"""
    data = load_tasks()
    available = []
    exclude = exclude or []
    now = datetime.now()
    
    for task_id, task in data["tasks"].items():
        if task_id in exclude:
            continue
        
        # Проверяем блокировку
        if task.get("locked_by") and task.get("locked_until"):
            locked_until = datetime.fromisoformat(task["locked_until"])
            if now < locked_until:
                continue  # Заблокирована
        
        # Проверяем приоритет
        if priority and task.get("priority") != priority:
            continue
        
        # Проверяем статус
        if task.get("status") in ["completed", "cancelled"]:
            continue
        
        available.append({
            "id": task_id,
            **task
        })
    
    # Сортируем по приоритету
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    available.sort(key=lambda x: priority_order.get(x.get("priority", "P2"), 2))
    
    return available


def generate_markdown_report() -> str:
    """Генерирует Markdown отчёт из JSON"""
    data = load_tasks()
    
    md = f"""# 📋 ЕДИНЫЙ ФАЙЛ ЗАДАЧ ПРОЕКТА EAIP

**Последнее обновление:** {data['metadata']['last_updated']}  
**Всего задач:** {data['metadata']['total_tasks']}  
**Версия:** {data['metadata']['version']}

---

## 🔴 КРИТИЧЕСКИЕ ЗАДАЧИ (P0)

"""
    
    critical_tasks = [t for t in data["tasks"].values() if t.get("priority") == "P0" and t.get("category") == "critical"]
    
    md += "| ID | Задача | Статус | Область | Агент | Блокировка |\n"
    md += "|---|--------|--------|---------|-------|------------|\n"
    
    for task in sorted(critical_tasks, key=lambda x: x.get("id", "")):
        status_emoji = {
            "completed": "✅",
            "in_progress": "🔄",
            "partial": "⚠️",
            "not_started": "❌",
            "pending": "⏳"
        }.get(task.get("status", "not_started"), "❓")
        
        locked = "🔒" if task.get("locked_by") else "🔓"
        agent = task.get("assigned_to") or "-"
        
        md += f"| {task['id']} | {task['name']} | {status_emoji} {task.get('status', 'unknown')} | {task.get('area', '-')} | {agent} | {locked} |\n"
    
    md += "\n---\n\n## 📦 БЛОКИ ИМПОРТА\n\n"
    
    import_tasks = [t for t in data["tasks"].values() if t.get("category") == "import_block"]
    
    md += "| ID | Задача | Статус | Приоритет | Агент | Блокировка |\n"
    md += "|---|--------|--------|-----------|-------|------------|\n"
    
    for task in sorted(import_tasks, key=lambda x: x.get("id", "")):
        status_emoji = {
            "completed": "✅",
            "in_progress": "🔄",
            "partial": "⚠️",
            "not_started": "❌",
            "pending": "⏳"
        }.get(task.get("status", "pending"), "❓")
        
        locked = "🔒" if task.get("locked_by") else "🔓"
        agent = task.get("assigned_to") or "-"
        priority = task.get("priority", "P2")
        
        md += f"| {task['id']} | {task['name']} | {status_emoji} {task.get('status', 'pending')} | {priority} | {agent} | {locked} |\n"
    
    return md


def save_markdown_report():
    """Сохраняет Markdown отчёт"""
    md = generate_markdown_report()
    with open(TASKS_MD_FILE, 'w', encoding='utf-8') as f:
        f.write(md)


if __name__ == "__main__":
    # Тестирование
    print("✅ Менеджер единого файла задач готов")
    print(f"   JSON: {TASKS_FILE}")
    print(f"   Markdown: {TASKS_MD_FILE}")
    
    # Генерируем Markdown
    save_markdown_report()
    print("✅ Markdown отчёт сгенерирован")

