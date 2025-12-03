"""
Модуль для полного AI-анализа энергетических данных
Объединяет верификацию, детекцию аномалий, анализ эффективности и проверку соответствия
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Импорты AI-модулей
try:
    from ai_energy_verifier import get_energy_data_verifier
    from ai_anomaly_detector import get_anomaly_detector
    from ai_efficiency_analyzer import get_efficiency_analyzer
    from ai_compliance_checker import get_compliance_checker

    HAS_AI_ANALYSIS = True
except ImportError:
    HAS_AI_ANALYSIS = False
    logger.warning("AI-модули анализа недоступны")


def enhanced_energy_analysis(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Полный AI-анализ энергетических данных

    Args:
        extracted_data: Извлеченные энергетические данные

    Returns:
        Словарь с результатами полного анализа
    """
    if not HAS_AI_ANALYSIS:
        return {
            "error": "AI-анализ недоступен",
            "verification": {},
            "anomalies": {},
            "efficiency": {},
            "compliance": {},
        }

    try:
        logger.info("Начинаю полный AI-анализ энергетических данных...")

        # 1. Верификация данных
        verifier = get_energy_data_verifier()
        verification = {}
        if verifier:
            verification = verifier.verify_energy_metrics(extracted_data)
            if not verification.get("is_valid", True):
                logger.warning("Данные не прошли верификацию")

        # 2. Детекция аномалий
        detector = get_anomaly_detector()
        anomalies = {}
        if detector:
            anomalies = detector.detect_data_anomalies(extracted_data)

        # 3. Анализ энергоэффективности
        analyzer = get_efficiency_analyzer()
        efficiency = {}
        if analyzer:
            efficiency = analyzer.calculate_efficiency_metrics(extracted_data)

        # 4. Проверка соответствия нормам
        checker = get_compliance_checker()
        compliance = {}
        if checker:
            compliance = checker.check_compliance(extracted_data)

        # Вычисляем общую уверенность
        confidence_score = calculate_confidence(verification, anomalies, compliance)

        result = {
            "verification": verification,
            "anomalies": anomalies,
            "efficiency": efficiency,
            "compliance": compliance,
            "confidence_score": confidence_score,
            "summary": {
                "is_valid": verification.get("is_valid", True),
                "has_anomalies": anomalies.get("anomaly_count", 0) > 0,
                "is_compliant": compliance.get("is_compliant", True),
                "efficiency_class": efficiency.get(
                    "comparison_with_normatives", {}
                ).get("energy_class", "N/A"),
            },
        }

        logger.info(
            f"Полный AI-анализ завершен: "
            f"валидно: {result['summary']['is_valid']}, "
            f"аномалий: {anomalies.get('anomaly_count', 0)}, "
            f"соответствует: {result['summary']['is_compliant']}, "
            f"уверенность: {confidence_score:.2f}"
        )

        return result

    except Exception as e:
        logger.error(f"Ошибка при полном AI-анализе: {e}")
        return {
            "error": str(e),
            "verification": {},
            "anomalies": {},
            "efficiency": {},
            "compliance": {},
        }


def calculate_confidence(
    verification: Dict[str, Any], anomalies: Dict[str, Any], compliance: Dict[str, Any]
) -> float:
    """Вычисляет общую уверенность в данных"""
    confidence = 1.0

    # Влияние верификации
    if "confidence" in verification:
        confidence *= verification["confidence"]

    # Влияние аномалий
    critical_anomalies = anomalies.get("critical_count", 0)
    confidence *= 1 - critical_anomalies * 0.2

    # Влияние соответствия
    if "compliance_score" in compliance:
        confidence *= compliance["compliance_score"]

    return max(0.0, min(1.0, confidence))
