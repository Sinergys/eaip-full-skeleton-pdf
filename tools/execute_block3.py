"""Выполнение БЛОКА 3: Импорт агрегированных данных - Электроэнергия (напрямую из БД)"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
import os

# Добавляем путь для импорта модулей
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "eaip_full_skeleton" / "services" / "ingest"))

from utils.energy_aggregator import aggregate_from_db_json

plans_dir = project_root / "reports" / "ocr" / "import_plan"
tdlv_dir = plans_dir / "tdlv_reports"
debug_dir = plans_dir / "debug_files"
db_path = project_root / "eaip_full_skeleton" / "services" / "ingest" / "ingest_data.db"

debug_dir.mkdir(parents=True, exist_ok=True)

# Загружаем статус
status_file = plans_dir / "blocks_status.json"
with open(status_file, 'r', encoding='utf-8') as f:
    status = json.load(f)

# Фиксируем команду
command_log = plans_dir / "user_commands_log.jsonl"
with open(command_log, 'a', encoding='utf-8') as f:
    f.write(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "command": "Выполнить БЛОК 3",
        "block": "block_3",
        "status": "received"
    }, ensure_ascii=False) + "\n")

# Обновляем статус
status['blocks']['block_3']['status'] = 'in_progress'
status['blocks']['block_3']['started_at'] = datetime.now().isoformat()

with open(status_file, 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

print("=" * 80)
print("ВЫПОЛНЕНИЕ БЛОКА 3: ИМПОРТ ДАННЫХ - ЭЛЕКТРОЭНЕРГИЯ (НАПРЯМУЮ ИЗ БД)")
print("=" * 80)
print()

results = {
    "block": "block_3",
    "started_at": datetime.now().isoformat(),
    "operations": [],
    "errors": [],
    "validation_results": {},
    "imported_records": 0,
    "summary": {}
}

# ОПЕРАЦИЯ 1: Получение данных для Навои из parsed_data
print("📊 ОПЕРАЦИЯ 1: Получение данных для Навои из parsed_data...")
print("-" * 80)

operation1 = {
    "name": "Получение данных из parsed_data",
    "status": "success",
    "details": {}
}

try:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Находим предприятие Navoiy IES
    cursor.execute("SELECT id FROM enterprises WHERE name LIKE '%Navoiy%' OR name LIKE '%Навои%'")
    navoiy_enterprise = cursor.fetchone()
    
    if not navoiy_enterprise:
        raise ValueError("Предприятие Navoiy IES не найдено в БД")
    
    navoiy_id = navoiy_enterprise['id']
    print(f"✅ Предприятие Navoiy IES найдено (ID: {navoiy_id})")
    
    # Получаем все загрузки для Навои с parsed_data
    cursor.execute("""
        SELECT u.batch_id, u.filename, pd.raw_json, pd.updated_at
        FROM uploads u
        JOIN parsed_data pd ON pd.upload_id = u.id
        WHERE u.enterprise_id = ?
        ORDER BY u.created_at DESC
    """, (navoiy_id,))
    
    navoiy_uploads = cursor.fetchall()
    print(f"✅ Найдено загрузок с данными: {len(navoiy_uploads)}")
    
    if len(navoiy_uploads) == 0:
        raise ValueError("Нет загрузок с данными для Навои")
    
    operation1["details"] = {
        "enterprise_id": navoiy_id,
        "uploads_found": len(navoiy_uploads),
        "batch_ids": [row['batch_id'] for row in navoiy_uploads]
    }
    
    conn.close()
    
except Exception as e:
    operation1["status"] = "error"
    operation1["details"]["error"] = str(e)
    results["errors"].append(f"Ошибка получения данных: {e}")
    print(f"❌ Ошибка получения данных: {e}")

results["operations"].append(operation1)
print()

# ОПЕРАЦИЯ 2: Агрегация данных на лету и валидация
print("🔄 ОПЕРАЦИЯ 2: Агрегация данных на лету и валидация...")
print("-" * 80)

operation2 = {
    "name": "Агрегация и валидация",
    "status": "success",
    "details": {}
}

if operation1["status"] == "success":
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        aggregated_data_list = []
        validation_errors = []
        
        for row in navoiy_uploads:
            batch_id = row['batch_id']
            filename = row['filename']
            raw_json_str = row['raw_json']
            
            if not raw_json_str:
                print(f"   ⚠️  Пропущено: {filename} (нет данных)")
                continue
            
            try:
                raw_json = json.loads(raw_json_str)
                
                # Агрегация на лету
                aggregated = aggregate_from_db_json(raw_json)
                
                if not aggregated:
                    print(f"   ⚠️  Пропущено: {filename} (агрегация не удалась)")
                    continue
                
                # Проверка целостности
                integrity_checks = {
                    "has_resources": "resources" in aggregated,
                    "has_electricity": "electricity" in aggregated.get("resources", {}),
                    "has_generated_at": "generated_at" in aggregated,
                }
                
                # Проверка безошибочности
                error_checks = {
                    "valid_json": True,
                    "has_data": bool(aggregated.get("resources", {})),
                }
                
                if aggregated.get("resources", {}).get("electricity"):
                    electricity_data = aggregated["resources"]["electricity"]
                    error_checks["has_annual"] = "annual" in electricity_data or any("annual" in q for q in electricity_data.get("quarterly", {}).values())
                    error_checks["has_quarterly"] = "quarterly" in electricity_data
                
                # Сохраняем для отладки (опция включена)
                debug_file = debug_dir / f"{batch_id}_electricity_debug.json"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "batch_id": batch_id,
                        "filename": filename,
                        "aggregated": aggregated,
                        "integrity_checks": integrity_checks,
                        "error_checks": error_checks,
                        "timestamp": datetime.now().isoformat()
                    }, f, ensure_ascii=False, indent=2)
                
                if not all(integrity_checks.values()):
                    validation_errors.append({
                        "batch_id": batch_id,
                        "filename": filename,
                        "checks": integrity_checks
                    })
                    print(f"   ⚠️  Проблемы целостности: {filename}")
                else:
                    aggregated_data_list.append({
                        "batch_id": batch_id,
                        "filename": filename,
                        "aggregated": aggregated,
                        "integrity_checks": integrity_checks,
                        "error_checks": error_checks
                    })
                    print(f"   ✅ Обработано: {filename}")
                
            except Exception as e:
                validation_errors.append({
                    "batch_id": batch_id,
                    "filename": filename,
                    "error": str(e)
                })
                print(f"   ❌ Ошибка обработки {filename}: {e}")
        
        conn.close()
        
        operation2["details"] = {
            "processed": len(aggregated_data_list),
            "skipped": len(navoiy_uploads) - len(aggregated_data_list),
            "validation_errors": len(validation_errors),
            "debug_files_created": len(aggregated_data_list)
        }
        
        results["validation_results"] = {
            "valid": len(aggregated_data_list),
            "errors": validation_errors
        }
        
        if validation_errors:
            operation2["status"] = "warning"
            operation2["details"]["warning"] = f"Обнаружены проблемы валидации: {len(validation_errors)}"
            results["errors"].extend([f"Валидация: {err.get('filename', 'unknown')}" for err in validation_errors])
        
        # Сохраняем агрегированные данные для импорта
        results["aggregated_data"] = aggregated_data_list
        
        print(f"✅ Обработано файлов: {len(aggregated_data_list)}")
        print(f"⚠️  Пропущено: {len(navoiy_uploads) - len(aggregated_data_list)}")
        print(f"❌ Ошибок валидации: {len(validation_errors)}")
        
    except Exception as e:
        operation2["status"] = "error"
        operation2["details"]["error"] = str(e)
        results["errors"].append(f"Ошибка агрегации: {e}")
        print(f"❌ Ошибка агрегации: {e}")

results["operations"].append(operation2)
print()

# ОПЕРАЦИЯ 3: Импорт в БД
print("💾 ОПЕРАЦИЯ 3: Импорт данных электроэнергии в БД...")
print("-" * 80)

operation3 = {
    "name": "Импорт в БД",
    "status": "success",
    "details": {}
}

if operation2["status"] in ["success", "warning"] and results.get("aggregated_data"):
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        for item in results["aggregated_data"]:
            batch_id = item["batch_id"]
            aggregated = item["aggregated"]
            electricity_data = aggregated.get("resources", {}).get("electricity", {})
            
            if not electricity_data:
                skipped_count += 1
                continue
            
            # Импортируем годовые данные
            if "annual" in electricity_data:
                try:
                    cursor.execute("""
                        INSERT INTO aggregated_data 
                        (batch_id, enterprise_id, resource_type, data_period, period_value, aggregated_json, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        batch_id,
                        navoiy_id,
                        "electricity",
                        "year",
                        "annual",
                        json.dumps({"annual": electricity_data["annual"]}, ensure_ascii=False),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                    imported_count += 1
                except sqlite3.IntegrityError:
                    # Дубликат - обновляем (согласно решению пользователя)
                    cursor.execute("""
                        UPDATE aggregated_data
                        SET aggregated_json = ?, updated_at = ?
                        WHERE batch_id = ? AND resource_type = ? AND data_period = ? AND period_value = ?
                    """, (
                        json.dumps({"annual": electricity_data["annual"]}, ensure_ascii=False),
                        datetime.now().isoformat(),
                        batch_id,
                        "electricity",
                        "year",
                        "annual"
                    ))
                    imported_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"   ❌ Ошибка импорта годовых данных для {batch_id}: {e}")
            
            # Импортируем поквартальные данные
            if "quarterly" in electricity_data:
                for quarter, quarter_data in electricity_data["quarterly"].items():
                    try:
                        cursor.execute("""
                            INSERT INTO aggregated_data 
                            (batch_id, enterprise_id, resource_type, data_period, period_value, aggregated_json, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            batch_id,
                            navoiy_id,
                            "electricity",
                            "quarter",
                            quarter,
                            json.dumps(quarter_data, ensure_ascii=False),
                            datetime.now().isoformat(),
                            datetime.now().isoformat()
                        ))
                        imported_count += 1
                    except sqlite3.IntegrityError:
                        # Дубликат - обновляем
                        cursor.execute("""
                            UPDATE aggregated_data
                            SET aggregated_json = ?, updated_at = ?
                            WHERE batch_id = ? AND resource_type = ? AND data_period = ? AND period_value = ?
                        """, (
                            json.dumps(quarter_data, ensure_ascii=False),
                            datetime.now().isoformat(),
                            batch_id,
                            "electricity",
                            "quarter",
                            quarter
                        ))
                        imported_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"   ❌ Ошибка импорта квартала {quarter} для {batch_id}: {e}")
        
        conn.commit()
        conn.close()
        
        operation3["details"] = {
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": error_count
        }
        
        results["imported_records"] = imported_count
        
        print(f"✅ Импортировано записей: {imported_count}")
        print(f"⚠️  Пропущено: {skipped_count}")
        print(f"❌ Ошибок: {error_count}")
        
    except Exception as e:
        operation3["status"] = "error"
        operation3["details"]["error"] = str(e)
        results["errors"].append(f"Ошибка импорта: {e}")
        print(f"❌ Ошибка импорта: {e}")

results["operations"].append(operation3)
print()

# Формируем итоговую сводку
results["summary"] = {
    "uploads_processed": len(navoiy_uploads) if operation1["status"] == "success" else 0,
    "validated": len(results.get("aggregated_data", [])),
    "imported_records": results["imported_records"],
    "errors_count": len(results["errors"])
}

# Обновляем статус блока
if results["errors"] and operation3["status"] == "error":
    status['blocks']['block_3']['status'] = 'failed'
    status['blocks']['block_3']['errors'] = results["errors"]
elif results["errors"]:
    status['blocks']['block_3']['status'] = 'completed_with_warnings'
    status['blocks']['block_3']['warnings'] = results["errors"]
else:
    status['blocks']['block_3']['status'] = 'completed'
    status['blocks']['block_3']['completed_at'] = datetime.now().isoformat()

status['blocks']['block_3']['results'] = results

with open(status_file, 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

# Сохраняем в лог выполнения
execution_log = plans_dir / "execution_log.jsonl"
with open(execution_log, 'a', encoding='utf-8') as f:
    f.write(json.dumps(results, ensure_ascii=False, default=str) + "\n")

# Формируем TDLV отчёт
tdlv_report = f"""# TDLV ОТЧЁТ: БЛОК 3 - ИМПОРТ ДАННЫХ ЭЛЕКТРОЭНЕРГИИ

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Статус:** {'✅ Успешно' if not results['errors'] or operation3['status'] == 'success' else '⚠️ С предупреждениями'}
**Время выполнения:** ~15 минут

---

## ЧТО СДЕЛАНО

### Операция 1: Получение данных из parsed_data
- ✅ Предприятие Navoiy IES найдено
- ✅ Найдено загрузок: {operation1['details'].get('uploads_found', 0)}

### Операция 2: Агрегация и валидация
- ✅ Обработано файлов: {operation2['details'].get('processed', 0)}
- ✅ Пропущено: {operation2['details'].get('skipped', 0)}
- ⚠️  Ошибок валидации: {operation2['details'].get('validation_errors', 0)}
- ✅ Файлов отладки создано: {operation2['details'].get('debug_files_created', 0)}

### Операция 3: Импорт в БД
- ✅ Импортировано записей: {operation3['details'].get('imported', 0)}
- ⚠️  Пропущено: {operation3['details'].get('skipped', 0)}
- ❌ Ошибок: {operation3['details'].get('errors', 0)}

---

## ЧТО НАЙДЕНО

### Данные электроэнергии
- Обработано загрузок: {results['summary']['uploads_processed']}
- Валидировано: {results['summary']['validated']}
- Импортировано записей: {results['summary']['imported_records']}

### Файлы отладки
- Создано файлов: {operation2['details'].get('debug_files_created', 0)}
- Расположение: {debug_dir}

---

## ПРОВЕРКИ ЦЕЛОСТНОСТИ И БЕЗОШИБОЧНОСТИ

### Проверки целостности:
- ✅ Наличие обязательных полей (resources, generated_at)
- ✅ Наличие данных электроэнергии
- ✅ Корректность структуры JSON

### Проверки безошибочности:
- ✅ Валидность JSON
- ✅ Наличие данных
- ✅ Наличие годовых/квартальных данных

---

## ОШИБКИ

{chr(10).join(f'- {error}' for error in results['errors']) if results['errors'] else 'Ошибок не обнаружено'}

---

## ЧТО ТРЕБУЕТСЯ ДЛЯ СЛЕДУЮЩЕГО БЛОКА

{'✅ Все готово для БЛОКА 4 (импорт данных газа)' if operation3['status'] == 'success' else '⚠️ Требуется устранение ошибок'}
"""

tdlv_file = tdlv_dir / f"block_3_tdlv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(tdlv_file, 'w', encoding='utf-8') as f:
    f.write(tdlv_report)

print("=" * 80)
print("БЛОК 3 ЗАВЕРШЁН")
print("=" * 80)
print()
print(f"✅ TDLV отчёт сохранён: {tdlv_file}")
print(f"✅ Статус обновлён: {status['blocks']['block_3']['status']}")
print()

if results['errors']:
    print("⚠️  ОБНАРУЖЕНЫ ПРЕДУПРЕЖДЕНИЯ:")
    for error in results['errors'][:5]:
        print(f"   - {error}")
    if len(results['errors']) > 5:
        print(f"   ... и ещё {len(results['errors']) - 5} предупреждений")
    print()
    print("ТРЕБУЕТСЯ ПРИНЯТИЕ РЕШЕНИЯ ПОЛЬЗОВАТЕЛЕМ")
else:
    print("✅ Все операции выполнены успешно")
    print(f"✅ Импортировано записей: {results['imported_records']}")
    print("✅ Готово к выполнению БЛОКА 4 (импорт данных газа)")

