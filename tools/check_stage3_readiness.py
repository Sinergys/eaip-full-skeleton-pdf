"""Проверка готовности к ЭТАПУ 3 и проверка конфликтов с другим агентом"""
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent
plans_dir = project_root / "reports" / "ocr" / "import_plan"
status_file = plans_dir / "blocks_status.json"

def check_stage3_readiness():
    """Проверяет готовность к ЭТАПУ 3 и возможные конфликты"""
    logger.info("=" * 80)
    logger.info("ПРОВЕРКА ГОТОВНОСТИ К ЭТАПУ 3")
    logger.info("=" * 80)
    
    # Проверка статуса блоков
    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        logger.info("\n📊 Статус блоков:")
        for block_id in ["block_3", "block_4", "block_5", "block_6"]:
            block_status = status.get("blocks", {}).get(block_id, {})
            block_status_str = block_status.get("status", "unknown")
            logger.info(f"  {block_id}: {block_status_str}")
            
            if block_status_str == "in_progress":
                logger.warning(f"  ⚠️ {block_id} в процессе выполнения другим агентом!")
    
    # Проверка файлов блоков
    logger.info("\n📁 Проверка файлов блоков:")
    block_files = {
        "block_3": project_root / "tools" / "execute_block3.py",
        "block_4": project_root / "tools" / "execute_block4.py",
        "block_5": project_root / "tools" / "execute_block5.py",
        "block_6": project_root / "tools" / "execute_block6.py"
    }
    
    for block_id, file_path in block_files.items():
        if file_path.exists():
            logger.info(f"  ✅ {block_id}: {file_path.name} существует")
            # Проверяем время последней модификации
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            logger.info(f"     Последнее изменение: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            logger.info(f"  ⏳ {block_id}: файл не существует (будет создан)")
    
    # Проверка модуля адаптера
    adapter_file = project_root / "eaip_full_skeleton" / "services" / "ingest" / "utils" / "ocr_data_adapter.py"
    if adapter_file.exists():
        logger.info(f"\n✅ Модуль адаптера существует: {adapter_file.name}")
    else:
        logger.error(f"\n❌ Модуль адаптера не найден: {adapter_file}")
        return False
    
    # Проверка статуса ЭТАПА 2
    if status.get("ocr_implementation", {}).get("stage_2", {}).get("blocks", {}).get("ocr_block_2_4", {}).get("status") == "completed":
        logger.info("\n✅ ЭТАП 2 завершён - адаптер готов")
    else:
        logger.warning("\n⚠️ ЭТАП 2 может быть не завершён")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Проверка завершена")
    logger.info("=" * 80)
    
    return True

if __name__ == "__main__":
    check_stage3_readiness()

