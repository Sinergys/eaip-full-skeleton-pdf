"""
AIProcessor - Интеграция с AI сервисами (Ollama + DeepSeek).
Соответствует разделу 3.1.5 ТЗ.

Основные задачи:
- Интеграция с Ollama (локальная AI) для предварительного анализа
- Интеграция с DeepSeek API для основной корректировки
- Retry механизм с exponential backoff
- Парсинг ответов с валидацией формата
"""
import httpx
import json
import asyncio
import logging
import re
from typing import Dict, Any, Optional

from core.config import Settings
from core.models import OllamaAnalysisResult, DeepSeekCorrectionResult
from core.constants import (
    START_CORRECTED_TEXT,
    END_CORRECTED_TEXT,
    START_RECOMMENDATIONS,
    END_RECOMMENDATIONS
)
from utils.prompts import create_ollama_prompt, create_deepseek_prompt
from utils.exceptions import (
    OllamaError,
    DeepSeekError,
    DeepSeekFormatError,
    DeepSeekTimeoutError
)

logger = logging.getLogger(__name__)


class AIProcessor:
    """
    Процессор для работы с AI сервисами (Ollama + DeepSeek).
    Соответствует разделу 3.1.5 ТЗ.
    """

    def __init__(
        self,
        ollama_url: str,
        deepseek_api_key: str,
        deepseek_url: str,
        ollama_model: str = "mistral:7b",
        deepseek_model: str = "deepseek-chat",
        deepseek_max_tokens: int = 4000,
        ollama_timeout: int = 300,
        deepseek_timeout: int = 300
    ):
        """
        Инициализация AI процессора.

        Args:
            ollama_url: URL Ollama сервера
            deepseek_api_key: API ключ DeepSeek
            deepseek_url: URL DeepSeek API
            ollama_model: Модель Ollama (по умолчанию mistral:7b)
            deepseek_model: Модель DeepSeek (по умолчанию deepseek-chat)
            deepseek_max_tokens: Максимум токенов для DeepSeek ответа
            ollama_timeout: Timeout для Ollama (секунды)
            deepseek_timeout: Timeout для DeepSeek (секунды)
        """
        self.ollama_url = ollama_url
        self.deepseek_api_key = deepseek_api_key
        self.deepseek_url = deepseek_url
        self.ollama_model = ollama_model
        self.deepseek_model = deepseek_model
        self.deepseek_max_tokens = deepseek_max_tokens
        self.ollama_timeout = ollama_timeout
        self.deepseek_timeout = deepseek_timeout

        # HTTP клиент с таймаутом
        self.client = httpx.AsyncClient(timeout=max(ollama_timeout, deepseek_timeout))

        logger.info(f"AIProcessor initialized: Ollama={ollama_url}, DeepSeek={deepseek_url}")

    async def analyze_with_ollama(
        self,
        chunk_text: str
    ) -> OllamaAnalysisResult:
        """
        Анализ текста через Ollama (предварительная проверка).

        Args:
            chunk_text: Текст чанка для анализа

        Returns:
            OllamaAnalysisResult с issues и fixes

        Raises:
            OllamaError: При ошибках Ollama
        """
        try:
            logger.info(f"Starting Ollama analysis (text length: {len(chunk_text)} chars)")

            # Создать промпт
            prompt = create_ollama_prompt(chunk_text)

            # Подготовить запрос к Ollama
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "format": "json"  # Ollama должен вернуть JSON
            }

            # Отправить POST запрос
            url = f"{self.ollama_url}/api/generate"

            try:
                response = await self.client.post(
                    url,
                    json=payload,
                    timeout=self.ollama_timeout
                )
                response.raise_for_status()

            except httpx.TimeoutException as e:
                raise OllamaError(f"Ollama timeout after {self.ollama_timeout}s: {str(e)}")
            except httpx.HTTPStatusError as e:
                raise OllamaError(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                raise OllamaError(f"Ollama request failed: {str(e)}")

            # Парсинг ответа
            try:
                response_data = response.json()
                response_text = response_data.get('response', '')

                # Парсинг JSON из ответа
                analysis_data = json.loads(response_text)

                # Валидация структуры
                if not isinstance(analysis_data, dict):
                    raise OllamaError(f"Ollama response is not a dict: {type(analysis_data)}")

                issues = analysis_data.get('issues', [])
                fixes = analysis_data.get('fixes', [])

                # Ensure lists
                if not isinstance(issues, list):
                    issues = []
                if not isinstance(fixes, list):
                    fixes = []

                result = OllamaAnalysisResult(
                    issues=issues,
                    fixes=fixes,
                    metadata={
                        'model': self.ollama_model,
                        'chunk_length': len(chunk_text)
                    }
                )

                logger.info(f"Ollama analysis complete: {len(issues)} issues, {len(fixes)} fixes")
                return result

            except json.JSONDecodeError as e:
                raise OllamaError(f"Failed to parse Ollama JSON response: {str(e)}")

        except OllamaError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Ollama analysis: {str(e)}", exc_info=True)
            raise OllamaError(f"Ollama analysis failed: {str(e)}")

    async def analyze_with_deepseek(
        self,
        chunk: str,
        ollama_report: OllamaAnalysisResult,
        pkm_requirements: str,
        chunk_index: int = 0
    ) -> DeepSeekCorrectionResult:
        """
        Корректировка текста через DeepSeek API.

        Args:
            chunk: Текст чанка с маркерами
            ollama_report: Результат анализа Ollama
            pkm_requirements: Требования ПКМ 690
            chunk_index: Индекс чанка для результата

        Returns:
            DeepSeekCorrectionResult с исправленным текстом

        Raises:
            DeepSeekError: При ошибках API
            DeepSeekFormatError: При неверном формате ответа
            DeepSeekTimeoutError: При timeout
        """
        try:
            logger.info(f"Starting DeepSeek correction for chunk {chunk_index}")

            # Создать промпт
            prompt = create_deepseek_prompt(
                chunk_text=chunk,
                pkm_requirements=pkm_requirements,
                ollama_report={
                    'issues': ollama_report.issues,
                    'fixes': ollama_report.fixes
                }
            )

            # Retry с exponential backoff
            response_text = await self._retry_with_backoff(
                lambda: self._call_deepseek_api(prompt)
            )

            # Парсинг ответа
            corrected_text, recommendations = self._parse_deepseek_response(response_text)

            result = DeepSeekCorrectionResult(
                corrected_text=corrected_text,
                recommendations=recommendations,
                chunk_index=chunk_index
            )

            logger.info(f"DeepSeek correction complete for chunk {chunk_index}: {len(recommendations)} recommendations")
            return result

        except (DeepSeekError, DeepSeekFormatError, DeepSeekTimeoutError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in DeepSeek correction: {str(e)}", exc_info=True)
            raise DeepSeekError(f"DeepSeek correction failed: {str(e)}")

    async def _call_deepseek_api(self, prompt: str) -> str:
        """
        Отправка запроса к DeepSeek API.

        Args:
            prompt: Промпт для DeepSeek

        Returns:
            str: Ответ от DeepSeek

        Raises:
            DeepSeekError: При ошибках API
            DeepSeekTimeoutError: При timeout
        """
        try:
            # Подготовить headers
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }

            # Подготовить payload
            payload = {
                "model": self.deepseek_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.deepseek_max_tokens,
                "temperature": 0.3  # Lower temperature для более консистентных результатов
            }

            # Отправить POST запрос
            response = await self.client.post(
                self.deepseek_url,
                json=payload,
                headers=headers,
                timeout=self.deepseek_timeout
            )
            response.raise_for_status()

            # Парсинг ответа
            response_data = response.json()

            # Извлечь текст из ответа
            if 'choices' not in response_data or len(response_data['choices']) == 0:
                raise DeepSeekError("DeepSeek response has no choices")

            message = response_data['choices'][0].get('message', {})
            content = message.get('content', '')

            if not content:
                raise DeepSeekError("DeepSeek response content is empty")

            return content

        except httpx.TimeoutException as e:
            raise DeepSeekTimeoutError(f"DeepSeek timeout after {self.deepseek_timeout}s")
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            raise DeepSeekError(f"DeepSeek HTTP error {e.response.status_code}: {error_detail}")
        except json.JSONDecodeError as e:
            raise DeepSeekError(f"Failed to parse DeepSeek JSON response: {str(e)}")

    async def _retry_with_backoff(
        self,
        func,
        max_retries: int = 2,
        initial_delay: float = 5.0
    ):
        """
        Retry decorator с exponential backoff.

        Args:
            func: Async функция для выполнения
            max_retries: Максимальное количество повторов
            initial_delay: Начальная задержка (секунды)

        Returns:
            Результат функции

        Raises:
            DeepSeekTimeoutError: После всех повторов при timeout
            DeepSeekError: После всех повторов при других ошибках
        """
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return await func()

            except DeepSeekTimeoutError as e:
                last_exception = e
                if attempt == max_retries:
                    logger.error(f"DeepSeek timeout after {max_retries} retries")
                    raise DeepSeekTimeoutError(f"Timeout after {max_retries} retries")

                delay = initial_delay * (2 ** attempt)  # 5s, 10s, 20s
                logger.warning(f"DeepSeek timeout, retry {attempt + 1}/{max_retries} after {delay}s")
                await asyncio.sleep(delay)

            except DeepSeekError as e:
                last_exception = e
                # Для некоторых ошибок не retry (например, 401 Unauthorized)
                if "401" in str(e) or "403" in str(e):
                    logger.error(f"DeepSeek authentication error, no retry: {str(e)}")
                    raise

                if attempt == max_retries:
                    logger.error(f"DeepSeek error after {max_retries} retries: {str(e)}")
                    raise

                delay = initial_delay * (2 ** attempt)
                logger.warning(f"DeepSeek error, retry {attempt + 1}/{max_retries} after {delay}s: {str(e)}")
                await asyncio.sleep(delay)

        # Fallback (should not reach here)
        if last_exception:
            raise last_exception

    def _parse_deepseek_response(self, response_text: str) -> tuple[str, list[str]]:
        """
        ГИБКИЙ парсинг ответа DeepSeek с fallback стратегиями.
        Пробует несколько стратегий извлечения текста.
        """
        # Логируем сырой ответ для дебага
        logger.debug(f"DeepSeek raw response (first 500 chars): {response_text[:500]}")
        
        corrected_text = None
        recommendations = []
        
        # === СТРАТЕГИЯ 1: Точные маркеры ===
        try:
            if START_CORRECTED_TEXT in response_text and END_CORRECTED_TEXT in response_text:
                start_idx = response_text.index(START_CORRECTED_TEXT) + len(START_CORRECTED_TEXT)
                end_idx = response_text.index(END_CORRECTED_TEXT)
                corrected_text = response_text[start_idx:end_idx].strip()
                logger.info("✅ Strategy 1: Found exact markers")
        except Exception as e:
            logger.warning(f"Strategy 1 failed: {e}")
        
        # === СТРАТЕГИЯ 2: Регулярки для маркеров (без точных скобок) ===
        if not corrected_text:
            try:
                # Ищем варианты: [START, START_OF, CORRECTED_TEXT и т.д.
                pattern = r'\[?START[_\s]OF[_\s]CORRECTED[_\s]TEXT\]?(.*?)\[?END[_\s]OF[_\s]CORRECTED[_\s]TEXT\]?'
                match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
                if match:
                    corrected_text = match.group(1).strip()
                    logger.info("✅ Strategy 2: Found with regex")
            except Exception as e:
                logger.warning(f"Strategy 2 failed: {e}")
        
        # === СТРАТЕГИЯ 3: Берём всё до секции рекомендаций ===
        if not corrected_text:
            try:
                # Ищем секцию рекомендаций
                rec_markers = [
                    'RECOMMENDATIONS',
                    'РЕКОМЕНДАЦИИ',
                    'CHUNK_RECOMMENDATIONS',
                    '---'
                ]
                
                split_idx = len(response_text)
                for marker in rec_markers:
                    idx = response_text.find(marker)
                    if idx > 0 and idx < split_idx:
                        split_idx = idx
                
                corrected_text = response_text[:split_idx].strip()
                
                # Убираем возможные начальные маркеры
                for marker in ['[START', 'START_OF', 'CORRECTED']:
                    if corrected_text.startswith(marker):
                        corrected_text = corrected_text[len(marker):].strip()
                
                logger.info("✅ Strategy 3: Took text before recommendations")
            except Exception as e:
                logger.warning(f"Strategy 3 failed: {e}")
        
        # === СТРАТЕГИЯ 4: Весь текст (last resort) ===
        if not corrected_text:
            corrected_text = response_text.strip()
            logger.warning("⚠️ Strategy 4: Using entire response as corrected text")
        
        # === Извлечение рекомендаций (гибко) ===
        try:
            # Попытка 1: точные маркеры
            if START_RECOMMENDATIONS in response_text and END_RECOMMENDATIONS in response_text:
                rec_start = response_text.index(START_RECOMMENDATIONS) + len(START_RECOMMENDATIONS)
                rec_end = response_text.index(END_RECOMMENDATIONS)
                rec_text = response_text[rec_start:rec_end].strip()
            else:
                # Попытка 2: ищем после "---" или "RECOMMENDATIONS"
                for marker in ['---', 'RECOMMENDATIONS', 'РЕКОМЕНДАЦИИ']:
                    if marker in response_text:
                        idx = response_text.index(marker) + len(marker)
                        rec_text = response_text[idx:].strip()
                        break
                else:
                    rec_text = ""
            
            # Парсинг списка
            if rec_text:
                lines = rec_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Убираем нумерацию
                        cleaned = re.sub(r'^[\d\.\-\•\*\[\]]+\s*', '', line)
                        # Убираем END маркеры
                        cleaned = re.sub(r'\[?END.*?\]?', '', cleaned).strip()
                        if cleaned and len(cleaned) > 10:  # Минимум 10 символов
                            recommendations.append(cleaned)
        
        except Exception as e:
            logger.warning(f"Failed to extract recommendations: {e}")
        
        # === Валидация ===
        if not corrected_text or len(corrected_text) < 10:
            raise DeepSeekFormatError(
                f"Failed to extract corrected text. Response length: {len(response_text)}"
            )
        
        logger.info(
            f"✅ Parsed: {len(corrected_text)} chars text, "
            f"{len(recommendations)} recommendations"
        )
        
        return corrected_text, recommendations

    async def close(self):
        """Закрыть HTTP клиент."""
        await self.client.aclose()
        logger.info("AIProcessor HTTP client closed")
