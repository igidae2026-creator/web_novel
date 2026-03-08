from __future__ import annotations

from typing import Any, Dict


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def build_retention_state(
    state: Dict[str, Any],
    event_plan: Dict[str, Any] | None = None,
    cliffhanger_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    conflict = state.get("conflict_engine", {})
    tension = state.get("tension_wave", {})
    event_plan = dict(event_plan or {})
    cliffhanger_plan = dict(cliffhanger_plan or {})

    unresolved_threads = [
        thread for thread in (conflict.get("threads", []) or []) if thread.get("status") != "resolved"
    ]
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
        + int(conflict.get("recent_losses", 0) or 0),
    )

    retention = {
        "unresolved_thread_pressure": unresolved_pressure,
        "threat_proximity": threat_proximity,
        "payoff_debt": payoff_debt,
        "curiosity_debt": curiosity_debt,
        "fallout_pressure": fallout_pressure,
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
    )
    penalty = float(fatigue or 0.0) * 0.22
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
