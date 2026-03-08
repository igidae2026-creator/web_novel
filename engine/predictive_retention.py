from __future__ import annotations

from typing import Any, Dict

from .story_state import chemistry_pressure, ensure_story_state, open_threads


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def build_retention_state(
    state: Dict[str, Any],
    event_plan: Dict[str, Any] | None = None,
    cliffhanger_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    conflict = story_state.get("conflict", {})
    tension = story_state.get("pacing", {})
    information = story_state.get("information", {})
    serialization = story_state.get("serialization", {})
    event_plan = dict(event_plan or {})
    cliffhanger_plan = dict(cliffhanger_plan or {})

    unresolved_threads = open_threads(story_state)
    unresolved_pressure = min(10, sum(int(thread.get("heat", 0) or 0) for thread in unresolved_threads[:3]))
    threat_proximity = min(10, int(conflict.get("threat_pressure", 0) or 0) + int(tension.get("target_tension", 0) or 0) // 2)
    payoff_debt = min(10, int(conflict.get("payoff_debt", 0) or 0) + len(unresolved_threads))
    curiosity_debt = min(
        10,
        int(cliffhanger_plan.get("carryover_pressure", 0) or 0)
        + int(bool(cliffhanger_plan.get("open_question")))
        + int(bool(event_plan.get("type"))),
    )
    fallout_pressure = min(
        10,
        int(event_plan.get("type") in {"loss", "betrayal", "arrival"}) * 3
        + int(story_state.get("world", {}).get("instability", 0) or 0),
    )
    chemistry = chemistry_pressure(story_state)
    info_gap = min(10, int(information.get("dramatic_irony", 0) or 0) + len(information.get("hidden_truths", []) or []))

    retention = {
        "unresolved_thread_pressure": unresolved_pressure,
        "threat_proximity": threat_proximity,
        "payoff_debt": payoff_debt,
        "curiosity_debt": curiosity_debt,
        "fallout_pressure": fallout_pressure,
        "chemistry_pressure": chemistry,
        "information_gap": info_gap,
        "sustainability": int(serialization.get("sustainability", 5) or 5),
    }
    state["retention_engine"] = retention
    return retention


def predict_retention(scores: dict, fatigue: float, retention_state: Dict[str, Any] | None = None) -> float:
    retention_state = dict(retention_state or {})
    base = (
        float(scores.get("emotion_density", 0.5) or 0.5) * 0.22
        + float(scores.get("hook_score", 0.5) or 0.5) * 0.18
        + float(scores.get("escalation", 0.5) or 0.5) * 0.15
    )
    pressure_bonus = (
        float(retention_state.get("unresolved_thread_pressure", 0) or 0) / 10.0 * 0.18
        + float(retention_state.get("threat_proximity", 0) or 0) / 10.0 * 0.10
        + float(retention_state.get("payoff_debt", 0) or 0) / 10.0 * 0.07
        + float(retention_state.get("curiosity_debt", 0) or 0) / 10.0 * 0.07
        + float(retention_state.get("fallout_pressure", 0) or 0) / 10.0 * 0.08
        + float(retention_state.get("chemistry_pressure", 0) or 0) / 10.0 * 0.06
        + float(retention_state.get("information_gap", 0) or 0) / 10.0 * 0.05
    )
    penalty = float(fatigue or 0.0) * 0.22 + max(0.0, (5 - float(retention_state.get("sustainability", 5) or 5)) / 10.0 * 0.08)
    return _clamp(base + pressure_bonus - penalty)


def retention_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    retention = state.get("retention_engine", {})
    return {
        "unresolved_thread_pressure": retention.get("unresolved_thread_pressure", 0),
        "threat_proximity": retention.get("threat_proximity", 0),
        "payoff_debt": retention.get("payoff_debt", 0),
        "curiosity_debt": retention.get("curiosity_debt", 0),
        "fallout_pressure": retention.get("fallout_pressure", 0),
    }
