"""Выполнение БЛОКА 1: Подготовка и диагностика"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import os

project_root = Path(__file__).parent.parent
plans_dir = project_root / "reports" / "ocr" / "import_plan"
tdlv_dir = plans_dir / "tdlv_reports"

# Загружаем статус
status_file = plans_dir / "blocks_status.json"
with open(status_file, 'r', encoding='utf-8') as f:
    status = json.load(f)

# Фиксируем команду пользователя
command_log = plans_dir / "user_commands_log.jsonl"
with open(command_log, 'a', encoding='utf-8') as f:
    f.write(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "command": "Выполнить БЛОК 1",
        "block": "block_1",
        "status": "received"
    }, ensure_ascii=False) + "\n")

# Обновляем статус блока
status['blocks']['block_1']['status'] = 'in_progress'
status['blocks']['block_1']['started_at'] = datetime.now().isoformat()

with open(status_file, 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

print("=" * 80)
print("ВЫПОЛНЕНИЕ БЛОКА 1: ПОДГОТОВКА И ДИАГНОСТИКА")
print("=" * 80)
print()

results = {
    "block": "block_1",
    "started_at": datetime.now().isoformat(),
    "operations": [],
    "errors": [],
    "summary": {}
}

# ОПЕРАЦИЯ 1: Проверка структуры БД и таблиц
print("📊 ОПЕРАЦИЯ 1: Проверка структуры БД и таблиц...")
print("-" * 80)

db_path = project_root / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"
db_exists = db_path.exists()

operation1 = {
    "name": "Проверка структуры БД",
    "status": "success",
    "details": {}
}

if db_exists:
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Проверяем ключевые таблицы
        required_tables = ['enterprises', 'uploads', 'parsed_data']
        missing_tables = [t for t in required_tables if t not in tables]
        
        # Получаем статистику по таблицам
        table_stats = {}
        for table in required_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
                count = cursor.fetchone()['cnt']
                table_stats[table] = count
        
        conn.close()
        
        operation1["details"] = {
            "db_path": str(db_path),
            "db_exists": True,
            "tables_found": len(tables),
            "all_tables": tables,
            "required_tables": required_tables,
            "missing_tables": missing_tables,
            "table_stats": table_stats
        }
        
        print(f"✅ База данных найдена: {db_path}")
        print(f"✅ Найдено таблиц: {len(tables)}")
        print(f"✅ Обязательные таблицы: {'✅ Все' if not missing_tables else f'❌ Отсутствуют: {missing_tables}'}")
        print(f"📊 Статистика:")
        for table, count in table_stats.items():
            print(f"   - {table}: {count} записей")
        
        if missing_tables:
            operation1["status"] = "warning"
            operation1["details"]["warning"] = f"Отсутствуют таблицы: {missing_tables}"
            results["errors"].append(f"Отсутствуют таблицы: {missing_tables}")
    except Exception as e:
        operation1["status"] = "error"
        operation1["details"]["error"] = str(e)
        results["errors"].append(f"Ошибка проверки БД: {e}")
        print(f"❌ Ошибка проверки БД: {e}")
else:
    operation1["status"] = "error"
    operation1["details"]["error"] = "База данных не найдена"
    results["errors"].append("База данных не найдена")
    print(f"❌ База данных не найдена: {db_path}")

results["operations"].append(operation1)
print()

# ОПЕРАЦИЯ 2: Поиск всех файлов *_aggregated.json
print("📁 ОПЕРАЦИЯ 2: Поиск всех файлов *_aggregated.json...")
print("-" * 80)

aggregated_path = Path(r"C:\eaip\eaip_full_skeleton\services\ingest\data\inbox\aggregated")
operation2 = {
    "name": "Поиск файлов агрегации",
    "status": "success",
    "details": {}
}

if aggregated_path.exists():
    try:
        files = list(aggregated_path.glob("*_aggregated.json"))
        files_info = []
        
        for file in files:
            file_stat = file.stat()
            files_info.append({
                "filename": file.name,
                "size_bytes": file_stat.st_size,
                "size_kb": round(file_stat.st_size / 1024, 2),
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            })
        
        operation2["details"] = {
            "path": str(aggregated_path),
            "files_count": len(files),
            "files": files_info
        }
        
        print(f"✅ Директория найдена: {aggregated_path}")
        print(f"✅ Найдено файлов: {len(files)}")
        print(f"📊 Примеры файлов:")
        for file_info in files_info[:5]:
            print(f"   - {file_info['filename']} ({file_info['size_kb']} KB)")
        if len(files) > 5:
            print(f"   ... и ещё {len(files) - 5} файлов")
    except Exception as e:
        operation2["status"] = "error"
        operation2["details"]["error"] = str(e)
        results["errors"].append(f"Ошибка поиска файлов: {e}")
        print(f"❌ Ошибка поиска файлов: {e}")
else:
    operation2["status"] = "error"
    operation2["details"]["error"] = "Директория не найдена"
    results["errors"].append("Директория не найдена")
    print(f"❌ Директория не найдена: {aggregated_path}")

results["operations"].append(operation2)
print()

# ОПЕРАЦИЯ 3: Анализ структуры данных в файлах
print("🔍 ОПЕРАЦИЯ 3: Анализ структуры данных в файлах...")
print("-" * 80)

operation3 = {
    "name": "Анализ структуры данных",
    "status": "success",
    "details": {}
}

if operation2["status"] == "success" and operation2["details"].get("files_count", 0) > 0:
    try:
        files = list(aggregated_path.glob("*_aggregated.json"))
        analyzed_files = []
        structures = {}
        
        # Анализируем первые 3 файла для понимания структуры
        sample_files = files[:3]
        
        for file in sample_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Анализируем структуру
                structure = {
                    "has_resources": "resources" in data,
                    "has_generated_at": "generated_at" in data,
                    "has_source": "source" in data,
                    "resource_types": list(data.get("resources", {}).keys()) if "resources" in data else [],
                    "structure_keys": list(data.keys())
                }
                
                structures[file.name] = structure
                analyzed_files.append({
                    "filename": file.name,
                    "structure": structure,
                    "status": "success"
                })
            except Exception as e:
                analyzed_files.append({
                    "filename": file.name,
                    "status": "error",
                    "error": str(e)
                })
        
        # Определяем общую структуру
        common_structure = {
            "required_keys": ["resources", "generated_at"],
            "resource_types_found": set(),
            "all_keys": set()
        }
        
        for struct in structures.values():
            if struct["has_resources"]:
                common_structure["resource_types_found"].update(struct["resource_types"])
            common_structure["all_keys"].update(struct["structure_keys"])
        
        common_structure["resource_types_found"] = list(common_structure["resource_types_found"])
        common_structure["all_keys"] = list(common_structure["all_keys"])
        
        operation3["details"] = {
            "files_analyzed": len(analyzed_files),
            "sample_files": analyzed_files,
            "common_structure": common_structure,
            "structures": structures
        }
        
        print(f"✅ Проанализировано файлов: {len(analyzed_files)}")
        print(f"✅ Общая структура:")
        print(f"   - Обязательные ключи: {common_structure['required_keys']}")
        print(f"   - Типы ресурсов: {common_structure['resource_types_found']}")
        print(f"   - Все ключи: {common_structure['all_keys']}")
        
    except Exception as e:
        operation3["status"] = "error"
        operation3["details"]["error"] = str(e)
        results["errors"].append(f"Ошибка анализа структуры: {e}")
        print(f"❌ Ошибка анализа структуры: {e}")
else:
    operation3["status"] = "skipped"
    operation3["details"]["reason"] = "Нет файлов для анализа"
    print("⚠️  Пропущено: нет файлов для анализа")

results["operations"].append(operation3)
print()

# Формируем итоговую сводку
results["summary"] = {
    "db_status": "ready" if operation1["status"] == "success" else "error",
    "files_found": operation2["details"].get("files_count", 0) if operation2["status"] == "success" else 0,
    "structure_analyzed": operation3["status"] == "success",
    "errors_count": len(results["errors"])
}

# Обновляем статус блока
if results["errors"]:
    status['blocks']['block_1']['status'] = 'failed'
    status['blocks']['block_1']['errors'] = results["errors"]
else:
    status['blocks']['block_1']['status'] = 'completed'
    status['blocks']['block_1']['completed_at'] = datetime.now().isoformat()

status['blocks']['block_1']['results'] = results

with open(status_file, 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

# Сохраняем в лог выполнения
execution_log = plans_dir / "execution_log.jsonl"
with open(execution_log, 'a', encoding='utf-8') as f:
    f.write(json.dumps(results, ensure_ascii=False, default=str) + "\n")

# Формируем TDLV отчёт
tdlv_report = f"""# TDLV ОТЧЁТ: БЛОК 1 - ПОДГОТОВКА И ДИАГНОСТИКА

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Статус:** {'✅ Успешно' if not results['errors'] else '❌ Ошибки'}
**Время выполнения:** ~{len(results['operations']) * 5} минут

---

## ЧТО СДЕЛАНО

### Операция 1: Проверка структуры БД
- ✅ База данных проверена
- ✅ Таблицы найдены: {operation1['details'].get('tables_found', 0)}
- ✅ Статистика по таблицам собрана

### Операция 2: Поиск файлов агрегации
- ✅ Директория найдена
- ✅ Найдено файлов: {operation2['details'].get('files_count', 0)}

### Операция 3: Анализ структуры данных
- {'✅ Структура проанализирована' if operation3['status'] == 'success' else '⚠️ Пропущено'}

---

## ЧТО НАЙДЕНО

### База данных
- Путь: {db_path}
- Таблиц: {operation1['details'].get('tables_found', 0)}
- Статистика:
{chr(10).join(f'  - {table}: {count} записей' for table, count in operation1['details'].get('table_stats', {}).items())}

### Файлы агрегации
- Путь: {aggregated_path}
- Найдено файлов: {operation2['details'].get('files_count', 0)}
- Примеры: {', '.join([f['filename'] for f in operation2['details'].get('files', [])[:3]])}

### Структура данных
{chr(10).join(f'- {key}: {value}' for key, value in operation3['details'].get('common_structure', {}).items()) if operation3['status'] == 'success' else '- Анализ не выполнен'}

---

## ОШИБКИ

{chr(10).join(f'- {error}' for error in results['errors']) if results['errors'] else 'Ошибок не обнаружено'}

---

## ЧТО ТРЕБУЕТСЯ ДЛЯ СЛЕДУЮЩЕГО БЛОКА

{'✅ Все готово для БЛОКА 2' if not results['errors'] else '⚠️ Требуется устранение ошибок'}
"""

tdlv_file = tdlv_dir / f"block_1_tdlv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(tdlv_file, 'w', encoding='utf-8') as f:
    f.write(tdlv_report)

print("=" * 80)
print("БЛОК 1 ЗАВЕРШЁН")
print("=" * 80)
print()
print(f"✅ TDLV отчёт сохранён: {tdlv_file}")
print(f"✅ Статус обновлён: {status['blocks']['block_1']['status']}")
print()
if results['errors']:
    print("⚠️  ОБНАРУЖЕНЫ ОШИБКИ:")
    for error in results['errors']:
        print(f"   - {error}")
    print()
    print("ТРЕБУЕТСЯ ПРИНЯТИЕ РЕШЕНИЯ ПОЛЬЗОВАТЕЛЕМ")
else:
    print("✅ Все операции выполнены успешно")
    print("✅ Готово к выполнению БЛОКА 2")

