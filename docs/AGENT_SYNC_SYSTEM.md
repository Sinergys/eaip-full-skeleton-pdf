# 🤝 СИСТЕМА СИНХРОНИЗАЦИИ AI-АГЕНТОВ

**Дата создания:** 2025-01-15  
**Цель:** Организация совместной работы двух AI-агентов без конфликтов

---

## 📋 ПРИНЦИПЫ РАБОТЫ

### 1. Единый источник правды
- **Файл статуса:** `docs/AGENT_TASK_STATUS.json`
- **Файл логов:** `docs/AGENT_WORK_LOG.jsonl`
- **Файл блокировок:** `docs/AGENT_LOCKS.json`

### 2. Правила работы агентов

#### Agent-1 (Текущий агент - Auto)
- **Роль:** Основной координатор, создатель отчетов, интегратор
- **Приоритет:** Критические задачи, документация, отчеты

#### Agent-2 (Второй агент)
- **Роль:** Реализация функциональности, импорт данных, OCR
- **Приоритет:** Блоки импорта, парсинг, интеграция модулей

### 3. Механизм блокировок

**Перед началом работы:**
1. Проверить `AGENT_LOCKS.json` на наличие блокировок
2. Заблокировать задачу перед началом работы
3. Обновить статус в `AGENT_TASK_STATUS.json`
4. Записать в лог начало работы

**После завершения:**
1. Обновить статус задачи
2. Снять блокировку
3. Записать в лог завершение работы
4. Обновить итоговую таблицу

---

## 📁 СТРУКТУРА ФАЙЛОВ

### `docs/AGENT_TASK_STATUS.json`
```json
{
  "last_updated": "2025-01-15T12:00:00",
  "agent_1": {
    "current_task": null,
    "completed_today": 5,
    "status": "idle"
  },
  "agent_2": {
    "current_task": "B4_import_electricity",
    "completed_today": 3,
    "status": "working"
  },
  "tasks": {
    "B4_import_electricity": {
      "status": "in_progress",
      "assigned_to": "agent_2",
      "started_at": "2025-01-15T11:30:00",
      "priority": "P0"
    }
  }
}
```

### `docs/AGENT_LOCKS.json`
```json
{
  "locks": {
    "B4_import_electricity": {
      "agent": "agent_2",
      "locked_at": "2025-01-15T11:30:00",
      "expires_at": "2025-01-15T12:00:00"
    }
  }
}
```

### `docs/AGENT_WORK_LOG.jsonl`
Формат: одна строка = одно событие
```json
{"timestamp": "2025-01-15T11:30:00", "agent": "agent_2", "action": "lock", "task": "B4_import_electricity"}
{"timestamp": "2025-01-15T11:35:00", "agent": "agent_2", "action": "start", "task": "B4_import_electricity"}
{"timestamp": "2025-01-15T12:00:00", "agent": "agent_2", "action": "complete", "task": "B4_import_electricity", "result": "success"}
```

---

## 🔄 ПРОЦЕСС СИНХРОНИЗАЦИИ

### Шаг 1: Проверка доступности задачи

```python
def is_task_available(task_id: str) -> bool:
    """Проверяет, доступна ли задача для работы"""
    locks = load_locks()
    if task_id in locks["locks"]:
        lock = locks["locks"][task_id]
        # Проверяем срок действия блокировки
        if datetime.now() < lock["expires_at"]:
            return False
        # Блокировка истекла - удаляем
        del locks["locks"][task_id]
        save_locks(locks)
    return True
```

### Шаг 2: Блокировка задачи

```python
def lock_task(task_id: str, agent: str, duration_minutes: int = 15) -> bool:
    """Блокирует задачу для работы агента
    
    По умолчанию блокировка на 15 минут (работа в блоке - 10 минут)
    """
    if not is_task_available(task_id):
        return False
    
    locks = load_locks()
    locks["locks"][task_id] = {
        "agent": agent,
        "locked_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
    }
    save_locks(locks)
    log_action(agent, "lock", task_id)
    return True
```

### Шаг 3: Обновление статуса

```python
def update_task_status(task_id: str, status: str, agent: str, details: dict = None):
    """Обновляет статус задачи"""
    status_file = load_status()
    if task_id not in status_file["tasks"]:
        status_file["tasks"][task_id] = {}
    
    status_file["tasks"][task_id].update({
        "status": status,
        "assigned_to": agent,
        "updated_at": datetime.now().isoformat()
    })
    
    if details:
        status_file["tasks"][task_id]["details"] = details
    
    save_status(status_file)
    log_action(agent, "update", task_id, status)
```

---

## 📝 ПРАВИЛА РАБОТЫ ДЛЯ АГЕНТОВ

### Agent-1 (Auto) должен:
1. ✅ Перед началом работы проверить `AGENT_TASK_STATUS.json`
2. ✅ Заблокировать задачу на 15 минут (работа в блоке - 10 минут)
3. ✅ Обновить статус в `AGENT_TASK_STATUS.json`
4. ✅ Записать в лог начало работы
5. ✅ После завершения блока (10 минут) обновить статус и снять блокировку
6. ✅ Обновить итоговую таблицу `PROJECT_STATUS_SUMMARY_TABLE.md`

### Agent-2 должен:
1. ✅ Следовать тем же правилам
2. ✅ Проверять, не работает ли Agent-1 над той же задачей
3. ✅ Обновлять статус после каждого блока (10 минут)
4. ✅ Использовать блокировки на 15 минут (работа в блоке - 10 минут)

---

## 🚨 РАЗРЕШЕНИЕ КОНФЛИКТОВ

### Если задача заблокирована другим агентом:
1. Проверить срок действия блокировки
2. Если истекла - автоматически снять
3. Если не истекла - выбрать другую задачу
4. Записать в лог попытку доступа к заблокированной задаче

### Если оба агента пытаются заблокировать одновременно:
1. Использовать временные метки
2. Победитель - тот, кто первым записал блокировку
3. Проигравший выбирает другую задачу

---

## 📊 МОНИТОРИНГ

### Ежедневный отчет:
- Количество задач, выполненных каждым агентом
- Конфликты и их разрешение
- Прогресс по приоритетам

### Еженедельный отчет:
- Статистика работы агентов
- Анализ эффективности синхронизации
- Рекомендации по улучшению

---

## 🔧 ИНСТРУКЦИИ ДЛЯ АГЕНТОВ

### Перед началом работы:
```python
# 1. Загрузить статус
status = load_status()

# 2. Выбрать задачу (по приоритету, не заблокированную)
task = select_available_task(status, priority="P0")

# 3. Заблокировать задачу на 15 минут (работа в блоке - 10 минут)
if lock_task(task["id"], "agent_1", duration_minutes=15):
    # 4. Обновить статус
    update_task_status(task["id"], "in_progress", "agent_1")
    # 5. Начать работу (блок до 10 минут)
    work_on_task(task)  # Работа в блоке - максимум 10 минут
    # 6. После завершения блока - снять блокировку
    unlock_task(task["id"])
else:
    # Задача недоступна - выбрать другую
    task = select_available_task(status, priority="P0", exclude=[task["id"]])
```

### После завершения работы:
```python
# 1. Обновить статус
update_task_status(task["id"], "completed", "agent_1", details={"result": "success"})

# 2. Снять блокировку
unlock_task(task["id"])

# 3. Обновить итоговую таблицу
update_summary_table(task["id"], "completed")
```

---

## 📌 ПРИОРИТЕТЫ ЗАДАЧ

### P0 (Критично) - выполняются первыми
- Блокируют заполнение документов
- Импорт данных в БД
- Критические баги

### P1 (Важно) - выполняются вторыми
- Затрудняют заполнение документов
- Улучшают качество данных

### P2 (Рекомендуется) - выполняются последними
- Улучшают качество документов
- Оптимизация

---

## ⏱️ ВРЕМЕННЫЕ ПАРАМЕТРЫ

**Важно:** Согласно правилам проекта:
- **Работа в 1 блоке задачи:** максимум 10 минут
- **Блокировка задачи:** 15 минут (немного больше для безопасности)
- **После каждого блока:** обновление статуса, TLDV отчёт, ожидание указаний пользователя

**Важно:** Оба агента должны:
- Работать блоками по 10 минут
- Блокировать задачи на 15 минут
- Обновлять файлы синхронизации после каждого блока

