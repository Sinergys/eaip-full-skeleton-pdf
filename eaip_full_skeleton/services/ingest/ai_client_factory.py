"""
Фабрика для создания AI-клиентов
Поддерживает автоматический выбор провайдера и создание клиентов
"""

import os
import logging
from typing import Optional
from ai_base_client import BaseAIClient

logger = logging.getLogger(__name__)


class AIClientFactory:
    """
    Фабрика для создания AI-клиентов
    Поддерживает внешние API и локальные модели
    """

    @staticmethod
    def create_client(client_type: str = "auto", **kwargs) -> Optional[BaseAIClient]:
        """
        Создает AI-клиент указанного типа

        Args:
            client_type: Тип клиента:
                - 'auto': автоматический выбор (сначала локальный, потом API)
                - 'local': локальная модель
                - 'openai': OpenAI API
                - 'anthropic': Anthropic API
                - 'deepseek': DeepSeek API
            **kwargs: Параметры для инициализации клиента

        Returns:
            Экземпляр BaseAIClient или None если не удалось создать
        """
        try:
            if client_type == "auto":
                return AIClientFactory._create_auto_client(**kwargs)
            elif client_type == "local":
                return AIClientFactory._create_local_client(**kwargs)
            elif client_type == "openai":
                return AIClientFactory._create_openai_client(**kwargs)
            elif client_type == "anthropic":
                return AIClientFactory._create_anthropic_client(**kwargs)
            elif client_type == "deepseek":
                return AIClientFactory._create_deepseek_client(**kwargs)
            else:
                logger.warning(f"Неизвестный тип клиента: {client_type}")
                return None
        except Exception as e:
            logger.error(f"Ошибка при создании AI-клиента типа {client_type}: {e}")
            return None

    @staticmethod
    def _create_auto_client(**kwargs) -> Optional[BaseAIClient]:
        """
        Автоматический выбор клиента:
        1. Проверяет доступность локальной модели
        2. Если недоступна - использует внешний API
        """
        # Сначала проверяем локальную модель
        try:
            from ai_local_client import LocalAIClient

            local_client = LocalAIClient(kwargs.get("model_path"))
            if local_client.is_available():
                logger.info("Используется локальная AI-модель")
                return local_client
        except ImportError:
            logger.debug("Локальный AI-клиент недоступен")
        except Exception as e:
            logger.debug(f"Локальная модель недоступна: {e}")

        # Fallback на внешний API
        fallback_to_api = kwargs.get("fallback_to_api", True)
        if fallback_to_api:
            # Определяем провайдер из переменных окружения
            provider = os.getenv("AI_PROVIDER", "deepseek").lower()
            if provider == "openai":
                return AIClientFactory._create_openai_client(**kwargs)
            elif provider == "anthropic":
                return AIClientFactory._create_anthropic_client(**kwargs)
            elif provider == "deepseek":
                return AIClientFactory._create_deepseek_client(**kwargs)

        logger.warning("Не удалось создать AI-клиент (ни локальный, ни API)")
        return None

    @staticmethod
    def _create_local_client(**kwargs) -> Optional[BaseAIClient]:
        """Создает локальный AI-клиент"""
        try:
            from ai_local_client import LocalAIClient

            model_path = kwargs.get("model_path") or os.getenv("LOCAL_AI_MODEL_PATH")
            local_client = LocalAIClient(model_path)

            # Пытаемся загрузить модель
            if not local_client.is_loaded:
                local_client.load_model()

            return local_client if local_client.is_available() else None
        except ImportError:
            logger.warning("Локальный AI-клиент не установлен")
            return None
        except Exception as e:
            logger.error(f"Ошибка при создании локального клиента: {e}")
            return None

    @staticmethod
    def _create_openai_client(**kwargs) -> Optional[BaseAIClient]:
        """Создает OpenAI API клиент"""
        try:
            from ai_api_clients import OpenAIClient

            api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY не установлен")
                return None
            return OpenAIClient(api_key)
        except ImportError:
            logger.warning("OpenAI клиент не установлен")
            return None
        except Exception as e:
            logger.error(f"Ошибка при создании OpenAI клиента: {e}")
            return None

    @staticmethod
    def _create_anthropic_client(**kwargs) -> Optional[BaseAIClient]:
        """Создает Anthropic API клиент"""
        try:
            from ai_api_clients import AnthropicClient

            api_key = kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY не установлен")
                return None
            return AnthropicClient(api_key)
        except ImportError:
            logger.warning("Anthropic клиент не установлен")
            return None
        except Exception as e:
            logger.error(f"Ошибка при создании Anthropic клиента: {e}")
            return None

    @staticmethod
    def _create_deepseek_client(**kwargs) -> Optional[BaseAIClient]:
        """Создает DeepSeek API клиент"""
        try:
            from ai_api_clients import DeepSeekClient

            api_key = kwargs.get("api_key") or os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                logger.warning("DEEPSEEK_API_KEY не установлен")
                return None
            return DeepSeekClient(api_key)
        except ImportError:
            logger.warning("DeepSeek клиент не установлен")
            return None
        except Exception as e:
            logger.error(f"Ошибка при создании DeepSeek клиента: {e}")
            return None

    @staticmethod
    def get_default_client() -> Optional[BaseAIClient]:
        """
        Получает клиент по умолчанию на основе конфигурации

        Returns:
            Экземпляр BaseAIClient или None
        """
        preferred_provider = os.getenv("AI_PREFERRED_PROVIDER", "auto")
        return AIClientFactory.create_client(client_type=preferred_provider)
