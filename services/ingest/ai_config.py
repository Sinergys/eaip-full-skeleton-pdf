"""
Конфигурация для AI-системы
Поддерживает настройку для внешних API и локальных моделей
"""

import os
from typing import Dict, Any, Optional

# Конфигурация AI-системы
AI_CONFIG = {
    # Предпочтительный провайдер: auto, local, openai, anthropic, deepseek
    "preferred_provider": os.getenv("AI_PREFERRED_PROVIDER", "auto"),
    # Автоматический fallback на API если локальная модель недоступна
    "fallback_to_api": os.getenv("AI_FALLBACK_TO_API", "true").lower() == "true",
    # Пути к локальным моделям (для будущего использования)
    "local_models": {
        "ocr_enhancer": os.getenv("LOCAL_MODEL_OCR_ENHANCER", "models/ocr_enhancer"),
        "energy_verifier": os.getenv(
            "LOCAL_MODEL_ENERGY_VERIFIER", "models/energy_verifier"
        ),
        "anomaly_detector": os.getenv(
            "LOCAL_MODEL_ANOMALY_DETECTOR", "models/anomaly_detector"
        ),
        "efficiency_analyzer": os.getenv(
            "LOCAL_MODEL_EFFICIENCY_ANALYZER", "models/efficiency_analyzer"
        ),
        "compliance_checker": os.getenv(
            "LOCAL_MODEL_COMPLIANCE_CHECKER", "models/compliance_checker"
        ),
        "table_parser": os.getenv("LOCAL_MODEL_TABLE_PARSER", "models/table_parser"),
        "data_validator": os.getenv(
            "LOCAL_MODEL_DATA_VALIDATOR", "models/data_validator"
        ),
    },
    # Конфигурация внешних API провайдеров
    "api_providers": {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model_text": os.getenv("OPENAI_MODEL_TEXT", "gpt-4"),
            "model_vision": os.getenv("OPENAI_MODEL_VISION", "gpt-4-vision-preview"),
            "base_url": "https://api.openai.com/v1",
        },
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model_text": os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            "model_vision": os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            "base_url": "https://api.anthropic.com",
        },
        "deepseek": {
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "model_text": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "model_vision": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "base_url": "https://api.deepseek.com",
        },
    },
    # Настройки по умолчанию для промптов
    "default_settings": {
        "max_tokens": int(os.getenv("AI_MAX_TOKENS", "2000")),
        "temperature": float(os.getenv("AI_TEMPERATURE", "0.2")),
        "timeout": int(os.getenv("AI_TIMEOUT", "60")),
    },
    # Включение/выключение AI
    "enabled": os.getenv("AI_ENABLED", "false").lower() == "true",
    # Приоритет использования AI для PDF
    "prefer_ai_for_pdf": os.getenv("AI_PREFER_FOR_PDF", "false").lower() == "true",
}


def get_ai_config() -> Dict[str, Any]:
    """
    Получить конфигурацию AI-системы

    Returns:
        Словарь с конфигурацией
    """
    return AI_CONFIG.copy()


def get_preferred_provider() -> str:
    """Получить предпочтительный провайдер"""
    return AI_CONFIG["preferred_provider"]


def is_ai_enabled() -> bool:
    """Проверка, включен ли AI"""
    return AI_CONFIG["enabled"]


def get_local_model_path(model_name: str) -> Optional[str]:
    """
    Получить путь к локальной модели

    Args:
        model_name: Имя модели (ocr_enhancer, energy_verifier, etc.)

    Returns:
        Путь к модели или None
    """
    return AI_CONFIG["local_models"].get(model_name)


def get_api_provider_config(provider: str) -> Optional[Dict[str, Any]]:
    """
    Получить конфигурацию API провайдера

    Args:
        provider: Имя провайдера (openai, anthropic, deepseek)

    Returns:
        Конфигурация провайдера или None
    """
    return AI_CONFIG["api_providers"].get(provider)
