"""
Скрипт для переагрегации всех существующих загрузок.
Используется для применения исправлений к уже загруженным файлам.
"""

import logging
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Импорты
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.energy_aggregator import (
    aggregate_from_db_json,
    write_aggregation_json,
)
import database
import os

# Путь к директории агрегированных данных
# Определяем путь относительно директории ingest
ingest_path = Path(__file__).resolve().parent.parent
INBOX_DIR = Path(os.getenv("INBOX_DIR", str(ingest_path / "data" / "inbox")))
AGGREGATED_DIR = Path(os.getenv("AGGREGATED_DIR", str(INBOX_DIR / "aggregated")))
AGGREGATED_DIR.mkdir(parents=True, exist_ok=True)


def reaggregate_enterprise(enterprise_id: int) -> Dict[str, Any]:
    """
    Переагрегирует все данные для предприятия.

    Args:
        enterprise_id: ID предприятия

    Returns:
        Статистика переагрегации
    """
    logger.info(f"🔄 Начинаю переагрегацию для предприятия ID: {enterprise_id}")

    uploads = database.list_uploads_for_enterprise(enterprise_id)
    stats = {"processed": 0, "success": 0, "failed": 0, "aggregated_files": []}

    for upload in uploads:
        batch_id = upload.get("batch_id")
        filename = upload.get("filename", "unknown")
        status = upload.get("status")

        if status != "success" or not batch_id:
            continue

        logger.info(f"📄 Обработка файла: {filename} (batch_id: {batch_id[:8]}...)")
        stats["processed"] += 1

        try:
            upload_record = database.get_upload_by_batch(batch_id)
            if not upload_record or not upload_record.get("raw_json"):
                logger.warning(f"⚠️ Нет raw_json для {filename}")
                stats["failed"] += 1
                continue

            raw_json = upload_record["raw_json"]

            # Агрегируем данные
            aggregation_data = aggregate_from_db_json(raw_json)

            if not aggregation_data:
                logger.warning(f"⚠️ Агрегация не удалась для {filename}")
                stats["failed"] += 1
                continue

            # Обрабатываем категории использования (если это файл pererashod)
            # Это делается автоматически в aggregate_from_db_json, если данные есть

            # Сохраняем агрегированные данные
            aggregated_file = write_aggregation_json(
                batch_id, aggregation_data, AGGREGATED_DIR
            )
            stats["aggregated_files"].append(str(aggregated_file))
            stats["success"] += 1

            logger.info(f"✅ Агрегированные данные сохранены: {aggregated_file.name}")

            # Логируем структуру
            if "resources" in aggregation_data:
                resources = aggregation_data["resources"]
                for resource_name, resource_data in resources.items():
                    if resource_data:
                        quarters = list(resource_data.keys())
                        logger.info(
                            f"  📊 {resource_name}: {len(quarters)} кварталов - {quarters[:3]}..."
                        )

        except Exception as e:
            logger.error(f"❌ Ошибка при переагрегации {filename}: {e}", exc_info=True)
            stats["failed"] += 1

    logger.info(
        f"✅ Переагрегация завершена: обработано={stats['processed']}, успешно={stats['success']}, ошибок={stats['failed']}"
    )
    return stats


def reaggregate_all() -> None:
    """Переагрегирует данные для всех предприятий"""
    enterprises = database.list_enterprises()

    logger.info(f"🔄 Найдено предприятий: {len(enterprises)}")

    for enterprise in enterprises:
        enterprise_id = enterprise["id"]
        enterprise_name = enterprise["name"]
        logger.info(f"\n{'=' * 60}")
        logger.info(f"🏢 Предприятие: {enterprise_name} (ID: {enterprise_id})")
        logger.info(f"{'=' * 60}")

        stats = reaggregate_enterprise(enterprise_id)

        logger.info(f"📊 Статистика для {enterprise_name}:")
        logger.info(f"   Обработано: {stats['processed']}")
        logger.info(f"   Успешно: {stats['success']}")
        logger.info(f"   Ошибок: {stats['failed']}")


if __name__ == "__main__":
    import os
    import sys

    # Добавляем путь к модулям
    ingest_path = Path(__file__).resolve().parent.parent
    if str(ingest_path) not in sys.path:
        sys.path.insert(0, str(ingest_path))

    # Проверяем аргументы
    if len(sys.argv) > 1:
        enterprise_id = int(sys.argv[1])
        reaggregate_enterprise(enterprise_id)
    else:
        reaggregate_all()
