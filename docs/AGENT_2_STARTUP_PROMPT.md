# 🚀 ПРОМПТ ДЛЯ AGENT-2: НОВЫЕ ПРАВИЛА РАБОТЫ

**Дата обновления:** 2025-11-30  
**Статус:** ✅ ОБЯЗАТЕЛЬНО К ПРОЧТЕНИЮ ПРИ СТАРТЕ  
**Версия:** 2.0

---

## ⚠️ ВАЖНО: ОБНОВЛЕНЫ ПРАВИЛА ЧТЕНИЯ ФАЙЛОВ ПРИ СТАРТЕ!

**Оптимизация завершена:** Список файлов для чтения при старте оптимизирован с 7 до 2 обязательных файлов.

---

## 📋 ОБЯЗАТЕЛЬНОЕ ЧТЕНИЕ ФАЙЛОВ ПРИ СТАРТЕ

### ✅ ОБЯЗАТЕЛЬНЫЕ ФАЙЛЫ (2 файла, ~44.79 КБ):

**Перед началом работы ОБЯЗАТЕЛЬНО загрузить:**

1. **`docs/AGENT_CONTEXT.json`** (7.06 КБ)
   - Единый файл контекста
   - Содержит все критически важные настройки, пути, конфигурации
   - **КРИТИЧЕСКИ НЕОБХОДИМ** для понимания структуры проекта

2. **`docs/AGENT_TASKS_UNIFIED.json`** (37.72 КБ)
   - Единый файл задач
   - Источник правды для всех задач
   - **КРИТИЧЕСКИ НЕОБХОДИМ** для выбора задачи

### 💡 ОПЦИОНАЛЬНЫЕ ФАЙЛЫ (загружать по требованию):

Эти файлы НЕ нужно загружать при старте! Загружать только когда необходимо:

3. **`docs/AGENT_TASK_STATUS.json`** (0.40 КБ)
   - Загружать при выборе задачи или проверке статуса

4. **`docs/AGENT_LOCKS.json`** (0.17 КБ)
   - Загружать при блокировке задачи

5. **`docs/AGENT_SESSION_STATE.json`** (2.61 КБ)
   - Загружать при восстановлении состояния после перезапуска

6. **`docs/AGENT_KNOWLEDGE_BASE.md`** (7.70 КБ)
   - Загружать при необходимости справки

7. **`docs/PROJECT_CRITICAL_SETTINGS.md`** (6.61 КБ)
   - Загружать как справочник (дублирует AGENT_CONTEXT.json)

---

## 🔧 ИСПОЛЬЗОВАНИЕ УТИЛИТЫ ЗАГРУЗКИ

### Рекомендуется использовать `tools/context_loader.py`:

```python
from tools.context_loader import load_critical_context, load_optional_file

# 1. ЗАГРУЗКА ОБЯЗАТЕЛЬНЫХ ФАЙЛОВ ПРИ СТАРТЕ
context_data = load_critical_context()
# context_data["context"] - AGENT_CONTEXT.json
# context_data["tasks"] - AGENT_TASKS_UNIFIED.json

# 2. ЗАГРУЗКА ОПЦИОНАЛЬНЫХ ФАЙЛОВ ПО ТРЕБОВАНИЮ
task_status = load_optional_file("task_status")  # При выборе задачи
locks = load_optional_file("locks")  # При блокировке задачи
session_state = load_optional_file("session_state")  # При восстановлении
knowledge_base = load_optional_file("knowledge_base")  # При необходимости справки
```

### Доступные ключи для опциональных файлов:
- `"task_status"` - AGENT_TASK_STATUS.json
- `"locks"` - AGENT_LOCKS.json
- `"session_state"` - AGENT_SESSION_STATE.json
- `"knowledge_base"` - AGENT_KNOWLEDGE_BASE.md
- `"critical_settings"` - PROJECT_CRITICAL_SETTINGS.md

---

## 📊 МЕТРИКИ ОПТИМИЗАЦИИ

### Улучшения:
- ✅ **Уменьшение размера:** с 62.27 КБ до 44.79 КБ (28.0% или 17.48 КБ)
- ✅ **Уменьшение количества файлов:** с 7 до 2 (71.4%)
- ✅ **Ожидаемое улучшение времени загрузки:** 40-60%

### Преимущества:
- Быстрее старт работы агента
- Меньше данных для загрузки
- Проще процесс инициализации
- Опциональные файлы доступны по требованию

---

## 🔄 ПРОЦЕСС СТАРТА РАБОТЫ

### Шаг 1: Загрузка обязательных файлов
```python
from tools.context_loader import load_critical_context

context_data = load_critical_context()
context = context_data["context"]  # Настройки проекта
tasks = context_data["tasks"]  # Все задачи
```

### Шаг 2: Выбор задачи
```python
from tools.unified_tasks_manager import get_available_tasks_unified

# Выбрать доступную задачу P0
available = get_available_tasks_unified(priority="P0")
if available:
    task = available[0]
    task_id = task["id"]
```

### Шаг 3: Блокировка задачи (если нужно)
```python
from tools.agent_sync_utils import lock_task, update_task_status
from tools.unified_tasks_manager import lock_task_unified

# Загрузить опциональный файл блокировок
locks = load_optional_file("locks")

# Заблокировать задачу
if lock_task_unified(task_id, "agent_2", duration_minutes=15):
    lock_task(task_id, "agent_2", duration_minutes=15)
    update_task_status(task_id, "in_progress", "agent_2")
```

### Шаг 4: Работа над задачей
- Работать блоками максимум 10 минут
- После каждого блока - TLDV отчёт
- Ожидать указаний пользователя

---

## 📝 ОБНОВЛЕННЫЕ ПРАВИЛА

### Основные правила (не изменились):
1. **Работа по блокам** - максимум 10 минут на блок
2. **TLDV отчёт** - после каждого блока
3. **Ожидание указаний** - после каждого блока
4. **Использование файлов** - настройки из файлов, не из контекста сеанса

### Новое правило:
5. **Оптимизированная загрузка** - загружать только 2 обязательных файла при старте, остальные по требованию

---

## ⚠️ ВАЖНЫЕ НАПОМИНАНИЯ

1. ✅ **ВСЕГДА** загружать обязательные файлы при старте (2 файла)
2. ✅ **НЕ** загружать опциональные файлы при старте (только по требованию)
3. ✅ **ИСПОЛЬЗОВАТЬ** `tools/context_loader.py` для загрузки файлов
4. ✅ **НЕ** полагаться на контекст сеанса - всегда читать из файлов
5. ✅ **ПРОВЕРЯТЬ** размер файлов перед записью (лимиты в правилах)

---

## 🔗 СВЯЗАННЫЕ ДОКУМЕНТЫ

- **Правила работы:** `docs/PROJECT_WORK_RULES.md` (обновлены)
- **Контекст:** `docs/AGENT_CONTEXT.json` (включает информацию о загрузке)
- **База знаний:** `docs/AGENT_KNOWLEDGE_BASE.md` (обновлена)
- **Утилита загрузки:** `tools/context_loader.py` (новая)
- **Система синхронизации:** `docs/AGENT_SYNC_SYSTEM.md`

---

## 📊 ПРИМЕР ПОЛНОГО СТАРТА

```python
# ============================================
# ПРИМЕР: ПОЛНЫЙ СТАРТ РАБОТЫ AGENT-2
# ============================================

from tools.context_loader import load_critical_context, load_optional_file
from tools.unified_tasks_manager import (
    get_available_tasks_unified,
    lock_task_unified,
    update_task
)
from tools.agent_sync_utils import (
    lock_task,
    update_task_status
)

# ШАГ 1: Загрузка обязательных файлов
print("📂 Загрузка обязательных файлов...")
context_data = load_critical_context()
context = context_data["context"]
tasks = context_data["tasks"]

print(f"✅ Контекст загружен: {len(context)} разделов")
print(f"✅ Задачи загружены: {len(tasks['tasks'])} задач")

# ШАГ 2: Выбор задачи
print("\n📋 Выбор задачи...")
available = get_available_tasks_unified(priority="P0")
if available:
    task = available[0]
    task_id = task["id"]
    print(f"✅ Выбрана задача: {task['name']} ({task_id})")
    
    # ШАГ 3: Блокировка (загружаем опциональный файл только при необходимости)
    print("\n🔒 Блокировка задачи...")
    locks = load_optional_file("locks")  # Загружаем только сейчас
    
    if lock_task_unified(task_id, "agent_2", duration_minutes=15):
        lock_task(task_id, "agent_2", duration_minutes=15)
        update_task_status(task_id, "in_progress", "agent_2")
        print(f"✅ Задача заблокирована: {task_id}")
        
        # ШАГ 4: Работа над задачей
        print("\n⚙️ Начало работы над задачей...")
        # ... ваша работа (максимум 10 минут) ...
        
        # После завершения блока
        update_task(task_id, {"status": "in_progress"}, "agent_2")
        # TLDV отчёт
        # Ожидание указаний пользователя
    else:
        print(f"❌ Задача {task_id} недоступна (заблокирована)")
else:
    print("❌ Нет доступных задач P0")
```

---

## ✅ ЧЕКЛИСТ ПРИ СТАРТЕ

- [ ] Загрузить `docs/AGENT_CONTEXT.json` (обязательно)
- [ ] Загрузить `docs/AGENT_TASKS_UNIFIED.json` (обязательно)
- [ ] Выбрать задачу из доступных
- [ ] Загрузить опциональные файлы только при необходимости
- [ ] Использовать `tools/context_loader.py` для загрузки
- [ ] НЕ полагаться на контекст сеанса

---

**Дата создания:** 2025-11-30  
**Версия:** 2.0  
**Статус:** ✅ АКТИВНО

**ВАЖНО:** Этот промпт должен быть прочитан при каждом старте работы Agent-2!

