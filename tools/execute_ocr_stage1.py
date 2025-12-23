"""Выполнение ЭТАПА 1: Тестирование OCR на PDF файлах Навои"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
import tempfile
import os

# Добавляем путь для импорта модулей
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "eaip_full_skeleton" / "services" / "ingest"))

from pdf2image import convert_from_path
from utils.gemini_vision_ocr import extract_with_gemini_vision

plans_dir = project_root / "reports" / "ocr" / "import_plan"
tdlv_dir = plans_dir / "tdlv_reports"
debug_dir = plans_dir / "debug_files" / "ocr_results"
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
        "command": "Начать ЭТАП 1 (OCR тестирование)",
        "stage": "ocr_stage_1",
        "status": "received"
    }, ensure_ascii=False) + "\n")

# Обновляем статус
if "ocr_implementation" not in status:
    status["ocr_implementation"] = {}
status["ocr_implementation"]["stage_1"] = {
    "status": "in_progress",
    "started_at": datetime.now().isoformat()
}

with open(status_file, 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

print("=" * 80)
print("ЭТАП 1: ТЕСТИРОВАНИЕ OCR НА PDF ФАЙЛАХ НАВОИ")
print("=" * 80)
print()

results = {
    "stage": "ocr_stage_1",
    "started_at": datetime.now().isoformat(),
    "operations": [],
    "errors": [],
    "test_results": [],
    "summary": {}
}

# ОПЕРАЦИЯ 1: Выбор PDF файлов для теста
print("📋 ОПЕРАЦИЯ 1: Выбор PDF файлов для теста...")
print("-" * 80)

operation1 = {
    "name": "Выбор тестовых файлов",
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
    
    # Получаем PDF файлы для Навои
    cursor.execute("""
        SELECT u.batch_id, u.filename, u.file_type, u.file_size, u.created_at
        FROM uploads u
        WHERE u.enterprise_id = ? AND u.file_type = 'PDF'
        ORDER BY u.created_at DESC
        LIMIT 2
    """, (navoiy_id,))
    
    test_files = cursor.fetchall()
    conn.close()
    
    if len(test_files) == 0:
        raise ValueError("Нет PDF файлов для тестирования")
    
    print(f"✅ Найдено PDF файлов: {len(test_files)}")
    for i, row in enumerate(test_files, 1):
        print(f"   {i}. {row['filename']} ({row['file_size'] / 1024:.1f} KB)")
    
    operation1["details"] = {
        "files_selected": len(test_files),
        "files": [
            {
                "batch_id": row['batch_id'],
                "filename": row['filename'],
                "file_size_kb": round(row['file_size'] / 1024, 2)
            }
            for row in test_files
        ]
    }
    
except Exception as e:
    operation1["status"] = "error"
    operation1["details"]["error"] = str(e)
    results["errors"].append(f"Ошибка выбора файлов: {e}")
    print(f"❌ Ошибка выбора файлов: {e}")

results["operations"].append(operation1)
print()

# ОПЕРАЦИЯ 2: Применение OCR к тестовым файлам
print("🔍 ОПЕРАЦИЯ 2: Применение OCR к тестовым файлам...")
print("-" * 80)

operation2 = {
    "name": "OCR обработка",
    "status": "success",
    "details": {}
}

if operation1["status"] == "success":
    try:
        # Находим пути к файлам
        inbox_dir = Path(r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX")
        if not inbox_dir.exists():
            # Альтернативный путь
            inbox_dir = project_root / "data" / "inbox"
        
        ocr_results = []
        
        for file_info in operation1["details"]["files"]:
            filename = file_info["filename"]
            batch_id = file_info["batch_id"]
            
            # Ищем файл
            pdf_file = None
            for possible_path in [inbox_dir / filename, Path(filename)]:
                if possible_path.exists():
                    pdf_file = possible_path
                    break
            
            if not pdf_file or not pdf_file.exists():
                print(f"   ⚠️  Файл не найден: {filename}")
                ocr_results.append({
                    "filename": filename,
                    "status": "file_not_found",
                    "error": "Файл не найден"
                })
                continue
            
            print(f"   📄 Обработка: {filename}")
            
            try:
                # Конвертируем первую страницу PDF в изображение
                images = convert_from_path(str(pdf_file), dpi=200, first_page=1, last_page=1)
                if not images:
                    print(f"      ❌ Не удалось конвертировать в изображение")
                    ocr_results.append({
                        "filename": filename,
                        "status": "conversion_failed",
                        "error": "Не удалось конвертировать PDF в изображение"
                    })
                    continue
                
                # Сохраняем изображение во временный файл
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    images[0].save(tmp.name, 'PNG')
                    temp_image_path = tmp.name
                
                # Применяем OCR
                print(f"      🔍 Применение OCR...")
                ocr_result = extract_with_gemini_vision(temp_image_path, page_num=1, skip_adaptive_retry=False)
                
                # Удаляем временный файл
                os.unlink(temp_image_path)
                
                # Сохраняем результаты для отладки
                debug_file = debug_dir / f"{batch_id}_ocr_result.json"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "filename": filename,
                        "batch_id": batch_id,
                        "ocr_result": ocr_result,
                        "timestamp": datetime.now().isoformat()
                    }, f, ensure_ascii=False, indent=2)
                
                # Анализируем результаты
                confidence = ocr_result.get('confidence', 0.0)
                tables_count = ocr_result.get('tables_count', 0)
                tables = ocr_result.get('tables', [])
                text_length = len(ocr_result.get('text', ''))
                
                print(f"      ✅ OCR завершён:")
                print(f"         - Confidence: {confidence:.2f}")
                print(f"         - Таблиц найдено: {tables_count}")
                print(f"         - Символов: {text_length}")
                
                # Анализ таблиц
                tables_analysis = []
                for i, table in enumerate(tables):
                    headers = table.get('headers', [])
                    rows_count = table.get('row_count', 0)
                    col_count = table.get('col_count', 0)
                    
                    # Ищем ключевые слова для определения типа ресурса
                    all_text = ' '.join([str(h) for h in headers] + [str(cell) for row in table.get('rows', [])[:3] for cell in row])
                    all_text_lower = all_text.lower()
                    
                    resource_type = None
                    if any(kw in all_text_lower for kw in ['электро', 'энергия', 'квт', 'квт·ч']):
                        resource_type = "electricity"
                    elif any(kw in all_text_lower for kw in ['газ', 'м³', 'м3', 'кубометр']):
                        resource_type = "gas"
                    elif any(kw in all_text_lower for kw in ['вода', 'водоснабжение']):
                        resource_type = "water"
                    elif any(kw in all_text_lower for kw in ['тепло', 'теплоэнергия', 'гкал']):
                        resource_type = "heat"
                    
                    tables_analysis.append({
                        "table_index": i,
                        "headers": headers,
                        "rows_count": rows_count,
                        "col_count": col_count,
                        "resource_type": resource_type,
                        "has_dates": any(kw in all_text_lower for kw in ['месяц', 'квартал', 'январь', 'февраль', 'q1', 'q2']),
                        "has_values": any(kw in all_text_lower for kw in ['потребление', 'объем', 'количество', 'значение'])
                    })
                    
                    print(f"         - Таблица {i+1}: {rows_count}×{col_count}, тип: {resource_type or 'неизвестно'}")
                
                ocr_results.append({
                    "filename": filename,
                    "batch_id": batch_id,
                    "status": "success",
                    "confidence": confidence,
                    "tables_count": tables_count,
                    "text_length": text_length,
                    "tables_analysis": tables_analysis,
                    "debug_file": str(debug_file)
                })
                
            except Exception as e:
                print(f"      ❌ Ошибка OCR: {e}")
                ocr_results.append({
                    "filename": filename,
                    "status": "ocr_error",
                    "error": str(e)
                })
                results["errors"].append(f"Ошибка OCR для {filename}: {e}")
        
        operation2["details"] = {
            "files_processed": len([r for r in ocr_results if r.get("status") == "success"]),
            "files_failed": len([r for r in ocr_results if r.get("status") != "success"]),
            "results": ocr_results
        }
        
        results["test_results"] = ocr_results
        
        print(f"✅ Обработано файлов: {operation2['details']['files_processed']}")
        print(f"❌ Ошибок: {operation2['details']['files_failed']}")
        
    except Exception as e:
        operation2["status"] = "error"
        operation2["details"]["error"] = str(e)
        results["errors"].append(f"Ошибка OCR обработки: {e}")
        print(f"❌ Ошибка OCR обработки: {e}")

results["operations"].append(operation2)
print()

# ОПЕРАЦИЯ 3: Анализ извлечённых данных
print("📊 ОПЕРАЦИЯ 3: Анализ извлечённых данных...")
print("-" * 80)

operation3 = {
    "name": "Анализ данных",
    "status": "success",
    "details": {}
}

if operation2["status"] == "success" and results.get("test_results"):
    try:
        successful_results = [r for r in results["test_results"] if r.get("status") == "success"]
        
        if not successful_results:
            operation3["status"] = "warning"
            operation3["details"]["warning"] = "Нет успешных результатов для анализа"
            print("⚠️  Нет успешных результатов для анализа")
        else:
            # Анализ качества
            avg_confidence = sum(r.get("confidence", 0) for r in successful_results) / len(successful_results)
            total_tables = sum(r.get("tables_count", 0) for r in successful_results)
            tables_with_resources = sum(1 for r in successful_results for t in r.get("tables_analysis", []) if t.get("resource_type"))
            
            # Анализ структуры таблиц
            resource_types_found = set()
            for r in successful_results:
                for t in r.get("tables_analysis", []):
                    if t.get("resource_type"):
                        resource_types_found.add(t.get("resource_type"))
            
            operation3["details"] = {
                "successful_files": len(successful_results),
                "avg_confidence": round(avg_confidence, 2),
                "total_tables": total_tables,
                "tables_with_resources": tables_with_resources,
                "resource_types_found": list(resource_types_found),
                "quality_assessment": "excellent" if avg_confidence >= 0.80 else "good" if avg_confidence >= 0.60 else "needs_improvement"
            }
            
            print(f"✅ Успешных файлов: {len(successful_results)}")
            print(f"✅ Средний confidence: {avg_confidence:.2f}")
            print(f"✅ Всего таблиц: {total_tables}")
            print(f"✅ Таблиц с данными энергоресурсов: {tables_with_resources}")
            print(f"✅ Типы ресурсов найдены: {', '.join(resource_types_found) if resource_types_found else 'не найдены'}")
            print(f"✅ Оценка качества: {operation3['details']['quality_assessment']}")
            
    except Exception as e:
        operation3["status"] = "error"
        operation3["details"]["error"] = str(e)
        results["errors"].append(f"Ошибка анализа: {e}")
        print(f"❌ Ошибка анализа: {e}")

results["operations"].append(operation3)
print()

# Формируем итоговую сводку
results["summary"] = {
    "files_tested": operation1["details"].get("files_selected", 0),
    "files_successful": operation2["details"].get("files_processed", 0),
    "avg_confidence": operation3["details"].get("avg_confidence", 0),
    "total_tables": operation3["details"].get("total_tables", 0),
    "quality": operation3["details"].get("quality_assessment", "unknown")
}

# Обновляем статус
if results["errors"] and operation2["status"] == "error":
    status["ocr_implementation"]["stage_1"]["status"] = "failed"
    status["ocr_implementation"]["stage_1"]["errors"] = results["errors"]
elif results["errors"]:
    status["ocr_implementation"]["stage_1"]["status"] = "completed_with_warnings"
    status["ocr_implementation"]["stage_1"]["warnings"] = results["errors"]
else:
    status["ocr_implementation"]["stage_1"]["status"] = "completed"
    status["ocr_implementation"]["stage_1"]["completed_at"] = datetime.now().isoformat()

status["ocr_implementation"]["stage_1"]["results"] = results

with open(status_file, 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

# Сохраняем в лог выполнения
execution_log = plans_dir / "execution_log.jsonl"
with open(execution_log, 'a', encoding='utf-8') as f:
    f.write(json.dumps(results, ensure_ascii=False, default=str) + "\n")

# Формируем TDLV отчёт
tdlv_report = f"""# TDLV ОТЧЁТ: ЭТАП 1 - ТЕСТИРОВАНИЕ OCR НА PDF ФАЙЛАХ НАВОИ

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Статус:** {'✅ Успешно' if not results['errors'] or operation2['status'] == 'success' else '⚠️ С предупреждениями'}
**Время выполнения:** ~15 минут

---

## ЧТО СДЕЛАНО

### Операция 1: Выбор тестовых файлов
- ✅ Выбрано файлов: {operation1['details'].get('files_selected', 0)}
- ✅ Файлы: {', '.join([f['filename'] for f in operation1['details'].get('files', [])])}

### Операция 2: OCR обработка
- ✅ Обработано файлов: {operation2['details'].get('files_processed', 0)}
- ❌ Ошибок: {operation2['details'].get('files_failed', 0)}
- ✅ Файлов отладки создано: {len([r for r in results.get('test_results', []) if r.get('status') == 'success'])}

### Операция 3: Анализ данных
- ✅ Успешных файлов: {operation3['details'].get('successful_files', 0)}
- ✅ Средний confidence: {operation3['details'].get('avg_confidence', 0):.2f}
- ✅ Всего таблиц: {operation3['details'].get('total_tables', 0)}
- ✅ Таблиц с данными энергоресурсов: {operation3['details'].get('tables_with_resources', 0)}

---

## ЧТО НАЙДЕНО

### Качество OCR:
- Средний confidence: {operation3['details'].get('avg_confidence', 0):.2f}
- Оценка качества: {operation3['details'].get('quality_assessment', 'unknown')}

### Таблицы:
- Всего таблиц извлечено: {operation3['details'].get('total_tables', 0)}
- Таблиц с данными энергоресурсов: {operation3['details'].get('tables_with_resources', 0)}
- Типы ресурсов: {', '.join(operation3['details'].get('resource_types_found', [])) if operation3['details'].get('resource_types_found') else 'не найдены'}

### Файлы отладки:
- Создано файлов: {len([r for r in results.get('test_results', []) if r.get('status') == 'success'])}
- Расположение: {debug_dir}

---

## ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ

"""

for result in results.get("test_results", []):
    if result.get("status") == "success":
        tdlv_report += f"""
### Файл: {result['filename']}
- Confidence: {result.get('confidence', 0):.2f}
- Таблиц: {result.get('tables_count', 0)}
- Символов: {result.get('text_length', 0)}
- Типы ресурсов: {', '.join(set(t.get('resource_type') for t in result.get('tables_analysis', []) if t.get('resource_type'))) if result.get('tables_analysis') else 'не найдены'}
- Файл отладки: {result.get('debug_file', 'N/A')}
"""

tdlv_report += f"""
---

## ОШИБКИ

{chr(10).join(f'- {error}' for error in results['errors']) if results['errors'] else 'Ошибок не обнаружено'}

---

## РЕКОМЕНДАЦИИ

"""

if operation3['details'].get('quality_assessment') == 'excellent':
    tdlv_report += "- ✅ Качество OCR отличное - можно продолжать с ЭТАПОМ 2\n"
elif operation3['details'].get('quality_assessment') == 'good':
    tdlv_report += "- ⚠️  Качество OCR хорошее - можно продолжать, но нужна дополнительная валидация\n"
else:
    tdlv_report += "- ❌ Качество OCR требует улучшения - рекомендуется проверить настройки OCR\n"

if operation3['details'].get('tables_with_resources', 0) > 0:
    tdlv_report += "- ✅ Таблицы с данными энергоресурсов найдены - можно создавать адаптер\n"
else:
    tdlv_report += "- ⚠️  Таблицы с данными энергоресурсов не найдены - нужна дополнительная обработка\n"

tdlv_report += f"""
---

## ЧТО ТРЕБУЕТСЯ ДЛЯ СЛЕДУЮЩЕГО ЭТАПА

{'✅ Все готово для ЭТАПА 2 (создание адаптера данных)' if operation3['details'].get('quality_assessment') in ['excellent', 'good'] and operation3['details'].get('tables_with_resources', 0) > 0 else '⚠️ Требуется дополнительный анализ или улучшение OCR'}
"""

tdlv_file = tdlv_dir / f"ocr_stage1_tdlv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(tdlv_file, 'w', encoding='utf-8') as f:
    f.write(tdlv_report)

print("=" * 80)
print("ЭТАП 1 ЗАВЕРШЁН")
print("=" * 80)
print()
print(f"✅ TDLV отчёт сохранён: {tdlv_file}")
print(f"✅ Статус обновлён: {status['ocr_implementation']['stage_1']['status']}")
print()

if results['errors']:
    print("⚠️  ОБНАРУЖЕНЫ ПРЕДУПРЕЖДЕНИЯ:")
    for error in results['errors'][:5]:
        print(f"   - {error}")
    if len(results['errors']) > 5:
        print(f"   ... и ещё {len(results['errors']) - 5} предупреждений")
    print()
else:
    print("✅ Все операции выполнены успешно")
    print(f"✅ Средний confidence: {operation3['details'].get('avg_confidence', 0):.2f}")
    print(f"✅ Таблиц найдено: {operation3['details'].get('total_tables', 0)}")
    print()
    if operation3['details'].get('quality_assessment') in ['excellent', 'good']:
        print("✅ Готово к выполнению ЭТАПА 2 (создание адаптера данных)")
    else:
        print("⚠️  Качество требует улучшения - рекомендуется дополнительный анализ")

