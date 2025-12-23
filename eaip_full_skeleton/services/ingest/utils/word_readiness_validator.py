"""
Валидация готовности данных для генерации Word-отчёта по ПКМ-690.

Проверяет наличие необходимых данных для каждого раздела отчёта,
используя требования из pkm690_sections и возможность fallback на эталонные таблицы.
"""

import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path

try:
    from ..domain.pkm690_sections import (
        PKM690_SECTIONS,
        get_section_by_number,
        can_generate_section,
        SectionType,
    )

    HAS_SECTIONS = True
except ImportError:
    # Fallback для случаев прямого импорта
    try:
        import sys
        from pathlib import Path

        _domain_path = Path(__file__).resolve().parent.parent / "domain"
        if str(_domain_path) not in sys.path:
            sys.path.insert(0, str(_domain_path))
        from pkm690_sections import (
            PKM690_SECTIONS,
            get_section_by_number,
            can_generate_section,
            SectionType,
        )

        HAS_SECTIONS = True
    except ImportError:
        HAS_SECTIONS = False

try:
    from .reference_tables_loader import (
        get_all_measures,
    )

    HAS_REFERENCE_TABLES = True
except ImportError:
    HAS_REFERENCE_TABLES = False

logger = logging.getLogger(__name__)


def validate_word_report_readiness(
    report_data: Any, check_reference_tables: bool = True
) -> Dict[str, Any]:
    """
    Проверяет готовность данных для генерации Word-отчёта.

    Args:
        report_data: Объект ReportData с вычисленными КПИ
        check_reference_tables: Проверять ли наличие эталонных таблиц для fallback

    Returns:
        Словарь с результатами проверки:
        {
            "ready": bool,
            "completeness_score": float,  # 0.0-1.0
            "sections_status": Dict[int, Dict],  # Статус каждого раздела
            "missing_sections": List[int],  # Разделы, которые нельзя сгенерировать
            "warnings": List[str],
            "errors": List[str],
            "reference_tables_available": bool,
        }
    """
    if not HAS_SECTIONS:
        logger.warning("Модуль pkm690_sections недоступен. Пропускаем проверку.")
        return {
            "ready": True,  # Разрешаем генерацию, если модуль недоступен
            "completeness_score": 1.0,
            "sections_status": {},
            "missing_sections": [],
            "warnings": ["Модуль проверки разделов недоступен"],
            "errors": [],
            "reference_tables_available": False,
        }

    sections_status = {}
    missing_sections = []
    warnings = []
    errors = []

    # Проверяем каждый раздел ПКМ-690
    for section in PKM690_SECTIONS:
        section_num = section.pkm690_number
        can_generate, missing_kpis = can_generate_section(section_num, report_data)

        # Специальная проверка для раздела 2 (ОБЩИЕ СВЕДЕНИЯ О ПРЕДПРИЯТИИ)
        if section_num == 2:
            # Проверяем наличие данных предприятия напрямую
            if hasattr(report_data, "enterprise_data") and report_data.enterprise_data:
                enterprise = report_data.enterprise_data
                if enterprise.get("name") and enterprise.get("address"):
                    can_generate = True
                    missing_kpis = [
                        kpi for kpi in missing_kpis if not kpi.startswith("enterprise.")
                    ]

        section_info = {
            "can_generate": can_generate,
            "missing_kpis": missing_kpis,
            "has_reference_fallback": False,
        }

        # Проверяем возможность fallback на эталонные таблицы
        if not can_generate and check_reference_tables:
            has_fallback = _check_section_fallback(section)
            section_info["has_reference_fallback"] = has_fallback

            if has_fallback:
                can_generate = True  # Можно генерировать с fallback
                warnings.append(
                    f"Раздел {section_num} ({section.pkm690_title}): "
                    f"недостающие КПИ будут взяты из эталонных таблиц"
                )

        sections_status[section_num] = section_info

        if not can_generate:
            missing_sections.append(section_num)
            errors.append(
                f"Раздел {section_num} ({section.pkm690_title}): "
                f"недостающие КПИ: {', '.join(missing_kpis)}"
            )

    # Проверяем наличие эталонных таблиц
    reference_tables_available = False
    if check_reference_tables and HAS_REFERENCE_TABLES:
        try:
            measures = get_all_measures()
            reference_tables_available = len(measures) > 0
        except Exception as e:
            logger.warning(f"Ошибка проверки эталонных таблиц: {e}")

    # Вычисляем общий показатель готовности
    total_sections = len(PKM690_SECTIONS)
    ready_sections = sum(1 for s in sections_status.values() if s["can_generate"])
    completeness_score = ready_sections / total_sections if total_sections > 0 else 0.0

    # Отчёт готов, если все обязательные разделы можно сгенерировать
    # (разделы с allow_empty=True не блокируют генерацию)
    critical_sections = [s for s in PKM690_SECTIONS if not s.requirements.allow_empty]
    critical_missing = [
        s.pkm690_number
        for s in critical_sections
        if not sections_status[s.pkm690_number]["can_generate"]
    ]

    ready = len(critical_missing) == 0

    return {
        "ready": ready,
        "completeness_score": completeness_score,
        "sections_status": sections_status,
        "missing_sections": missing_sections,
        "critical_missing_sections": critical_missing,
        "warnings": warnings,
        "errors": errors,
        "reference_tables_available": reference_tables_available,
        "ready_sections_count": ready_sections,
        "total_sections_count": total_sections,
    }


def _check_section_fallback(section) -> bool:
    """
    Проверяет, есть ли эталонные таблицы для fallback данного раздела.

    Args:
        section: PKM690Section

    Returns:
        True если есть fallback
    """
    if not HAS_REFERENCE_TABLES:
        return False

    try:
        # Проверяем наличие эталонных таблиц в зависимости от типа раздела
        if section.section_type == SectionType.MEASURES:
            measures = get_all_measures()
            return len(measures) > 0

        elif section.section_type == SectionType.EQUIPMENT_ANALYSIS:
            # Можно проверить наличие оборудования в эталонных таблицах
            # Пока возвращаем False, так как нет прямой функции
            return False

        elif section.section_type == SectionType.ENERGY_ANALYSIS:
            # Для анализа энергопотребления обычно нет эталонных таблиц
            return False

        # Для остальных разделов fallback обычно не требуется
        return False

    except Exception as e:
        logger.warning(
            f"Ошибка проверки fallback для раздела {section.pkm690_number}: {e}"
        )
        return False


def validate_section_data(
    section_number: int, report_data: Any
) -> Tuple[bool, List[str], List[str]]:
    """
    Валидирует данные для конкретного раздела.

    Args:
        section_number: Номер раздела ПКМ-690
        report_data: Объект ReportData

    Returns:
        (is_valid, missing_kpis, warnings)
    """
    if not HAS_SECTIONS:
        return True, [], []

    section = get_section_by_number(section_number)
    if not section:
        return False, [f"Раздел {section_number} не найден"], []

    can_generate, missing_kpis = can_generate_section(section_number, report_data)
    warnings = []

    # Проверяем опциональные КПИ
    for optional_kpi in section.requirements.optional_kpis:
        if not _has_kpi(report_data, optional_kpi):
            warnings.append(f"Опциональный КПИ отсутствует: {optional_kpi}")

    return can_generate, missing_kpis, warnings


def _has_kpi(report_data: Any, kpi_path: str) -> bool:
    """Проверяет наличие КПИ в report_data по пути."""
    try:
        parts = kpi_path.split(".")
        value = report_data
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return False
        return value is not None and value != 0
    except Exception:
        # Если произошла ошибка при доступе к вложенным атрибутам/ключам
        return False


def get_missing_data_summary(validation_result: Dict[str, Any]) -> str:
    """
    Формирует текстовую сводку о недостающих данных.

    Args:
        validation_result: Результат validate_word_report_readiness()

    Returns:
        Текстовая сводка
    """
    if validation_result["ready"]:
        return "Все необходимые данные для генерации Word-отчёта доступны."

    summary_parts = [
        f"Готовность: {validation_result['completeness_score'] * 100:.0f}%",
        f"Готовых разделов: {validation_result['ready_sections_count']}/{validation_result['total_sections_count']}",
    ]

    if validation_result["critical_missing_sections"]:
        summary_parts.append(
            f"\nКритические недостающие разделы: {', '.join(map(str, validation_result['critical_missing_sections']))}"
        )

    if validation_result["errors"]:
        summary_parts.append("\nОшибки:")
        for error in validation_result["errors"][:5]:  # Показываем первые 5
            summary_parts.append(f"  - {error}")

    if validation_result["warnings"]:
        summary_parts.append("\nПредупреждения:")
        for warning in validation_result["warnings"][:5]:
            summary_parts.append(f"  - {warning}")

    return "\n".join(summary_parts)
