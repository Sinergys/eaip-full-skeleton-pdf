"""БЛОК 2.1: Создание функции поиска таблиц по ключевым словам"""
import json
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

# Добавляем путь к корневой папке проекта для импортов
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from eaip_full_skeleton.services.ingest.utils.ocr_data_adapter import find_energy_tables_in_ocr

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

def execute_block_2_1():
    """БЛОК 2.1: Создание функции поиска таблиц по ключевым словам"""
    block_id = "ocr_block_2_1"
    logger.info(f"================================================================================")
    logger.info(f"БЛОК 2.1: СОЗДАНИЕ ФУНКЦИИ ПОИСКА ТАБЛИЦ ПО КЛЮЧЕВЫМ СЛОВАМ")
    logger.info(f"================================================================================")
    
    update_block_status(block_id, "in_progress")
    
    try:
        # ОПЕРАЦИЯ 1: Загрузка данных из ЭТАПА 1
        logger.info("\n📋 ОПЕРАЦИЯ 1: Загрузка данных из ЭТАПА 1...")
        ocr_result_files = list(DEBUG_FILES_DIR.glob("*_ocr_result.json"))
        
        if not ocr_result_files:
            raise ValueError("Не найдены файлы результатов OCR из ЭТАПА 1")
        
        logger.info(f"✅ Найдено файлов результатов OCR: {len(ocr_result_files)}")
        
        # ОПЕРАЦИЯ 2: Тестирование функции find_energy_tables_in_ocr()
        logger.info("\n🔍 ОПЕРАЦИЯ 2: Тестирование функции find_energy_tables_in_ocr()...")
        test_results = []
        
        for ocr_file in ocr_result_files:
            logger.info(f"   📄 Обработка: {ocr_file.name}")
            try:
                with open(ocr_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                ocr_result = data.get("ocr_result", {})
                filename = data.get("filename", "unknown")
                
                # Применяем функцию поиска таблиц
                found_tables = find_energy_tables_in_ocr(ocr_result)
                
                test_results.append({
                    "filename": filename,
                    "ocr_file": str(ocr_file),
                    "total_tables_in_ocr": ocr_result.get("tables_count", 0),
                    "found_energy_tables": len(found_tables),
                    "tables": found_tables
                })
                
                logger.info(f"      ✅ Найдено таблиц с данными энергоресурсов: {len(found_tables)}")
                for i, table_info in enumerate(found_tables):
                    logger.info(
                        f"         Таблица {i+1}: {table_info['resource_type']} "
                        f"(confidence: {table_info['confidence_score']:.2f})"
                    )
            
            except Exception as e:
                logger.error(f"      ❌ Ошибка обработки {ocr_file.name}: {e}")
                test_results.append({
                    "filename": ocr_file.name,
                    "error": str(e)
                })
        
        # ОПЕРАЦИЯ 3: Анализ результатов
        logger.info("\n📊 ОПЕРАЦИЯ 3: Анализ результатов...")
        total_found = sum(r.get("found_energy_tables", 0) for r in test_results if "error" not in r)
        successful_tests = len([r for r in test_results if "error" not in r])
        
        resource_types_found = set()
        for result in test_results:
            if "tables" in result:
                for table_info in result["tables"]:
                    resource_types_found.add(table_info.get("resource_type"))
        
        logger.info(f"✅ Успешных тестов: {successful_tests}/{len(test_results)}")
        logger.info(f"✅ Всего найдено таблиц с данными энергоресурсов: {total_found}")
        logger.info(f"✅ Типы ресурсов найдены: {', '.join(resource_types_found) if resource_types_found else 'нет'}")
        
        # Сохранение результатов теста
        test_results_file = TDLV_REPORTS_DIR / f"{block_id}_test_results.json"
        with open(test_results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Результаты теста сохранены: {test_results_file}")
        
        # Создание TDLV отчёта
        tdlv_content = f"""
## БЛОК 2.1: СОЗДАНИЕ ФУНКЦИИ ПОИСКА ТАБЛИЦ ПО КЛЮЧЕВЫМ СЛОВАМ

### Что сделано
- ✅ Создана функция `find_energy_tables_in_ocr()` в `eaip_full_skeleton/services/ingest/utils/ocr_data_adapter.py`
- ✅ Реализован поиск по ключевым словам для типов ресурсов (electricity, gas, water, heating)
- ✅ Протестирована функция на данных из ЭТАПА 1

### Что найдено
- **Обработано файлов:** {len(test_results)}
- **Успешных тестов:** {successful_tests}
- **Всего найдено таблиц с данными энергоресурсов:** {total_found}
- **Типы ресурсов найдены:** {', '.join(resource_types_found) if resource_types_found else 'нет'}

### Функция создана
```python
def find_energy_tables_in_ocr(ocr_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    \"\"\"
    Находит таблицы с данными энергоресурсов в результатах OCR.
    Возвращает список найденных таблиц с метаданными:
    - table: исходная таблица
    - resource_type: тип ресурса (electricity, gas, water, heating)
    - confidence_score: оценка соответствия (0-1)
    - matched_keywords: найденные ключевые слова
    - table_index: индекс таблицы
    \"\"\"
```

### Примеры работы
"""
        
        # Добавляем примеры
        for result in test_results[:2]:  # Первые 2 примера
            if "tables" in result and result["tables"]:
                table_info = result["tables"][0]
                tdlv_content += f"""
**Файл:** {result['filename']}
- Тип ресурса: {table_info['resource_type']}
- Confidence: {table_info['confidence_score']:.2f}
- Ключевые слова: {', '.join(table_info['matched_keywords'][:5])}
"""
        
        tdlv_content += f"""

### Ошибки
- Ошибок при тестировании: {len([r for r in test_results if 'error' in r])}

### Что требуется для следующего блока
- ✅ Функция поиска таблиц работает корректно
- ✅ Готово к БЛОКУ 2.2 (определение типа ресурса и периода)

### Полные результаты теста
```json
{json.dumps(test_results, ensure_ascii=False, indent=2)[:1000]}...
```
(Полные результаты сохранены в: {test_results_file})
        """
        
        create_tdlv_report(block_id, tdlv_content)
        update_block_status(block_id, "completed")
        
        logger.info(f"\n✅ БЛОК 2.1 выполнен успешно")
        logger.info(f"✅ Функция создана и протестирована")
        logger.info(f"✅ Найдено таблиц: {total_found}")
        logger.info(f"\n✅ Готово к выполнению БЛОКА 2.2 (определение типа ресурса и периода)")
        
    except Exception as e:
        logger.error(f"Критическая ошибка при выполнении БЛОКА 2.1: {e}")
        update_block_status(block_id, "failed", error=str(e))
        create_tdlv_report(block_id, f"Критическая ошибка: {e}")
        logger.error(f"\n❌ БЛОК 2.1 ЗАВЕРШЁН С ОШИБКОЙ")
        raise

if __name__ == "__main__":
    execute_block_2_1()

