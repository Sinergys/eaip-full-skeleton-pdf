"""
PostgreSQL подключение для EAIP ingest сервиса
Параллельная работа с SQLite
"""

import os
import logging
import asyncpg
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class PostgresDB:
    def __init__(self):
        self.pool = None
        self.connected = False
    
    async def connect(self):
        """Подключение к PostgreSQL"""
        try:
            self.pool = await asyncpg.create_pool(
                host=os.getenv('POSTGRES_HOST', 'postgres'),
                port=int(os.getenv('POSTGRES_PORT', 5432)),
                user=os.getenv('POSTGRES_USER', 'eaip'),
                password=os.getenv('POSTGRES_PASSWORD', 'eaip_pw'),
                database=os.getenv('POSTGRES_DB', 'eaip'),
                min_size=1,
                max_size=10
            )
            self.connected = True
            logger.info("✅ PostgreSQL подключен")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            self.connected = False
    
    async def disconnect(self):
        """Отключение от PostgreSQL"""
        if self.pool:
            await self.pool.close()
            self.connected = False
            logger.info("🔌 PostgreSQL отключен")
    
    async def test_connection(self) -> bool:
        """Тест подключения"""
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"❌ Тест PostgreSQL не пройден: {e}")
            return False
    
    # Заглушки для совместимости с SQLite API
    async def init_db(self):
        """Инициализация БД (заглушка)"""
        logger.info("📝 PostgreSQL инициализация (заглушка)")
    
    async def get_upload_by_batch(self, batch_id: str) -> Optional[Dict]:
        """Получение загрузки по batch_id (заглушка)"""
        return None
    
    async def create_upload(self, data: Dict) -> str:
        """Создание загрузки (заглушка)"""
        return data.get('batch_id', '')
    
    async def list_enterprises(self) -> List[Dict]:
        """Список предприятий (заглушка)"""
        return []
    
    async def get_or_create_enterprise(self, name: str) -> Dict:
        """Получение/создание предприятия (заглушка)"""
        return {"id": 1, "name": name}

# Глобальный экземпляр
postgres_db = PostgresDB()

async def init_postgres():
    """Инициализация PostgreSQL подключения"""
    await postgres_db.connect()

async def close_postgres():
    """Закрытие PostgreSQL подключения"""
    await postgres_db.disconnect()