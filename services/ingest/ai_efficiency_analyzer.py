"""
Модуль для AI-анализа энергоэффективности
Рассчитывает показатели энергоэффективности предприятия
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
        "ai_parser модуль не найден. AI-анализ энергоэффективности недоступен."
    )


class EnergyEfficiencyAnalyzer:
    """
    Класс для AI-анализа энергоэффективности
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
                    logger.info("AI-анализ энергоэффективности включен")
                else:
                    logger.debug(
                        "AI парсер недоступен, AI-анализ энергоэффективности отключен"
                    )
            except Exception as e:
                logger.warning(
                    f"Не удалось инициализировать AI парсер для анализа энергоэффективности: {e}"
                )

    def calculate_efficiency_metrics(
        self,
        enterprise_data: Dict[str, Any],
        production_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        AI рассчитывает показатели энергоэффективности

        Args:
            enterprise_data: Данные предприятия и энергопотребления
            production_data: Данные о производстве (опционально)

        Returns:
            Словарь с показателями энергоэффективности
        """
        if not self.enabled or not self.ai_parser:
            return {
                "efficiency_metrics": {},
                "comparison_with_normatives": {},
                "potential_savings": {},
                "ai_used": False,
            }

        try:
            logger.info("Начинаю AI-анализ энергоэффективности...")

            # Формируем данные для анализа
            data_text = self._format_data_for_efficiency_analysis(
                enterprise_data, production_data
            )

            # Формируем промпт
            prompt = self._build_efficiency_analysis_prompt(data_text)

            # Отправляем запрос в AI
            ai_result = self._call_ai_efficiency_analysis(prompt)

            # Парсим результат
            parsed_result = self._parse_efficiency_result(ai_result)

            # Добавляем базовые расчеты
            basic_metrics = self._calculate_basic_metrics(
                enterprise_data, production_data
            )
            parsed_result["efficiency_metrics"].update(basic_metrics)

            logger.info("AI-анализ энергоэффективности завершен")

            return parsed_result

        except Exception as e:
            logger.error(f"Ошибка при AI-анализе энергоэффективности: {e}")
            return {
                "efficiency_metrics": {},
                "comparison_with_normatives": {},
                "potential_savings": {},
                "ai_used": False,
                "error": str(e),
            }

    def _format_data_for_efficiency_analysis(
        self,
        enterprise_data: Dict[str, Any],
        production_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Форматирует данные для анализа энергоэффективности"""
        formatted = []

        formatted.append(
            f"Данные предприятия:\n{json.dumps(enterprise_data, ensure_ascii=False, indent=2)}"
        )

        if production_data:
            formatted.append(
                f"\nДанные о производстве:\n{json.dumps(production_data, ensure_ascii=False, indent=2)}"
            )

        return "\n".join(formatted)

    def _build_efficiency_analysis_prompt(self, data_text: str) -> str:
        """Формирует промпт для анализа энергоэффективности"""
        prompt = f"""Рассчитай ключевые показатели энергоэффективности для предприятия.

{data_text[:4000]}

Рассчитай следующие показатели:

1. **Удельное энергопотребление на единицу продукции:**
   - кВт·ч на единицу продукции
   - Гкал на единицу продукции
   - м³ газа на единицу продукции

2. **Энергоемкость производства:**
   - Общая энергоемкость (т.у.т. на единицу продукции)
   - Энергоемкость по видам ресурсов
   - Динамика изменения энергоемкости

3. **Сравнение с отраслевыми нормативами:**
   - Отклонение от нормативов (%)
   - Класс энергоэффективности (A/B/C/D/E)
   - Позиция относительно средних показателей отрасли

4. **Динамика изменения показателей:**
   - Тренд энергопотребления (рост/снижение/стабильность)
   - Изменение энергоемкости по периодам
   - Сезонные колебания

5. **Потенциал энергосбережения:**
   - Оценка потенциала снижения потребления (%)
   - Приоритетные направления энергосбережения
   - Оценка экономии (сум/год)

Верни результат в формате JSON:
{{
    "efficiency_metrics": {{
        "specific_consumption": {{
            "electricity_per_unit": 123.45,
            "heat_per_unit": 67.89,
            "gas_per_unit": 12.34
        }},
        "energy_intensity": {{
            "total": 1.23,
            "by_resource": {{
                "electricity": 0.5,
                "gas": 0.4,
                "heat": 0.3
            }}
        }},
        "trend": "increasing/decreasing/stable"
    }},
    "comparison_with_normatives": {{
        "deviation_percent": 15.5,
        "energy_class": "C",
        "industry_average": 1.0,
        "enterprise_value": 1.15
    }},
    "potential_savings": {{
        "percent": 20.0,
        "priority_areas": ["освещение", "отопление"],
        "estimated_annual_savings": 5000000
    }}
}}
"""
        return prompt

    def _call_ai_efficiency_analysis(self, prompt: str) -> str:
        """Вызывает AI для анализа энергоэффективности"""
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
                            "content": "Ты эксперт по анализу энергоэффективности предприятий. Твоя задача - рассчитывать показатели энергоэффективности и сравнивать с нормативами. Всегда возвращай валидный JSON.",
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
            logger.error(f"Ошибка при вызове AI для анализа энергоэффективности: {e}")
            raise

    def _parse_efficiency_result(self, ai_response: str) -> Dict[str, Any]:
        """Парсит результат анализа энергоэффективности от AI"""
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
                "efficiency_metrics": result.get("efficiency_metrics", {}),
                "comparison_with_normatives": result.get(
                    "comparison_with_normatives", {}
                ),
                "potential_savings": result.get("potential_savings", {}),
                "ai_used": True,
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Не удалось распарсить JSON ответ AI: {e}")
            return {
                "efficiency_metrics": {},
                "comparison_with_normatives": {},
                "potential_savings": {},
                "ai_used": True,
                "raw_response": ai_response,
            }

    def _calculate_basic_metrics(
        self,
        enterprise_data: Dict[str, Any],
        production_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Вычисляет базовые метрики энергоэффективности"""
        metrics = {}

        # Базовые расчеты можно добавить здесь
        # Например, если есть данные о производстве и потреблении

        return metrics


def get_efficiency_analyzer() -> Optional[EnergyEfficiencyAnalyzer]:
    """
    Получить экземпляр AI-анализатора энергоэффективности

    Returns:
        EnergyEfficiencyAnalyzer или None если AI недоступен
    """
    try:
        analyzer = EnergyEfficiencyAnalyzer()
        if analyzer.enabled:
            return analyzer
        return None
    except Exception as e:
        logger.warning(
            f"Не удалось инициализировать AI-анализатор энергоэффективности: {e}"
        )
        return None
