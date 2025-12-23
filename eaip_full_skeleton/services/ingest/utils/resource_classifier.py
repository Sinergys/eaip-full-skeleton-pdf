"""
Единый классификатор типов энергоресурсов.

Использует приоритет: содержимое файла > имя файла > fallback на "other".
Теперь с поддержкой AI для улучшения классификации.
"""

import logging
from typing import Dict, Any, Optional

from utils.content_analyzer import analyze_file_content
from config.required_data_matrix import get_resource_for_file

# Импорт AI классификатора (опционально)
try:
    from utils.ai_content_classifier import get_ai_content_classifier

    HAS_AI_CLASSIFIER = True
except ImportError:
    HAS_AI_CLASSIFIER = False
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("ai_content_classifier модуль не найден. AI-классификация недоступна.")

logger = logging.getLogger(__name__)


class ResourceClassifier:
    """
    Единый классификатор для определения типа энергоресурса.

    Приоритет классификации:
    1. Анализ содержимого файла (если доступен raw_json)
    2. Анализ имени файла
    3. Fallback на "other"
    """

    @staticmethod
    def classify(
        filename: str,
        raw_json: Optional[Dict[str, Any]] = None,
        user_provided_type: Optional[str] = None,
    ) -> str:
        """
        Классифицирует файл и определяет тип энергоресурса.

        Args:
            filename: Имя файла
            raw_json: Распарсенные данные файла (опционально)
            user_provided_type: Тип, указанный пользователем (опционально)

        Returns:
            Тип ресурса (electricity, gas, water, heat, fuel, coal, equipment, envelope, nodes, other)
        """
        # Если пользователь указал тип, проверяем его валидность
        if user_provided_type:
            validated_type = ResourceClassifier._validate_user_type(
                filename, raw_json, user_provided_type
            )
            if validated_type:
                return validated_type

        # Приоритет 1: Анализ содержимого (если доступен)
        if raw_json:
            # Сначала пробуем классификацию по правилам
            content_type = analyze_file_content(raw_json, filename)

            if content_type:
                logger.info(
                    f"Тип ресурса определен по содержимому (правила): {content_type} "
                    f"для файла {filename}"
                )
                return content_type

            # Если правила не определили тип, пробуем AI (только если уверенность правил низкая)
            # Используем AI когда правила неуверенны или не смогли определить тип
            if HAS_AI_CLASSIFIER:
                try:
                    ai_classifier = get_ai_content_classifier()
                    if ai_classifier:
                        ai_type, ai_confidence = ai_classifier.classify_with_ai(
                            raw_json, filename
                        )

                        if ai_type and ai_confidence >= 0.7:
                            logger.info(
                                f"Тип ресурса определен по содержимому (AI): {ai_type} "
                                f"(уверенность: {ai_confidence:.2f}) для файла {filename}"
                            )
                            return ai_type
                        elif ai_type and ai_confidence >= 0.5:
                            # AI определил тип, но с низкой уверенностью - используем, но логируем
                            logger.info(
                                f"Тип ресурса определен по содержимому (AI, низкая уверенность): {ai_type} "
                                f"(уверенность: {ai_confidence:.2f}) для файла {filename}"
                            )
                            return ai_type
                        else:
                            logger.debug(
                                f"AI не смог определить тип ресурса с достаточной уверенностью "
                                f"для файла {filename}"
                            )
                except Exception as e:
                    logger.warning(f"Ошибка при AI классификации файла {filename}: {e}")
                    # Продолжаем с обычной классификацией

        # Приоритет 2: Анализ имени файла
        name_type = get_resource_for_file(filename)
        if name_type:
            logger.info(
                f"Тип ресурса определен по имени файла: {name_type} "
                f"для файла {filename}"
            )
            return name_type

        # Приоритет 3: Fallback на "other"
        logger.warning(
            f"Не удалось определить тип ресурса для файла {filename}. "
            f"Используется 'other'"
        )
        return "other"

    @staticmethod
    def _validate_user_type(
        filename: str, raw_json: Optional[Dict[str, Any]], user_type: str
    ) -> Optional[str]:
        """
        Валидирует тип, указанный пользователем, на соответствие содержимому.

        Args:
            filename: Имя файла
            raw_json: Распарсенные данные файла
            user_type: Тип, указанный пользователем

        Returns:
            Валидированный тип или None, если есть несоответствие
        """
        if not raw_json:
            # Если нет содержимого, принимаем тип пользователя
            return user_type

        # Анализируем содержимое для проверки соответствия
        content_type = analyze_file_content(raw_json, filename)

        if content_type and content_type != user_type:
            logger.warning(
                f"⚠️ Несоответствие типа: пользователь указал '{user_type}', "
                f"но содержимое указывает на '{content_type}' для файла {filename}. "
                f"Используется тип из содержимого."
            )
            return content_type

        # Тип соответствует содержимому или содержимое не определено
        return user_type

    @staticmethod
    def classify_with_confidence(
        filename: str, raw_json: Optional[Dict[str, Any]] = None
    ) -> tuple[str, float]:
        """
        Классифицирует файл и возвращает тип с уровнем уверенности.

        Args:
            filename: Имя файла
            raw_json: Распарсенные данные файла

        Returns:
            Кортеж (тип_ресурса, уверенность_0.0-1.0)
        """
        # Анализ содержимого дает более высокую уверенность
        if raw_json:
            # Сначала пробуем классификацию по правилам
            content_type = analyze_file_content(raw_json, filename)
            if content_type:
                # Высокая уверенность при определении по содержимому (правила)
                return (content_type, 0.9)

            # Если правила не определили, пробуем AI
            if HAS_AI_CLASSIFIER:
                try:
                    ai_classifier = get_ai_content_classifier()
                    if ai_classifier:
                        ai_type, ai_confidence = ai_classifier.classify_with_ai(
                            raw_json, filename
                        )
                        if ai_type and ai_confidence >= 0.5:
                            # Используем уверенность от AI
                            return (ai_type, ai_confidence)
                except Exception as e:
                    logger.debug(
                        f"Ошибка при AI классификации для определения уверенности: {e}"
                    )

        # Анализ имени файла дает среднюю уверенность
        name_type = get_resource_for_file(filename)
        if name_type:
            return (name_type, 0.7)

        # Fallback на "other" - низкая уверенность
        return ("other", 0.3)
