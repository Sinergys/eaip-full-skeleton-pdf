"""
Обертки для внешних API-клиентов (OpenAI, Anthropic, DeepSeek)
Наследуются от BaseAIClient для единого интерфейса
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from ai_base_client import BaseAIClient

logger = logging.getLogger(__name__)

# Проверка доступности библиотек
HAS_OPENAI = False
try:
    from openai import OpenAI

    HAS_OPENAI = True
except ImportError:
    logger.debug("openai библиотека не установлена")

HAS_ANTHROPIC = False
try:
    import anthropic

    HAS_ANTHROPIC = True
except ImportError:
    logger.debug("anthropic библиотека не установлена")


class OpenAIClient(BaseAIClient):
    """Клиент для OpenAI API"""

    def __init__(self, api_key: str):
        """
        Инициализация OpenAI клиента

        Args:
            api_key: API ключ OpenAI
        """
        super().__init__("openai")
        if not HAS_OPENAI:
            raise ImportError(
                "openai библиотека не установлена. Установите: pip install openai"
            )

        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.model_text = os.getenv("OPENAI_MODEL_TEXT", "gpt-4")
        self.model_vision = os.getenv("OPENAI_MODEL_VISION", "gpt-4-vision-preview")
        self.enabled = True

        self._usage_metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "average_response_time": 0.0,
            "errors_count": 0,
        }

    def process_prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.2,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Обработка промпта через OpenAI API"""
        if not self.enabled:
            raise RuntimeError("OpenAI клиент не инициализирован")

        try:
            start_time = time.time()

            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format=response_format,
                **kwargs,
            )

            response_time = time.time() - start_time
            result_text = response.choices[0].message.content.strip()
            usage = response.usage

            # Обновление метрик
            self._update_metrics(usage, response_time)

            return {
                "text": result_text,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
                "model": self.model_text,
                "provider": "openai",
            }

        except Exception as e:
            self._usage_metrics["errors_count"] += 1
            logger.error(f"Ошибка при обработке промпта через OpenAI: {e}")
            raise

    def process_vision_prompt(
        self,
        images: List[str],
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Обработка промпта с изображениями через OpenAI Vision API"""
        if not self.enabled:
            raise RuntimeError("OpenAI клиент не инициализирован")

        try:
            start_time = time.time()

            content = []
            if system_message:
                content.append({"type": "text", "text": system_message})

            content.append({"type": "text", "text": prompt})

            for img_base64 in images:
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_base64}"},
                    }
                )

            response = self.client.chat.completions.create(
                model=self.model_vision,
                messages=[{"role": "user", "content": content}],
                max_tokens=max_tokens,
                **kwargs,
            )

            response_time = time.time() - start_time
            result_text = response.choices[0].message.content.strip()
            usage = response.usage

            self._update_metrics(usage, response_time)

            return {
                "text": result_text,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
                "model": self.model_vision,
                "provider": "openai",
            }

        except Exception as e:
            self._usage_metrics["errors_count"] += 1
            logger.error(f"Ошибка при обработке vision промпта через OpenAI: {e}")
            raise

    def get_usage_metrics(self) -> Dict[str, Any]:
        """Возвращает метрики использования"""
        return {**self._usage_metrics, "type": "api", "provider": "openai"}

    def is_available(self) -> bool:
        """Проверка доступности OpenAI API"""
        return self.enabled and self.client is not None

    def _update_metrics(self, usage, response_time: float):
        """Обновляет метрики использования"""
        self._usage_metrics["total_requests"] += 1
        self._usage_metrics["total_tokens"] += usage.total_tokens

        # Примерная стоимость (зависит от модели)
        # GPT-4: ~$0.03/1K prompt tokens, ~$0.06/1K completion tokens
        cost_per_1k_prompt = 0.03
        cost_per_1k_completion = 0.06
        cost = (
            usage.prompt_tokens / 1000 * cost_per_1k_prompt
            + usage.completion_tokens / 1000 * cost_per_1k_completion
        )
        self._usage_metrics["total_cost"] += cost

        # Обновление среднего времени ответа
        n = self._usage_metrics["total_requests"]
        current_avg = self._usage_metrics["average_response_time"]
        self._usage_metrics["average_response_time"] = (
            current_avg * (n - 1) + response_time
        ) / n


class AnthropicClient(BaseAIClient):
    """Клиент для Anthropic (Claude) API"""

    def __init__(self, api_key: str):
        """
        Инициализация Anthropic клиента

        Args:
            api_key: API ключ Anthropic
        """
        super().__init__("anthropic")
        if not HAS_ANTHROPIC:
            raise ImportError(
                "anthropic библиотека не установлена. Установите: pip install anthropic"
            )

        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_text = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.model_vision = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.enabled = True

        self._usage_metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "average_response_time": 0.0,
            "errors_count": 0,
        }

    def process_prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.2,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Обработка промпта через Anthropic API"""
        if not self.enabled:
            raise RuntimeError("Anthropic клиент не инициализирован")

        try:
            start_time = time.time()

            messages = [{"role": "user", "content": prompt}]

            response = self.client.messages.create(
                model=self.model_text,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=messages,
                **kwargs,
            )

            response_time = time.time() - start_time
            result_text = response.content[0].text.strip()
            usage = response.usage

            self._update_metrics(usage, response_time)

            return {
                "text": result_text,
                "usage": {
                    "prompt_tokens": usage.input_tokens,
                    "completion_tokens": usage.output_tokens,
                    "total_tokens": usage.input_tokens + usage.output_tokens,
                },
                "model": self.model_text,
                "provider": "anthropic",
            }

        except Exception as e:
            self._usage_metrics["errors_count"] += 1
            logger.error(f"Ошибка при обработке промпта через Anthropic: {e}")
            raise

    def process_vision_prompt(
        self,
        images: List[str],
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Обработка промпта с изображениями через Anthropic API"""
        if not self.enabled:
            raise RuntimeError("Anthropic клиент не инициализирован")

        try:
            start_time = time.time()

            content = []
            for img_base64 in images:
                content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_base64,
                        },
                    }
                )
            content.append({"type": "text", "text": prompt})

            response = self.client.messages.create(
                model=self.model_vision,
                max_tokens=max_tokens,
                system=system_message,
                messages=[{"role": "user", "content": content}],
                **kwargs,
            )

            response_time = time.time() - start_time
            result_text = response.content[0].text.strip()
            usage = response.usage

            self._update_metrics(usage, response_time)

            return {
                "text": result_text,
                "usage": {
                    "prompt_tokens": usage.input_tokens,
                    "completion_tokens": usage.output_tokens,
                    "total_tokens": usage.input_tokens + usage.output_tokens,
                },
                "model": self.model_vision,
                "provider": "anthropic",
            }

        except Exception as e:
            self._usage_metrics["errors_count"] += 1
            logger.error(f"Ошибка при обработке vision промпта через Anthropic: {e}")
            raise

    def get_usage_metrics(self) -> Dict[str, Any]:
        """Возвращает метрики использования"""
        return {**self._usage_metrics, "type": "api", "provider": "anthropic"}

    def is_available(self) -> bool:
        """Проверка доступности Anthropic API"""
        return self.enabled and self.client is not None

    def _update_metrics(self, usage, response_time: float):
        """Обновляет метрики использования"""
        self._usage_metrics["total_requests"] += 1
        total_tokens = usage.input_tokens + usage.output_tokens
        self._usage_metrics["total_tokens"] += total_tokens

        # Примерная стоимость Claude (зависит от модели)
        # Claude 3 Opus: ~$0.015/1K input tokens, ~$0.075/1K output tokens
        cost_per_1k_input = 0.015
        cost_per_1k_output = 0.075
        cost = (
            usage.input_tokens / 1000 * cost_per_1k_input
            + usage.output_tokens / 1000 * cost_per_1k_output
        )
        self._usage_metrics["total_cost"] += cost

        n = self._usage_metrics["total_requests"]
        current_avg = self._usage_metrics["average_response_time"]
        self._usage_metrics["average_response_time"] = (
            current_avg * (n - 1) + response_time
        ) / n


class DeepSeekClient(BaseAIClient):
    """Клиент для DeepSeek API (OpenAI-совместимый)"""

    def __init__(self, api_key: str):
        """
        Инициализация DeepSeek клиента

        Args:
            api_key: API ключ DeepSeek
        """
        super().__init__("deepseek")
        if not HAS_OPENAI:
            raise ImportError(
                "openai библиотека не установлена. Установите: pip install openai"
            )

        self.api_key = api_key
        try:
            self.client = OpenAI(
                api_key=api_key, base_url="https://api.deepseek.com", timeout=60.0
            )
        except TypeError:
            # Fallback для старых версий openai
            self.client = OpenAI(api_key=api_key, timeout=60.0)
            if hasattr(self.client, "_client") and hasattr(
                self.client._client, "base_url"
            ):
                self.client._client.base_url = "https://api.deepseek.com"

        self.model_text = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.model_vision = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.enabled = True

        self._usage_metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,  # DeepSeek обычно дешевле
            "average_response_time": 0.0,
            "errors_count": 0,
        }

    def process_prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.2,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Обработка промпта через DeepSeek API"""
        if not self.enabled:
            raise RuntimeError("DeepSeek клиент не инициализирован")

        try:
            start_time = time.time()

            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            response_time = time.time() - start_time
            result_text = response.choices[0].message.content.strip()
            usage = response.usage

            self._update_metrics(usage, response_time)

            return {
                "text": result_text,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
                "model": self.model_text,
                "provider": "deepseek",
            }

        except Exception as e:
            self._usage_metrics["errors_count"] += 1
            logger.error(f"Ошибка при обработке промпта через DeepSeek: {e}")
            raise

    def process_vision_prompt(
        self,
        images: List[str],
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 4000,
        **kwargs,
    ) -> Dict[str, Any]:
        """Обработка промпта с изображениями (DeepSeek может не поддерживать vision)"""
        # DeepSeek может не поддерживать vision, используем текстовую модель
        logger.warning(
            "DeepSeek может не поддерживать vision API, используем текстовую модель"
        )
        return self.process_prompt(prompt, system_message, max_tokens, **kwargs)

    def get_usage_metrics(self) -> Dict[str, Any]:
        """Возвращает метрики использования"""
        return {**self._usage_metrics, "type": "api", "provider": "deepseek"}

    def is_available(self) -> bool:
        """Проверка доступности DeepSeek API"""
        return self.enabled and self.client is not None

    def _update_metrics(self, usage, response_time: float):
        """Обновляет метрики использования"""
        self._usage_metrics["total_requests"] += 1
        self._usage_metrics["total_tokens"] += usage.total_tokens

        # DeepSeek обычно дешевле (примерные цены)
        cost_per_1k_tokens = 0.001  # Примерная стоимость
        cost = usage.total_tokens / 1000 * cost_per_1k_tokens
        self._usage_metrics["total_cost"] += cost

        n = self._usage_metrics["total_requests"]
        current_avg = self._usage_metrics["average_response_time"]
        self._usage_metrics["average_response_time"] = (
            current_avg * (n - 1) + response_time
        ) / n
