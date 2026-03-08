from __future__ import annotations

import json
import os
from collections import Counter
from typing import Any, Dict, List

from .track_loader import list_track_dirs


def _clamp(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def _load_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path or not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def compute_portfolio_signals(tracks_root: str, last_n: int = 8) -> Dict[str, int]:
    tdirs = list_track_dirs(tracks_root)
    event_counter: Counter[str] = Counter()
    platform_counter: Counter[str] = Counter()
    fatigue_hits = 0
    cadence_hits = 0
    active_tracks = 0

    for tdir in tdirs:
        track = _load_json(os.path.join(tdir, "track.json"))
        platform = str((track.get("project", {}) or {}).get("platform", "UNKNOWN"))
        platform_counter[platform] += 1
        rows = _load_jsonl(os.path.join(tdir, "outputs", "metrics.jsonl"))[-last_n:]
        if not rows:
            continue
        active_tracks += 1
        events = [str((row.get("meta", {}) or {}).get("event_plan", {}).get("type", "")).strip() for row in rows]
        events = [evt for evt in events if evt]
        event_counter.update(events)
        mean_repetition = sum(float((row.get("scores", {}) or {}).get("repetition_score", 0.0) or 0.0) for row in rows) / len(rows)
        if mean_repetition >= 0.20:
            fatigue_hits += 1
        if len(rows) >= max(2, last_n // 2):
            cadence_hits += 1

    crowded = event_counter.most_common(1)[0][1] if event_counter else 0
    duplicated_platforms = sum(1 for _, count in platform_counter.items() if count >= 2)
    distinct_events = len(event_counter) or 1

    return {
        "pattern_crowding": _clamp(crowded * 2),
        "shared_risk": _clamp(fatigue_hits * 3 + duplicated_platforms),
        "novelty_debt": _clamp(max(0, crowded - distinct_events) * 2 + max(0, fatigue_hits - 1)),
        "cadence_pressure": _clamp(cadence_hits * 2),
        "market_overlap": _clamp(duplicated_platforms * 3),
        "release_timing_interference": _clamp(max(0, active_tracks - distinct_events) * 2 + cadence_hits),
    }
