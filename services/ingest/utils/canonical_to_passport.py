from __future__ import annotations

import logging
from typing import Any, Dict

from ai.ai_excel_semantic_parser import (
    CanonicalSourceData,
    EquipmentItem,
    NodeItem,
    ResourceEntry,
    TimeSeries,
)
from domain.passport_field_map import (
    get_default_passport_field_map,
    DEFAULT_ELECTRICITY_USAGE_CATEGORIES,
)
from domain.electricity_usage_classifier import classify_equipment_usage

logger = logging.getLogger(__name__)


def canonical_to_passport_payload(canonical: CanonicalSourceData) -> Dict[str, Any]:
    """
    Convert CanonicalSourceData into a payload structure consumable by existing
    template filling helpers. Design-first: returns a sketch payload to be used later.
    """
    field_map = get_default_passport_field_map()

    # Sketch: assemble per-section containers; detail mapping will be implemented incrementally.
    payload: Dict[str, Any] = {
        "structure": {},  # for 'Структура пр 2' (future)
        "balance": {},  # for 'Баланс' (annual_totals + electricity.by_usage)
        "dynamics": {},  # for 'Динамика ср' (future)
        "fuel_coal": {},  # for 'мазут,уголь 5' (future)
        "specific": {},  # for 'Расход на ед.п' (future)
        "nodes": [],
        "equipment": [],
        "provenance": canonical.provenance,
        "_mapping_info": {"sections": list(field_map.sections.keys())},
    }

    # Nodes → list[dict] compatible with fill_nodes_sheet default path
    for node in canonical.nodes or []:
        if isinstance(node, NodeItem):
            payload["nodes"].append(
                {
                    "name": node.node_id or node.location or "Узел учета",
                    "resource": node.resource or "Электрическая энергия",
                    "meter_type": node.meter_type or "",
                    "location": node.location or "",
                    "notes": node.notes or "",
                }
            )
        else:
            # assume dict-like
            payload["nodes"].append(dict(node))  # type: ignore[arg-type]

    # Equipment → dict compatible with fill_equipment_sheet (sheets/sections/items/summary)
    sections = [
        {
            "title": "Canonical Equipment",
            "items": [],
        }
    ]
    total_power = 0.0
    total_items = 0
    for item in canonical.equipment or []:
        if isinstance(item, EquipmentItem):
            unit_power = item.nominal_power_kw or 0.0
            sections[0]["items"].append(
                {
                    "name": item.name,
                    "type": item.type or "",
                    "unit_power_kw": unit_power,
                    "total_power_kw": unit_power,  # no quantity in canonical yet
                }
            )
            total_power += float(unit_power or 0.0)
            total_items += 1
        else:
            try:
                name = item.get("name", "Оборудование")
                unit_power = float(item.get("nominal_power_kw") or 0.0)
                sections[0]["items"].append(
                    {
                        "name": name,
                        "type": item.get("type", ""),
                        "unit_power_kw": unit_power,
                        "total_power_kw": unit_power,
                    }
                )
                total_power += unit_power
                total_items += 1
            except Exception:
                continue

    equipment_data = {
        "source": "canonical",
        "sheets": [{"sheet": "Canonical", "sections": sections}],
        "summary": {
            "total_sheets": 1,
            "total_sections": len(sections),
            "total_items": total_items,
            "total_power_kw": round(total_power, 2),
            "vfd_with_frequency_drive": 0,
        },
    }
    payload["equipment"] = equipment_data

    # Minimal annual totals per resource (for future mappers; current fillers expect quarterly)
    annual_totals: Dict[str, float] = {}
    for entry in canonical.resources or []:
        if isinstance(entry, ResourceEntry):
            series: TimeSeries = entry.series
            if (
                series
                and series.annual is not None
                and isinstance(series.annual, (int, float))
            ):
                annual_totals[entry.resource] = float(series.annual)
            elif series and series.monthly:
                try:
                    annual_totals[entry.resource] = float(
                        sum(
                            v
                            for v in series.monthly.values()
                            if isinstance(v, (int, float))
                        )
                    )
                except Exception:
                    pass

    payload["balance"]["annual_totals"] = annual_totals

    # Compute electricity by_usage from equipment composition if possible
    # Uses the new deterministic classifier from electricity_usage_classifier
    def compute_electricity_by_usage(
        canonical_src: CanonicalSourceData, annual_total: float
    ) -> Dict[str, float]:
        """
        Вычисляет распределение электроэнергии по категориям использования на основе оборудования.

        Детерминистическая процедура:
        1. Для каждого оборудования определяет релевантность к электроэнергии
        2. Классифицирует оборудование по категории использования
        3. Вычисляет веса на основе мощности и коэффициента использования
        4. Распределяет annual_total пропорционально весам

        Args:
                canonical_src: CanonicalSourceData с оборудованием и узлами
                annual_total: Годовое потребление электроэнергии (кВт·ч)

        Returns:
                Словарь {category_id: value} с распределением по категориям
        """
        weights: Dict[str, float] = {}
        total_weight = 0.0

        # Получаем узлы для улучшения классификации
        nodes = canonical_src.nodes if canonical_src.nodes else None

        for eq in canonical_src.equipment or []:
            try:
                # Определяем релевантность оборудования к электроэнергии
                is_electricity_relevant = False

                if isinstance(eq, EquipmentItem):
                    # Проверяем явную подсказку в extra
                    extra = getattr(eq, "extra", {}) or {}
                    if isinstance(extra, dict):
                        res_hint = (
                            (extra.get("resource") or extra.get("energy") or "")
                            .strip()
                            .lower()
                        )
                        if res_hint:
                            is_electricity_relevant = (
                                res_hint == "electricity"
                                or res_hint == "электроэнергия"
                            )

                    # Если нет явной подсказки, предполагаем что все оборудование относится к электроэнергии
                    # TODO: В будущем можно добавить более точную проверку релевантности
                    if not is_electricity_relevant:
                        # Эвристика: если оборудование имеет nominal_power_kw, оно потребляет электроэнергию
                        if eq.nominal_power_kw is not None and eq.nominal_power_kw > 0:
                            is_electricity_relevant = True

                    if not is_electricity_relevant:
                        continue

                    # Получаем мощность и коэффициент использования
                    power = (
                        float(eq.nominal_power_kw)
                        if eq.nominal_power_kw is not None
                        else 0.0
                    )
                    util = (
                        float(eq.utilization_factor)
                        if getattr(eq, "utilization_factor", None) is not None
                        else 1.0
                    )

                    if power <= 0:
                        continue

                    # Классифицируем оборудование
                    usage_category = classify_equipment_usage(eq, nodes)

                    # Вычисляем вес (мощность * коэффициент использования)
                    weight = max(0.0, power * util)
                    weights[usage_category] = weights.get(usage_category, 0.0) + weight
                    total_weight += weight

                else:
                    # dict-like fallback (для совместимости)
                    power = float(eq.get("nominal_power_kw") or 0.0)
                    if power <= 0:
                        continue

                    util = float(eq.get("utilization_factor") or 1.0)
                    weight = max(0.0, power * util)

                    # Для dict-like используем простую нормализацию или создаем EquipmentItem
                    extra = eq.get("extra", {}) or {}
                    usage_category_hint = extra.get("usage_category") or eq.get(
                        "usage_category"
                    )

                    if usage_category_hint:
                        # Используем нормализацию из классификатора
                        from domain.electricity_usage_classifier import (
                            _normalize_category_id,
                        )

                        usage_category = _normalize_category_id(
                            str(usage_category_hint)
                        )
                    else:
                        # Пытаемся создать EquipmentItem для классификации
                        try:
                            eq_item = EquipmentItem(
                                name=str(eq.get("name", "")),
                                type=str(eq.get("type", "")),
                                location=str(eq.get("location", "")),
                                nominal_power_kw=power,
                                utilization_factor=util,
                                extra=extra,
                            )
                            usage_category = classify_equipment_usage(eq_item, nodes)
                        except Exception:
                            # Fallback на production
                            usage_category = "production"

                    weights[usage_category] = weights.get(usage_category, 0.0) + weight
                    total_weight += weight

            except Exception as e:
                logger.debug(f"Ошибка при обработке оборудования для by_usage: {e}")
                continue

        # Если нет весов или annual_total отсутствует, возвращаем пустой словарь
        if total_weight <= 0.0 or annual_total is None:
            return {}

        # Распределяем annual_total пропорционально весам
        by_usage: Dict[str, float] = {}
        for cat, w in weights.items():
            by_usage[cat] = (
                float(annual_total) * (w / total_weight) if total_weight > 0 else 0.0
            )

        # Проверяем, что сумма близка к annual_total (с учетом округления)
        total_distributed = sum(by_usage.values())
        if abs(total_distributed - annual_total) > 0.01:  # допуск 0.01 кВт·ч
            # Корректируем последнюю категорию для точного соответствия
            if by_usage:
                last_cat = list(by_usage.keys())[-1]
                by_usage[last_cat] += annual_total - total_distributed

        return by_usage

    # Build electricity.by_usage mapping for Balance (canonical-side)
    electricity_total = annual_totals.get("electricity")
    if electricity_total is not None and (canonical.equipment or []):
        by_usage = compute_electricity_by_usage(canonical, electricity_total)
        if by_usage:
            # Map to template keys
            template_by_usage: Dict[str, float] = {}
            for uc in DEFAULT_ELECTRICITY_USAGE_CATEGORIES:
                if uc.id in by_usage:
                    template_by_usage[uc.template_key] = by_usage[uc.id]
            if template_by_usage:
                payload["balance"].setdefault("by_usage", {})
                payload["balance"]["by_usage"]["electricity"] = template_by_usage

    # Generalized by_usage for other resources (heat/gas/water/fuel/coal) — simple relevance + same categories
    def equipment_relevant_for(resource: str, item: EquipmentItem) -> bool:
        try:
            extra = getattr(item, "extra", {}) or {}
            res_hint = (
                (extra.get("resource") or extra.get("energy") or "").strip().lower()
            )
            if res_hint:
                return res_hint == resource
        except Exception:
            pass
        # Heuristic keywords (extend later)
        name = (getattr(item, "name", "") or "").lower()
        typ = (getattr(item, "type", "") or "").lower()
        if resource == "gas":
            return any(
                k in name or k in typ
                for k in ["газ", "gas", "котел", "котёл", "boiler"]
            )
        if resource == "water":
            return any(
                k in name or k in typ for k in ["вода", "water", "насос", "pump"]
            )
        if resource == "heat":
            return any(
                k in name or k in typ
                for k in ["тепло", "heat", "кал", "гкал", "котел", "boiler"]
            )
        if resource == "fuel":
            return any(
                k in name or k in typ for k in ["мазут", "fuel", "дизель", "нефте"]
            )
        if resource == "coal":
            return any(k in name or k in typ for k in ["уголь", "coal"])
        return False

    def compute_resource_by_usage(
        resource: str, annual_total: float
    ) -> Dict[str, float]:
        weights: Dict[str, float] = {}
        total_weight = 0.0
        # Получаем узлы для улучшения классификации
        nodes = canonical.nodes if canonical.nodes else None
        for eq in canonical.equipment or []:
            try:
                if not isinstance(eq, EquipmentItem):
                    # dict-like
                    power = float(eq.get("nominal_power_kw") or 0.0)
                    util = float(eq.get("utilization_factor") or 1.0)
                    if power <= 0:
                        continue
                    # resource relevance
                    relevant = False
                    extra = eq.get("extra", {}) or {}
                    rh = str(extra.get("resource", "")).strip().lower()
                    if rh:
                        relevant = rh == resource
                    else:
                        relevant = equipment_relevant_for(
                            resource,
                            EquipmentItem(
                                name=str(eq.get("name", "")),
                                type=str(eq.get("type", "")),
                                nominal_power_kw=power,
                                extra=extra,
                            ),
                        )
                    if not relevant:
                        continue
                    weight = max(0.0, power * util)
                    # Используем нормализацию из классификатора
                    usage_category_hint = extra.get("usage_category")
                    if usage_category_hint:
                        from domain.electricity_usage_classifier import (
                            _normalize_category_id,
                        )

                        cat = _normalize_category_id(str(usage_category_hint))
                    else:
                        # Пытаемся создать EquipmentItem для классификации
                        try:
                            eq_item = EquipmentItem(
                                name=str(eq.get("name", "")),
                                type=str(eq.get("type", "")),
                                location=str(eq.get("location", "")),
                                nominal_power_kw=power,
                                utilization_factor=util,
                                extra=extra,
                            )
                            cat = classify_equipment_usage(eq_item, nodes)
                        except Exception:
                            # Fallback на production
                            cat = "production"
                    weights[cat] = weights.get(cat, 0.0) + weight
                    total_weight += weight
                else:
                    # pydantic item
                    power = (
                        float(eq.nominal_power_kw)
                        if eq.nominal_power_kw is not None
                        else 0.0
                    )
                    util = (
                        float(eq.utilization_factor)
                        if getattr(eq, "utilization_factor", None) is not None
                        else 1.0
                    )
                    if power <= 0:
                        continue
                    if not equipment_relevant_for(resource, eq):
                        continue
                    weight = max(0.0, power * util)
                    # Используем новый классификатор с узлами для улучшения точности
                    cat = classify_equipment_usage(eq, nodes)
                    weights[cat] = weights.get(cat, 0.0) + weight
                    total_weight += weight
            except Exception:
                continue
        if total_weight <= 0.0 or annual_total is None:
            return {}
        by_usage: Dict[str, float] = {}
        for cat, w in weights.items():
            by_usage[cat] = (
                float(annual_total) * (w / total_weight) if total_weight > 0 else 0.0
            )
        # Map to template keys
        template_by_usage: Dict[str, float] = {}
        for uc in DEFAULT_ELECTRICITY_USAGE_CATEGORIES:
            if uc.id in by_usage:
                template_by_usage[uc.template_key] = by_usage[uc.id]
        return template_by_usage

    for res_name in ("heat", "gas", "water", "fuel", "coal"):
        total = annual_totals.get(res_name)
        if total is not None and (canonical.equipment or []):
            byu = compute_resource_by_usage(res_name, total)
            if byu:
                payload["balance"].setdefault("by_usage", {})
                payload["balance"]["by_usage"][res_name] = byu
    return payload
