# Dual-write функции для синхронной записи в обе БД
import logging
from typing import Dict, Optional
import database
import postgres_db

logger = logging.getLogger(__name__)

async def create_upload_dual(data: Dict) -> str:
    """Создание загрузки в обе БД"""
    # SQLite (основная)
    sqlite_id = database.create_upload(data)
    
    # PostgreSQL (дублирование)
    try:
        await postgres_db.create_upload(data)
        logger.info(f"✅ Дублирование в PostgreSQL: {sqlite_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка дублирования в PostgreSQL: {e}")
    
    return sqlite_id

async def get_upload_dual(batch_id: str) -> Optional[Dict]:
    """Получение загрузки из PostgreSQL (приоритет)"""
    # Сначала пробуем PostgreSQL
    try:
        result = await postgres_db.get_upload_by_batch(batch_id)
        if result:
            logger.info(f"📊 Данные из PostgreSQL: {batch_id}")
            return result
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL недоступен, использую SQLite: {e}")
    
    # Fallback на SQLite
    return database.get_upload_by_batch(batch_id)