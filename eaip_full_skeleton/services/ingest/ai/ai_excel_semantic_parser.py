from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, Field
import os
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TimeSeries(BaseModel):
    """Generic time series supporting monthly, quarterly and annual values."""

    monthly: Optional[Dict[str, float]] = None  # keys: "01".."12" or "jan".."dec"
    quarterly: Optional[Dict[str, float]] = None  # keys: "Q1","Q2","Q3","Q4"
    annual: Optional[float] = None
    unit: Optional[str] = None


class ResourceEntry(BaseModel):
    """Single resource entry describing consumption or production."""

    resource: Literal["electricity", "heat", "gas", "water", "fuel", "coal"]
    category: Optional[str] = None  # e.g., "consumption", "production", "losses"
    name: Optional[str] = None  # free-form label (sheet-level or line item)
    series: TimeSeries
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EquipmentItem(BaseModel):
    """Equipment description aligned with ПКМ 690 needs."""

    name: str
    type: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    nominal_power_kw: Optional[float] = None
    capacity: Optional[float] = None
    unit: Optional[str] = None
    utilization_factor: Optional[float] = None
    notes: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class NodeItem(BaseModel):
    """Metering node information."""

    node_id: Optional[str] = None
    resource: Optional[str] = None
    location: Optional[str] = None
    meter_type: Optional[str] = None
    notes: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class EnvelopeItem(BaseModel):
    """Building envelope element."""

    element: Optional[str] = None  # e.g., wall, window, roof
    material: Optional[str] = None
    area_m2: Optional[float] = None
    u_value_w_m2k: Optional[float] = None
    notes: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class FieldProvenance(BaseModel):
    """Traceability from canonical fields back to Excel origin."""

    sheet: Optional[str] = None
    header_cells: List[str] = Field(default_factory=list)  # e.g., A1:C1
    data_cells: List[str] = Field(default_factory=list)  # e.g., B3, C3
    confidence: float = 0.0
    notes: Optional[str] = None


class CanonicalSourceData(BaseModel):
    """Canonical schema for energy passport source data."""

    resources: List[ResourceEntry] = Field(default_factory=list)
    equipment: List[EquipmentItem] = Field(default_factory=list)
    nodes: List[NodeItem] = Field(default_factory=list)
    envelope: List[EnvelopeItem] = Field(default_factory=list)
    provenance: Dict[str, FieldProvenance] = Field(default_factory=dict)


class AnalyzeSheetInput(BaseModel):
    """Input to the semantic analyzer for a single Excel sheet."""

    sheet_name: str
    header_rows: List[List[str]] = Field(default_factory=list)
    sample_rows: List[List[str]] = Field(default_factory=list)
    language_hints: List[str] = Field(default_factory=list)  # e.g., ["ru", "uz"]
    current_mapping_rules: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeSheetResult(BaseModel):
    """Result of analyzing a sheet: deterministic + AI suggestions."""

    partial: CanonicalSourceData = Field(default_factory=CanonicalSourceData)
    confidence: float = 0.0
    notes: List[str] = Field(default_factory=list)
    used_ai: bool = False


def analyze_excel_sheet(payload: AnalyzeSheetInput) -> AnalyzeSheetResult:
    """
    Deterministic-first analysis of a single Excel sheet.
    - Try to infer resource type and columns (monthly/quarterly/annual) based on headers.
    - If headers are unknown or confidence is low, this function should request an LLM mapping
      via `call_llm_for_semantic_mapping(...)`.
    - Returned result must be expressed in the CanonicalSourceData schema with provenance.
    Note: This is a stub. Implementation will be added incrementally and tested with real messy sheets.
    """
    # Minimal deterministic implementation based on sheet name and header patterns
    sheet_name_lower = payload.sheet_name.lower().strip()
    res = CanonicalSourceData()
    notes: List[str] = []
    confidence = 0.0

    # Month aliases (ru/en short)
    month_aliases = {
        "янв": "01",
        "фев": "02",
        "мар": "03",
        "апр": "04",
        "май": "05",
        "июн": "06",
        "июл": "07",
        "авг": "08",
        "сен": "09",
        "oct": "10",
        "окт": "10",
        "ноя": "11",
        "дек": "12",
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "sept": "09",
        "nov": "11",
        "dec": "12",
    }

    def detect_resource_from_name(name: str) -> Optional[str]:
        if any(k in name for k in ["электр", "electr", "тп"]):
            return "electricity"
        if "газ" in name or "gas" in name:
            return "gas"
        if "сув" in name or "water" in name or "вода" in name:
            return "water"
        if "тепл" in name or "heat" in name or "отоплен" in name or "kotel" in name:
            return "heat"
        if "уголь" in name or "coal" in name:
            return "coal"
        if "мазут" in name or "fuel" in name or "топливо" in name:
            return "fuel"
        if "узел" in name or "node" in name or "счетч" in name:
            return "nodes"
        if "оборуд" in name or "equipment" in name:
            return "equipment"
        if "ограж" in name or "envelope" in name or "теплопровод" in name:
            return "envelope"
        return None

    resource_hint = detect_resource_from_name(sheet_name_lower)

    # Try to extract a simple monthly time series if first column looks like month labels
    def extract_simple_timeseries() -> Optional[TimeSeries]:
        if not payload.sample_rows:
            return None
        monthly: Dict[str, float] = {}
        matches = 0
        for row in payload.sample_rows:
            if not row or row[0] is None:
                continue
            key_raw = str(row[0]).strip().lower()
            key = key_raw[:3]  # short match
            if key in month_aliases:
                # pick first numeric after the label
                val = None
                for cell in row[1:]:
                    if isinstance(cell, (int, float)):
                        val = float(cell)
                        break
                    try:
                        if isinstance(cell, str):
                            clean = cell.replace(" ", "").replace(",", ".")
                            val = float(clean)
                            break
                    except Exception:
                        pass
                if val is not None:
                    monthly[month_aliases[key]] = val
                    matches += 1
        if matches >= 5:
            series = TimeSeries(monthly=dict(sorted(monthly.items())))
            return series
        return None

    if resource_hint in {"electricity", "gas", "water", "heat", "fuel", "coal"}:
        series = extract_simple_timeseries()
        if series:
            res.resources.append(
                ResourceEntry(
                    resource=resource_hint,
                    category="consumption",
                    name=payload.sheet_name,
                    series=series,
                )
            )
            res.provenance[f"{payload.sheet_name}:series"] = FieldProvenance(
                sheet=payload.sheet_name,
                header_cells=[],
                data_cells=[],
                confidence=0.7,
                notes="Simple monthly series extracted by header/row heuristic",
            )
            confidence = 0.7
            notes.append("deterministic: monthly series recognized")
        else:
            notes.append("deterministic: could not recognize monthly series")
            confidence = 0.2
    elif resource_hint == "equipment":
        # For deterministic skeleton: only mark recognition; detailed extraction is handled by specialized parser elsewhere.
        notes.append(
            "deterministic: equipment sheet recognized (detailed parsing via equipment_parser)"
        )
        confidence = 0.6
    elif resource_hint == "nodes":
        notes.append(
            "deterministic: nodes sheet recognized (detailed parsing via nodes_parser)"
        )
        confidence = 0.6
    elif resource_hint == "envelope":
        notes.append(
            "deterministic: envelope sheet recognized (detailed parsing via building_envelope_parser)"
        )
        confidence = 0.6
    else:
        notes.append("deterministic: unknown sheet type")
        confidence = 0.1

    # Decide whether to augment with AI based on mode and confidence
    try:
        from services.ingest.settings.excel_semantic_settings import (
            get_excel_semantic_mode,
        )
    except Exception:
        # Fallback import path when running inside service
        try:
            from settings.excel_semantic_settings import get_excel_semantic_mode  # type: ignore
        except Exception:

            def get_excel_semantic_mode():  # type: ignore
                return "off"

    mode = get_excel_semantic_mode()
    AI_EXCEL_MIN_CONF_FOR_AI_CALL = float(
        os.getenv("AI_EXCEL_MIN_CONF_FOR_AI_CALL", "0.6")
    )

    if mode == "off":
        return AnalyzeSheetResult(
            partial=res,
            confidence=confidence,
            notes=notes + [f"mode:{mode}"],
            used_ai=False,
        )

    # Assist/Strict: Only call AI if low deterministic confidence
    if confidence >= AI_EXCEL_MIN_CONF_FOR_AI_CALL:
        return AnalyzeSheetResult(
            partial=res,
            confidence=confidence,
            notes=notes + [f"mode:{mode}", "ai:skipped_high_conf"],
            used_ai=False,
        )

    # Attempt AI mapping
    logger.info(
        "AI semantic mapping attempt for sheet='%s' mode=%s conf=%.2f",
        payload.sheet_name,
        mode,
        confidence,
    )
    ai_data, ai_conf, ai_notes = call_llm_for_semantic_mapping(
        payload.sheet_name,
        payload.header_rows,
        payload.sample_rows,
        payload.language_hints,
        payload.current_mapping_rules,
    )
    merged = merge_deterministic_and_ai_results(res, ai_data, confidence, ai_conf)
    merged.notes = (
        (notes or [])
        + (ai_notes or [])
        + [f"mode:{mode}", f"det_conf:{confidence:.2f}", f"ai_conf:{ai_conf:.2f}"]
    )
    logger.info(
        "AI semantic mapping result for sheet='%s': used_ai=%s det_conf=%.2f ai_conf=%.2f",
        payload.sheet_name,
        merged.used_ai,
        confidence,
        ai_conf,
    )
    return merged


def call_llm_for_semantic_mapping(
    sheet_name: str,
    header_rows: List[List[str]],
    sample_rows: List[List[str]],
    language_hints: Optional[List[str]] = None,
    current_mapping_rules: Optional[Dict[str, Any]] = None,
) -> Tuple[CanonicalSourceData, float, List[str]]:
    """
    Call the configured LLM provider to map arbitrary tabular content into CanonicalSourceData.
    - Uses env-configured AI stack (AI_ENABLED, AI_PROVIDER, OPENAI_API_KEY/DEEPSEEK_API_KEY).
    - Returns: (canonical_data, confidence, notes)
    Implementation details:
    - Builds a concise prompt with schema summary and trimmed table content.
    - Uses AIClientFactory to obtain a client and generates a JSON-only response.
    - Parses and validates the JSON response against CanonicalSourceData.
    """
    try:
        from settings.ai_settings import is_ai_enabled, get_ai_settings

        if not is_ai_enabled():
            return CanonicalSourceData(), 0.0, ["AI disabled"]
        settings = get_ai_settings()
        if not settings.has_valid_config:
            return (
                CanonicalSourceData(),
                0.0,
                ["AI misconfigured (no API key/provider)"],
            )
        from ai_client_factory import AIClientFactory

        client = AIClientFactory.create_client(
            client_type=os.getenv("AI_PROVIDER", "deepseek")
        )
        if client is None:
            return CanonicalSourceData(), 0.0, ["No AI client available"]

        # Prompt (concise): system + user messages if client supports chat; otherwise, a single prompt string
        schema_summary = (
            "- resources: array of {resource: electricity|heat|gas|water|fuel|coal, category?, name?, "
            "series: {monthly{MM:number}?, quarterly{Qx:number}?, annual:number?, unit?}}\n"
            "- equipment: array of {name, type?, model?, nominal_power_kw?, location?}\n"
            "- nodes: array of {node_id?, resource?, location?, meter_type?}\n"
            "- envelope: array of {element?, material?, area_m2?, u_value_w_m2k?}\n"
        )

        def trim_matrix(rows: List[List[str]], max_rows=8, max_cols=12):
            return [
                list(map(lambda v: str(v) if v is not None else "", r[:max_cols]))
                for r in rows[:max_rows]
            ]

        user_payload = {
            "task": "Map noisy Excel-like table to CanonicalSourceData JSON (no extra text).",
            "schema_summary": schema_summary,
            "sheet_name": sheet_name,
            "language_hints": language_hints or [],
            "header_rows": trim_matrix(header_rows, 3, 12),
            "sample_rows": trim_matrix(sample_rows, 10, 12),
            "current_mapping_rules": current_mapping_rules or {},
            "output_format": {
                "resources": "array",
                "equipment": "array",
                "nodes": "array",
                "envelope": "array",
                "provenance": "object",
            },
            "return": "JSON only",
        }

        logger.info(
            "LLM call: sheet='%s' provider='%s' langs=%s",
            sheet_name,
            settings.provider,
            ",".join(language_hints or []),
        )

        data: Dict[str, Any] = {}
        temperature = float(os.getenv("AI_EXCEL_TEMPERATURE", "0.1"))
        max_tokens = int(os.getenv("AI_EXCEL_MAX_TOKENS", "1200"))

        # Prefer structured method if available
        if hasattr(client, "generate_json"):
            data = (
                client.generate_json(
                    prompt=json.dumps(
                        {
                            "system": "You are an energy-audit assistant. Respond with pure JSON.",
                            "user": user_payload,
                        },
                        ensure_ascii=False,
                    ),
                    temperature=temperature,
                )
                or {}
            )
        else:
            prompt_text = (
                "You are an energy-audit assistant. Respond with pure JSON only.\n"
                f"INPUT:\n{json.dumps(user_payload, ensure_ascii=False)}"
            )
            text = client.generate(
                prompt=prompt_text, temperature=temperature, max_tokens=max_tokens
            )
            try:
                data = json.loads(text)
            except Exception:
                logger.warning("LLM returned non-JSON text for sheet='%s'", sheet_name)
                return CanonicalSourceData(), 0.0, ["AI returned non-JSON text"]

        canonical = CanonicalSourceData.parse_obj(data)
        # Confidence heuristics: presence of at least one section
        has_any = any(
            [
                canonical.resources,
                canonical.equipment,
                canonical.nodes,
                canonical.envelope,
            ]
        )
        conf = 0.75 if has_any else 0.3
        logger.info(
            "LLM mapping success sheet='%s' conf=%.2f has_any=%s",
            sheet_name,
            conf,
            has_any,
        )
        return canonical, conf, ["LLM mapping used" if has_any else "LLM mapping empty"]
    except Exception as exc:
        logger.warning(f"AI semantic mapping failed: {exc}")
        return CanonicalSourceData(), 0.0, [f"AI error: {exc!s}"]


def merge_deterministic_and_ai_results(
    deterministic: CanonicalSourceData,
    ai_data: CanonicalSourceData,
    deterministic_conf: float,
    ai_conf: float,
) -> AnalyzeSheetResult:
    """
    Merge deterministic and AI results with a confidence-aware strategy:
    - Prefer deterministic mapping where headers and units are unambiguous.
    - Fill gaps from AI output only when confidence exceeds a configurable threshold.
    - Preserve provenance for traceability.
    Note: This is a stub. The implementation will define merge policies and thresholds.
    """
    # Thresholds
    AI_EXCEL_MIN_CONF_FOR_FILL = float(os.getenv("AI_EXCEL_MIN_CONF_FOR_FILL", "0.6"))
    AI_EXCEL_MIN_CONF_FOR_OVERRIDE = float(
        os.getenv("AI_EXCEL_MIN_CONF_FOR_OVERRIDE", "0.8")
    )

    def dedup_by_key(items: List[Any], key_fn) -> List[Any]:
        seen = set()
        out: List[Any] = []
        for it in items or []:
            k = key_fn(it)
            if k in seen:
                continue
            seen.add(k)
            out.append(it)
        return out

    def merge_lists(
        det_list: List[Any], ai_list: List[Any], key_fn=lambda x: str(x)
    ) -> List[Any]:
        # Prefer AI when very confident and deterministic weak; else fill gaps
        if (
            ai_conf >= AI_EXCEL_MIN_CONF_FOR_OVERRIDE
            and deterministic_conf < AI_EXCEL_MIN_CONF_FOR_FILL
        ):
            return dedup_by_key(ai_list or [], key_fn)
        if (
            ai_conf >= AI_EXCEL_MIN_CONF_FOR_FILL
            and deterministic_conf < AI_EXCEL_MIN_CONF_FOR_OVERRIDE
        ):
            return dedup_by_key((det_list or []) + (ai_list or []), key_fn)
        return dedup_by_key(det_list or [], key_fn)

    merged = CanonicalSourceData(
        resources=merge_lists(
            deterministic.resources,
            ai_data.resources,
            key_fn=lambda r: getattr(r, "name", None) or getattr(r, "resource", None),
        ),
        equipment=merge_lists(
            deterministic.equipment,
            ai_data.equipment,
            key_fn=lambda e: getattr(e, "name", None),
        ),
        nodes=merge_lists(
            deterministic.nodes,
            ai_data.nodes,
            key_fn=lambda n: getattr(n, "node_id", None)
            or getattr(n, "location", None),
        ),
        envelope=merge_lists(
            deterministic.envelope,
            ai_data.envelope,
            key_fn=lambda ev: getattr(ev, "element", None)
            or getattr(ev, "material", None),
        ),
        provenance={**deterministic.provenance, **ai_data.provenance},
    )
    used_ai = any(
        [
            (
                ai_conf >= AI_EXCEL_MIN_CONF_FOR_FILL
                and (
                    ai_data.resources
                    or ai_data.equipment
                    or ai_data.nodes
                    or ai_data.envelope
                )
            )
        ]
    )
    confidence = max(deterministic_conf or 0.0, ai_conf or 0.0)
    notes = []
    if used_ai:
        notes.append("ai contributed")
    return AnalyzeSheetResult(
        partial=merged,
        confidence=confidence,
        notes=notes or ["deterministic only"],
        used_ai=used_ai,
    )


__all__ = [
    "TimeSeries",
    "ResourceEntry",
    "EquipmentItem",
    "NodeItem",
    "EnvelopeItem",
    "FieldProvenance",
    "CanonicalSourceData",
    "AnalyzeSheetInput",
    "AnalyzeSheetResult",
    "analyze_excel_sheet",
    "call_llm_for_semantic_mapping",
    "merge_deterministic_and_ai_results",
]
