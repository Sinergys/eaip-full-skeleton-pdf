"""
Детерминистический классификатор использования электроэнергии по категориям.

Классифицирует оборудование на 4 категории:
- technological (технологические)
- own_needs (собственные нужды)
- production (производственные)
- household (хоз-бытовые)

Использует конфигурацию из passport_field_map.py как единый источник истины.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from ai.ai_excel_semantic_parser import EquipmentItem, NodeItem
from domain.passport_field_map import (
    ELECTRICITY_USAGE_KEYWORDS,
    ELECTRICITY_USAGE_COLUMN_MAP,
    USAGE_CLASSIFICATION_PRIORITY,
    ELECTRICITY_USAGE_TECH,
    ELECTRICITY_USAGE_OWN,
    ELECTRICITY_USAGE_PROD,
    ELECTRICITY_USAGE_HOUSEHOLD,
)

logger = logging.getLogger(__name__)


def _normalize_category_id(category_id: str) -> str:
    """
    Нормализует строку категории к стандартному ID.

    Args:
            category_id: Строка с категорией (может быть на RU/UZ/EN)

    Returns:
            Нормализованный ID категории
    """
    if not category_id:
        return ELECTRICITY_USAGE_PROD  # default

    s = category_id.strip().lower()

    # Прямые маппинги
    aliases = {
        # RU variants
        "технолог": ELECTRICITY_USAGE_TECH,
        "технологический": ELECTRICITY_USAGE_TECH,
        "технология": ELECTRICITY_USAGE_TECH,
        "собственные нужды": ELECTRICITY_USAGE_OWN,
        "с.н.": ELECTRICITY_USAGE_OWN,
        "собств. нужды": ELECTRICITY_USAGE_OWN,
        "производств": ELECTRICITY_USAGE_PROD,
        "производственный": ELECTRICITY_USAGE_PROD,
        "хоз-быт": ELECTRICITY_USAGE_HOUSEHOLD,
        "хозбыт": ELECTRICITY_USAGE_HOUSEHOLD,
        "хозяйственно-бытовые": ELECTRICITY_USAGE_HOUSEHOLD,
        "бытовые": ELECTRICITY_USAGE_HOUSEHOLD,
        "быт": ELECTRICITY_USAGE_HOUSEHOLD,
        # EN variants
        "tech": ELECTRICITY_USAGE_TECH,
        "techn": ELECTRICITY_USAGE_TECH,
        "technological": ELECTRICITY_USAGE_TECH,
        "own": ELECTRICITY_USAGE_OWN,
        "aux": ELECTRICITY_USAGE_OWN,
        "own_needs": ELECTRICITY_USAGE_OWN,
        "prod": ELECTRICITY_USAGE_PROD,
        "production": ELECTRICITY_USAGE_PROD,
        "general": ELECTRICITY_USAGE_PROD,
        "house": ELECTRICITY_USAGE_HOUSEHOLD,
        "household": ELECTRICITY_USAGE_HOUSEHOLD,
    }

    # Проверяем точное совпадение
    if s in aliases:
        return aliases[s]

    # Проверяем частичное совпадение
    for alias, category in aliases.items():
        if alias in s or s in alias:
            return category

    # Проверяем по ключевым словам из конфигурации
    for category_id_key, keywords in ELECTRICITY_USAGE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in s:
                return category_id_key

    # По умолчанию
    return ELECTRICITY_USAGE_PROD


def _check_keywords_in_text(text: str, category_id: str) -> bool:
    """
    Проверяет наличие ключевых слов категории в тексте.

    Args:
            text: Текст для проверки
            category_id: ID категории

    Returns:
            True если найдено совпадение
    """
    if not text:
        return False

    text_lower = text.lower()
    keywords = ELECTRICITY_USAGE_KEYWORDS.get(category_id, [])

    for keyword in keywords:
        if keyword.lower() in text_lower:
            return True

    return False


def _classify_by_nodes(
    item: EquipmentItem, nodes: Optional[List[NodeItem]]
) -> Optional[str]:
    """
    Пытается классифицировать оборудование на основе узлов учета.

    Это опциональная эвристика второго уровня.

    Args:
            item: Оборудование
            nodes: Список узлов учета

    Returns:
            ID категории или None
    """
    if not nodes or not item.location:
        return None

    item_location_lower = item.location.lower()

    for node in nodes:
        if not isinstance(node, NodeItem):
            continue

        node_location = (node.location or "").lower()
        if not node_location:
            continue

        # Если оборудование и узел в одном месте
        if item_location_lower in node_location or node_location in item_location_lower:
            # Эвристики по location узла
            if any(
                kw in node_location for kw in ["котельная", "котел", "подстанц", "тп"]
            ):
                return ELECTRICITY_USAGE_OWN
            if any(kw in node_location for kw in ["офис", "админ", "склад"]):
                return ELECTRICITY_USAGE_HOUSEHOLD
            if any(kw in node_location for kw in ["цех", "участок"]):
                return ELECTRICITY_USAGE_PROD

    return None


def classify_equipment_usage(
    item: EquipmentItem, nodes: Optional[List[NodeItem]] = None
) -> str:
    """
    Классифицирует оборудование по категории использования электроэнергии.

    Детерминистическая процедура с четким приоритетом:
    1. Явное указание в extra/metadata
    2. Анализ по ключевым словам в name/type/location
    3. Анализ по узлам учета (опционально)
    4. Значение по умолчанию (production)

    Args:
            item: Оборудование для классификации
            nodes: Список узлов учета (опционально, для улучшения классификации)

    Returns:
            ID категории использования: "technological", "own_needs", "production", "household"
    """
    # Приоритет 1: Явное указание в extra/metadata
    try:
        extra = getattr(item, "extra", {}) or {}
        if not isinstance(extra, dict):
            extra = {}

        # Проверяем возможные ключи
        for key in ELECTRICITY_USAGE_COLUMN_MAP:
            if key in extra:
                value = extra[key]
                if isinstance(value, str) and value.strip():
                    normalized = _normalize_category_id(value)
                    if (
                        normalized != ELECTRICITY_USAGE_PROD
                        or value.strip().lower() in ["производств", "production"]
                    ):
                        logger.debug(
                            f"Классификация по extra.{key}='{value}' → {normalized}"
                        )
                        return normalized
    except Exception as e:
        logger.debug(f"Ошибка при проверке extra: {e}")

    # Приоритет 2: Анализ по ключевым словам
    # Собираем все текстовые поля
    text_fields = []

    name = (getattr(item, "name", "") or "").strip()
    if name:
        text_fields.append(("name", name))

    typ = (getattr(item, "type", "") or "").strip()
    if typ:
        text_fields.append(("type", typ))

    location = (getattr(item, "location", "") or "").strip()
    if location:
        text_fields.append(("location", location))

    notes = (getattr(item, "notes", "") or "").strip()
    if notes:
        text_fields.append(("notes", notes))

    # Проверяем каждую категорию в порядке приоритета
    matched_categories = []
    for category_id in USAGE_CLASSIFICATION_PRIORITY:
        for field_name, field_value in text_fields:
            if _check_keywords_in_text(field_value, category_id):
                matched_categories.append((category_id, field_name, field_value))
                break  # Одна категория может совпасть только один раз

    # Если найдено несколько совпадений, берем первое по приоритету
    if matched_categories:
        result = matched_categories[0][0]
        logger.debug(
            f"Классификация по ключевым словам: {matched_categories[0]} → {result}"
        )
        return result

    # Приоритет 3: Анализ по узлам учета (опционально)
    if nodes:
        node_based = _classify_by_nodes(item, nodes)
        if node_based:
            logger.debug(f"Классификация по узлам учета → {node_based}")
            return node_based

    # Приоритет 4: Значение по умолчанию
    logger.debug(f"Классификация по умолчанию → {ELECTRICITY_USAGE_PROD}")
    return ELECTRICITY_USAGE_PROD
