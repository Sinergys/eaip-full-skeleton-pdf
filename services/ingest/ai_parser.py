"""
Модуль для распознавания файлов с помощью ИИ API
Поддерживает DeepSeek, OpenAI, Anthropic, Gemini
"""

import os
import base64
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# Определяем доступные провайдеры
HAS_OPENAI = False
try:
    from openai import OpenAI

    HAS_OPENAI = True
except ImportError:
    logger.warning("openai библиотека не установлена. ИИ функции недоступны.")

HAS_ANTHROPIC = False
try:
    import anthropic

    HAS_ANTHROPIC = True
except ImportError:
    pass

HAS_GOOGLE = False
try:
    import google.generativeai  # noqa: F401

    HAS_GOOGLE = True
except ImportError:
    pass


class AIParser:
    """
    Парсер для распознавания документов с помощью ИИ API
    """

    def __init__(self):
        # Используем единый модуль настроек
        try:
            from settings.ai_settings import get_ai_settings

            ai_settings = get_ai_settings()
            self.provider = ai_settings.provider
            self.enabled = ai_settings.enabled and ai_settings.has_valid_config
        except ImportError:
            # Fallback на старую логику, если модуль настроек недоступен
            logger.warning(
                "Модуль settings.ai_settings недоступен, используется fallback логика"
            )
            self.provider = os.getenv("AI_PROVIDER", "deepseek").lower()
            self.enabled = os.getenv("AI_ENABLED", "false").lower() == "true"

        self.client = None
        self.model_vision = None
        self.model_text = None

        if self.enabled:
            self.setup_provider()

    def setup_provider(self):
        """Настройка провайдера ИИ"""
        if self.provider == "deepseek":
            if not HAS_OPENAI:
                raise ImportError(
                    "openai библиотека не установлена. Установите: pip install openai"
                )

            # Используем единый модуль настроек для получения API ключа
            try:
                from settings.ai_settings import get_ai_settings

                ai_settings = get_ai_settings()
                api_key = ai_settings.api_key
            except ImportError:
                # Fallback на старую логику
                api_key = os.getenv("DEEPSEEK_API_KEY")

            if not api_key:
                raise ValueError(
                    "DEEPSEEK_API_KEY не установлен в переменных окружения"
                )

            # DeepSeek использует OpenAI-совместимый API
            try:
                self.client = OpenAI(
                    api_key=api_key, base_url="https://api.deepseek.com", timeout=60.0
                )
            except TypeError as e:
                # Если есть проблемы с параметрами, пробуем без base_url
                # и устанавливаем через _client
                logger.warning(
                    f"Проблема с base_url параметром: {e}, использую альтернативный способ"
                )
                self.client = OpenAI(api_key=api_key, timeout=60.0)
                # Устанавливаем base_url через внутренний клиент
                if hasattr(self.client, "_client") and hasattr(
                    self.client._client, "base_url"
                ):
                    self.client._client.base_url = "https://api.deepseek.com"
                else:
                    # Используем httpx напрямую как fallback
                    logger.warning(
                        "Не удалось установить base_url, будет использован стандартный OpenAI endpoint"
                    )
                    raise ValueError(
                        "DeepSeek требует base_url, но текущая версия openai не поддерживает его. Обновите openai: pip install --upgrade openai"
                    )
            self.model_vision = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            self.model_text = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            logger.info(f"DeepSeek API настроен, модель: {self.model_text}")

        elif self.provider == "openai":
            if not HAS_OPENAI:
                raise ImportError(
                    "openai библиотека не установлена. Установите: pip install openai"
                )

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY не установлен в переменных окружения")

            self.client = OpenAI(api_key=api_key)
            self.model_vision = os.getenv("OPENAI_MODEL_VISION", "gpt-4-vision-preview")
            self.model_text = os.getenv("OPENAI_MODEL_TEXT", "gpt-4")
            logger.info(
                f"OpenAI API настроен, модель Vision: {self.model_vision}, Text: {self.model_text}"
            )

        elif self.provider == "anthropic":
            if not HAS_ANTHROPIC:
                raise ImportError(
                    "anthropic библиотека не установлена. Установите: pip install anthropic"
                )

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY не установлен в переменных окружения"
                )

            self.client = anthropic.Anthropic(api_key=api_key)
            self.model_vision = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            self.model_text = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            logger.info(f"Anthropic API настроен, модель: {self.model_text}")

        else:
            raise ValueError(f"Неподдерживаемый провайдер ИИ: {self.provider}")

    def _image_to_base64(self, image_path: str) -> str:
        """Конвертация изображения в base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _pdf_to_images(self, pdf_path: str) -> List[str]:
        """Конвертация PDF в список base64 изображений"""
        try:
            from pdf2image import convert_from_path
            import io

            # Конвертируем PDF в изображения (200 DPI для экономии)
            images = convert_from_path(pdf_path, dpi=200)
            base64_images = []

            for img in images:
                # Конвертируем PIL Image в base64
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_bytes = buffer.getvalue()
                base64_str = base64.b64encode(img_bytes).decode("utf-8")
                base64_images.append(base64_str)

            return base64_images
        except Exception as e:
            logger.error(f"Ошибка конвертации PDF в изображения: {e}")
            raise

    def recognize_document(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Распознавание документа с помощью ИИ Vision API

        Args:
            file_path: Путь к файлу
            file_type: Тип файла (pdf, image, etc.)

        Returns:
            Распознанные данные
        """
        if not self.enabled or not self.client:
            raise ValueError("ИИ не настроен или отключен")

        try:
            logger.info(
                f"Начинаю ИИ распознавание файла: {file_path} (тип: {file_type}, провайдер: {self.provider})"
            )

            # Подготовка изображений для Vision API
            images_base64 = []

            if file_type == "pdf":
                images_base64 = self._pdf_to_images(file_path)
            elif file_type in ["image", "jpg", "jpeg", "png"]:
                images_base64 = [self._image_to_base64(file_path)]
            else:
                raise ValueError(
                    f"Неподдерживаемый тип файла для ИИ распознавания: {file_type}"
                )

            # Распознавание через ИИ
            recognized_texts = []

            for i, img_base64 in enumerate(images_base64, 1):
                logger.info(
                    f"Обрабатываю страницу {i}/{len(images_base64)} через ИИ..."
                )

                if self.provider in ["deepseek", "openai"]:
                    # OpenAI-совместимый API (DeepSeek и OpenAI)
                    response = self.client.chat.completions.create(
                        model=self.model_vision
                        if self.provider == "openai"
                        else self.model_text,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Распознай текст с этого изображения. Извлеки весь текст, включая таблицы, если они есть. Сохрани структуру документа.",
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{img_base64}"
                                        },
                                    },
                                ],
                            }
                        ],
                        max_tokens=4000,
                    )
                    text = response.choices[0].message.content
                    recognized_texts.append(f"--- Страница {i} ---\n{text}")

                elif self.provider == "anthropic":
                    # Anthropic Claude API
                    response = self.client.messages.create(
                        model=self.model_vision,
                        max_tokens=4000,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/png",
                                            "data": img_base64,
                                        },
                                    },
                                    {
                                        "type": "text",
                                        "text": "Распознай текст с этого изображения. Извлеки весь текст, включая таблицы, если они есть. Сохрани структуру документа.",
                                    },
                                ],
                            }
                        ],
                    )
                    text = response.content[0].text
                    recognized_texts.append(f"--- Страница {i} ---\n{text}")

            full_text = "\n\n".join(recognized_texts)

            result = {
                "file_path": file_path,
                "file_type": file_type,
                "text": full_text,
                "total_characters": len(full_text),
                "pages_processed": len(images_base64),
                "ai_provider": self.provider,
                "ai_used": True,
            }

            logger.info(
                f"ИИ распознавание завершено: извлечено {len(full_text)} символов из {len(images_base64)} страниц"
            )
            return result

        except Exception as e:
            logger.error(f"Ошибка при ИИ распознавании файла {file_path}: {e}")
            raise

    def structure_data(
        self, raw_text: str, template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Структурирование данных с помощью ИИ

        Args:
            raw_text: Извлеченный текст
            template: Шаблон структуры (опционально, например, "EnergyPassport")

        Returns:
            Структурированные данные в JSON
        """
        if not self.enabled or not self.client:
            raise ValueError("ИИ не настроен или отключен")

        try:
            logger.info("Начинаю структурирование данных через ИИ...")

            # Промпт для структурирования
            prompt = f"""Извлеки структурированные данные из следующего текста документа.
            
Текст документа:
{raw_text[:8000]}  # Ограничиваем размер для экономии токенов

Верни результат в формате JSON со следующей структурой:
{{
    "document_type": "тип документа",
    "fields": {{
        "field1": "значение1",
        "field2": "значение2"
    }},
    "tables": [],
    "metadata": {{
        "pages": 0,
        "date": null
    }}
}}

Если это энергетический паспорт (EnergyPassport), извлеки все поля согласно шаблону."""

            if self.provider in ["deepseek", "openai"]:
                response = self.client.chat.completions.create(
                    model=self.model_text,
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты помощник для извлечения структурированных данных из документов. Всегда возвращай валидный JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"}
                    if self.provider == "openai"
                    else None,
                    max_tokens=2000,
                )
                result_text = response.choices[0].message.content

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_text,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                )
                result_text = response.content[0].text

            # Парсинг JSON ответа
            import json

            try:
                # Извлекаем JSON из ответа (может быть обернут в markdown)
                if "```json" in result_text:
                    result_text = (
                        result_text.split("```json")[1].split("```")[0].strip()
                    )
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()

                structured_data = json.loads(result_text)
                logger.info("Структурирование данных завершено успешно")
                return structured_data
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON ответа: {e}")
                logger.debug(f"Ответ ИИ: {result_text}")
                return {
                    "error": "Не удалось распарсить JSON ответ",
                    "raw_response": result_text,
                }

        except Exception as e:
            logger.error(f"Ошибка при структурировании данных: {e}")
            raise


def get_ai_parser() -> Optional[AIParser]:
    """
    Получить экземпляр AI парсера, если ИИ включен

    Returns:
        AIParser или None если ИИ отключен
    """
    try:
        parser = AIParser()
        if parser.enabled:
            return parser
        return None
    except Exception as e:
        logger.warning(f"Не удалось инициализировать ИИ парсер: {e}")
        return None
