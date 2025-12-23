import os
from typing import Literal

ExcelSemanticMode = Literal["off", "assist", "strict"]


def get_excel_semantic_mode() -> ExcelSemanticMode:
    """
    Read feature flag for Excel semantic AI layer.
    Values: off | assist | strict (default: off)
    """
    mode = os.getenv("EXCEL_SEMANTIC_AI_MODE", "off").strip().lower()
    if mode not in ("off", "assist", "strict"):
        return "off"
    return mode  # type: ignore[return-value]
