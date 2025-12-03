"""
Модуль для улучшения качества OCR через AI
Использует AI для исправления типичных ошибок OCR и улучшения распознавания
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Импорт AI парсера
try:
    from ai_parser import get_ai_parser

    HAS_AI_PARSER = True
except ImportError:
    HAS_AI_PARSER = False
    logger.warning("ai_parser модуль не найден. AI-усиление OCR недоступно.")


class OCRAIEnhancer:
    """
    Класс для улучшения качества OCR через AI
    """

    def __init__(self):
        self.ai_parser = None
        self.enabled = False

        # Проверяем доступность AI
        if HAS_AI_PARSER:
            try:
                self.ai_parser = get_ai_parser()
                if self.ai_parser and self.ai_parser.enabled:
                    self.enabled = True
                    logger.info("AI-усиление OCR включено")
                else:
                    logger.debug("AI парсер недоступен, AI-усиление OCR отключено")
            except Exception as e:
                logger.warning(f"Не удалось инициализировать AI парсер для OCR: {e}")

    def enhance_ocr_accuracy(
        self,
        initial_ocr_text: str,
        image_path: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        AI помогает улучшить качество OCR распознавания

        Args:
            initial_ocr_text: Текст, полученный из OCR
            image_path: Путь к изображению (опционально, для дополнительного контекста)
            context: Дополнительный контекст о документе (тип, ожидаемые данные)

        Returns:
            Словарь с улучшенным текстом и метаданными
        """
        if not self.enabled or not self.ai_parser:
            return {
                "enhanced_text": initial_ocr_text,
                "improvements": [],
                "confidence_score": 0.0,
                "ai_used": False,
            }

        try:
            logger.info("Начинаю AI-улучшение OCR текста...")

            # Формируем промпт для улучшения OCR
            prompt = self._build_enhancement_prompt(initial_ocr_text, context)

            # Отправляем запрос в AI
            enhanced_text = self._call_ai_enhancement(prompt)

            # Анализируем улучшения
            improvements = self._analyze_improvements(initial_ocr_text, enhanced_text)
            confidence_score = self._calculate_confidence(
                initial_ocr_text, enhanced_text
            )

            result = {
                "enhanced_text": enhanced_text,
                "original_text": initial_ocr_text,
                "improvements": improvements,
                "confidence_score": confidence_score,
                "ai_used": True,
                "char_count_original": len(initial_ocr_text),
                "char_count_enhanced": len(enhanced_text),
            }

            logger.info(
                f"AI-улучшение OCR завершено: "
                f"улучшений: {len(improvements)}, "
                f"уверенность: {confidence_score:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Ошибка при AI-улучшении OCR: {e}")
            return {
                "enhanced_text": initial_ocr_text,
                "improvements": [],
                "confidence_score": 0.0,
                "ai_used": False,
                "error": str(e),
            }

    def _build_enhancement_prompt(
        self, ocr_text: str, context: Optional[str] = None
    ) -> str:
        """
        Формирует промпт для AI-улучшения OCR
        """
        base_prompt = f"""Улучши OCR распознавание этого энергетического документа.

Исходный OCR текст:
{ocr_text[:5000]}  # Ограничиваем размер для экономии токенов

Особое внимание удели:
- Числовым значениям (потребление энергии, показания счетчиков)
- Единицам измерения (кВт·ч, Гкал, м³, кВт, МВт)
- Названиям предприятий и приборов учета
- Датам и периодам (формат: ДД.ММ.ГГГГ или ГГГГ-ММ-ДД)
- Техническим терминам и аббревиатурам
- Табличным данным (сохрани структуру таблиц)

Исправь типичные OCR ошибки:
- Замены похожих символов (0/O, 1/l/I, 5/S, 8/B)
- Пробелы в числах и единицах измерения
- Разрывы слов и строк
- Неправильное распознавание русских букв (особенно: о/а, р/р, с/с, у/у)

Верни улучшенный текст, сохраняя структуру и форматирование документа.
"""

        if context:
            base_prompt += f"\n\nДополнительный контекст: {context}"

        return base_prompt

    def _call_ai_enhancement(self, prompt: str) -> str:
        """
        Вызывает AI для улучшения текста
        """
        if not self.ai_parser or not self.ai_parser.enabled:
            raise ValueError("AI парсер недоступен")

        provider = self.ai_parser.provider

        try:
            if provider in ["deepseek", "openai"]:
                response = self.ai_parser.client.chat.completions.create(
                    model=self.ai_parser.model_text,
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты эксперт по улучшению качества OCR распознавания документов. Твоя задача - исправить ошибки OCR, сохраняя структуру и смысл документа.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=4000,
                    temperature=0.3,  # Низкая температура для более точных исправлений
                )
                return response.choices[0].message.content.strip()

            elif provider == "anthropic":
                response = self.ai_parser.client.messages.create(
                    model=self.ai_parser.model_text,
                    max_tokens=4000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text.strip()

            else:
                raise ValueError(f"Неподдерживаемый провайдер: {provider}")

        except Exception as e:
            logger.error(f"Ошибка при вызове AI для улучшения OCR: {e}")
            raise

    def _analyze_improvements(self, original: str, enhanced: str) -> list:
        """
        Анализирует улучшения между оригинальным и улучшенным текстом
        """
        improvements = []

        # Простой анализ различий
        if len(enhanced) > len(original) * 1.1:
            improvements.append("Значительное увеличение объема текста")
        elif len(enhanced) < len(original) * 0.9:
            improvements.append("Удаление лишних символов/шума")

        # Подсчет потенциальных исправлений (упрощенный метод)
        # В реальности можно использовать более сложные алгоритмы сравнения
        if original != enhanced:
            improvements.append("Текст был улучшен AI")

        return improvements

    def _calculate_confidence(self, original: str, enhanced: str) -> float:
        """
        Вычисляет оценку уверенности в улучшении
        """
        # Упрощенная метрика уверенности
        # В реальности можно использовать более сложные метрики

        if not enhanced or len(enhanced) == 0:
            return 0.0

        # Базовая уверенность, если текст был изменен
        confidence = 0.5

        # Увеличиваем уверенность, если текст стал длиннее (возможно, распознано больше)
        if len(enhanced) > len(original) * 1.05:
            confidence += 0.2

        # Увеличиваем уверенность, если текст стал короче (возможно, удален шум)
        if len(enhanced) < len(original) * 0.95:
            confidence += 0.1

        return min(confidence, 1.0)

    def enhance_page_by_page(
        self, ocr_results: list, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Улучшает OCR результаты постранично

        Args:
            ocr_results: Список словарей с результатами OCR по страницам
            context: Дополнительный контекст

        Returns:
            Словарь с улучшенными результатами
        """
        if not self.enabled:
            return {"enhanced_pages": ocr_results, "ai_used": False}

        enhanced_pages = []
        total_improvements = 0

        for page_data in ocr_results:
            page_text = page_data.get("text", "")
            if page_text:
                enhanced = self.enhance_ocr_accuracy(page_text, context=context)
                enhanced_pages.append(
                    {
                        **page_data,
                        "text": enhanced.get("enhanced_text", page_text),
                        "ai_enhanced": True,
                        "improvements": enhanced.get("improvements", []),
                    }
                )
                total_improvements += len(enhanced.get("improvements", []))
            else:
                enhanced_pages.append(page_data)

        return {
            "enhanced_pages": enhanced_pages,
            "total_improvements": total_improvements,
            "ai_used": True,
        }


def get_ocr_ai_enhancer() -> Optional[OCRAIEnhancer]:
    """
    Получить экземпляр AI-усилителя OCR

    Returns:
        OCRAIEnhancer или None если AI недоступен
    """
    try:
        enhancer = OCRAIEnhancer()
        if enhancer.enabled:
            return enhancer
        return None
    except Exception as e:
        logger.warning(f"Не удалось инициализировать AI-усилитель OCR: {e}")
        return None
