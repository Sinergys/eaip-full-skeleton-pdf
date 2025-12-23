from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional, Dict, Any, Set
from enum import Enum

from ai.ai_excel_semantic_parser import CanonicalSourceData, ResourceEntry

Severity = Literal["required", "recommended"]
Overall = Literal["ready", "partially_ready", "blocked"]


@dataclass
class RequiredField:
    id: str
    section: str
    description: str
    severity: Severity
    path_hint: str


@dataclass
class GenerationReadinessResult:
    overall_status: Overall
    missing_required: List[RequiredField] = field(default_factory=list)
    missing_optional: List[RequiredField] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def get_default_passport_requirements() -> List[RequiredField]:
    return [
        RequiredField(
            id="annual_electricity_total",
            section="resources",
            description="Annual electricity consumption total",
            severity="required",
            path_hint="resources.electricity.annual",
        ),
        # Recommended extensions (not blocking)
        RequiredField(
            id="annual_gas_total",
            section="resources",
            description="Annual gas consumption total",
            severity="recommended",
            path_hint="resources.gas.annual",
        ),
        RequiredField(
            id="annual_water_total",
            section="resources",
            description="Annual water consumption total",
            severity="recommended",
            path_hint="resources.water.annual",
        ),
        RequiredField(
            id="annual_fuel_total",
            section="resources",
            description="Annual fuel consumption total",
            severity="recommended",
            path_hint="resources.fuel.annual",
        ),
        RequiredField(
            id="annual_coal_total",
            section="resources",
            description="Annual coal consumption total",
            severity="recommended",
            path_hint="resources.coal.annual",
        ),
        RequiredField(
            id="annual_heat_total",
            section="resources",
            description="Annual heat consumption total",
            severity="required",
            path_hint="resources.heat.annual",
        ),
        RequiredField(
            id="at_least_one_equipment_item",
            section="equipment",
            description="At least one equipment item with nominal_power_kw",
            severity="required",
            path_hint="equipment[*].nominal_power_kw",
        ),
        RequiredField(
            id="at_least_one_node",
            section="nodes",
            description="At least one metering node",
            severity="required",
            path_hint="nodes[*]",
        ),
        RequiredField(
            id="envelope_u_values",
            section="envelope",
            description="U-values for key envelope elements",
            severity="recommended",
            path_hint="envelope[*].u_value_w_m2k",
        ),
    ]


def _annual_total_by_resource(
    canonical: CanonicalSourceData, resource: str
) -> Optional[float]:
    for entry in canonical.resources:
        if isinstance(entry, ResourceEntry) and entry.resource == resource:
            series = entry.series
            if series and series.annual is not None:
                return series.annual
            # derive annual from monthly if present
            if series and series.monthly:
                try:
                    return float(
                        sum(
                            v
                            for v in series.monthly.values()
                            if isinstance(v, (int, float))
                        )
                    )
                except Exception:
                    return None
    return None


def evaluate_generation_readiness(
    canonical: Optional[CanonicalSourceData],
) -> GenerationReadinessResult:
    if canonical is None:
        return GenerationReadinessResult(
            overall_status="blocked",
            missing_required=get_default_passport_requirements(),
            notes=["CanonicalSourceData unavailable"],
        )

    reqs = get_default_passport_requirements()
    missing_required: List[RequiredField] = []
    missing_optional: List[RequiredField] = []

    # Simple checks guided by path_hint
    for rf in reqs:
        ok = False
        if rf.id == "annual_electricity_total":
            ok = _annual_total_by_resource(canonical, "electricity") is not None
        elif rf.id == "annual_heat_total":
            ok = _annual_total_by_resource(canonical, "heat") is not None
        elif rf.id == "at_least_one_equipment_item":
            ok = any(
                getattr(item, "nominal_power_kw", None) is not None
                for item in (canonical.equipment or [])
            )
        elif rf.id == "at_least_one_node":
            ok = len(canonical.nodes or []) > 0
        elif rf.id == "envelope_u_values":
            ok = any(
                getattr(item, "u_value_w_m2k", None) is not None
                for item in (canonical.envelope or [])
            )
        else:
            ok = False

        if not ok:
            (
                missing_required if rf.severity == "required" else missing_optional
            ).append(rf)

    if missing_required:
        overall: Overall = "blocked"
    elif missing_optional:
        overall = "partially_ready"
    else:
        overall = "ready"

    return GenerationReadinessResult(
        overall_status=overall,
        missing_required=missing_required,
        missing_optional=missing_optional,
        notes=[],
    )


"""
Определение обязательных данных для заполнения каждого листа энергопаспорта.

Этот модуль описывает, какие данные необходимы для корректного заполнения
каждого листа Excel-паспорта, и откуда они берутся.
"""


class DataSource(Enum):
    """Источники данных для заполнения паспорта."""

    DB_UPLOADS = "db_uploads"  # Таблица uploads в БД
    DB_PARSED_DATA = "db_parsed_data"  # Таблица parsed_data в БД
    AGGREGATED_JSON = "aggregated_json"  # Файлы в data/aggregated/*.json
    EQUIPMENT_JSON = "equipment_json"  # oborudovanie_equipment.json
    ENVELOPE_JSON = (
        "envelope_json"  # ograjdayuschie_envelope.json (расчет теплопотерь по зданиям)
    )
    NODES_JSON = "nodes_json"  # nodes JSON файлы
    USAGE_CATEGORIES_JSON = "usage_categories_json"  # usage_categories.json
    DEFAULT_VALUES = "default_values"  # Значения по умолчанию


@dataclass
class FieldRequirement:
    """Требование к полю данных."""

    field_name: str
    description: str
    required: bool = True
    sources: List[DataSource] = field(default_factory=list)
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Any = None


@dataclass
class SheetRequirement:
    """Требования к заполнению листа."""

    sheet_name: str
    alternative_names: List[str] = field(default_factory=list)
    required: bool = True
    critical_fields: List[FieldRequirement] = field(default_factory=list)
    optional_fields: List[FieldRequirement] = field(default_factory=list)
    description: str = ""


# Определение требований для каждого листа
PASSPORT_SHEET_REQUIREMENTS: Dict[str, SheetRequirement] = {
    "Struktura pr2": SheetRequirement(
        sheet_name="Struktura pr2",
        alternative_names=["Структура пр 2", "02_Структура", "Структура потребления"],
        required=True,
        description="Структура потребления энергоресурсов по кварталам",
        critical_fields=[
            FieldRequirement(
                field_name="electricity.active_kwh",
                description="Активное потребление электроэнергии по кварталам",
                required=True,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 4, "min_value": 0},
            ),
            FieldRequirement(
                field_name="electricity.reactive_kvarh",
                description="Реактивное потребление электроэнергии по кварталам",
                required=True,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 4, "min_value": 0},
            ),
            FieldRequirement(
                field_name="gas.volume_m3",
                description="Потребление газа по кварталам",
                required=True,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 4, "min_value": 0},
            ),
            FieldRequirement(
                field_name="water.volume_m3",
                description="Потребление воды по кварталам",
                required=False,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 2, "min_value": 0},
            ),
        ],
        optional_fields=[
            FieldRequirement(
                field_name="loss_active_month",
                description="Потери активной энергии за месяц",
                required=False,
                sources=[DataSource.DEFAULT_VALUES],
                default_value=0.0,
            ),
            FieldRequirement(
                field_name="loss_reactive_month",
                description="Потери реактивной энергии за месяц",
                required=False,
                sources=[DataSource.DEFAULT_VALUES],
                default_value=0.0,
            ),
        ],
    ),
    "01_Узлы учета": SheetRequirement(
        sheet_name="01_Узлы учета",
        alternative_names=["Узел учета", "Узлы учета", "Nodes", "Узлы учёта"],
        required=True,
        description="Узлы учёта энергоресурсов",
        critical_fields=[
            FieldRequirement(
                field_name="nodes",
                description="Список узлов учёта (минимум 1 узел)",
                required=True,
                sources=[DataSource.NODES_JSON, DataSource.DEFAULT_VALUES],
                validation_rules={"min_count": 1},
            ),
        ],
        optional_fields=[
            FieldRequirement(
                field_name="node.meter_type",
                description="Тип счётчика",
                required=False,
                sources=[DataSource.NODES_JSON],
            ),
            FieldRequirement(
                field_name="node.serial_number",
                description="Серийный номер счётчика",
                required=False,
                sources=[DataSource.NODES_JSON],
            ),
        ],
    ),
    "Equipment": SheetRequirement(
        sheet_name="Equipment",
        alternative_names=[
            "Оборудование",
            "03_Оборудование",
            "АНАЛИЗ ОБОРУДОВАНИЯ",
            "оборудование",
        ],
        required=False,
        description="Перечень основного оборудования и анализ эффективности",
        critical_fields=[
            FieldRequirement(
                field_name="equipment.sheets",
                description="Список листов с оборудованием",
                required=False,
                sources=[DataSource.EQUIPMENT_JSON],
                validation_rules={"min_count": 0},
            ),
            FieldRequirement(
                field_name="equipment.sections",
                description="Секции оборудования (цехи, участки)",
                required=False,
                sources=[DataSource.EQUIPMENT_JSON],
                validation_rules={"min_count": 0},
            ),
            FieldRequirement(
                field_name="equipment.items",
                description="Единицы оборудования",
                required=False,
                sources=[DataSource.EQUIPMENT_JSON],
                validation_rules={"min_count": 0},
            ),
        ],
        optional_fields=[
            FieldRequirement(
                field_name="equipment.summary.total_power_kw",
                description="Общая установленная мощность",
                required=False,
                sources=[DataSource.EQUIPMENT_JSON],
            ),
            FieldRequirement(
                field_name="equipment.summary.vfd_with_frequency_drive",
                description="Количество единиц с частотным приводом",
                required=False,
                sources=[DataSource.EQUIPMENT_JSON],
            ),
        ],
    ),
    "02_Исходные данные": SheetRequirement(
        sheet_name="02_Исходные данные",
        alternative_names=["Исходные данные", "Ограждающие конструкции", "Envelope"],
        required=True,
        description="Расчет теплопотерь по зданиям",
        critical_fields=[
            FieldRequirement(
                field_name="envelope.sections",
                description="Секции расчета теплопотерь по зданиям (минимум 1 секция)",
                required=True,
                sources=[DataSource.ENVELOPE_JSON],
                validation_rules={"min_count": 1},
            ),
            FieldRequirement(
                field_name="envelope.items",
                description="Элементы расчета теплопотерь по зданиям",
                required=True,
                sources=[DataSource.ENVELOPE_JSON],
                validation_rules={"min_count": 1},
            ),
        ],
        optional_fields=[
            FieldRequirement(
                field_name="envelope.summary.total_area_m2",
                description="Общая площадь ограждающих конструкций",
                required=False,
                sources=[DataSource.ENVELOPE_JSON],
            ),
            FieldRequirement(
                field_name="envelope.summary.total_heat_loss",
                description="Общие теплопотери по зданиям",
                required=False,
                sources=[DataSource.ENVELOPE_JSON],
            ),
        ],
    ),
    "04_Баланс": SheetRequirement(
        sheet_name="04_Баланс",
        alternative_names=["Баланс", "Balans", "04_Balans", "Энергетический баланс"],
        required=True,
        description="Энергетический баланс по категориям потребления",
        critical_fields=[
            FieldRequirement(
                field_name="electricity.by_usage",
                description="Потребление электроэнергии по категориям (технологические, собственные нужды, производственные, хоз-бытовые)",
                required=True,
                sources=[DataSource.AGGREGATED_JSON, DataSource.USAGE_CATEGORIES_JSON],
                validation_rules={
                    "min_quarters": 4,
                    "required_categories": [
                        "technological",
                        "own_needs",
                        "production",
                        "household",
                    ],
                },
            ),
        ],
        optional_fields=[
            FieldRequirement(
                field_name="usage_data.years",
                description="Данные по категориям по годам",
                required=False,
                sources=[DataSource.USAGE_CATEGORIES_JSON],
            ),
        ],
    ),
    "05_Динамика": SheetRequirement(
        sheet_name="05_Динамика",
        alternative_names=["Динамика ср", "Dinamika sr", "05_Dinamika", "Динамика"],
        required=True,
        description="Динамика потребления и удельные показатели",
        critical_fields=[
            FieldRequirement(
                field_name="electricity.quarter_totals",
                description="Квартальные итоги потребления электроэнергии",
                required=True,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 4},
            ),
            FieldRequirement(
                field_name="gas.quarter_totals",
                description="Квартальные итоги потребления газа",
                required=True,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 4},
            ),
            FieldRequirement(
                field_name="water.quarter_totals",
                description="Квартальные итоги потребления воды",
                required=False,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 2},
            ),
            FieldRequirement(
                field_name="production.quarter_totals",
                description="Квартальные итоги производства",
                required=False,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 2},
            ),
        ],
    ),
    "мазут,уголь 5": SheetRequirement(
        sheet_name="мазут,уголь 5",
        alternative_names=["05_Мазут_Уголь", "Fuel Dynamics", "Топливо"],
        required=False,
        description="Динамика потребления топлива (мазут, уголь)",
        critical_fields=[
            FieldRequirement(
                field_name="fuel.quarter_totals",
                description="Квартальные итоги потребления мазута",
                required=False,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 2},
            ),
            FieldRequirement(
                field_name="coal.quarter_totals",
                description="Квартальные итоги потребления угля",
                required=False,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 2},
            ),
        ],
    ),
    "Расход на ед.п": SheetRequirement(
        sheet_name="Расход на ед.п",
        alternative_names=[
            "Расход  на ед.п",
            "06_Расход_на_ед",
            "Specific Consumption",
        ],
        required=False,
        description="Расход энергоресурсов на единицу продукции",
        critical_fields=[
            FieldRequirement(
                field_name="electricity.quarter_totals.active_kwh",
                description="Потребление электроэнергии для расчёта удельного расхода",
                required=True,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 4},
            ),
            FieldRequirement(
                field_name="production.quarter_totals",
                description="Объём производства для расчёта удельного расхода",
                required=False,
                sources=[DataSource.AGGREGATED_JSON],
                validation_rules={"min_quarters": 2, "allow_zero": True},
            ),
        ],
    ),
    "06_Мероприятия": SheetRequirement(
        sheet_name="06_Мероприятия",
        alternative_names=[
            "Мероприятия",
            "Meropriyatiya",
            "06_Meropriyatiya",
            "Мериаприятия 1",
        ],
        required=False,
        description="Энергосберегающие мероприятия",
        critical_fields=[
            FieldRequirement(
                field_name="measures",
                description="Список энергосберегающих мероприятий",
                required=False,
                sources=[DataSource.DEFAULT_VALUES],
                default_value=[],
                validation_rules={"min_count": 0},
            ),
        ],
    ),
    "08_Потери_электроэнергии": SheetRequirement(
        sheet_name="08_Потери_электроэнергии",
        alternative_names=["Потери", "Losses"],
        required=False,
        description="Потери электроэнергии в трансформаторе",
        critical_fields=[
            FieldRequirement(
                field_name="loss_active_month",
                description="Потери активной энергии за месяц",
                required=False,
                sources=[DataSource.DEFAULT_VALUES],
                default_value=0.0,
            ),
            FieldRequirement(
                field_name="loss_reactive_month",
                description="Потери реактивной энергии за месяц",
                required=False,
                sources=[DataSource.DEFAULT_VALUES],
                default_value=0.0,
            ),
            FieldRequirement(
                field_name="transformer_power_kva",
                description="Мощность трансформатора",
                required=False,
                sources=[DataSource.DEFAULT_VALUES],
                default_value=0.0,
            ),
        ],
    ),
}


def get_sheet_requirement(sheet_name: str) -> Optional[SheetRequirement]:
    """
    Получает требования для листа по его имени.

    Args:
        sheet_name: Название листа

    Returns:
        SheetRequirement или None, если лист не найден
    """
    # Прямой поиск
    if sheet_name in PASSPORT_SHEET_REQUIREMENTS:
        return PASSPORT_SHEET_REQUIREMENTS[sheet_name]

    # Поиск по альтернативным именам
    for req in PASSPORT_SHEET_REQUIREMENTS.values():
        if sheet_name in req.alternative_names:
            return req

    return None


def get_required_sheets() -> List[str]:
    """Возвращает список обязательных листов."""
    return [
        req.sheet_name for req in PASSPORT_SHEET_REQUIREMENTS.values() if req.required
    ]


def get_required_data_sources() -> Set[DataSource]:
    """Возвращает набор необходимых источников данных."""
    sources = set()
    for req in PASSPORT_SHEET_REQUIREMENTS.values():
        for field_req in req.critical_fields:
            sources.update(field_req.sources)
    return sources


def validate_sheet_data(
    sheet_name: str, data: Dict[str, Any]
) -> tuple[bool, List[str]]:
    """
    Валидирует данные для заполнения листа.

    Args:
        sheet_name: Название листа
        data: Данные для заполнения

    Returns:
        (is_valid, list_of_errors)
    """
    req = get_sheet_requirement(sheet_name)
    if not req:
        return True, []  # Лист не требует валидации

    errors = []

    # Проверяем критические поля
    for field_req in req.critical_fields:
        if not field_req.required:
            continue

        # Проверяем наличие поля в данных
        field_parts = field_req.field_name.split(".")
        field_value = data
        for part in field_parts:
            if isinstance(field_value, dict):
                field_value = field_value.get(part)
            else:
                field_value = None
                break

        if field_value is None:
            if field_req.default_value is None:
                errors.append(
                    f"Лист '{sheet_name}': отсутствует обязательное поле '{field_req.field_name}' "
                    f"({field_req.description})"
                )
        else:
            # Проверяем правила валидации
            if field_req.validation_rules:
                rules = field_req.validation_rules

                # Проверка минимального количества
                if "min_count" in rules:
                    if isinstance(field_value, (list, dict)):
                        count = len(field_value)
                        if count < rules["min_count"]:
                            errors.append(
                                f"Лист '{sheet_name}': поле '{field_req.field_name}' "
                                f"должно содержать минимум {rules['min_count']} элементов, "
                                f"найдено {count}"
                            )

                # Проверка минимального значения
                if "min_value" in rules:
                    if isinstance(field_value, (int, float)):
                        # Если allow_zero=True, пропускаем проверку для нулевых значений
                        if not rules.get("allow_zero", False) or field_value != 0:
                            if field_value < rules["min_value"]:
                                errors.append(
                                    f"Лист '{sheet_name}': поле '{field_req.field_name}' "
                                    f"должно быть >= {rules['min_value']}, найдено {field_value}"
                                )

    return len(errors) == 0, errors
