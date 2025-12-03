from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union


def _default_log_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "logs"


def log_aggregation_event(
    *,
    batch_id: str,
    source_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    status: str = "success",
    message: Optional[str] = None,
    log_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Append aggregation event to JSONL log file.
    """
    directory = Path(log_dir) if log_dir else _default_log_dir()
    directory.mkdir(parents=True, exist_ok=True)
    log_path = directory / "aggregation_events.jsonl"

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "batch_id": batch_id,
        "source_file": str(source_file),
        "output_file": str(output_file) if output_file else None,
        "status": status,
        "message": message,
    }

    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    return log_path
