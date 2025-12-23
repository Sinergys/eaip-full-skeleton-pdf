"""
Единый модуль конфигурации AI для всего приложения.

Централизованное управление настройками AI:
- Проверка включения AI
- Выбор провайдера
- Проверка наличия API ключей
- Безопасная загрузка конфигурации
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# === КРИТИЧНО: ЗАГРУЗКА .ENV ДО СОЗДАНИЯ SINGLETON ===
try:
    from dotenv import load_dotenv
    # .env находится в той же директории, что и main.py (services/ingest/)
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)  # Не перезаписывать существующие
        logging.getLogger(__name__).debug(f"✅ .env загружен из: {env_path}")
except ImportError:
    # python-dotenv не установлен - используем только системные переменные
    pass
# === КОНЕЦ ЗАГРУЗКИ .ENV ===

logger = logging.getLogger(__name__)

# Поддерживаемые провайдеры
SUPPORTED_PROVIDERS = ["deepseek", "openai", "anthropic"]

# Названия переменных окружения для API ключей по провайдерам
PROVIDER_API_KEY_VARS = {
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}

# Названия переменных окружения для моделей по провайдерам
PROVIDER_MODEL_VARS = {
    "deepseek": "DEEPSEEK_MODEL",
    "openai": {
        "text": "OPENAI_MODEL_TEXT",
        "vision": "OPENAI_MODEL_VISION",
    },
    "anthropic": "ANTHROPIC_MODEL",
}


class AISettings:
    """
    Единый класс для управления настройками AI.
    Все проверки и загрузка конфигурации в одном месте.
    """

    def __init__(self):
        """Инициализация настроек AI из переменных окружения"""
        self._enabled = self._load_enabled()
        self._provider = self._load_provider()
        self._api_key = self._load_api_key()
        self._has_valid_config = self._check_valid_config()

    def _load_enabled(self) -> bool:
        """Загрузить флаг включения AI"""
        value = os.getenv("AI_ENABLED", "false").lower().strip()
        # Поддерживаем различные варианты: "true", "1", "yes", "on"
        return value in ("true", "1", "yes", "on")

    def _load_provider(self) -> str:
        """Загрузить провайдера AI"""
        provider = os.getenv("AI_PROVIDER", "deepseek").lower().strip()
        # Валидация провайдера
        if provider not in SUPPORTED_PROVIDERS:
            logger.warning(
                f"Неподдерживаемый провайдер '{provider}'. "
                f"Поддерживаются: {', '.join(SUPPORTED_PROVIDERS)}. "
                f"Используется 'deepseek' по умолчанию."
            )
            return "deepseek"
        return provider

    def _load_api_key(self) -> Optional[str]:
        """Загрузить API ключ для текущего провайдера"""
        key_var = PROVIDER_API_KEY_VARS.get(self._provider)
        if not key_var:
            return None

        # Прямая загрузка из переменной окружения
        api_key = os.getenv(key_var)

        # Fallback: для разработки можно загрузить из тестового файла
        # (только если не установлено в env и только для deepseek)
        if not api_key and self._provider == "deepseek":
            api_key = self._try_load_from_test_file()

        return api_key

    def _try_load_from_test_file(self) -> Optional[str]:
        """
        Попытка загрузить API ключ из тестового файла (только для разработки).
        Это fallback для локальной разработки, не используется в продакшене.
        """
        try:
            # Ищем корень проекта eaip_full_skeleton
            current_file = Path(__file__).resolve()
            # settings/ai_settings.py -> ingest -> services -> eaip_full_skeleton
            project_root = current_file.parent.parent.parent.parent
            test_file = project_root / "test_deepseek_simple.py"

            if test_file.exists():
                import re

                content = test_file.read_text(encoding="utf-8")
                match = re.search(
                    r'DEEPSEEK_API_KEY\s*=\s*["\']([^"\']+)["\']', content
                )
                if match:
                    logger.debug(
                        "Используется API ключ из test_deepseek_simple.py (fallback для разработки)"
                    )
                    return match.group(1)
        except Exception as e:
            logger.debug(f"Не удалось загрузить ключ из тестового файла: {e}")

        return None

    def _check_valid_config(self) -> bool:
        """Проверить, что конфигурация валидна (AI включен и есть API ключ)"""
        if not self._enabled:
            return False

        if not self._api_key:
            logger.warning(
                f"AI включен, но API ключ для провайдера '{self._provider}' не найден. "
                f"Установите переменную {PROVIDER_API_KEY_VARS.get(self._provider, 'UNKNOWN')}"
            )
            return False

        return True

    @property
    def enabled(self) -> bool:
        """AI включен?"""
        return self._enabled

    @property
    def provider(self) -> str:
        """Текущий провайдер AI"""
        return self._provider

    @property
    def api_key(self) -> Optional[str]:
        """API ключ для текущего провайдера"""
        return self._api_key

    @property
    def has_valid_config(self) -> bool:
        """Есть ли валидная конфигурация (AI включен + API ключ)"""
        return self._has_valid_config

    def get_api_key_for_provider(self, provider: str) -> Optional[str]:
        """Получить API ключ для указанного провайдера"""
        key_var = PROVIDER_API_KEY_VARS.get(provider.lower())
        if not key_var:
            return None
        return os.getenv(key_var)

    def get_model_config(self) -> Dict[str, str]:
        """Получить конфигурацию моделей для текущего провайдера"""
        if self._provider == "openai":
            return {
                "text": os.getenv("OPENAI_MODEL_TEXT", "gpt-4"),
                "vision": os.getenv("OPENAI_MODEL_VISION", "gpt-4-vision-preview"),
            }
        elif self._provider == "anthropic":
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            return {
                "text": model,
                "vision": model,
            }
        elif self._provider == "deepseek":
            model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            return {
                "text": model,
                "vision": model,
            }
        else:
            return {}

    def get_status_dict(self) -> Dict[str, Any]:
        """
        Получить словарь со статусом AI для API ответов.

        Returns:
            Словарь с полной информацией о статусе AI
        """
        return {
            "ai_enabled": self._enabled,
            "ai_provider": self._provider,
            "has_api_key": bool(self._api_key),
            "has_valid_config": self._has_valid_config,
            "message": self._get_status_message(),
        }

    def _get_status_message(self) -> str:
        """Получить текстовое сообщение о статусе"""
        if self._has_valid_config:
            return f"✅ AI настроен и готов к работе (провайдер: {self._provider})"
        elif self._enabled:
            key_var = PROVIDER_API_KEY_VARS.get(self._provider, "UNKNOWN")
            return f"⚠️ AI включен, но API ключ не найден. Установите {key_var}"
        else:
            return "⚠️ AI не настроен. Для извлечения формул и нормативов нужно настроить AI."


# Глобальный экземпляр настроек (singleton)
_ai_settings_instance: Optional[AISettings] = None


def get_ai_settings() -> AISettings:
    """
    Получить экземпляр настроек AI (singleton).

    Returns:
        Экземпляр AISettings
    """
    global _ai_settings_instance
    if _ai_settings_instance is None:
        _ai_settings_instance = AISettings()
    return _ai_settings_instance


# Удобные функции для быстрого доступа
def is_ai_enabled() -> bool:
    """Проверить, включен ли AI"""
    return get_ai_settings().enabled


def get_ai_provider() -> str:
    """Получить текущего провайдера AI"""
    return get_ai_settings().provider


def has_ai_config() -> bool:
    """Проверить, есть ли валидная конфигурация AI"""
    return get_ai_settings().has_valid_config


def get_ai_status() -> Dict[str, Any]:
    """Получить статус AI для API"""
    return get_ai_settings().get_status_dict()
