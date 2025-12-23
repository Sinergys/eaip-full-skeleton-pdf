"""
Модуль для генерации отчетов о качестве данных
Создает детальные отчеты на основе AI-анализа
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataQualityReporter:
    """
    Класс для генерации отчетов о качестве данных
    """

    def __init__(self):
        pass

    def generate_quality_report(
        self,
        ai_analysis: Dict[str, Any],
        extraction_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Генерирует детальный отчет о качестве данных

        Args:
            ai_analysis: Результаты AI-анализа
            extraction_result: Результаты извлечения данных (опционально)

        Returns:
            Словарь с отчетом о качестве данных
        """
        try:
            logger.info("Генерирую отчет о качестве данных...")

            # Вычисляем общий score
            overall_score = self.calculate_overall_score(ai_analysis)

            # Статус верификации
            verification_status = self._get_verification_status(ai_analysis)

            # Количество аномалий
            anomalies_found = ai_analysis.get("anomalies", {}).get("anomaly_count", 0)

            # Метрики энергоэффективности
            efficiency_metrics = ai_analysis.get("efficiency", {}).get(
                "efficiency_metrics", {}
            )

            # Проблемы соответствия
            compliance_issues = ai_analysis.get("compliance", {}).get("issues", [])

            # Рекомендации
            recommendations = self.generate_recommendations(ai_analysis)

            # Детальная разбивка по категориям
            category_scores = self._calculate_category_scores(ai_analysis)

            report = {
                "generated_at": datetime.now().isoformat(),
                "overall_score": overall_score,
                "confidence_score": ai_analysis.get("confidence_score", 0.0),
                "verification_status": verification_status,
                "anomalies_found": anomalies_found,
                "anomalies_breakdown": {
                    "critical": ai_analysis.get("anomalies", {}).get(
                        "critical_count", 0
                    ),
                    "warning": ai_analysis.get("anomalies", {}).get("warning_count", 0),
                    "info": ai_analysis.get("anomalies", {}).get("info_count", 0),
                },
                "efficiency_metrics": efficiency_metrics,
                "efficiency_class": ai_analysis.get("efficiency", {})
                .get("comparison_with_normatives", {})
                .get("energy_class", "N/A"),
                "compliance_status": {
                    "is_compliant": ai_analysis.get("compliance", {}).get(
                        "is_compliant", True
                    ),
                    "compliance_score": ai_analysis.get("compliance", {}).get(
                        "compliance_score", 0.5
                    ),
                    "missing_sections": ai_analysis.get("compliance", {}).get(
                        "missing_sections", []
                    ),
                    "issues_count": len(compliance_issues),
                },
                "compliance_issues": compliance_issues,
                "recommendations": recommendations,
                "category_scores": category_scores,
                "summary": {
                    "is_valid": ai_analysis.get("summary", {}).get("is_valid", True),
                    "has_anomalies": ai_analysis.get("summary", {}).get(
                        "has_anomalies", False
                    ),
                    "is_compliant": ai_analysis.get("summary", {}).get(
                        "is_compliant", True
                    ),
                    "needs_review": overall_score < 0.7
                    or anomalies_found > 0
                    or not ai_analysis.get("summary", {}).get("is_compliant", True),
                },
            }

            logger.info(
                f"Отчет о качестве данных сгенерирован: "
                f"общий score: {overall_score:.2f}, "
                f"аномалий: {anomalies_found}, "
                f"требует проверки: {report['summary']['needs_review']}"
            )

            return report

        except Exception as e:
            logger.error(f"Ошибка при генерации отчета о качестве данных: {e}")
            return {
                "error": str(e),
                "overall_score": 0.0,
                "generated_at": datetime.now().isoformat(),
            }

    def calculate_overall_score(self, ai_analysis: Dict[str, Any]) -> float:
        """
        Вычисляет общую оценку качества данных

        Args:
            ai_analysis: Результаты AI-анализа

        Returns:
            Оценка от 0.0 до 1.0
        """
        # Используем confidence_score как основу
        base_score = ai_analysis.get("confidence_score", 0.5)

        # Корректируем на основе верификации
        verification = ai_analysis.get("verification", {})
        if verification.get("is_valid", True):
            verification_bonus = 0.1
        else:
            verification_bonus = -0.3

        # Корректируем на основе аномалий
        anomalies = ai_analysis.get("anomalies", {})
        critical_anomalies = anomalies.get("critical_count", 0)
        warning_anomalies = anomalies.get("warning_count", 0)
        anomaly_penalty = critical_anomalies * 0.2 + warning_anomalies * 0.05

        # Корректируем на основе соответствия
        compliance = ai_analysis.get("compliance", {})
        compliance_score = compliance.get("compliance_score", 0.5)
        compliance_factor = compliance_score

        # Итоговый score
        overall_score = base_score + verification_bonus - anomaly_penalty
        overall_score = (overall_score + compliance_factor) / 2

        return max(0.0, min(1.0, overall_score))

    def _get_verification_status(self, ai_analysis: Dict[str, Any]) -> str:
        """Определяет статус верификации"""
        verification = ai_analysis.get("verification", {})

        if not verification.get("is_valid", True):
            return "failed"

        confidence = verification.get("confidence", 0.5)
        if confidence >= 0.9:
            return "excellent"
        elif confidence >= 0.7:
            return "good"
        elif confidence >= 0.5:
            return "acceptable"
        else:
            return "poor"

    def _calculate_category_scores(
        self, ai_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Вычисляет оценки по категориям"""
        scores = {}

        # Верификация
        verification = ai_analysis.get("verification", {})
        scores["verification"] = verification.get("confidence", 0.5)

        # Соответствие
        compliance = ai_analysis.get("compliance", {})
        scores["compliance"] = compliance.get("compliance_score", 0.5)

        # Качество данных (на основе аномалий)
        anomalies = ai_analysis.get("anomalies", {})
        anomaly_count = anomalies.get("anomaly_count", 0)
        if anomaly_count == 0:
            scores["data_quality"] = 1.0
        else:
            # Снижаем оценку за аномалии
            scores["data_quality"] = max(0.0, 1.0 - (anomaly_count * 0.1))

        # Энергоэффективность (если есть данные)
        efficiency = ai_analysis.get("efficiency", {})
        if efficiency:
            # Используем отклонение от нормативов
            comparison = efficiency.get("comparison_with_normatives", {})
            deviation = abs(comparison.get("deviation_percent", 0))
            # Меньше отклонение = лучше
            scores["efficiency"] = max(0.0, 1.0 - (deviation / 100))
        else:
            scores["efficiency"] = 0.5  # Нет данных

        return scores

    def generate_recommendations(
        self, ai_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Генерирует рекомендации на основе AI-анализа

        Args:
            ai_analysis: Результаты AI-анализа

        Returns:
            Список рекомендаций
        """
        recommendations = []

        # Рекомендации на основе верификации
        verification = ai_analysis.get("verification", {})
        if not verification.get("is_valid", True):
            recommendations.append(
                {
                    "type": "critical",
                    "category": "verification",
                    "title": "Данные не прошли верификацию",
                    "description": "Обнаружены критические проблемы при верификации данных",
                    "action": "Проверьте данные вручную и исправьте выявленные проблемы",
                }
            )

        issues = verification.get("issues", [])
        for issue in issues[:3]:  # Берем первые 3 проблемы
            if issue.get("severity") == "critical":
                recommendations.append(
                    {
                        "type": "critical",
                        "category": "verification",
                        "title": issue.get("issue", "Проблема в данных"),
                        "description": issue.get("suggestion", ""),
                        "action": "Исправьте проблему перед сохранением данных",
                    }
                )

        # Рекомендации на основе аномалий
        anomalies = ai_analysis.get("anomalies", {})
        if anomalies.get("critical_count", 0) > 0:
            recommendations.append(
                {
                    "type": "critical",
                    "category": "anomalies",
                    "title": f"Обнаружено {anomalies['critical_count']} критических аномалий",
                    "description": "Данные содержат критические аномалии, требующие проверки",
                    "action": "Проверьте данные на наличие ошибок ввода или измерений",
                }
            )

        # Рекомендации на основе соответствия
        compliance = ai_analysis.get("compliance", {})
        if not compliance.get("is_compliant", True):
            missing_sections = compliance.get("missing_sections", [])
            if missing_sections:
                recommendations.append(
                    {
                        "type": "warning",
                        "category": "compliance",
                        "title": f"Отсутствуют обязательные разделы: {', '.join(missing_sections[:3])}",
                        "description": "Энергетический паспорт не соответствует требованиям ПКМ №690",
                        "action": "Добавьте недостающие разделы для полного соответствия",
                    }
                )

        # Рекомендации на основе энергоэффективности
        efficiency = ai_analysis.get("efficiency", {})
        potential_savings = efficiency.get("potential_savings", {})
        if potential_savings.get("percent", 0) > 10:
            recommendations.append(
                {
                    "type": "info",
                    "category": "efficiency",
                    "title": f"Потенциал энергосбережения: {potential_savings['percent']:.1f}%",
                    "description": f"Оценка годовой экономии: {potential_savings.get('estimated_annual_savings', 0):,.0f} сум",
                    "action": f"Рассмотрите мероприятия в областях: {', '.join(potential_savings.get('priority_areas', [])[:3])}",
                }
            )

        return recommendations

    def generate_summary_text(self, report: Dict[str, Any]) -> str:
        """
        Генерирует текстовую сводку отчета

        Args:
            report: Отчет о качестве данных

        Returns:
            Текстовая сводка
        """
        lines = []

        lines.append(f"Оценка качества данных: {report['overall_score']:.1%}")
        lines.append(f"Уверенность: {report['confidence_score']:.1%}")
        lines.append(f"Статус верификации: {report['verification_status']}")
        lines.append(f"Обнаружено аномалий: {report['anomalies_found']}")

        if report["compliance_status"]["is_compliant"]:
            lines.append("Соответствие ПКМ №690: ✓")
        else:
            lines.append(
                f"Соответствие ПКМ №690: ✗ (отсутствует разделов: {len(report['compliance_status']['missing_sections'])})"
            )

        if report["summary"]["needs_review"]:
            lines.append("⚠ Требуется ручная проверка")

        return "\n".join(lines)


def get_quality_reporter() -> DataQualityReporter:
    """
    Получить экземпляр генератора отчетов о качестве

    Returns:
        DataQualityReporter
    """
    return DataQualityReporter()
