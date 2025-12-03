# EXCEL Pipeline Overview (Audit + AI Readiness)

This document summarizes how Excel files are currently parsed and transformed into aggregated energy data, highlights fragility points, and proposes an AI-assisted semantic layer for robust understanding and mapping to the ПКМ 690 energy passport.

## 1) Current Excel → Aggregate Pipeline

Scope examined:

- `services/ingest/parsers/excel_passport_parser.py`
- `services/ingest/utils/energy_aggregator.py`
- `services/ingest/utils/equipment_parser.py`
- `services/ingest/utils/nodes_parser.py`
- `services/ingest/utils/building_envelope_parser.py`
- `services/ingest/main.py` (endpoints and template filling flow)
- Any writer to `data/aggregated` or Excel template

### 1.1 Modules that read Excel

- `services/ingest/file_parser.py`
  - Entrypoint for parsing uploaded files; detects file type and calls `parse_excel_file()`.
  - Uses `openpyxl.load_workbook(..., data_only=True)` for reading.
  - Produces a normalized JSON for sheets: names, header rows (best-effort), and row data.
- `services/ingest/utils/energy_aggregator.py`
  - Aggregates energy data from Excel workbooks into canonical quarterly consumptions.
  - Handles both single-resource (e.g., `gaz.xlsx`, `voda.xlsx`) and multi-resource (e.g., `pererashod.xlsx`) patterns.
  - Uses `openpyxl` for reading; expects certain sheet names like `ГАЗ`, `СУВ`, electricity sheets, etc.
- `services/ingest/utils/equipment_parser.py`
  - Parses equipment-related sheets (equipment inventory, key parameters) to structured dicts used later in template filling.
- `services/ingest/utils/nodes_parser.py`
  - Parses “Узлы учета” (metering nodes) to a structured representation.
- `services/ingest/utils/building_envelope_parser.py`
  - Parses building envelope (ограждающие конструкции) data.
- `services/ingest/parsers/excel_passport_parser.py`
  - Helpers for reading and mapping cells/sheets into the passport structure.

### 1.2 Mapping sheets/columns to internal structures

- Sheet-by-sheet parsing converts tabular data into Python dicts keyed by resource or section:
  - Energy resources: electricity, gas, water, heat, fuel, coal (names vary; detection relies on sheet names and header heuristics).
  - Equipment: equipment lists with type/model/power/capacity and optional metadata.
  - Nodes: metering nodes with identifiers, locations, and measurement points.
  - Envelope: building envelope elements with area/U-value-type fields when present.
- Aggregator (`energy_aggregator.py`) unifies numeric columns into quarterly totals/series:
  - Identifies sheet by name or keyword.
  - Picks header rows via heuristics or assumes a fixed layout.
  - Maps month columns (if present) to Q1..Q4 or annual totals.
- Template filling in `main.py`:
  - Loads a ПКМ 690 Excel template with `openpyxl`.
  - Calls specific section fillers (e.g., “Структура пр 2”, “Баланс”, “Динамика ср”, “мазут,уголь 5”, “Расход на ед.п”, “Мероприятия”, “Узлы учета”, and equipment sheet).
  - Writes parsed/aggregated data into prepared ranges, sometimes restoring formulas via `utils/ai_formula_restorer.py`.

### 1.3 Assumptions and hardcoded structure

- Sheet names: presence of known Russian/Uzbek names (e.g., `ГАЗ`, `СУВ`, electricity sheet variants).
- Header position: often assumed at the first data-containing row or inferred by simple heuristics.
- Column semantics: expected columns for consumption and units; fragile when headers differ or language varies.
- Equipment and nodes: assumed field sets (name/type/power/etc.) and predictable column order.
- Template layout: sheet names and target ranges exist; fallback logic iterates workbook.sheetnames to “best match”.

### 1.4 Current limitations and fragility points

- Header variability: messy or multi-row headers easily break column matching.
- Language variance (RU/UZ) and synonyms not fully normalized.
- Non-standard files: merged cells, rotated headers, or non-tabular blocks reduce reliability.
- Resource detection: depends on sheet names and simple keyword rules.
- Error handling: openpyxl read failures or unexpected structures result in partial data.
- Weak semantic mapping: numbers lack explicit meaning without context (e.g., fuel vs. heat vs. electricity).

## 2) Current AI usage in ingestion

Searched for AI usage and config flags:

- Env/config hints: `AI_ENABLED`, `AI_PROVIDER`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY` (see `settings/ai_settings.py`, `set_ai_env.ps1`, normative UI).
- AI helpers present for OCR/table extraction/classification/validation:
  - `ai_parser.py`, `ai_table_parser.py`, `ai_ocr_enhancer.py`, `utils/ai_content_classifier.py`,
    `ai_data_validator.py`, `ai_energy_analysis.py`, `ai_quality_reporter.py`, `ai_formula_restorer.py`.
- Normative logic:
  - `domain/normative_importer.py` and `/api/normative/*` endpoints in `main.py` expose an AI-enabled path for importing normative documents when configured.

Conclusion for Excel parsing:

- AI is NOT the primary mechanism for parsing structured Excel consumption data today. Deterministic parsing via `openpyxl`/heuristics is the default, with some AI-assisted modules used for OCR/structure hints/validation where available.

## 3) Proposed AI-assisted semantic Excel layer

Introduce a semantic layer to make table understanding resilient and explicit:

- Canonical JSON schema for “energy passport source data” (resources: electricity, heat, gas, water, fuel, coal, equipment, nodes, envelope, etc.).
- Deterministic-first strategy:
  - Attempt structured reading and pattern-based mapping.
  - If headers/structure uncertain, call LLM with sheet name, header row(s), sample rows, and language hints.
  - LLM returns normalized JSON mapped to canonical schema with confidence and notes.
- Configurable AI usage:
  - Controlled by existing env vars: `AI_ENABLED`, `AI_PROVIDER`, `OPENAI_API_KEY`/`DEEPSEEK_API_KEY`.
  - Pluggable provider via existing `ai_client_factory.py`.

### Canonical schema (high-level)

- Top-level object:
  - `resources`: per resource arrays of entries with time series (monthly/quarterly/annual), units, and optional meta.
  - `equipment`: list of equipment items (type/model/power/capacity, location, utilization, notes).
  - `nodes`: metering nodes with identifiers, resource, and measurement specifics.
  - `envelope`: building envelope elements with area/U-value/material/classification.
  - `provenance`: sheet/row/column mappings and confidence scores.

### LLM call contract

- Input:
  - `sheet_name`, `header_rows`, `sample_rows`, `language_hints` (RU/UZ), `current_mapping_rules` (if any).
- Output:
  - Canonical structured JSON subset + `confidence` + `notes` + optional `field_mappings`.
- Usage:
  - Only triggered when deterministic parser signals low-confidence or unknown headers.

## 4) Code skeleton added

Created: `services/ingest/ai/ai_excel_semantic_parser.py`

- Pydantic models for canonical schema (resources/equipment/nodes/envelope/provenance).
- Stubs:
  - `analyze_excel_sheet(...)`
  - `call_llm_for_semantic_mapping(...)`
  - `merge_deterministic_and_ai_results(...)`
- Uses existing AI env variables and is provider-agnostic (integration with `ai_client_factory.py` planned).
- Not wired into the main pipeline yet (design-first).

## 5) Assumptions about ПКМ 690 template

- Sheets expected: “Узел учета”, “Структура пр 2”, “Баланс”, “Динамика ср”, “мазут,уголь 5”, “Расход на ед.п”, “Мероприятия”, sometimes “Monthly”.
- Numeric targets: quarterly/annual totals per resource, structure shares, and calculated KPIs remain in-template formulas.
- Equipment and nodes sections require stable identifiers and unit normalization before write.

## 6) Next steps (integration-ready)

- Add readiness checks per resource to block generation when required inputs missing.
- Wire `ai_excel_semantic_parser` behind a confidence threshold; only call LLM on uncertain sheets.
- Persist `provenance` for traceability from template cells back to source rows/columns.
- Add tests with messy Excel variants (multi-row headers, RU/UZ mixes, merged headers).

## AI Excel semantic layer: implementation status

- Deterministic sheet analysis is implemented in `services/ingest/ai/ai_excel_semantic_parser.py::analyze_excel_sheet` (initial heuristic).
- Workbook-level collection is available via `services/ingest/utils/canonical_collector.py::collect_canonical_from_workbook`.
- The ingest pipeline now “taps” CanonicalSourceData (attached to `parse_excel_file(... )` result as `canonical_source`) without changing existing behavior.
- Feature flag: `EXCEL_SEMANTIC_AI_MODE = off|assist|strict` (read by `services/ingest/settings/excel_semantic_settings.py`). Current iteration uses deterministic-only path; AI calls will be enabled under "assist/strict" in subsequent steps.
- Next iteration: enable AI mapping on low-confidence sheets, implement merge policy thresholds, and connect `CanonicalSourceData` to passport mapping stubs.

### Debug endpoint

- Internal debugging endpoint is available to inspect canonical data:
  - `GET /api/batches/{batch_id}/canonical-debug` returns:
    - `mode` (current EXCEL_SEMANTIC_AI_MODE),
    - `canonical_source` (if present or reconstructed),
    - `provenance`,
    - placeholder for per-sheet details (will be filled when persisted).
