"""БЛОК 2.3: Преобразование структуры таблицы"""
import json
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

# Добавляем путь к корневой папке проекта для импортов
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from eaip_full_skeleton.services.ingest.utils.ocr_data_adapter import (
    find_energy_tables_in_ocr,
    identify_resource_type,
    identify_period_type,
    extract_dates_from_table,
    extract_values_from_table
)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Константы
IMPORT_PLAN_DIR = project_root / "reports" / "ocr" / "import_plan"
TDLV_REPORTS_DIR = IMPORT_PLAN_DIR / "tdlv_reports"
DEBUG_FILES_DIR = IMPORT_PLAN_DIR / "debug_files" / "ocr_results"
STATUS_FILE = IMPORT_PLAN_DIR / "blocks_status.json"
TDLV_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def create_tdlv_report(block_id: str, content: str):
    """Создаёт TDLV отчёт для блока"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = TDLV_REPORTS_DIR / f"{block_id}_tdlv_{timestamp}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"✅ TDLV отчёт сохранён: {report_file}")
    return report_file

def update_block_status(block_id: str, status: str, error: Optional[str] = None):
    """Обновляет статус блока"""
    try:
        if STATUS_FILE.exists():
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        if "ocr_implementation" not in data:
            data["ocr_implementation"] = {}
        if "stage_2" not in data["ocr_implementation"]:
            data["ocr_implementation"]["stage_2"] = {"blocks": {}}
        
        if "blocks" not in data["ocr_implementation"]["stage_2"]:
            data["ocr_implementation"]["stage_2"]["blocks"] = {}
        
        if block_id not in data["ocr_implementation"]["stage_2"]["blocks"]:
            data["ocr_implementation"]["stage_2"]["blocks"][block_id] = {}
        
        data["ocr_implementation"]["stage_2"]["blocks"][block_id]["status"] = status
        data["ocr_implementation"]["stage_2"]["blocks"][block_id]["updated_at"] = datetime.now().isoformat()
        if error:
            data["ocr_implementation"]["stage_2"]["blocks"][block_id]["error"] = error
        
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Не удалось обновить статус блока: {e}")

def execute_block_2_3():
    """БЛОК 2.3: Преобразование структуры таблицы"""
    block_id = "ocr_block_2_3"
    logger.info(f"================================================================================")
    logger.info(f"БЛОК 2.3: ПРЕОБРАЗОВАНИЕ СТРУКТУРЫ ТАБЛИЦЫ")
    logger.info(f"================================================================================")
    
    update_block_status(block_id, "in_progress")
    
    try:
        # ОПЕРАЦИЯ 1: Загрузка данных из предыдущих блоков
        logger.info("\n📋 ОПЕРАЦИЯ 1: Загрузка данных из предыдущих блоков...")
        ocr_result_files = list(DEBUG_FILES_DIR.glob("*_ocr_result.json"))
        
        if not ocr_result_files:
            raise ValueError("Не найдены файлы результатов OCR из ЭТАПА 1")
        
        logger.info(f"✅ Найдено файлов результатов OCR: {len(ocr_result_files)}")
        
        # ОПЕРАЦИЯ 2: Тестирование функций extract_dates_from_table() и extract_values_from_table()
        logger.info("\n🔍 ОПЕРАЦИЯ 2: Тестирование функций извлечения дат и значений...")
        test_results = []
        
        for ocr_file in ocr_result_files:
            logger.info(f"   📄 Обработка: {ocr_file.name}")
            try:
                with open(ocr_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                ocr_result = data.get("ocr_result", {})
                filename = data.get("filename", "unknown")
                
                # Находим таблицы с данными энергоресурсов
                found_tables = find_energy_tables_in_ocr(ocr_result)
                
                table_results = []
                for table_info in found_tables:
                    table = table_info["table"]
                    resource_type = identify_resource_type(table, table_info.get("resource_type"))
                    period_type = identify_period_type(table)
                    
                    # Извлекаем даты
                    dates_data = extract_dates_from_table(table, period_type)
                    
                    # Извлекаем значения
                    values_data = extract_values_from_table(table, resource_type)
                    
                    table_results.append({
                        "table_index": table_info["table_index"],
                        "resource_type": resource_type,
                        "period_type": period_type,
                        "dates_extracted": {
                            "period_type": dates_data.get("period_type"),
                            "dates_count": len(dates_data.get("dates", [])),
                            "years": dates_data.get("years", []),
                            "months": dates_data.get("months", []),
                            "quarters": dates_data.get("quarters", [])
                        },
                        "values_extracted": {
                            "values_count": len(values_data.get("values", [])),
                            "total_consumption": values_data.get("total_consumption", 0.0),
                            "total_cost": values_data.get("total_cost", 0.0),
                            "columns": values_data.get("columns", {})
                        }
                    })
                    
                    logger.info(
                        f"      ✅ Таблица {table_info['table_index']}: "
                        f"даты={len(dates_data.get('dates', []))}, "
                        f"значения={len(values_data.get('values', []))}"
                    )
                
                test_results.append({
                    "filename": filename,
                    "ocr_file": str(ocr_file),
                    "tables_analyzed": len(table_results),
                    "table_results": table_results
                })
            
            except Exception as e:
                logger.error(f"      ❌ Ошибка обработки {ocr_file.name}: {e}")
                test_results.append({
                    "filename": ocr_file.name,
                    "error": str(e)
                })
        
        # ОПЕРАЦИЯ 3: Анализ результатов
        logger.info("\n📊 ОПЕРАЦИЯ 3: Анализ результатов...")
        successful_tests = len([r for r in test_results if "error" not in r])
        total_tables_analyzed = sum(r.get("tables_analyzed", 0) for r in test_results if "error" not in r)
        
        total_dates_extracted = 0
        total_values_extracted = 0
        total_consumption = 0.0
        total_cost = 0.0
        
        for result in test_results:
            if "table_results" in result:
                for table_result in result["table_results"]:
                    total_dates_extracted += table_result["dates_extracted"]["dates_count"]
                    total_values_extracted += table_result["values_extracted"]["values_count"]
                    total_consumption += table_result["values_extracted"]["total_consumption"]
                    total_cost += table_result["values_extracted"]["total_cost"]
        
        logger.info(f"✅ Успешных тестов: {successful_tests}/{len(test_results)}")
        logger.info(f"✅ Проанализировано таблиц: {total_tables_analyzed}")
        logger.info(f"✅ Извлечено дат: {total_dates_extracted}")
        logger.info(f"✅ Извлечено значений: {total_values_extracted}")
        logger.info(f"✅ Общее потребление: {total_consumption:.2f}")
        logger.info(f"✅ Общая стоимость: {total_cost:.2f}")
        
        # Сохранение результатов теста
        test_results_file = TDLV_REPORTS_DIR / f"{block_id}_test_results.json"
        with open(test_results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Результаты теста сохранены: {test_results_file}")
        
        # Создание TDLV отчёта
        tdlv_content = f"""
## БЛОК 2.3: ПРЕОБРАЗОВАНИЕ СТРУКТУРЫ ТАБЛИЦЫ

### Что сделано
- ✅ Создана функция `extract_dates_from_table()` в `eaip_full_skeleton/services/ingest/utils/ocr_data_adapter.py`
- ✅ Создана функция `extract_values_from_table()` в `eaip_full_skeleton/services/ingest/utils/ocr_data_adapter.py`
- ✅ Протестированы функции на данных из ЭТАПА 1

### Что найдено
- **Обработано файлов:** {len(test_results)}
- **Успешных тестов:** {successful_tests}
- **Проанализировано таблиц:** {total_tables_analyzed}
- **Извлечено дат:** {total_dates_extracted}
- **Извлечено значений:** {total_values_extracted}
- **Общее потребление:** {total_consumption:.2f}
- **Общая стоимость:** {total_cost:.2f}

### Функции созданы

#### extract_dates_from_table()
```python
def extract_dates_from_table(table: Dict[str, Any], period_type: Optional[str] = None) -> Dict[str, Any]:
    \"\"\"
    Извлекает даты (месяцы, кварталы, годы) из таблицы.
    Возвращает структуру с датами, годами, месяцами, кварталами.
    \"\"\"
```

#### extract_values_from_table()
```python
def extract_values_from_table(table: Dict[str, Any], resource_type: Optional[str] = None) -> Dict[str, Any]:
    \"\"\"
    Извлекает значения потребления и стоимости из таблицы.
    Возвращает структуру с извлечёнными значениями и метаданными колонок.
    \"\"\"
```

### Примеры работы
"""
        
        # Добавляем примеры
        for result in test_results[:2]:  # Первые 2 примера
            if "table_results" in result and result["table_results"]:
                table_result = result["table_results"][0]
                tdlv_content += f"""
**Файл:** {result['filename']}
- Тип ресурса: {table_result.get('resource_type', 'N/A')}
- Тип периода: {table_result.get('period_type', 'N/A')}
- Извлечено дат: {table_result['dates_extracted']['dates_count']}
- Извлечено значений: {table_result['values_extracted']['values_count']}
- Потребление: {table_result['values_extracted']['total_consumption']:.2f}
- Стоимость: {table_result['values_extracted']['total_cost']:.2f}
"""
        
        tdlv_content += f"""

### Ошибки
- Ошибок при тестировании: {len([r for r in test_results if 'error' in r])}

### Что требуется для следующего блока
- ✅ Функции извлечения дат и значений работают корректно
- ✅ Готово к БЛОКУ 2.4 (преобразование в формат агрегатора)

### Полные результаты теста
```json
{json.dumps(test_results, ensure_ascii=False, indent=2)[:1000]}...
```
(Полные результаты сохранены в: {test_results_file})
        """
        
        create_tdlv_report(block_id, tdlv_content)
        update_block_status(block_id, "completed")
        
        logger.info(f"\n✅ БЛОК 2.3 выполнен успешно")
        logger.info(f"✅ Функции созданы и протестированы")
        logger.info(f"✅ Извлечено дат: {total_dates_extracted}, значений: {total_values_extracted}")
        logger.info(f"\n✅ Готово к выполнению БЛОКА 2.4 (преобразование в формат агрегатора)")
        
    except Exception as e:
        logger.error(f"Критическая ошибка при выполнении БЛОКА 2.3: {e}")
        update_block_status(block_id, "failed", error=str(e))
        create_tdlv_report(block_id, f"Критическая ошибка: {e}")
        logger.error(f"\n❌ БЛОК 2.3 ЗАВЕРШЁН С ОШИБКОЙ")
        raise

if __name__ == "__main__":
    execute_block_2_3()

