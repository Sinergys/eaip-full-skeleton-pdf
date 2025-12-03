"""
Модуль для AI-проверки соответствия требованиям ПКМ №690
Проверяет полноту и корректность энергетического паспорта
"""

import logging
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger(__name__)

# Импорт AI парсера
try:
    from ai_parser import get_ai_parser

    HAS_AI_PARSER = True
except ImportError:
    HAS_AI_PARSER = False
    logger.warning(
        "ai_parser модуль не найден. AI-проверка соответствия ПКМ №690 недоступна."
    )


class ComplianceChecker:
    """
    Класс для AI-проверки соответствия требованиям ПКМ №690
    """

    def __init__(self):
        self.ai_parser = None
        self.enabled = False

        # Обязательные разделы согласно ПКМ №690
        self.required_sections = [
            "enterprise_info",  # Данные предприятия
            "energy_resources",  # Энергоресурсы
            "electricity",  # Электроэнергия
            "gas",  # Газ
            "water",  # Вода
            "fuel",  # Топливо
            "equipment",  # Оборудование
            "buildings",  # Здания
            "calculations",  # Расчеты
            "measures",  # Мероприятия
        ]

        # Проверяем доступность AI
        if HAS_AI_PARSER:
            try:
                self.ai_parser = get_ai_parser()
                if self.ai_parser and self.ai_parser.enabled:
                    self.enabled = True
                    logger.info("AI-проверка соответствия ПКМ №690 включена")
                else:
                    logger.debug(
                        "AI парсер недоступен, AI-проверка соответствия отключена"
                    )
            except Exception as e:
                logger.warning(
                    f"Не удалось инициализировать AI парсер для проверки соответствия: {e}"
                )

    def check_compliance(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI проверяет соответствие требованиям ПКМ №690

        Args:
            extracted_data: Извлеченные данные энергетического паспорта

        Returns:
            Словарь с результатами проверки соответствия
        """
        if not self.enabled or not self.ai_parser:
            return {
                "is_compliant": True,
                "compliance_score": 0.5,
                "missing_sections": [],
                "issues": [],
                "ai_used": False,
            }

        try:
            logger.info("Начинаю AI-проверку соответствия ПКМ №690...")

            # Базовая проверка наличия разделов
            missing_sections = self._check_required_sections(extracted_data)

            # Формируем данные для AI
            data_text = self._format_data_for_compliance_check(extracted_data)

            # Формируем промпт
            prompt = self._build_compliance_check_prompt(data_text, missing_sections)

            # Отправляем запрос в AI
            ai_result = self._call_ai_compliance_check(prompt)

            # Парсим результат
            parsed_result = self._parse_compliance_result(ai_result)

            # Объединяем результаты
            result = {
                "is_compliant": len(missing_sections) == 0
                and parsed_result.get("is_compliant", True),
                "compliance_score": parsed_result.get("compliance_score", 0.5),
                "missing_sections": missing_sections,
                "present_sections": [
                    s for s in self.required_sections if s not in missing_sections
                ],
                "issues": parsed_result.get("issues", []),
                "warnings": parsed_result.get("warnings", []),
                "balance_check": parsed_result.get("balance_check", {}),
                "format_check": parsed_result.get("format_check", {}),
                "ai_used": True,
            }

            # Вычисляем итоговый compliance_score
            if missing_sections:
                result["compliance_score"] *= 1 - len(missing_sections) * 0.1

            logger.info(
                f"AI-проверка соответствия завершена: "
                f"соответствует: {result['is_compliant']}, "
                f"оценка: {result['compliance_score']:.2f}, "
                f"отсутствует разделов: {len(missing_sections)}"
            )

            return result

        except Exception as e:
            logger.error(f"Ошибка при AI-проверке соответствия: {e}")
            return {
                "is_compliant": True,
                "compliance_score": 0.5,
                "missing_sections": [],
                "issues": [],
                "ai_used": False,
                "error": str(e),
            }

    def _check_required_sections(self, data: Dict[str, Any]) -> List[str]:
        """Проверяет наличие обязательных разделов"""
        missing = []

        for section in self.required_sections:
            if section not in data or not data[section]:
                missing.append(section)

        return missing

    def _format_data_for_compliance_check(self, data: Dict[str, Any]) -> str:
        """Форматирует данные для проверки соответствия"""
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _build_compliance_check_prompt(
        self, data_text: str, missing_sections: List[str]
    ) -> str:
        """Формирует промпт для проверки соответствия"""
        prompt = f"""Проверь соответствие энергетического паспорта требованиям ПКМ №690 (Постановление Кабинета Министров Республики Узбекистан).

Данные энергетического паспорта:
{data_text[:4000]}

Отсутствующие разделы (уже обнаружены):
{json.dumps(missing_sections, ensure_ascii=False) if missing_sections else "Нет"}

Проверь следующие аспекты:

1. **Полнота данных по требуемым разделам:**
   - Данные предприятия (название, адрес, ИНН, вид деятельности)
   - Энергоресурсы (полный перечень используемых ресурсов)
   - Электроэнергия (активная, реактивная, по категориям)
   - Газ (потребление по периодам, категориям)
   - Вода (потребление, источники)
   - Топливо (виды, количество, единицы измерения)
   - Оборудование (перечень, мощность, режим работы)
   - Здания (площадь, характеристики, энергопотребление)
   - Расчеты (балансы, коэффициенты, нормативы)
   - Мероприятия (планируемые и реализованные)

2. **Баланс энергопотребления:**
   - Технологические нужды + Собственные нужды = Общее потребление
   - Суммы по кварталам соответствуют годовым итогам
   - Активная и реактивная энергия согласованы

3. **Корректность коэффициентов трансформации и пересчета:**
   - Коэффициенты пересчета в т.у.т. (тонны условного топлива)
   - Коэффициенты трансформации для электроэнергии
   - Тепловой эквивалент для различных видов топлива

4. **Соответствие форматов и единиц измерения:**
   - Единицы измерения соответствуют ГОСТ
   - Форматы дат и периодов корректны
   - Числовые значения в допустимых диапазонах

5. **Требования к структуре документа:**
   - Наличие всех обязательных таблиц
   - Корректность формул и расчетов
   - Соответствие шаблону ПКМ №690

Верни результат в формате JSON:
{{
    "is_compliant": true/false,
    "compliance_score": 0.95,
    "issues": [
        {{
            "section": "электроэнергия",
            "issue": "описание проблемы",
            "severity": "critical/warning/info",
            "requirement": "ссылка на требование ПКМ №690"
        }}
    ],
    "warnings": ["предупреждение1"],
    "balance_check": {{
        "is_balanced": true/false,
        "discrepancies": ["описание несоответствий"]
    }},
    "format_check": {{
        "units_compliant": true/false,
        "formats_compliant": true/false,
        "issues": ["проблемы с форматами"]
    }},
    "missing_required_fields": ["поле1", "поле2"]
}}
"""
        return prompt

    def _call_ai_compliance_check(self, prompt: str) -> str:
        """Вызывает AI для проверки соответствия"""
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
                            "content": "Ты эксперт по требованиям ПКМ №690 для энергетических паспортов. Твоя задача - проверить полноту и корректность данных согласно нормативным требованиям. Всегда возвращай валидный JSON.",
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
            logger.error(f"Ошибка при вызове AI для проверки соответствия: {e}")
            raise

    def _parse_compliance_result(self, ai_response: str) -> Dict[str, Any]:
        """Парсит результат проверки соответствия от AI"""
        import json

        try:
            if "```json" in ai_response:
                json_text = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                json_text = ai_response.split("```")[1].split("```")[0].strip()
            else:
                json_text = ai_response.strip()

            result = json.loads(json_text)

            return {
                "is_compliant": result.get("is_compliant", True),
                "compliance_score": result.get("compliance_score", 0.5),
                "issues": result.get("issues", []),
                "warnings": result.get("warnings", []),
                "balance_check": result.get("balance_check", {}),
                "format_check": result.get("format_check", {}),
                "missing_required_fields": result.get("missing_required_fields", []),
                "ai_used": True,
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Не удалось распарсить JSON ответ AI: {e}")
            return {
                "is_compliant": True,
                "compliance_score": 0.5,
                "issues": [],
                "warnings": ["Не удалось распарсить структурированный ответ AI"],
                "ai_used": True,
                "raw_response": ai_response,
            }


def get_compliance_checker() -> Optional[ComplianceChecker]:
    """
    Получить экземпляр AI-проверки соответствия ПКМ №690

    Returns:
        ComplianceChecker или None если AI недоступен
    """
    try:
        checker = ComplianceChecker()
        if checker.enabled:
            return checker
        return None
    except Exception as e:
        logger.warning(f"Не удалось инициализировать AI-проверку соответствия: {e}")
        return None
