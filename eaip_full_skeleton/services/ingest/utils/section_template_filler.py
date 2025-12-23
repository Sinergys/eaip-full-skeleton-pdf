"""
Заполнение текстовых шаблонов разделов данными из ReportData.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from ..domain.pkm690_sections import get_section_by_number

    HAS_SECTIONS = True
except ImportError:
    # Fallback для случаев прямого импорта
    try:
        import sys
        from pathlib import Path

        _domain_path = Path(__file__).resolve().parent.parent / "domain"
        if str(_domain_path) not in sys.path:
            sys.path.insert(0, str(_domain_path))
        from pkm690_sections import get_section_by_number

        HAS_SECTIONS = True
    except ImportError:
        HAS_SECTIONS = False

logger = logging.getLogger(__name__)


def fill_section_template(
    section_number: int, report_data: Any, template_override: Optional[str] = None
) -> str:
    """
    Заполняет шаблон раздела данными из ReportData.

    Args:
        section_number: Номер раздела ПКМ-690 (1-8)
        report_data: Объект ReportData с вычисленными КПИ
        template_override: Опциональный переопределенный шаблон

    Returns:
        Заполненный текст раздела
    """
    if not HAS_SECTIONS:
        logger.warning("Модуль pkm690_sections недоступен. Используется пустой шаблон.")
        return ""

    section = get_section_by_number(section_number)
    if not section:
        logger.warning(f"Раздел {section_number} не найден.")
        return ""

    # Используем переопределенный шаблон или шаблон из раздела
    template = template_override or section.template
    if not template:
        logger.warning(f"Шаблон для раздела {section_number} не найден.")
        return ""

    # Подготавливаем данные для подстановки
    context = _build_template_context(section_number, report_data)

    # Заполняем шаблон
    try:
        filled_text = template.format(**context)
        return filled_text
    except KeyError as e:
        logger.warning(f"Отсутствует ключ в шаблоне раздела {section_number}: {e}")
        # Пытаемся заполнить с доступными данными
        try:
            filled_text = template.format(
                **{k: v for k, v in context.items() if k in template}
            )
            return filled_text
        except (KeyError, ValueError, TypeError):
            # Если все равно не удалось заполнить, возвращаем оригинальный шаблон
            return template
    except Exception as e:
        logger.error(f"Ошибка заполнения шаблона раздела {section_number}: {e}")
        return template


def _build_template_context(section_number: int, report_data: Any) -> Dict[str, Any]:
    """
    Строит контекст для заполнения шаблона на основе report_data.

    Args:
        section_number: Номер раздела
        report_data: Объект ReportData

    Returns:
        Словарь с данными для подстановки в шаблон
    """
    context = {}

    # Данные предприятия
    if hasattr(report_data, "enterprise_data") and report_data.enterprise_data:
        enterprise = report_data.enterprise_data
        context.update(
            {
                "enterprise_name": enterprise.get("name", "Не указано"),
                "enterprise_address": enterprise.get("address", "Не указано"),
                "enterprise_inn": enterprise.get("inn", "Не указано"),
                "enterprise_director": enterprise.get("director", "Не указано"),
                "enterprise_industry": enterprise.get("industry", "Не указано"),
            }
        )

    # Данные по ресурсам
    if hasattr(report_data, "electricity"):
        context.update(
            {
                "electricity_total": report_data.electricity.total_consumption,
                "electricity_cost": report_data.electricity.total_cost,
            }
        )

    if hasattr(report_data, "gas"):
        context.update(
            {
                "gas_total": report_data.gas.total_consumption,
                "gas_cost": report_data.gas.total_cost,
            }
        )

    if hasattr(report_data, "water"):
        context.update(
            {
                "water_total": report_data.water.total_consumption,
                "water_cost": report_data.water.total_cost,
            }
        )

    # Данные по оборудованию
    if hasattr(report_data, "equipment"):
        context.update(
            {
                "total_power": report_data.equipment.total_installed_power_kw,
                "total_items": report_data.equipment.total_items_count,
            }
        )

    # Данные по мероприятиям
    if hasattr(report_data, "measures"):
        context.update(
            {
                "payback_years": report_data.measures.average_payback_years,
            }
        )

    # Общие затраты
    if hasattr(report_data, "total_energy_cost"):
        context["total_cost"] = report_data.total_energy_cost

    # Дополнительные данные в зависимости от раздела
    if section_number == 2:  # ОБЩИЕ СВЕДЕНИЯ О ПРЕДПРИЯТИИ
        context["processes_description"] = _get_processes_description(report_data)

    elif section_number == 3:  # АНАЛИЗ ЭНЕРГОПОТРЕБЛЕНИЯ
        context["specific_consumption_text"] = _get_specific_consumption_text(
            report_data
        )

    elif section_number == 5:  # МЕРОПРИЯТИЯ
        context["measures_summary"] = _get_measures_summary(report_data)

    # Дата отчёта
    if hasattr(report_data, "generated_at"):
        context["report_date"] = report_data.generated_at.strftime("%d.%m.%Y")
    else:
        context["report_date"] = datetime.now().strftime("%d.%m.%Y")

    return context


def _get_processes_description(report_data: Any) -> str:
    """Получает описание технологических процессов."""
    if hasattr(report_data, "enterprise_data") and report_data.enterprise_data:
        processes = report_data.enterprise_data.get("processes", "")
        if processes:
            return f"Основные технологические процессы: {processes}"
    return "Описание технологических процессов будет добавлено при наличии данных."


def _get_specific_consumption_text(report_data: Any) -> str:
    """Получает текст об удельном потреблении."""
    # Можно расширить, добавив расчет удельного потребления
    return """
3.3 Удельное потребление энергии

Удельное потребление электроэнергии рассчитывается как отношение общего потребления к объему выпущенной продукции.
    """.strip()


def _get_measures_summary(report_data: Any) -> str:
    """Получает сводку по мероприятиям."""
    if hasattr(report_data, "measures") and report_data.measures.total_count > 0:
        return f"""
Общая стоимость реализации мероприятий: {report_data.measures.total_capex:,.0f} сум.
Общая годовая экономия электроэнергии: {report_data.measures.total_saving_kwh:,.0f} кВт·ч/год.
Средний срок окупаемости: {report_data.measures.average_payback_years:.1f} лет.
        """.strip()
    return "Мероприятия по энергосбережению будут разработаны на основе результатов анализа."
