from __future__ import annotations

from typing import Any, Dict, List

from .story_state import ensure_story_state, sync_story_state


def _clamp(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def _track_signature(cfg: Dict[str, Any] | None) -> str:
    cfg = dict(cfg or {})
    project = cfg.get("project", {})
    return f"{project.get('platform', 'unknown')}::{project.get('genre_bucket', 'X')}"


def update_portfolio_memory(
    state: Dict[str, Any],
    cfg: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
    portfolio_snapshot: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state, cfg=cfg)
    memory = story_state["portfolio_memory"]
    pattern_memory = story_state["pattern_memory"]
    market = story_state["market"]
    serialization = story_state["serialization"]
    event_plan = dict(event_plan or {})
    portfolio_snapshot = list(portfolio_snapshot or [])

    event_type = str(event_plan.get("type", "")).strip()
    signature = _track_signature(cfg or state.get("_cfg_for_models", {}))
    crowded = set(pattern_memory.get("overused_events", []) or [])
    winners = set(pattern_memory.get("recent_event_types", [])[-2:])

    for item in portfolio_snapshot:
        if int(item.get("heat", 0) or 0) >= 7 and item.get("winning_pattern"):
            winners.add(str(item.get("winning_pattern")))
        if int(item.get("crowding", 0) or 0) >= 7 and item.get("pattern"):
            crowded.add(str(item.get("pattern")))

    if event_type and event_type not in crowded:
        winners.add(event_type)

    memory["track_signature"] = signature
    memory["winning_patterns"] = sorted(winners)[:6]
    memory["crowded_patterns"] = sorted(crowded)[:6]
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
        "diversity_pressure": memory.get("diversity_pressure", 0),
        "portfolio_fit": memory.get("portfolio_fit", 0),
        "shared_risk_alert": memory.get("shared_risk_alert", 0),
    }
