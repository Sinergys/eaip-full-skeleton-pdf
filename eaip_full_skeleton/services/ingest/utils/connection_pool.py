"""
Модуль connection pooling для оптимизации работы с базами данных
"""

import logging
import os
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Попытка использовать SQLAlchemy для connection pooling
try:
    from sqlalchemy import create_engine, pool
    from sqlalchemy.orm import sessionmaker

    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    logger.warning(
        "SQLAlchemy не установлен, используется стандартный connection pooling"
    )

# Попытка использовать psycopg2 для PostgreSQL
try:
    from psycopg2 import pool as pg_pool  # noqa: F401

    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


class DatabaseConnectionPool:
    """
    Класс для управления пулом соединений с базой данных
    """

    def __init__(self):
        """Инициализация пула соединений"""
        self.sqlalchemy_engine = None
        self.sqlalchemy_session = None
        self.postgres_pool = None

        self._init_postgres_pool()
        self._init_sqlalchemy()

    def _init_postgres_pool(self):
        """Инициализация пула PostgreSQL"""
        if not HAS_PSYCOPG2:
            return

        try:
            postgres_host = os.getenv("POSTGRES_HOST", "localhost")
            postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
            postgres_user = os.getenv("POSTGRES_USER")
            postgres_password = os.getenv("POSTGRES_PASSWORD")
            postgres_db = os.getenv("POSTGRES_DB")

            if not all([postgres_user, postgres_password, postgres_db]):
                logger.debug("PostgreSQL credentials не настроены, пропускаем пул")
                return

            # Создаем пул соединений
            min_conn = int(os.getenv("POSTGRES_POOL_MIN", "2"))
            max_conn = int(os.getenv("POSTGRES_POOL_MAX", "10"))

            self.postgres_pool = pg_pool.ThreadedConnectionPool(
                minconn=min_conn,
                maxconn=max_conn,
                host=postgres_host,
                port=postgres_port,
                user=postgres_user,
                password=postgres_password,
                database=postgres_db,
            )

            logger.info(f"PostgreSQL пул создан: {min_conn}-{max_conn} соединений")
        except Exception as e:
            logger.warning(f"Не удалось создать PostgreSQL пул: {e}")

    def _init_sqlalchemy(self):
        """Инициализация SQLAlchemy engine с connection pooling"""
        if not HAS_SQLALCHEMY:
            return

        try:
            # Пробуем PostgreSQL
            postgres_user = os.getenv("POSTGRES_USER")
            postgres_password = os.getenv("POSTGRES_PASSWORD")
            postgres_db = os.getenv("POSTGRES_DB")
            postgres_host = os.getenv("POSTGRES_HOST", "localhost")
            postgres_port = os.getenv("POSTGRES_PORT", "5432")

            if all([postgres_user, postgres_password, postgres_db]):
                database_url = (
                    f"postgresql://{postgres_user}:{postgres_password}"
                    f"@{postgres_host}:{postgres_port}/{postgres_db}"
                )

                # Настройки connection pool
                pool_size = int(os.getenv("SQLALCHEMY_POOL_SIZE", "5"))
                max_overflow = int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "10"))
                pool_timeout = int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30"))

                self.sqlalchemy_engine = create_engine(
                    database_url,
                    poolclass=pool.QueuePool,
                    pool_size=pool_size,
                    max_overflow=max_overflow,
                    pool_timeout=pool_timeout,
                    pool_pre_ping=True,  # Проверка соединений перед использованием
                    echo=False,
                )

                self.sqlalchemy_session = sessionmaker(bind=self.sqlalchemy_engine)

                logger.info(
                    f"SQLAlchemy engine создан с пулом: "
                    f"size={pool_size}, max_overflow={max_overflow}"
                )
        except Exception as e:
            logger.warning(f"Не удалось создать SQLAlchemy engine: {e}")

    @contextmanager
    def get_postgres_connection(self):
        """
        Получение соединения PostgreSQL из пула

        Yields:
            PostgreSQL соединение
        """
        if not self.postgres_pool:
            raise RuntimeError("PostgreSQL пул не инициализирован")

        conn = None
        try:
            conn = self.postgres_pool.getconn()
            yield conn
        finally:
            if conn:
                self.postgres_pool.putconn(conn)

    @contextmanager
    def get_sqlalchemy_session(self):
        """
        Получение SQLAlchemy сессии

        Yields:
            SQLAlchemy сессия
        """
        if not self.sqlalchemy_session:
            raise RuntimeError("SQLAlchemy не инициализирован")

        session = self.sqlalchemy_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_pool_stats(self) -> dict:
        """
        Получение статистики пула соединений

        Returns:
            Словарь со статистикой
        """
        stats = {"postgres_pool": None, "sqlalchemy_pool": None}

        if self.postgres_pool:
            stats["postgres_pool"] = {
                "minconn": self.postgres_pool.minconn,
                "maxconn": self.postgres_pool.maxconn,
                "closed": self.postgres_pool.closed,
            }

        if self.sqlalchemy_engine:
            pool = self.sqlalchemy_engine.pool
            stats["sqlalchemy_pool"] = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
            }

        return stats

    def close(self):
        """Закрытие всех пулов соединений"""
        if self.postgres_pool:
            self.postgres_pool.closeall()
            logger.info("PostgreSQL пул закрыт")

        if self.sqlalchemy_engine:
            self.sqlalchemy_engine.dispose()
            logger.info("SQLAlchemy engine закрыт")


# Глобальный экземпляр пула
_db_pool_instance: Optional[DatabaseConnectionPool] = None


def get_db_pool() -> DatabaseConnectionPool:
    """
    Получение глобального экземпляра пула соединений

    Returns:
        Экземпляр DatabaseConnectionPool
    """
    global _db_pool_instance

    if _db_pool_instance is None:
        _db_pool_instance = DatabaseConnectionPool()

    return _db_pool_instance
