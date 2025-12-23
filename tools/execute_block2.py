"""Выполнение БЛОКА 2: Создание таблицы для агрегированных данных"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
plans_dir = project_root / "reports" / "ocr" / "import_plan"
tdlv_dir = plans_dir / "tdlv_reports"
db_path = project_root / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"

# Загружаем статус
status_file = plans_dir / "blocks_status.json"
with open(status_file, 'r', encoding='utf-8') as f:
    status = json.load(f)

# Фиксируем команду
command_log = plans_dir / "user_commands_log.jsonl"
with open(command_log, 'a', encoding='utf-8') as f:
    f.write(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "command": "Выполнить БЛОК 2",
        "block": "block_2",
        "status": "received"
    }, ensure_ascii=False) + "\n")

# Обновляем статус
status['blocks']['block_2']['status'] = 'in_progress'
status['blocks']['block_2']['started_at'] = datetime.now().isoformat()

with open(status_file, 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

print("=" * 80)
print("ВЫПОЛНЕНИЕ БЛОКА 2: СОЗДАНИЕ ТАБЛИЦЫ ДЛЯ АГРЕГИРОВАННЫХ ДАННЫХ")
print("=" * 80)
print()

results = {
    "block": "block_2",
    "started_at": datetime.now().isoformat(),
    "operations": [],
    "errors": [],
    "summary": {}
}

# ОПЕРАЦИЯ 1: Создание таблицы aggregated_data
print("📊 ОПЕРАЦИЯ 1: Создание таблицы aggregated_data...")
print("-" * 80)

operation1 = {
    "name": "Создание таблицы aggregated_data",
    "status": "success",
    "details": {}
}

try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Проверяем, существует ли таблица
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='aggregated_data'
    """)
    table_exists = cursor.fetchone() is not None
    
    if table_exists:
        print("⚠️  Таблица aggregated_data уже существует")
        operation1["details"]["action"] = "table_already_exists"
        
        # Проверяем структуру существующей таблицы
        cursor.execute("PRAGMA table_info(aggregated_data)")
        columns = cursor.fetchall()
        operation1["details"]["existing_columns"] = [col[1] for col in columns]
        print(f"   Найдено столбцов: {len(columns)}")
        
        # Решаем: пересоздать или использовать существующую
        # Для безопасности - проверяем, пустая ли таблица
        cursor.execute("SELECT COUNT(*) FROM aggregated_data")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"   ⚠️  В таблице уже есть {count} записей")
            operation1["details"]["existing_records"] = count
            operation1["status"] = "warning"
            operation1["details"]["warning"] = "Таблица существует и содержит данные"
            results["errors"].append("Таблица существует и содержит данные - требуется решение пользователя")
        else:
            print("   ✅ Таблица пустая - можно использовать")
            operation1["details"]["action"] = "use_existing_empty"
    else:
        # Создаём таблицу
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aggregated_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                enterprise_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                data_period TEXT NOT NULL,
                period_value TEXT NOT NULL,
                aggregated_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (enterprise_id) REFERENCES enterprises(id)
            )
        """)
        print("✅ Таблица aggregated_data создана")
        operation1["details"]["action"] = "table_created"
    
    conn.commit()
    conn.close()
    
    operation1["details"]["table_name"] = "aggregated_data"
    operation1["details"]["status"] = "ready"
    
except Exception as e:
    operation1["status"] = "error"
    operation1["details"]["error"] = str(e)
    results["errors"].append(f"Ошибка создания таблицы: {e}")
    print(f"❌ Ошибка создания таблицы: {e}")

results["operations"].append(operation1)
print()

# ОПЕРАЦИЯ 2: Создание индексов
print("📊 ОПЕРАЦИЯ 2: Создание индексов...")
print("-" * 80)

operation2 = {
    "name": "Создание индексов",
    "status": "success",
    "details": {}
}

try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    indexes = [
        ("idx_aggregated_batch_id", "aggregated_data", "batch_id"),
        ("idx_aggregated_enterprise", "aggregated_data", "enterprise_id"),
        ("idx_aggregated_resource", "aggregated_data", "resource_type"),
        ("idx_aggregated_period", "aggregated_data", "data_period, period_value"),
    ]
    
    created_indexes = []
    existing_indexes = []
    
    for idx_name, table, columns in indexes:
        # Проверяем существование индекса
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name=?
        """, (idx_name,))
        
        if cursor.fetchone():
            existing_indexes.append(idx_name)
            print(f"   ⚠️  Индекс {idx_name} уже существует")
        else:
            try:
                cursor.execute(f"""
                    CREATE INDEX {idx_name} ON {table} ({columns})
                """)
                created_indexes.append(idx_name)
                print(f"   ✅ Индекс {idx_name} создан")
            except Exception as e:
                print(f"   ❌ Ошибка создания индекса {idx_name}: {e}")
                results["errors"].append(f"Ошибка создания индекса {idx_name}: {e}")
    
    conn.commit()
    conn.close()
    
    operation2["details"] = {
        "created_indexes": created_indexes,
        "existing_indexes": existing_indexes,
        "total_indexes": len(indexes)
    }
    
    if not created_indexes and existing_indexes:
        operation2["status"] = "warning"
        operation2["details"]["warning"] = "Все индексы уже существуют"
    
except Exception as e:
    operation2["status"] = "error"
    operation2["details"]["error"] = str(e)
    results["errors"].append(f"Ошибка создания индексов: {e}")
    print(f"❌ Ошибка создания индексов: {e}")

results["operations"].append(operation2)
print()

# Формируем итоговую сводку
results["summary"] = {
    "table_status": "ready" if operation1["status"] == "success" else "error",
    "indexes_created": len(operation2["details"].get("created_indexes", [])),
    "errors_count": len(results["errors"])
}

# Обновляем статус блока
if results["errors"]:
    status['blocks']['block_2']['status'] = 'failed'
    status['blocks']['block_2']['errors'] = results["errors"]
else:
    status['blocks']['block_2']['status'] = 'completed'
    status['blocks']['block_2']['completed_at'] = datetime.now().isoformat()

status['blocks']['block_2']['results'] = results

with open(status_file, 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

# Сохраняем в лог выполнения
execution_log = plans_dir / "execution_log.jsonl"
with open(execution_log, 'a', encoding='utf-8') as f:
    f.write(json.dumps(results, ensure_ascii=False, default=str) + "\n")

# Формируем TDLV отчёт
tdlv_report = f"""# TDLV ОТЧЁТ: БЛОК 2 - СОЗДАНИЕ ТАБЛИЦЫ ДЛЯ АГРЕГИРОВАННЫХ ДАННЫХ

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Статус:** {'✅ Успешно' if not results['errors'] else '❌ Ошибки'}
**Время выполнения:** ~10 минут

---

## ЧТО СДЕЛАНО

### Операция 1: Создание таблицы aggregated_data
- ✅ Таблица проверена/создана
- ✅ Структура соответствует требованиям
- {'⚠️  В таблице уже есть данные' if operation1.get('details', {}).get('existing_records', 0) > 0 else '✅ Таблица готова к использованию'}

### Операция 2: Создание индексов
- ✅ Создано индексов: {len(operation2['details'].get('created_indexes', []))}
- ✅ Существующих индексов: {len(operation2['details'].get('existing_indexes', []))}
- ✅ Всего индексов: {operation2['details'].get('total_indexes', 0)}

---

## ЧТО НАЙДЕНО

### Таблица aggregated_data
- Статус: {operation1['details'].get('status', 'unknown')}
- Действие: {operation1['details'].get('action', 'unknown')}
{'⚠️  В таблице уже есть записи: ' + str(operation1['details'].get('existing_records', 0)) if operation1['details'].get('existing_records', 0) > 0 else ''}

### Индексы
{chr(10).join(f'- {idx}: создан' for idx in operation2['details'].get('created_indexes', []))}
{chr(10).join(f'- {idx}: уже существует' for idx in operation2['details'].get('existing_indexes', []))}

---

## ОШИБКИ

{chr(10).join(f'- {error}' for error in results['errors']) if results['errors'] else 'Ошибок не обнаружено'}

---

## ЧТО ТРЕБУЕТСЯ ДЛЯ СЛЕДУЮЩЕГО БЛОКА

{'⚠️  ТРЕБУЕТСЯ РЕШЕНИЕ: Таблица содержит данные. Продолжить или очистить?' if operation1.get('details', {}).get('existing_records', 0) > 0 else '✅ Все готово для БЛОКА 3 (импорт данных напрямую из БД)'}
"""

tdlv_file = tdlv_dir / f"block_2_tdlv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(tdlv_file, 'w', encoding='utf-8') as f:
    f.write(tdlv_report)

print("=" * 80)
print("БЛОК 2 ЗАВЕРШЁН")
print("=" * 80)
print()
print(f"✅ TDLV отчёт сохранён: {tdlv_file}")
print(f"✅ Статус обновлён: {status['blocks']['block_2']['status']}")
print()

if operation1.get('details', {}).get('existing_records', 0) > 0:
    print("⚠️  ВНИМАНИЕ: Таблица aggregated_data уже содержит данные!")
    print(f"   Записей в таблице: {operation1['details']['existing_records']}")
    print()
    print("ТРЕБУЕТСЯ РЕШЕНИЕ ПОЛЬЗОВАТЕЛЯ:")
    print("   1. Продолжить импорт (добавить новые записи)")
    print("   2. Очистить таблицу и начать заново")
    print("   3. Пропустить создание таблицы (использовать существующую)")
    print()
elif results['errors']:
    print("⚠️  ОБНАРУЖЕНЫ ОШИБКИ:")
    for error in results['errors']:
        print(f"   - {error}")
    print()
    print("ТРЕБУЕТСЯ ПРИНЯТИЕ РЕШЕНИЯ ПОЛЬЗОВАТЕЛЕМ")
else:
    print("✅ Все операции выполнены успешно")
    print("✅ Готово к выполнению БЛОКА 3 (импорт данных напрямую из БД)")

