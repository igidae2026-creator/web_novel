from __future__ import annotations
import json
from typing import List, Dict, Any

from analytics.content_ceiling import aggregate_series
from engine.safe_io import safe_write_text

def write_report(results: List[Dict[str, Any]], out_path: str, safe_mode: bool = True) -> None:
    payload = {
        "series": aggregate_series(results),
        "episodes": results,
    }
    safe_write_text(out_path, json.dumps(payload, ensure_ascii=False, indent=2), safe_mode=safe_mode)
