from __future__ import annotations

from typing import Any, Dict


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def evaluate_protagonist_guard(
    story_state: Dict[str, Any],
    score_obj: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = dict(story_state or {})
    score_obj = dict(score_obj or {})
    cast = dict(story_state.get("cast", {}) or {})
    protagonist = dict(cast.get("protagonist", {}) or {})
    rivals = [dict(value or {}) for key, value in cast.items() if key != "protagonist"]
    promise_graph = dict(story_state.get("promise_graph", {}) or {})
    character_promises = dict(promise_graph.get("character_promises", {}) or {})
    protagonist_promises = list(character_promises.get("protagonist", []) or [])
    open_protagonist_promises = sum(1 for item in protagonist_promises if item.get("status") == "open")
    protagonist_pressure = (
        int(protagonist.get("urgency", 0) or 0)
        + int(protagonist.get("decision_pressure", 0) or 0)
        + int(protagonist.get("progress", 0) or 0)
        - int(protagonist.get("backlash", 0) or 0)
    )
    rival_pressure = max(
        [
            int(item.get("urgency", 0) or 0) + int(item.get("decision_pressure", 0) or 0) + int(item.get("progress", 0) or 0)
            for item in rivals
        ] or [0]
    )
    agency = _clamp(0.45 + protagonist_pressure / 30.0 + float(score_obj.get("character_score", 0.0) or 0.0) * 0.12 - max(0, rival_pressure - protagonist_pressure) * 0.03)
    reward_loop_integrity = _clamp(
        0.42
        + min(0.18, open_protagonist_promises * 0.05)
        + float(story_state.get("promise_graph", {}).get("payoff_integrity", 0.0) or 0.0) * 0.28
        + int(story_state.get("rewards", {}).get("reward_density", 0) or 0) / 10.0 * 0.12
    )
    takeover_risk = _clamp(0.35 + max(0, rival_pressure - protagonist_pressure) * 0.05 + (0.12 if agency < 0.58 else 0.0))
    sovereignty = _clamp(agency * 0.54 + reward_loop_integrity * 0.30 + (1.0 - takeover_risk) * 0.16)
    return {
        "protagonist_sovereignty": round(sovereignty, 4),
        "protagonist_agency_score": round(agency, 4),
        "secondary_takeover_risk": round(takeover_risk, 4),
        "reward_loop_integrity": round(reward_loop_integrity, 4),
    }
