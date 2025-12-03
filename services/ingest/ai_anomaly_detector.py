"""
Модуль для AI-детекции аномалий в энергетических данных
Выявляет скрытые аномалии и ошибки
"""

import logging
from typing import Dict, Any, Optional, List
import json
import statistics

logger = logging.getLogger(__name__)

# Импорт AI парсера
try:
    from ai_parser import get_ai_parser

    HAS_AI_PARSER = True
except ImportError:
    HAS_AI_PARSER = False
    logger.warning("ai_parser модуль не найден. AI-детекция аномалий недоступна.")


class AnomalyDetector:
    """
    Класс для AI-детекции аномалий в энергетических данных
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
                    logger.info("AI-детекция аномалий включена")
                else:
                    logger.debug("AI парсер недоступен, AI-детекция аномалий отключена")
            except Exception as e:
                logger.warning(
                    f"Не удалось инициализировать AI парсер для детекции аномалий: {e}"
                )

    def detect_data_anomalies(
        self,
        structured_data: Dict[str, Any],
        historical_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        AI выявляет скрытые аномалии в данных

        Args:
            structured_data: Структурированные энергетические данные
            historical_data: Исторические данные для сравнения (опционально)

        Returns:
            Словарь с обнаруженными аномалиями
        """
        if not self.enabled or not self.ai_parser:
            return {
                "anomalies": [],
                "anomaly_count": 0,
                "severity_distribution": {},
                "ai_used": False,
            }

        try:
            logger.info("Начинаю AI-детекцию аномалий в энергетических данных...")

            # Статистический анализ перед AI
            statistical_anomalies = self._statistical_anomaly_detection(structured_data)

            # Формируем данные для AI
            data_text = self._format_data_for_anomaly_detection(
                structured_data, historical_data
            )

            # Формируем промпт
            prompt = self._build_anomaly_detection_prompt(
                data_text, statistical_anomalies
            )

            # Отправляем запрос в AI
            ai_result = self._call_ai_anomaly_detection(prompt)

            # Парсим результат
            parsed_result = self._parse_anomaly_result(ai_result)

            # Объединяем статистические и AI-аномалии
            all_anomalies = statistical_anomalies + parsed_result.get("anomalies", [])

            # Группируем по серьезности
            severity_distribution = self._group_by_severity(all_anomalies)

            result = {
                "anomalies": all_anomalies,
                "anomaly_count": len(all_anomalies),
                "severity_distribution": severity_distribution,
                "critical_count": len(
                    [a for a in all_anomalies if a.get("severity") == "critical"]
                ),
                "warning_count": len(
                    [a for a in all_anomalies if a.get("severity") == "warning"]
                ),
                "info_count": len(
                    [a for a in all_anomalies if a.get("severity") == "info"]
                ),
                "ai_used": True,
            }

            logger.info(
                f"AI-детекция аномалий завершена: "
                f"найдено {result['anomaly_count']} аномалий "
                f"(критических: {result['critical_count']})"
            )

            return result

        except Exception as e:
            logger.error(f"Ошибка при AI-детекции аномалий: {e}")
            return {
                "anomalies": [],
                "anomaly_count": 0,
                "severity_distribution": {},
                "ai_used": False,
                "error": str(e),
            }

    def _statistical_anomaly_detection(
        self, data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Статистический анализ для выявления аномалий"""
        anomalies = []

        # Анализ потребления электроэнергии
        if "electricity" in data:
            electricity = data["electricity"]
            # Извлекаем значения потребления
            values = self._extract_consumption_values(electricity)

            if len(values) > 2:
                mean = statistics.mean(values)
                stdev = statistics.stdev(values) if len(values) > 1 else 0

                # Аномалии: значения > 3 стандартных отклонений
                threshold = mean + 3 * stdev
                for i, value in enumerate(values):
                    if value > threshold:
                        anomalies.append(
                            {
                                "type": "statistical_outlier",
                                "resource": "electricity",
                                "value": value,
                                "mean": mean,
                                "threshold": threshold,
                                "severity": "warning",
                                "description": f"Потребление электроэнергии ({value}) значительно превышает среднее значение ({mean:.2f})",
                            }
                        )

        return anomalies

    def _extract_consumption_values(self, data: Any) -> List[float]:
        """Извлекает числовые значения потребления из данных"""
        values = []

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    values.append(float(value))
                elif isinstance(value, dict):
                    values.extend(self._extract_consumption_values(value))
                elif isinstance(value, list):
                    for item in value:
                        values.extend(self._extract_consumption_values(item))
        elif isinstance(data, list):
            for item in data:
                values.extend(self._extract_consumption_values(item))

        return values

    def _format_data_for_anomaly_detection(
        self, data: Dict[str, Any], historical: Optional[Dict[str, Any]] = None
    ) -> str:
        """Форматирует данные для детекции аномалий"""
        formatted = []

        formatted.append(
            f"Текущие данные:\n{json.dumps(data, ensure_ascii=False, indent=2)}"
        )

        if historical:
            formatted.append(
                f"\nИсторические данные для сравнения:\n{json.dumps(historical, ensure_ascii=False, indent=2)}"
            )

        return "\n".join(formatted)

    def _build_anomaly_detection_prompt(
        self, data_text: str, statistical_anomalies: List[Dict[str, Any]]
    ) -> str:
        """Формирует промпт для детекции аномалий"""
        prompt = f"""Проанализируй энергетические данные на аномалии и ошибки.

{data_text[:4000]}

Ищи следующие типы аномалий:

1. **Резкие скачки потребления без причины:**
   - Внезапное увеличение потребления на 50%+ без объяснения
   - Резкое снижение потребления до нуля в активный период
   - Несоответствие сезонным паттернам

2. **Несоответствие между связанными показателями:**
   - Активная энергия vs реактивная энергия
   - Потребление газа vs выработка тепла
   - Общее потребление ≠ сумма по категориям

3. **Данные вне типичных диапазонов:**
   - Отрицательные значения потребления
   - Значения, превышающие технические возможности оборудования
   - Нереалистично большие или малые значения

4. **Признаки ошибок ввода или измерений:**
   - Одинаковые значения в разные периоды
   - Пропуски данных в критических периодах
   - Несоответствие единиц измерения

5. **Противоречия в отчетных периодах:**
   - Квартальные суммы не соответствуют месячным данным
   - Годовые итоги не соответствуют квартальным
   - Несоответствие дат и периодов

Статистические аномалии (уже обнаружены):
{json.dumps(statistical_anomalies, ensure_ascii=False, indent=2) if statistical_anomalies else "Нет"}

Верни результат в формате JSON:
{{
    "anomalies": [
        {{
            "type": "spike/contradiction/outlier/error",
            "resource": "электроэнергия/газ/вода",
            "period": "2024-Q1",
            "value": 1234.56,
            "expected_range": [100, 1000],
            "severity": "critical/warning/info",
            "description": "подробное описание аномалии",
            "suggestion": "рекомендация по исправлению"
        }}
    ],
    "summary": {{
        "total_anomalies": 5,
        "critical": 1,
        "warnings": 3,
        "info": 1
    }}
}}
"""
        return prompt

    def _call_ai_anomaly_detection(self, prompt: str) -> str:
        """Вызывает AI для детекции аномалий"""
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
                            "content": "Ты эксперт по анализу энергетических данных. Твоя задача - выявлять аномалии, ошибки и несоответствия. Всегда возвращай валидный JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"}
                    if provider == "openai"
                    else None,
                    max_tokens=3000,
                    temperature=0.3,
                )
                return response.choices[0].message.content.strip()

            elif provider == "anthropic":
                response = self.ai_parser.client.messages.create(
                    model=self.ai_parser.model_text,
                    max_tokens=3000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text.strip()

            else:
                raise ValueError(f"Неподдерживаемый провайдер: {provider}")

        except Exception as e:
            logger.error(f"Ошибка при вызове AI для детекции аномалий: {e}")
            raise

    def _parse_anomaly_result(self, ai_response: str) -> Dict[str, Any]:
        """Парсит результат детекции аномалий от AI"""
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
                "anomalies": result.get("anomalies", []),
                "summary": result.get("summary", {}),
                "ai_used": True,
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Не удалось распарсить JSON ответ AI: {e}")
            return {
                "anomalies": [],
                "summary": {},
                "ai_used": True,
                "raw_response": ai_response,
            }

    def _group_by_severity(self, anomalies: List[Dict[str, Any]]) -> Dict[str, int]:
        """Группирует аномалии по серьезности"""
        distribution = {"critical": 0, "warning": 0, "info": 0}

        for anomaly in anomalies:
            severity = anomaly.get("severity", "info")
            distribution[severity] = distribution.get(severity, 0) + 1

        return distribution


def get_anomaly_detector() -> Optional[AnomalyDetector]:
    """
    Получить экземпляр AI-детектора аномалий

    Returns:
        AnomalyDetector или None если AI недоступен
    """
    try:
        detector = AnomalyDetector()
        if detector.enabled:
            return detector
        return None
    except Exception as e:
        logger.warning(f"Не удалось инициализировать AI-детектор аномалий: {e}")
        return None
