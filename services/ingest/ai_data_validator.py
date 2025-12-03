"""
Модуль для валидации извлеченных данных через AI
Проверяет правдоподобность данных энергопотребления
"""

import logging
from typing import Dict, Any, Optional, List
import re

logger = logging.getLogger(__name__)

# Импорт AI парсера
try:
    from ai_parser import get_ai_parser

    HAS_AI_PARSER = True
except ImportError:
    HAS_AI_PARSER = False
    logger.warning("ai_parser модуль не найден. AI-валидация данных недоступна.")


class AIDataValidator:
    """
    Класс для валидации извлеченных данных через AI
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
                    logger.info("AI-валидация данных включена")
                else:
                    logger.debug("AI парсер недоступен, AI-валидация отключена")
            except Exception as e:
                logger.warning(
                    f"Не удалось инициализировать AI парсер для валидации: {e}"
                )

    def validate_extracted_data(
        self, extracted_data: str, document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI проверяет правдоподобность извлеченных данных

        Args:
            extracted_data: Извлеченные данные (текст или структурированные данные)
            document_type: Тип документа (например, "energy_passport", "meter_reading")

        Returns:
            Словарь с результатами валидации
        """
        if not self.enabled or not self.ai_parser:
            return {
                "is_valid": True,
                "confidence": 0.5,
                "issues": [],
                "warnings": [],
                "ai_used": False,
            }

        try:
            logger.info("Начинаю AI-валидацию извлеченных данных...")

            # Формируем промпт для валидации
            prompt = self._build_validation_prompt(extracted_data, document_type)

            # Отправляем запрос в AI
            validation_result = self._call_ai_validation(prompt)

            # Парсим результат
            parsed_result = self._parse_validation_result(validation_result)

            # Добавляем базовую валидацию через регулярные выражения
            regex_issues = self._regex_validation(extracted_data)
            parsed_result["issues"].extend(regex_issues)

            # Вычисляем общую уверенность
            confidence = self._calculate_validation_confidence(parsed_result)
            parsed_result["confidence"] = confidence

            logger.info(
                f"AI-валидация завершена: "
                f"валидно: {parsed_result['is_valid']}, "
                f"проблем: {len(parsed_result['issues'])}, "
                f"уверенность: {confidence:.2f}"
            )

            return parsed_result

        except Exception as e:
            logger.error(f"Ошибка при AI-валидации данных: {e}")
            return {
                "is_valid": True,  # По умолчанию считаем валидным при ошибке
                "confidence": 0.5,
                "issues": [],
                "warnings": [f"Ошибка валидации: {str(e)}"],
                "ai_used": False,
                "error": str(e),
            }

    def _build_validation_prompt(
        self, extracted_data: str, document_type: Optional[str] = None
    ) -> str:
        """
        Формирует промпт для AI-валидации
        """
        base_prompt = f"""Проверь правдоподобность данных энергопотребления из следующего документа.

Извлеченные данные:
{extracted_data[:5000]}  # Ограничиваем размер

Критерии проверки:
1. Соответствие единиц измерения (кВт·ч, Гкал, м³, кВт, МВт)
2. Логические соотношения показателей (например, потребление не может быть отрицательным)
3. Типичные диапазоны значений для предприятий:
   - Электроэнергия: обычно от 100 кВт·ч до миллионов кВт·ч
   - Тепло: обычно от 0.1 Гкал до тысяч Гкал
   - Вода: обычно от 1 м³ до десятков тысяч м³
4. Выявление аномалий и опечаток
5. Корректность дат и периодов
6. Соответствие названий предприятий и адресов

Верни результат в формате JSON:
{{
    "is_valid": true/false,
    "issues": ["проблема1", "проблема2"],
    "warnings": ["предупреждение1"],
    "suggestions": ["предложение1"]
}}
"""

        if document_type:
            base_prompt += f"\n\nТип документа: {document_type}"

        return base_prompt

    def _call_ai_validation(self, prompt: str) -> str:
        """
        Вызывает AI для валидации данных
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
                            "content": "Ты эксперт по валидации данных энергопотребления. Твоя задача - проверить правдоподобность и корректность данных. Всегда возвращай валидный JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"}
                    if provider == "openai"
                    else None,
                    max_tokens=2000,
                    temperature=0.2,  # Низкая температура для более точной валидации
                )
                return response.choices[0].message.content.strip()

            elif provider == "anthropic":
                response = self.ai_parser.client.messages.create(
                    model=self.ai_parser.model_text,
                    max_tokens=2000,
                    temperature=0.2,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text.strip()

            else:
                raise ValueError(f"Неподдерживаемый провайдер: {provider}")

        except Exception as e:
            logger.error(f"Ошибка при вызове AI для валидации: {e}")
            raise

    def _parse_validation_result(self, ai_response: str) -> Dict[str, Any]:
        """
        Парсит результат валидации от AI
        """
        import json

        try:
            # Извлекаем JSON из ответа (может быть обернут в markdown)
            if "```json" in ai_response:
                json_text = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                json_text = ai_response.split("```")[1].split("```")[0].strip()
            else:
                json_text = ai_response.strip()

            result = json.loads(json_text)

            # Нормализуем структуру
            return {
                "is_valid": result.get("is_valid", True),
                "issues": result.get("issues", []),
                "warnings": result.get("warnings", []),
                "suggestions": result.get("suggestions", []),
                "ai_used": True,
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Не удалось распарсить JSON ответ AI: {e}")
            logger.debug(f"Ответ AI: {ai_response[:500]}")

            # Пытаемся извлечь информацию из текста
            issues = []
            if "невалид" in ai_response.lower() or "ошибка" in ai_response.lower():
                issues.append("AI обнаружил проблемы, но не смог их структурировать")

            return {
                "is_valid": len(issues) == 0,
                "issues": issues,
                "warnings": ["Не удалось распарсить структурированный ответ AI"],
                "suggestions": [],
                "ai_used": True,
                "raw_response": ai_response,
            }

    def _regex_validation(self, data: str) -> List[str]:
        """
        Базовая валидация через регулярные выражения
        """
        issues = []

        # Проверка на отрицательные значения потребления
        negative_pattern = r"-\s*\d+[.,]\d*\s*(кВт·ч|Гкал|м³|кВт|МВт)"
        if re.search(negative_pattern, data, re.IGNORECASE):
            issues.append("Обнаружены отрицательные значения потребления")

        # Проверка на подозрительно большие значения
        large_pattern = r"(\d{10,})\s*(кВт·ч|Гкал|м³)"
        if re.search(large_pattern, data, re.IGNORECASE):
            issues.append(
                "Обнаружены подозрительно большие значения (возможна опечатка)"
            )

        # Проверка на некорректные единицы измерения
        invalid_units = re.findall(r"\d+\s*[^кГмВт·чал³\s]+", data)
        if invalid_units:
            issues.append(
                f"Обнаружены подозрительные единицы измерения: {invalid_units[:3]}"
            )

        return issues

    def _calculate_validation_confidence(
        self, validation_result: Dict[str, Any]
    ) -> float:
        """
        Вычисляет общую уверенность в валидности данных
        """
        confidence = 1.0

        # Снижаем уверенность за каждую проблему
        issues_count = len(validation_result.get("issues", []))
        confidence -= issues_count * 0.15

        # Снижаем уверенность за каждое предупреждение
        warnings_count = len(validation_result.get("warnings", []))
        confidence -= warnings_count * 0.05

        # Если данные невалидны, значительно снижаем уверенность
        if not validation_result.get("is_valid", True):
            confidence *= 0.5

        return max(0.0, min(1.0, confidence))

    def validate_energy_values(self, values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Валидирует список значений энергопотребления

        Args:
            values: Список словарей с данными (например, [{"value": 1000, "unit": "кВт·ч", "date": "2024-01-01"}])

        Returns:
            Результаты валидации
        """
        if not values:
            return {"is_valid": True, "confidence": 1.0, "issues": [], "ai_used": False}

        # Формируем текстовое представление для валидации
        values_text = "\n".join(
            [
                f"{v.get('value', 'N/A')} {v.get('unit', 'N/A')} на {v.get('date', 'N/A')}"
                for v in values
            ]
        )

        return self.validate_extracted_data(values_text, "energy_values")


def get_ai_data_validator() -> Optional[AIDataValidator]:
    """
    Получить экземпляр AI-валидатора данных

    Returns:
        AIDataValidator или None если AI недоступен
    """
    try:
        validator = AIDataValidator()
        if validator.enabled:
            return validator
        return None
    except Exception as e:
        logger.warning(f"Не удалось инициализировать AI-валидатор данных: {e}")
        return None
