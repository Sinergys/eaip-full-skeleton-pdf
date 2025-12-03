"""
Модуль кэширования AI-запросов для оптимизации производительности
"""

import hashlib
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

# Попытка использовать Redis если доступен
try:
    import redis

    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logger.warning("Redis не установлен, используется in-memory кэш")


class AICache:
    """
    Класс для кэширования AI-запросов
    Поддерживает Redis и in-memory кэш
    """

    def __init__(self, ttl_seconds: int = 3600):
        """
        Инициализация кэша

        Args:
            ttl_seconds: Время жизни кэша в секундах (по умолчанию 1 час)
        """
        self.ttl_seconds = ttl_seconds
        self.redis_client = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}

        # Попытка подключиться к Redis
        if HAS_REDIS:
            try:
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = int(os.getenv("REDIS_PORT", "6379"))
                redis_password = os.getenv("REDIS_PASSWORD")

                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                )
                # Проверка подключения
                self.redis_client.ping()
                logger.info("Redis кэш подключен")
            except Exception as e:
                logger.warning(
                    f"Не удалось подключиться к Redis: {e}, используется in-memory кэш"
                )
                self.redis_client = None

    def _generate_cache_key(self, prompt: str, **kwargs) -> str:
        """
        Генерация ключа кэша на основе промпта и параметров

        Args:
            prompt: Текст промпта
            **kwargs: Дополнительные параметры

        Returns:
            Хеш-ключ для кэша
        """
        # Создаем строку для хеширования
        cache_data = {"prompt": prompt, **kwargs}
        cache_string = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        cache_hash = hashlib.sha256(cache_string.encode("utf-8")).hexdigest()
        return f"ai_cache:{cache_hash}"

    def get(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Получение результата из кэша

        Args:
            prompt: Текст промпта
            **kwargs: Дополнительные параметры

        Returns:
            Результат из кэша или None
        """
        cache_key = self._generate_cache_key(prompt, **kwargs)

        try:
            if self.redis_client:
                # Получаем из Redis
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    result = json.loads(cached_data)
                    logger.debug(f"Кэш попадание (Redis): {cache_key[:16]}...")
                    return result
            else:
                # Получаем из памяти
                if cache_key in self.memory_cache:
                    cached_entry = self.memory_cache[cache_key]
                    # Проверяем TTL
                    if datetime.now() < cached_entry["expires_at"]:
                        logger.debug(f"Кэш попадание (memory): {cache_key[:16]}...")
                        return cached_entry["data"]
                    else:
                        # Удаляем истекший кэш
                        del self.memory_cache[cache_key]
        except Exception as e:
            logger.error(f"Ошибка при получении из кэша: {e}")

        return None

    def set(self, prompt: str, result: Dict[str, Any], **kwargs) -> bool:
        """
        Сохранение результата в кэш

        Args:
            prompt: Текст промпта
            result: Результат для кэширования
            **kwargs: Дополнительные параметры

        Returns:
            True если успешно сохранено
        """
        cache_key = self._generate_cache_key(prompt, **kwargs)

        try:
            if self.redis_client:
                # Сохраняем в Redis
                cache_data = json.dumps(result, ensure_ascii=False)
                self.redis_client.setex(cache_key, self.ttl_seconds, cache_data)
                logger.debug(f"Кэш сохранен (Redis): {cache_key[:16]}...")
            else:
                # Сохраняем в память
                self.memory_cache[cache_key] = {
                    "data": result,
                    "expires_at": datetime.now() + timedelta(seconds=self.ttl_seconds),
                }
                logger.debug(f"Кэш сохранен (memory): {cache_key[:16]}...")

            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении в кэш: {e}")
            return False

    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Очистка кэша

        Args:
            pattern: Паттерн для очистки (опционально)

        Returns:
            Количество удаленных записей
        """
        count = 0

        try:
            if self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        count = self.redis_client.delete(*keys)
                else:
                    # Очищаем все ключи кэша
                    keys = self.redis_client.keys("ai_cache:*")
                    if keys:
                        count = self.redis_client.delete(*keys)
            else:
                if pattern:
                    # Фильтруем по паттерну
                    keys_to_delete = [
                        key for key in self.memory_cache.keys() if pattern in key
                    ]
                    for key in keys_to_delete:
                        del self.memory_cache[key]
                        count += 1
                else:
                    count = len(self.memory_cache)
                    self.memory_cache.clear()

            logger.info(f"Очищено записей кэша: {count}")
        except Exception as e:
            logger.error(f"Ошибка при очистке кэша: {e}")

        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Получение статистики кэша

        Returns:
            Словарь со статистикой
        """
        stats = {
            "backend": "redis" if self.redis_client else "memory",
            "ttl_seconds": self.ttl_seconds,
        }

        try:
            if self.redis_client:
                keys = self.redis_client.keys("ai_cache:*")
                stats["total_entries"] = len(keys)
            else:
                stats["total_entries"] = len(self.memory_cache)
                # Подсчитываем истекшие записи
                now = datetime.now()
                expired = sum(
                    1
                    for entry in self.memory_cache.values()
                    if entry["expires_at"] < now
                )
                stats["expired_entries"] = expired
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            stats["error"] = str(e)

        return stats


# Глобальный экземпляр кэша
_ai_cache_instance: Optional[AICache] = None


def get_ai_cache() -> AICache:
    """
    Получение глобального экземпляра кэша

    Returns:
        Экземпляр AICache
    """
    global _ai_cache_instance

    if _ai_cache_instance is None:
        ttl = int(os.getenv("AI_CACHE_TTL_SECONDS", "3600"))
        _ai_cache_instance = AICache(ttl_seconds=ttl)

    return _ai_cache_instance
