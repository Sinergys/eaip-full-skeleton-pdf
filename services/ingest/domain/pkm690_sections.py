"""
Маппинг структуры ПКМ-690 с содержанием образцового отчёта.

Определяет соответствие между разделами ПКМ-690, разделами образцового отчёта,
необходимыми данными и текстовыми шаблонами.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, List, Callable
from enum import Enum


class SectionType(Enum):
    """Тип раздела."""

    INTRODUCTION = "introduction"
    ENTERPRISE_INFO = "enterprise_info"
    ENERGY_ANALYSIS = "energy_analysis"
    EQUIPMENT_ANALYSIS = "equipment_analysis"
    MEASURES = "measures"
    ECONOMIC_ANALYSIS = "economic_analysis"
    CONCLUSION = "conclusion"
    APPENDIX = "appendix"


@dataclass
class SectionRequirement:
    """Требования к данным для раздела."""

    # Минимальные КПИ, необходимые для генерации раздела
    required_kpis: List[str] = field(default_factory=list)
    # Опциональные КПИ, которые улучшают качество раздела
    optional_kpis: List[str] = field(default_factory=list)
    # Минимальные таблицы, необходимые для раздела
    required_tables: List[str] = field(default_factory=list)
    # Опциональные таблицы
    optional_tables: List[str] = field(default_factory=list)
    # Можно ли генерировать раздел без данных (с fallback)
    allow_empty: bool = False


@dataclass
class PKM690Section:
    """Раздел ПКМ-690 с маппингом на образцовый отчёт."""

    # Номер и название раздела по ПКМ-690
    pkm690_number: int
    pkm690_title: str

    # Соответствующие разделы из образцового отчёта
    reference_sections: List[str] = field(default_factory=list)

    # Тип раздела
    section_type: SectionType = SectionType.INTRODUCTION

    # Требования к данным
    requirements: SectionRequirement = field(default_factory=SectionRequirement)

    # Текстовый шаблон (может быть функцией или строкой)
    template: Optional[str] = None
    template_func: Optional[Callable] = None

    # Минимальный уровень детализации (1-3)
    detail_level: int = 2


# Маппинг разделов ПКМ-690 на образцовый отчёт
PKM690_SECTIONS = [
    PKM690Section(
        pkm690_number=1,
        pkm690_title="ВВЕДЕНИЕ",
        reference_sections=[
            "Вводная часть",
        ],
        section_type=SectionType.INTRODUCTION,
        requirements=SectionRequirement(
            allow_empty=True,
        ),
        template="""
Настоящий энергетический аудит проведен в соответствии с требованиями стандарта ПКМ 690 Узбекистан.

Целью энергетического аудита является:
- Оценка текущего состояния энергопотребления предприятия
- Выявление резервов энергосбережения
- Разработка рекомендаций по повышению энергоэффективности
- Определение потенциала снижения затрат на энергоресурсы

Нормативная база:
- Постановление Кабинета Министров Республики Узбекистан №690 от 19.10.2024
- ГОСТ Р 51379-99 «Энергосбережение. Энергетический паспорт промышленного потребителя топливно-энергетических ресурсов»
- Внутренние регламенты предприятия
        """.strip(),
        detail_level=1,
    ),
    PKM690Section(
        pkm690_number=2,
        pkm690_title="ОБЩИЕ СВЕДЕНИЯ О ПРЕДПРИЯТИИ",
        reference_sections=[
            "Общие сведения о предприятии",
            "Местоположение и основные параметры",
            "Договора аренды",
            "Описание технологических процессов",
        ],
        section_type=SectionType.ENTERPRISE_INFO,
        requirements=SectionRequirement(
            required_kpis=[],  # enterprise.name и address проверяются отдельно
            optional_kpis=[
                "enterprise.inn",
                "enterprise.director",
                "enterprise.industry",
            ],
            allow_empty=False,
        ),
        template="""
{enterprise_name} расположено по адресу: {enterprise_address}.

Основные параметры предприятия:
- Отрасль: {enterprise_industry}
- Руководитель: {enterprise_director}
- ИНН: {enterprise_inn}

{processes_description}
        """.strip(),
        detail_level=2,
    ),
    PKM690Section(
        pkm690_number=3,
        pkm690_title="АНАЛИЗ ЭНЕРГОПОТРЕБЛЕНИЯ",
        reference_sections=[
            "Анализ объема выпущенной продукции (ед.энp.кг)",
            "Объём выпущенной продукции",
            "Расход электроэнергии на единицу продукции (ед. изм. кВт/тонна)",
            "Динамика расхода энергии на единицу продукции.",
            "Анализ расхода электроэнергии",
            "Анализ выработки реактивной энергии",
        ],
        section_type=SectionType.ENERGY_ANALYSIS,
        requirements=SectionRequirement(
            required_kpis=[
                "electricity.total_consumption",
                "gas.total_consumption",
                "water.total_consumption",
            ],
            optional_kpis=[
                "electricity.by_quarter",
                "gas.by_quarter",
                "water.by_quarter",
                "specific_consumption",
            ],
            required_tables=["consumption_by_quarters"],
            optional_tables=["specific_consumption", "consumption_structure"],
            allow_empty=False,
        ),
        template="""
3.1 Общая характеристика энергопотребления

Предприятие потребляет следующие виды энергетических ресурсов:
- Электрическая энергия
- Природный газ
- Вода (холодная и горячая)

Общее энергопотребление предприятия за отчетный период составляет:
- Электрическая энергия: {electricity_total:,.0f} кВт·ч
- Природный газ: {gas_total:,.0f} м³
- Вода: {water_total:,.0f} м³

3.2 Энергопотребление по кварталам

[Таблица энергопотребления по кварталам будет вставлена здесь]

{specific_consumption_text}
        """.strip(),
        detail_level=3,
    ),
    PKM690Section(
        pkm690_number=4,
        pkm690_title="АНАЛИЗ ОБОРУДОВАНИЯ",
        reference_sections=[
            "Электроснабжение",
            "Общие сведения",
            "Список трансформаторных подстанций",
            "Список оборудования предприятия",
            "Электрооборудование в разрезе производственных цехов",
            "Система освещения предприятия",
            "Электрические водонагреватели",
            "Мощность оборудования Вентиляции",
        ],
        section_type=SectionType.EQUIPMENT_ANALYSIS,
        requirements=SectionRequirement(
            required_kpis=["equipment.total_installed_power_kw"],
            optional_kpis=[
                "equipment.total_used_power_kw",
                "equipment.total_items_count",
                "equipment.vfd_count",
            ],
            required_tables=["equipment_list"],
            optional_tables=["equipment_by_section"],
            allow_empty=True,  # Может быть пустым, если нет данных об оборудовании
        ),
        template="""
4.1 Общая характеристика оборудования

На предприятии установлено следующее энергопотребляющее оборудование:
- Производственное оборудование
- Электрооборудование
- Системы отопления и вентиляции
- Осветительные установки

Общая установленная мощность: {total_power:,.2f} кВт
Количество единиц оборудования: {total_items}

4.2 Перечень основного оборудования

[Таблица оборудования будет вставлена здесь]
        """.strip(),
        detail_level=2,
    ),
    PKM690Section(
        pkm690_number=5,
        pkm690_title="МЕРОПРИЯТИЯ ПО ЭНЕРГОСБЕРЕЖЕНИЮ",
        reference_sections=[
            "Мероприятия по энергосбережению",
        ],
        section_type=SectionType.MEASURES,
        requirements=SectionRequirement(
            required_tables=["measures"],
            allow_empty=True,  # Может использовать эталонные таблицы
        ),
        template="""
5.1 Рекомендуемые мероприятия

На основе проведенного анализа энергопотребления разработаны следующие мероприятия по энергосбережению:

[Таблица мероприятий будет вставлена здесь]

{measures_summary}
        """.strip(),
        detail_level=2,
    ),
    PKM690Section(
        pkm690_number=6,
        pkm690_title="ЭКОНОМИЧЕСКИЙ АНАЛИЗ",
        reference_sections=[
            "Экономический анализ",
        ],
        section_type=SectionType.ECONOMIC_ANALYSIS,
        requirements=SectionRequirement(
            required_kpis=[
                "total_energy_cost",
                "electricity.total_cost",
                "gas.total_cost",
                "water.total_cost",
            ],
            optional_kpis=[
                "measures.total_saving_money",
                "measures.average_payback_years",
            ],
            allow_empty=False,
        ),
        template="""
8.1 Анализ затрат на энергоресурсы

Общие затраты предприятия на энергоресурсы за отчетный период:
- Электрическая энергия: {electricity_cost:,.0f} сум
- Природный газ: {gas_cost:,.0f} сум
- Вода: {water_cost:,.0f} сум
- Общие затраты: {total_cost:,.0f} сум

8.2 Экономический эффект от мероприятий

Реализация предложенных мероприятий позволит:
- Снизить энергопотребление на 15-25%
- Экономить денежные средства на оплате энергоресурсов
- Срок окупаемости мероприятий: {payback_years:.1f} лет
        """.strip(),
        detail_level=2,
    ),
    PKM690Section(
        pkm690_number=7,
        pkm690_title="ЗАКЛЮЧЕНИЕ",
        reference_sections=[
            "Заключение",
        ],
        section_type=SectionType.CONCLUSION,
        requirements=SectionRequirement(
            allow_empty=True,
        ),
        template="""
На основе проведенного энергетического аудита можно сделать следующие выводы:

1. Текущее состояние энергопотребления предприятия характеризуется следующими показателями:
   - Общее потребление электроэнергии: {electricity_total:,.0f} кВт·ч/год
   - Общее потребление газа: {gas_total:,.0f} м³/год
   - Общие затраты на энергоресурсы: {total_cost:,.0f} сум/год

2. Выявлены следующие резервы энергосбережения:
   - Оптимизация работы оборудования
   - Внедрение энергосберегающих технологий
   - Улучшение системы учета энергоресурсов

3. Рекомендуется реализовать предложенные мероприятия по энергосбережению для снижения затрат и повышения энергоэффективности.

Дата составления отчёта: {report_date}
        """.strip(),
        detail_level=1,
    ),
    PKM690Section(
        pkm690_number=8,
        pkm690_title="ПРИЛОЖЕНИЯ",
        reference_sections=[
            "Приложения",
        ],
        section_type=SectionType.APPENDIX,
        requirements=SectionRequirement(
            optional_tables=["all"],
            allow_empty=True,
        ),
        template="""
Приложения:
- Таблицы детального энергопотребления
- Схемы энергоснабжения
- Дополнительные расчеты и графики
        """.strip(),
        detail_level=1,
    ),
]


def get_section_by_number(number: int) -> Optional[PKM690Section]:
    """Получает раздел ПКМ-690 по номеру."""
    for section in PKM690_SECTIONS:
        if section.pkm690_number == number:
            return section
    return None


def get_section_by_type(section_type: SectionType) -> List[PKM690Section]:
    """Получает все разделы заданного типа."""
    return [s for s in PKM690_SECTIONS if s.section_type == section_type]


def get_required_kpis_for_section(section_number: int) -> List[str]:
    """Получает список необходимых КПИ для раздела."""
    section = get_section_by_number(section_number)
    if section:
        return section.requirements.required_kpis
    return []


def can_generate_section(
    section_number: int, report_data: Any
) -> tuple[bool, List[str]]:
    """
    Проверяет, можно ли сгенерировать раздел на основе имеющихся данных.

    Returns:
        (can_generate, missing_kpis) - можно ли генерировать и список недостающих КПИ
    """
    section = get_section_by_number(section_number)
    if not section:
        return False, ["Раздел не найден"]

    if section.requirements.allow_empty:
        return True, []

    missing = []
    for kpi in section.requirements.required_kpis:
        # Простая проверка наличия КПИ (можно расширить)
        if not _has_kpi(report_data, kpi):
            missing.append(kpi)

    return len(missing) == 0, missing


def _has_kpi(report_data: Any, kpi_path: str) -> bool:
    """Проверяет наличие КПИ в report_data по пути (например, 'electricity.total_consumption')."""
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
        return value is not None
    except Exception:
        # Если произошла ошибка при доступе к вложенным атрибутам/ключам
        return False
