import sys
from pathlib import Path

# Ensure project root on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from eaip_full_skeleton.services.ingest.ai.ai_excel_semantic_parser import (  # type: ignore
    CanonicalSourceData,
    ResourceEntry,
    TimeSeries,
    EquipmentItem,
    NodeItem,
)
from eaip_full_skeleton.services.ingest.utils.canonical_to_passport import (  # type: ignore
    canonical_to_passport_payload,
)


def test_canonical_to_passport_payload_nodes_equipment_and_annual():
    canonical = CanonicalSourceData(
        resources=[
            ResourceEntry(resource="electricity", series=TimeSeries(annual=1234.0)),
        ],
        equipment=[
            EquipmentItem(
                name="Compressor-1",
                type="Compressor",
                nominal_power_kw=45.0,
                location="Shop-1",
            ),
            EquipmentItem(
                name="Fan-2", type="Fan", nominal_power_kw=7.5, location="Shop-2"
            ),
        ],
        nodes=[
            NodeItem(
                node_id="NODE-001", resource="Электрическая энергия", location="ТП-1"
            ),
            NodeItem(
                node_id="NODE-002", resource="Электрическая энергия", location="ТП-2"
            ),
        ],
    )

    payload = canonical_to_passport_payload(canonical)

    # Nodes assertions
    assert "nodes" in payload
    assert isinstance(payload["nodes"], list)
    assert len(payload["nodes"]) >= 2
    assert isinstance(payload["nodes"][0], dict)
    assert payload["nodes"][0].get("resource") is not None

    # Equipment assertions
    assert "equipment" in payload
    eq = payload["equipment"]
    assert isinstance(eq, dict)
    assert "sheets" in eq and isinstance(eq["sheets"], list) and len(eq["sheets"]) >= 1
    sections = eq["sheets"][0].get("sections", [])
    assert isinstance(sections, list) and len(sections) >= 1
    items = sections[0].get("items", [])
    assert isinstance(items, list) and len(items) >= 2
    first_item = items[0]
    assert (
        "name" in first_item
        and "unit_power_kw" in first_item
        and "total_power_kw" in first_item
    )

    # Balance annual totals (skeleton for future mapping)
    balance = payload.get("balance", {})
    annual = balance.get("annual_totals", {})
    assert isinstance(annual, dict)
    assert annual.get("electricity") == 1234.0
