"""
Модуль для проверки соответствия фактических значений нормативным требованиям
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Импорт database функций
try:
    import database

    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    logger.error("database модуль не найден.")


def validate_against_normative(
    actual_value: float,
    field_name: str,
    sheet_name: Optional[str] = None,
    tolerance_percent: float = 10.0,
) -> Dict[str, Any]:
    """
    Проверить соответствие фактического значения нормативу

    Args:
        actual_value: Фактическое значение
        field_name: Название поля энергопаспорта
        sheet_name: Имя листа (опционально)
        tolerance_percent: Допустимое отклонение в процентах (по умолчанию 10%)

    Returns:
        Словарь с результатами проверки:
        {
            "status": "compliant" | "violation" | "unknown",
            "actual": float,
            "normative": float | None,
            "deviation_percent": float,
            "message": str,
            "rule": dict | None  # Правило из БД
        }
    """
    if not HAS_DATABASE:
        logger.warning("database модуль недоступен, проверка невозможна")
        return {
            "status": "unknown",
            "actual": actual_value,
            "normative": None,
            "deviation_percent": 0.0,
            "message": "База данных недоступна",
            "rule": None,
        }

    # Получаем нормативы для поля
    try:
        rules = database.get_normative_rules_for_field(field_name, sheet_name)
    except Exception as e:
        logger.error(f"Ошибка получения нормативов для поля {field_name}: {e}")
        return {
            "status": "unknown",
            "actual": actual_value,
            "normative": None,
            "deviation_percent": 0.0,
            "message": f"Ошибка получения нормативов: {e}",
            "rule": None,
        }

    if not rules:
        return {
            "status": "unknown",
            "actual": actual_value,
            "normative": None,
            "deviation_percent": 0.0,
            "message": f"Норматив не найден для поля '{field_name}'",
            "rule": None,
        }

    # Берем норматив с наивысшей уверенностью (confidence)
    best_rule = max(
        rules,
        key=lambda r: r.get("extraction_confidence", 0.0) or 0.0,
    )

    normative_value = best_rule.get("numeric_value")

    if normative_value is None:
        return {
            "status": "unknown",
            "actual": actual_value,
            "normative": None,
            "deviation_percent": 0.0,
            "message": "Норматив не имеет числового значения",
            "rule": best_rule,
        }

    # Вычисляем отклонение
    if normative_value == 0:
        deviation_percent = 0.0 if actual_value == 0 else float("inf")
    else:
        deviation_percent = abs(actual_value - normative_value) / abs(normative_value) * 100

    # Определяем статус
    if actual_value > normative_value * (1 + tolerance_percent / 100):
        status = "violation"
        message = (
            f"⚠️ Превышение норматива на {deviation_percent:.1f}%. "
            f"Факт: {actual_value}, Норматив: {normative_value}"
        )
    elif actual_value < normative_value * (1 - tolerance_percent / 100):
        status = "below_norm"
        message = (
            f"✅ Значение ниже норматива на {deviation_percent:.1f}%. "
            f"Факт: {actual_value}, Норматив: {normative_value}"
        )
    else:
        status = "compliant"
        message = (
            f"✅ Соответствует нормативу. "
            f"Факт: {actual_value}, Норматив: {normative_value} "
            f"(отклонение: {deviation_percent:.1f}%)"
        )

    return {
        "status": status,
        "actual": actual_value,
        "normative": normative_value,
        "deviation_percent": deviation_percent,
        "message": message,
        "rule": best_rule,
        "unit": best_rule.get("unit"),
        "document_title": best_rule.get("document_title"),
    }


def check_critical_fields(
    enterprise_id: int,
    batch_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Проверить все критические поля для предприятия

    Args:
        enterprise_id: ID предприятия
        batch_id: ID загрузки (опционально)

    Returns:
        Словарь с результатами проверки всех критических полей
    """
    # Список критических полей
    critical_fields = [
        {"field_name": "Удельный расход электроэнергии", "sheet_name": "Динамика ср"},
        {"field_name": "Удельный расход", "sheet_name": "Динамика ср"},
        {"field_name": "Удельный расход газа", "sheet_name": "Динамика ср"},
        {"field_name": "Удельный расход воды", "sheet_name": "Динамика ср"},
        {"field_name": "Потери электроэнергии", "sheet_name": "08_Потери"},
        # Можно добавить больше полей
    ]

    violations = []
    compliant = []
    unknown = []

    # TODO: Получить фактические значения из паспорта
    # Пока заглушка - нужно интегрировать с fill_energy_passport.py
    for field in critical_fields:
        # Здесь нужно получить фактическое значение из паспорта
        # actual_value = get_field_value_from_passport(enterprise_id, field)
        # Пока пропускаем

        # Проверяем наличие нормативов
        rules = database.get_normative_rules_for_field(
            field["field_name"], field.get("sheet_name")
        )

        if rules:
            compliant.append(
                {
                    "field_name": field["field_name"],
                    "sheet_name": field.get("sheet_name"),
                    "has_normative": True,
                    "rules_count": len(rules),
                }
            )
        else:
            unknown.append(
                {
                    "field_name": field["field_name"],
                    "sheet_name": field.get("sheet_name"),
                    "has_normative": False,
                }
            )

    return {
        "enterprise_id": enterprise_id,
        "batch_id": batch_id,
        "total_critical_fields": len(critical_fields),
        "violations_count": len(violations),
        "compliant_count": len(compliant),
        "unknown_count": len(unknown),
        "violations": violations,
        "compliant": compliant,
        "unknown": unknown,
        "status": "compliant" if len(violations) == 0 else "has_violations",
    }


def get_top_fields_with_normatives(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Получить топ полей с наибольшим количеством нормативов

    Args:
        limit: Количество полей в топе

    Returns:
        Список полей с количеством нормативов
    """
    if not HAS_DATABASE:
        return []

    try:
        with database.get_connection() as conn:
            conn.row_factory = database.sqlite3.Row
            rows = conn.execute(
                """
                SELECT 
                    nref.field_name,
                    nref.sheet_name,
                    COUNT(DISTINCT nref.rule_id) as rules_count
                FROM normative_references nref
                GROUP BY nref.field_name, nref.sheet_name
                ORDER BY rules_count DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            return [
                {
                    "field_name": row["field_name"],
                    "sheet_name": row["sheet_name"],
                    "rules_count": row["rules_count"],
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Ошибка получения топ полей: {e}")
        return []


def get_normative_statistics() -> Dict[str, Any]:
    """
    Получить статистику по нормативным документам

    Returns:
        Словарь со статистикой
    """
    if not HAS_DATABASE:
        return {
            "total_documents": 0,
            "total_rules": 0,
            "by_type": {},
            "top_fields": [],
        }

    try:
        documents = database.list_normative_documents()
        total_rules = sum(doc.get("rules_count", 0) for doc in documents)

        # Статистика по типам
        by_type = {}
        for doc in documents:
            doc_type = doc.get("document_type", "unknown")
            by_type[doc_type] = by_type.get(doc_type, 0) + 1

        # Топ полей
        top_fields = get_top_fields_with_normatives(10)

        return {
            "total_documents": len(documents),
            "total_rules": total_rules,
            "by_type": by_type,
            "top_fields": top_fields,
            "ai_processed": sum(1 for d in documents if d.get("ai_processed")),
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return {
            "total_documents": 0,
            "total_rules": 0,
            "by_type": {},
            "top_fields": [],
            "error": str(e),
        }


