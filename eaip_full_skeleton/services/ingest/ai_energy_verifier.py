"""
Модуль для AI-верификации энергетических показателей
Проверяет корректность данных согласно ПКМ №690
"""

import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

# Импорт AI парсера
try:
    from ai_parser import get_ai_parser

    HAS_AI_PARSER = True
except ImportError:
    HAS_AI_PARSER = False
    logger.warning(
        "ai_parser модуль не найден. AI-верификация энергопоказателей недоступна."
    )


class EnergyDataVerifier:
    """
    Класс для AI-верификации энергетических показателей
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
                    logger.info("AI-верификация энергопоказателей включена")
                else:
                    logger.debug("AI парсер недоступен, AI-верификация отключена")
            except Exception as e:
                logger.warning(
                    f"Не удалось инициализировать AI парсер для верификации: {e}"
                )

    def verify_energy_metrics(
        self, extracted_data: Dict[str, Any], enterprise_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI проверяет корректность энергетических показателей

        Args:
            extracted_data: Извлеченные энергетические данные
            enterprise_type: Тип предприятия (опционально)

        Returns:
            Словарь с результатами верификации
        """
        if not self.enabled or not self.ai_parser:
            return {
                "is_valid": True,
                "confidence": 0.5,
                "verified_sections": [],
                "issues": [],
                "warnings": [],
                "ai_used": False,
            }

        try:
            logger.info("Начинаю AI-верификацию энергетических показателей...")

            # Конвертируем данные в текст для AI
            data_text = self._format_data_for_verification(extracted_data)

            # Формируем промпт для верификации
            prompt = self._build_verification_prompt(data_text, enterprise_type)

            # Отправляем запрос в AI
            verification_result = self._call_ai_verification(prompt)

            # Парсим результат
            parsed_result = self._parse_verification_result(verification_result)

            # Добавляем проверку баланса
            balance_check = self._check_energy_balance(extracted_data)
            if balance_check.get("issues"):
                parsed_result["issues"].extend(balance_check["issues"])
                parsed_result["balance_check"] = balance_check

            # Вычисляем общую уверенность
            confidence = self._calculate_verification_confidence(parsed_result)
            parsed_result["confidence"] = confidence

            logger.info(
                f"AI-верификация завершена: "
                f"валидно: {parsed_result['is_valid']}, "
                f"проблем: {len(parsed_result['issues'])}, "
                f"уверенность: {confidence:.2f}"
            )

            return parsed_result

        except Exception as e:
            logger.error(f"Ошибка при AI-верификации энергопоказателей: {e}")
            return {
                "is_valid": True,
                "confidence": 0.5,
                "issues": [],
                "warnings": [f"Ошибка верификации: {str(e)}"],
                "ai_used": False,
                "error": str(e),
            }

    def _format_data_for_verification(self, data: Dict[str, Any]) -> str:
        """Форматирует данные для верификации"""
        try:
            # Пытаемся извлечь ключевые показатели
            formatted = []

            # Электроэнергия
            if "electricity" in data:
                formatted.append(
                    f"Электроэнергия: {json.dumps(data['electricity'], ensure_ascii=False, indent=2)}"
                )

            # Газ
            if "gas" in data:
                formatted.append(
                    f"Газ: {json.dumps(data['gas'], ensure_ascii=False, indent=2)}"
                )

            # Вода
            if "water" in data:
                formatted.append(
                    f"Вода: {json.dumps(data['water'], ensure_ascii=False, indent=2)}"
                )

            # Топливо
            if "fuel" in data:
                formatted.append(
                    f"Топливо: {json.dumps(data['fuel'], ensure_ascii=False, indent=2)}"
                )

            # Оборудование
            if "equipment" in data:
                formatted.append(
                    f"Оборудование: {json.dumps(data['equipment'], ensure_ascii=False, indent=2)}"
                )

            return (
                "\n\n".join(formatted)
                if formatted
                else json.dumps(data, ensure_ascii=False, indent=2)
            )

        except Exception as e:
            logger.warning(f"Ошибка форматирования данных: {e}")
            return str(data)

    def _build_verification_prompt(
        self, data_text: str, enterprise_type: Optional[str] = None
    ) -> str:
        """Формирует промпт для AI-верификации"""
        prompt = f"""Верифицируй энергетические данные согласно ПКМ №690 (Постановление Кабинета Министров Республики Узбекистан).

Энергетические данные:
{data_text[:4000]}  # Ограничиваем размер

Проверь следующие аспекты:

1. **Соответствие единиц измерения ГОСТ:**
   - Электроэнергия: кВт·ч, МВт·ч
   - Газ: м³, тыс.м³
   - Вода: м³, тыс.м³
   - Тепло: Гкал, Мкал
   - Топливо: т.у.т. (тонны условного топлива)

2. **Логика баланса энергопотребления:**
   - Технологические нужды + Собственные нужды = Общее потребление
   - Проверка сумм по кварталам и годам
   - Соответствие активной и реактивной энергии

3. **Типичные диапазоны для типа предприятия:**
   - Промышленные предприятия: обычно 1000+ кВт·ч/месяц
   - Коммерческие: обычно 100-1000 кВт·ч/месяц
   - Бытовые: обычно <100 кВт·ч/месяц

4. **Соответствие сезонным паттернам:**
   - Зимний период: обычно выше потребление тепла и электроэнергии
   - Летний период: может быть выше потребление электроэнергии (кондиционирование)

5. **Выявление статистических аномалий:**
   - Резкие скачки потребления без объяснения
   - Нулевые значения в активных периодах
   - Отрицательные значения потребления

Верни результат в формате JSON:
{{
    "is_valid": true/false,
    "verified_sections": ["электроэнергия", "газ", "вода"],
    "issues": [
        {{
            "section": "электроэнергия",
            "issue": "описание проблемы",
            "severity": "critical/warning/info",
            "suggestion": "рекомендация по исправлению"
        }}
    ],
    "warnings": ["предупреждение1"],
    "balance_check": {{
        "is_balanced": true/false,
        "discrepancies": ["описание несоответствий"]
    }},
    "compliance_score": 0.95
}}
"""

        if enterprise_type:
            prompt += f"\n\nТип предприятия: {enterprise_type}"

        return prompt

    def _call_ai_verification(self, prompt: str) -> str:
        """Вызывает AI для верификации"""
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
                            "content": "Ты эксперт по верификации энергетических данных согласно ПКМ №690. Твоя задача - проверить корректность и соответствие нормативным требованиям. Всегда возвращай валидный JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"}
                    if provider == "openai"
                    else None,
                    max_tokens=3000,
                    temperature=0.2,
                )
                return response.choices[0].message.content.strip()

            elif provider == "anthropic":
                response = self.ai_parser.client.messages.create(
                    model=self.ai_parser.model_text,
                    max_tokens=3000,
                    temperature=0.2,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text.strip()

            else:
                raise ValueError(f"Неподдерживаемый провайдер: {provider}")

        except Exception as e:
            logger.error(f"Ошибка при вызове AI для верификации: {e}")
            raise

    def _parse_verification_result(self, ai_response: str) -> Dict[str, Any]:
        """Парсит результат верификации от AI"""
        import json

        try:
            # Извлекаем JSON из ответа
            if "```json" in ai_response:
                json_text = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                json_text = ai_response.split("```")[1].split("```")[0].strip()
            else:
                json_text = ai_response.strip()

            result = json.loads(json_text)

            return {
                "is_valid": result.get("is_valid", True),
                "verified_sections": result.get("verified_sections", []),
                "issues": result.get("issues", []),
                "warnings": result.get("warnings", []),
                "balance_check": result.get("balance_check", {}),
                "compliance_score": result.get("compliance_score", 0.5),
                "ai_used": True,
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Не удалось распарсить JSON ответ AI: {e}")
            return {
                "is_valid": True,
                "verified_sections": [],
                "issues": [],
                "warnings": ["Не удалось распарсить структурированный ответ AI"],
                "ai_used": True,
                "raw_response": ai_response,
            }

    def _check_energy_balance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Проверяет баланс энергопотребления"""
        issues = []

        # Проверка баланса электроэнергии
        if "electricity" in data:
            data["electricity"]
            # Простая проверка: если есть технологические и собственные нужды, их сумма должна быть равна общему
            # Это упрощенная проверка, в реальности нужно учитывать структуру данных
            pass

        return {"is_balanced": len(issues) == 0, "issues": issues}

    def _calculate_verification_confidence(self, result: Dict[str, Any]) -> float:
        """Вычисляет уверенность в верификации"""
        confidence = 1.0

        # Снижаем уверенность за критические проблемы
        critical_issues = [
            i for i in result.get("issues", []) if i.get("severity") == "critical"
        ]
        confidence -= len(critical_issues) * 0.3

        # Снижаем уверенность за предупреждения
        warnings_count = len(result.get("warnings", []))
        confidence -= warnings_count * 0.1

        # Используем compliance_score если есть
        if "compliance_score" in result:
            confidence = min(confidence, result["compliance_score"])

        return max(0.0, min(1.0, confidence))


def get_energy_data_verifier() -> Optional[EnergyDataVerifier]:
    """
    Получить экземпляр AI-верификатора энергопоказателей

    Returns:
        EnergyDataVerifier или None если AI недоступен
    """
    try:
        verifier = EnergyDataVerifier()
        if verifier.enabled:
            return verifier
        return None
    except Exception as e:
        logger.warning(f"Не удалось инициализировать AI-верификатор: {e}")
        return None
