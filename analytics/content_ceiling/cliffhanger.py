from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

CLIFF = {
  "question": ["?", "？"],
  "ellipsis": ["…"],
  "pre_peak_cut": ["그 순간", "바로 그때", "하지만"],
  "reveal_delay": ["아직", "말하지 않았다", "답은", "진실은"],
  "threat": ["위협", "추격", "협박", "총", "칼", "죽"],
}

def _count_any(text: str, ms: List[str]) -> int:
    return sum(text.count(m) for m in ms)

@dataclass
class CliffStats:
    counts: Dict[str, int]
    dominant: str

def classify(text: str) -> CliffStats:
    tail = text[-900:] if len(text) > 900 else text
    counts = {k: _count_any(tail, ms) for k, ms in CLIFF.items()}
    dominant = max(counts.items(), key=lambda kv: kv[1])[0] if counts else "none"
    return CliffStats(counts=counts, dominant=dominant)
