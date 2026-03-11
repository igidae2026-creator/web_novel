from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class CliffStats:
    counts: Dict[str, int]
    dominant: str

def classify(text: str, meta: Dict[str, Any] | None = None) -> CliffStats:
    meta = dict(meta or {})
    plan = meta.get("cliffhanger_plan") or {}
    event_plan = meta.get("event_plan") or {}
    tail = meta.get("cliffhanger") or (text[-240:] if len(text) > 240 else text)
    mode = str(plan.get("mode") or "")
    event_type = str(event_plan.get("type") or "")
    counts = {
        "open_question": int("?" in tail or "무엇" in tail or "누가" in tail),
        "withheld_consequence": int(any(token in tail for token in ["대가", "진실", "끝나지", "붕괴", "배신"])),
        "carryover_pressure": int(int(plan.get("carryover_pressure", 0) or 0) >= 5),
        "event_link": int(bool(event_type)),
        "mode_link": int(bool(mode)),
    }
    dominant = mode or event_type or max(counts.items(), key=lambda kv: kv[1])[0]
    return CliffStats(counts=counts, dominant=dominant)
