from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from .story_state import ensure_story_state, sync_story_state
from .track_loader import list_track_dirs


def _clamp(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def _track_signature(cfg: Dict[str, Any] | None) -> str:
    cfg = dict(cfg or {})
    project = cfg.get("project", {})
    return f"{project.get('platform', 'unknown')}::{project.get('genre_bucket', 'X')}"


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


def learn_portfolio_snapshot(tracks_root: str, last_n: int = 8) -> List[Dict[str, Any]]:
    snapshot: List[Dict[str, Any]] = []
    for tdir in list_track_dirs(tracks_root):
        metrics_path = os.path.join(tdir, "outputs", "metrics.jsonl")
        rows = _load_jsonl(metrics_path)[-last_n:]
        if not rows:
            continue
        event_types = [str((row.get("meta", {}) or {}).get("event_plan", {}).get("type", "")).strip() for row in rows]
        event_types = [evt for evt in event_types if evt]
        if not event_types:
            continue
        dominant = max(set(event_types), key=event_types.count)
        mean_ceiling = sum(int((row.get("content_ceiling", {}) or {}).get("ceiling_total", 0) or 0) for row in rows) / len(rows)
        mean_retention = sum(float((row.get("retention", {}) or {}).get("predicted_next_episode", 0.0) or 0.0) for row in rows) / len(rows)
        repetition_scores = [float((row.get("scores", {}) or {}).get("repetition_score", 0.0) or 0.0) for row in rows]
        mean_repetition = sum(repetition_scores) / len(repetition_scores) if repetition_scores else 0.0
        snapshot.append(
            {
                "track": os.path.basename(tdir),
                "pattern": dominant,
                "winning_pattern": dominant if mean_ceiling >= 60 and mean_retention >= 0.6 else "",
                "crowding": min(10, event_types.count(dominant) * 3 + int(mean_repetition >= 0.22) * 2),
                "fatigue": min(10, int(mean_repetition * 10) + int(mean_retention < 0.55) * 3),
                "heat": min(10, int(mean_ceiling / 10) + int(mean_retention * 5)),
            }
        )
    return snapshot


def update_portfolio_memory(
    state: Dict[str, Any],
    cfg: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
    portfolio_snapshot: List[Dict[str, Any]] | None = None,
    tracks_root: str | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state, cfg=cfg)
    memory = story_state["portfolio_memory"]
    pattern_memory = story_state["pattern_memory"]
    market = story_state["market"]
    serialization = story_state["serialization"]
    event_plan = dict(event_plan or {})
    if portfolio_snapshot is None:
        root = tracks_root or os.path.join("domains", "webnovel", "tracks")
        portfolio_snapshot = learn_portfolio_snapshot(root)
    portfolio_snapshot = list(portfolio_snapshot or [])

    event_type = str(event_plan.get("type", "")).strip()
    signature = _track_signature(cfg or state.get("_cfg_for_models", {}))
    crowded = set(pattern_memory.get("overused_events", []) or [])
    winners = set(pattern_memory.get("recent_event_types", [])[-2:])
    fatigue = set()

    for item in portfolio_snapshot:
        if int(item.get("heat", 0) or 0) >= 7 and item.get("winning_pattern"):
            winners.add(str(item.get("winning_pattern")))
        if int(item.get("crowding", 0) or 0) >= 7 and item.get("pattern"):
            crowded.add(str(item.get("pattern")))
        if int(item.get("fatigue", 0) or 0) >= 6 and item.get("pattern"):
            fatigue.add(str(item.get("pattern")))

    if event_type and event_type not in crowded:
        winners.add(event_type)

    memory["track_signature"] = signature
    memory["winning_patterns"] = sorted(winners)[:6]
    memory["crowded_patterns"] = sorted(crowded)[:6]
    memory["fatigue_patterns"] = sorted(fatigue)[:6]
    memory["diversity_pressure"] = _clamp(4 + len(crowded) + int(event_type in crowded))
    memory["portfolio_fit"] = _clamp(
        market.get("reader_trust", 5) // 2
        + serialization.get("market_fit", 5) // 2
        + int(event_type in winners)
        - int(event_type in crowded)
    )
    memory["shared_risk_alert"] = _clamp(
        len(crowded) + max(0, 6 - market.get("release_confidence", 5)) // 2
    )
    memory["learned_from_logs"] = bool(portfolio_snapshot)
    memory["observed_tracks"] = len(portfolio_snapshot)
    memory["learning_confidence"] = _clamp(
        len(portfolio_snapshot) * 2 + sum(int(item.get("heat", 0) or 0) >= 7 for item in portfolio_snapshot)
    )

    state["story_state_v2"] = story_state
    sync_story_state(state)
    return memory


def portfolio_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    memory = story_state["portfolio_memory"]
    return {
        "track_signature": memory.get("track_signature"),
        "winning_patterns": memory.get("winning_patterns", [])[:4],
        "crowded_patterns": memory.get("crowded_patterns", [])[:4],
        "fatigue_patterns": memory.get("fatigue_patterns", [])[:4],
        "diversity_pressure": memory.get("diversity_pressure", 0),
        "portfolio_fit": memory.get("portfolio_fit", 0),
        "shared_risk_alert": memory.get("shared_risk_alert", 0),
        "learned_from_logs": memory.get("learned_from_logs", False),
        "learning_confidence": memory.get("learning_confidence", 0),
        "observed_tracks": memory.get("observed_tracks", 0),
    }
