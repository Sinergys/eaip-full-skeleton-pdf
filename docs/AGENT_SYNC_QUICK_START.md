# 🚀 БЫСТРЫЙ СТАРТ: СИНХРОНИЗАЦИЯ АГЕНТОВ

## 📋 Что создано:

1. **Итоговая таблица:** `docs/PROJECT_STATUS_SUMMARY_TABLE.md`
   - Все задачи в удобном табличном формате
   - С колонкой "Агент" для отслеживания исполнителя

2. **Система синхронизации:** `docs/AGENT_SYNC_SYSTEM.md`
   - Полное описание механизма работы
   - Правила для обоих агентов

3. **Утилиты:** `tools/agent_sync_utils.py`
   - Готовые функции для работы с синхронизацией

4. **Файлы синхронизации:**
   - `docs/AGENT_TASK_STATUS.json` - статус всех задач
   - `docs/AGENT_LOCKS.json` - текущие блокировки
   - `docs/AGENT_WORK_LOG.jsonl` - лог работы агентов

---

## ⚡ Как использовать (для обоих агентов):

### ⚠️ ВАЖНО: ОБНОВЛЕНЫ ПРАВИЛА (2025-11-30)!

**Теперь при старте загружайте только 2 обязательных файла:**
- `docs/AGENT_CONTEXT.json`
- `docs/AGENT_TASKS_UNIFIED.json`

**Остальные файлы загружайте по требованию через `tools/context_loader.py`**

**Подробности:** См. `docs/AGENT_2_STARTUP_PROMPT.md` (для Agent-2) или `docs/PROJECT_WORK_RULES.md`

---

### Перед началом работы:

```python
# 0. ЗАГРУЗИТЬ ОБЯЗАТЕЛЬНЫЕ ФАЙЛЫ ПРИ СТАРТЕ (НОВОЕ!)
from tools.context_loader import load_critical_context, load_optional_file
from tools.agent_sync_utils import (
    select_task_for_agent, 
    lock_task, 
    update_task_status,
    unlock_task
)
from tools.unified_tasks_manager import (
    get_available_tasks_unified,
    lock_task_unified,
    update_task
)

# 0. Загрузить обязательные файлы (2 файла, ~44.79 КБ)
context_data = load_critical_context()
context = context_data["context"]  # Настройки проекта
tasks = context_data["tasks"]  # Все задачи

# 1. Выбрать задачу
available = get_available_tasks_unified(priority="P0")
if available:
    task = available[0]
    task_id = task["id"]
    
    # 2. Заблокировать на 15 минут (работа в блоке - 10 минут)
    # Загружаем опциональный файл блокировок только при необходимости
    locks = load_optional_file("locks")
    
    if lock_task_unified(task_id, "agent_1", duration_minutes=15):
        lock_task(task_id, "agent_1", duration_minutes=15)
        # 3. Обновить статус
        update_task_status(task_id, "in_progress", "agent_1")
        update_task(task_id, {"status": "in_progress"}, "agent_1")
        
        # 4. Выполнить работу (блок до 10 минут)
        # ... ваш код (максимум 10 минут работы) ...
        
        # 5. После завершения блока
        update_task_status(task_id, "in_progress", "agent_1", details={"block_completed": True})
        unlock_task(task_id)
        # 6. Предоставить TLDV отчёт и ожидать указаний пользователя
    else:
        print("Задача недоступна или заблокирована другим агентом")
else:
    print("Нет доступных задач P0")
```

### Проверка доступности задачи:

```python
from tools.agent_sync_utils import is_task_available

if is_task_available("B4_import_electricity"):
    print("Задача доступна")
else:
    print("Задача заблокирована")
```

---

## 📊 Просмотр статуса:

### Через Python:
```python
from tools.agent_sync_utils import load_status, load_locks

status = load_status()
locks = load_locks()

print(f"Agent-1: {status['agent_1']['status']}")
print(f"Agent-2: {status['agent_2']['status']}")
print(f"Активных блокировок: {len(locks['locks'])}")
```

### Через файлы:
- Откройте `docs/AGENT_TASK_STATUS.json` - увидите текущий статус
- Откройте `docs/AGENT_LOCKS.json` - увидите активные блокировки
- Откройте `docs/AGENT_WORK_LOG.jsonl` - увидите историю работы

---

## 🎯 Рекомендации:

1. **Agent-1 (Auto):** Фокус на документации, отчетах, интеграции
2. **Agent-2:** Фокус на импорте данных, OCR, функциональности

3. **Приоритеты:**
   - Сначала P0 (критично)
   - Затем P1 (важно)
   - В конце P2 (рекомендуется)

4. **Блокировки и время работы:**
   - **Работа в блоке:** максимум 10 минут (согласно правилам проекта)
   - **Блокировка задачи:** 15 минут (немного больше для безопасности)
   - **После каждого блока:** TLDV отчёт и ожидание указаний пользователя

---

## ⚠️ Важно:

- **Всегда проверяйте блокировки** перед началом работы
- **Обновляйте статус** после каждого значимого шага
- **Снимайте блокировки** после завершения работы
- **Не работайте над одной задачей одновременно**

---

**Готово к использованию!** 🎉

