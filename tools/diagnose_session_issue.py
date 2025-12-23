"""Диагностика проблемы с обрывом сеанса Cursor IDE"""
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent
plans_dir = project_root / "reports" / "ocr" / "import_plan"
status_file = plans_dir / "blocks_status.json"

def diagnose_session_issue():
    """Диагностирует проблему с обрывом сеанса"""
    logger.info("=" * 80)
    logger.info("ДИАГНОСТИКА ПРОБЛЕМЫ С ОБРЫВОМ СЕАНСА")
    logger.info("=" * 80)
    
    # 1. Проверка статуса блоков
    logger.info("\n📊 1. Проверка статуса блоков:")
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        # Проверяем блоки на "in_progress"
        in_progress_blocks = []
        for block_type in ["blocks", "ocr_implementation"]:
            if block_type in status:
                blocks = status[block_type]
                if isinstance(blocks, dict):
                    for block_id, block_data in blocks.items():
                        if isinstance(block_data, dict) and block_data.get("status") == "in_progress":
                            in_progress_blocks.append(f"{block_type}.{block_id}")
        
        if in_progress_blocks:
            logger.warning(f"  ⚠️ Найдены блоки в статусе 'in_progress': {in_progress_blocks}")
            logger.warning("     Это может указывать на незавершённую работу другого агента")
        else:
            logger.info("  ✅ Нет блоков в статусе 'in_progress'")
    
    # 2. Проверка временных файлов
    logger.info("\n📁 2. Проверка временных файлов:")
    temp_files_found = []
    
    # Проверяем директорию INBOX
    inbox_dir = Path(r"C:\AUDIT\OBJECTS\Navoiy IES\INBOX")
    if inbox_dir.exists():
        temp_files = list(inbox_dir.glob("temp_ocr_*.png"))
        if temp_files:
            logger.warning(f"  ⚠️ Найдено временных файлов: {len(temp_files)}")
            for temp_file in temp_files:
                logger.warning(f"     {temp_file.name} (размер: {temp_file.stat().st_size} байт)")
                temp_files_found.append(temp_file)
        else:
            logger.info("  ✅ Временных файлов не найдено")
    
    # 3. Проверка последних изменений файлов
    logger.info("\n🕐 3. Проверка последних изменений файлов:")
    
    key_files = [
        project_root / "tools" / "execute_block3.py",
        project_root / "eaip_full_skeleton" / "services" / "ingest" / "utils" / "ocr_integration.py",
        status_file
    ]
    
    for file_path in key_files:
        if file_path.exists():
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            logger.info(f"  {file_path.name}: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 4. Проверка логов выполнения
    logger.info("\n📝 4. Проверка логов выполнения:")
    execution_log = plans_dir / "execution_log.jsonl"
    if execution_log.exists():
        with open(execution_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            logger.info(f"  ✅ Лог содержит {len(lines)} записей")
            if lines:
                last_entry = json.loads(lines[-1])
                logger.info(f"     Последняя запись: {last_entry.get('step', 'unknown')} ({last_entry.get('status', 'unknown')})")
    else:
        logger.info("  ⏳ Лог выполнения не найден")
    
    # 5. Рекомендации
    logger.info("\n💡 5. РЕКОМЕНДАЦИИ:")
    logger.info("  ✅ Проверьте, не запущен ли другой процесс/агент, работающий с теми же файлами")
    logger.info("  ✅ Удалите временные файлы вручную, если они заблокированы")
    logger.info("  ✅ Проверьте логи Cursor IDE на наличие ошибок")
    logger.info("  ✅ Если проблема повторяется, попробуйте:")
    logger.info("     - Перезапустить Cursor IDE")
    logger.info("     - Проверить, не открыты ли файлы в других программах")
    logger.info("     - Использовать более короткие операции (< 5 минут)")
    
    # 6. Статистика
    logger.info("\n📊 6. СТАТИСТИКА:")
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        ocr_blocks = status.get("ocr_implementation", {}).get("stage_3", {}).get("blocks", {})
        completed = sum(1 for b in ocr_blocks.values() if isinstance(b, dict) and b.get("status") == "completed")
        total = len(ocr_blocks)
        logger.info(f"  Завершено блоков ЭТАПА 3: {completed}/{total}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Диагностика завершена")
    logger.info("=" * 80)
    
    return {
        "in_progress_blocks": in_progress_blocks,
        "temp_files": [str(f) for f in temp_files_found],
        "recommendations": [
            "Проверить наличие других процессов",
            "Удалить временные файлы",
            "Использовать более короткие операции"
        ]
    }

if __name__ == "__main__":
    diagnose_session_issue()

