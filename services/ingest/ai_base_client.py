"""
Базовый абстрактный класс для всех AI-клиентов
Поддерживает как внешние API, так и локальные модели
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class BaseAIClient(ABC):
    """
    Абстрактный базовый класс для всех AI-клиентов
    Обеспечивает единый интерфейс для внешних API и локальных моделей
    """

    def __init__(self, provider_name: str):
        """
        Инициализация базового клиента

        Args:
            provider_name: Имя провайдера (openai, anthropic, deepseek, local)
        """
        self.provider_name = provider_name
        self.enabled = False

    @abstractmethod
    def process_prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.2,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Основной метод обработки промптов

        Args:
            prompt: Текст промпта
            system_message: Системное сообщение (опционально)
            max_tokens: Максимальное количество токенов
            temperature: Температура генерации
            response_format: Формат ответа (например, JSON)
            **kwargs: Дополнительные параметры

        Returns:
            Словарь с результатом:
            {
                "text": str,  # Текст ответа
                "usage": dict,  # Метрики использования
                "model": str,  # Модель, которая использовалась
                "provider": str  # Провайдер
            }
        """
        pass

    @abstractmethod
    def process_vision_prompt(
        self,
        images: List[str],  # base64 encoded images
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Обработка промптов с изображениями (Vision API)

        Args:
            images: Список base64-encoded изображений
            prompt: Текст промпта
            system_message: Системное сообщение
            max_tokens: Максимальное количество токенов
            **kwargs: Дополнительные параметры

        Returns:
            Словарь с результатом (аналогично process_prompt)
        """
        pass

    @abstractmethod
    def get_usage_metrics(self) -> Dict[str, Any]:
        """
        Метрики использования (для мониторинга)

        Returns:
            Словарь с метриками:
            {
                "total_requests": int,
                "total_tokens": int,
                "total_cost": float,  # Для API провайдеров
                "average_response_time": float,
                "errors_count": int
            }
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Проверка доступности провайдера

        Returns:
            True если провайдер доступен и готов к использованию
        """
        pass

    def get_provider_name(self) -> str:
        """Возвращает имя провайдера"""
        return self.provider_name

    def reset_metrics(self):
        """Сброс метрик использования (опционально)"""
        pass
