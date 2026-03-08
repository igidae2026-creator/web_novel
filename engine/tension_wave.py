from __future__ import annotations

from typing import Any, Dict


def _clamp_float(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _clamp_int(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def prepare_tension_wave(state: Dict[str, Any], episode: int) -> Dict[str, Any]:
    tension = state.get("tension_wave")
    if not isinstance(tension, dict):
        tension = {
            "target_tension": 7,
            "current_tension": 6,
            "peak_count": 0,
            "release_debt": 0,
            "spike_debt": 1,
            "band": "pressure",
        }

    recent_events = list(state.get("story_events", []) or [])[-3:]
    recent_scores = state.get("score_history", [])[-3:]
    avg_escalation = (
        sum(float(score.get("escalation", 0.0) or 0.0) for score in recent_scores) / len(recent_scores)
        if recent_scores
        else 0.7
    )
    conflict = state.get("conflict_engine", {})
    pressure = int(conflict.get("threat_pressure", 5) or 5)
    consequence = int(conflict.get("consequence_level", 5) or 5)

    cycle = episode % 4
    base_target = 8 if cycle in (0, 3) else 6
    if "loss" in recent_events or "betrayal" in recent_events:
        base_target += 1
    if avg_escalation < 0.7:
        base_target += 1
    if tension.get("release_debt", 0) >= 2:
        base_target -= 1

    target_tension = _clamp_int(base_target + max(0, pressure - 6) + max(0, consequence - 6))
    band = "spike" if target_tension >= 8 else "release" if target_tension <= 5 else "pressure"

    tension["target_tension"] = target_tension
    tension["band"] = band
    state["tension_wave"] = tension
    return tension


def apply_tension_wave(knobs: Dict[str, Any], tension: Dict[str, Any]) -> Dict[str, Any]:
    adjusted = dict(knobs)
    target = int(tension.get("target_tension", 7) or 7)
    band = str(tension.get("band", "pressure"))

    if band == "spike":
        adjusted["hook_intensity"] = _clamp_float(float(adjusted.get("hook_intensity", 0.7)) + 0.08)
        adjusted["compression"] = _clamp_float(float(adjusted.get("compression", 0.6)) + 0.06)
        adjusted["novelty_boost"] = _clamp_float(float(adjusted.get("novelty_boost", 0.5)) + 0.08)
    elif band == "release":
        adjusted["payoff_intensity"] = _clamp_float(float(adjusted.get("payoff_intensity", 0.7)) + 0.08)
        adjusted["compression"] = _clamp_float(float(adjusted.get("compression", 0.6)) - 0.05)
    else:
        adjusted["hook_intensity"] = _clamp_float(float(adjusted.get("hook_intensity", 0.7)) + 0.03)
        adjusted["payoff_intensity"] = _clamp_float(float(adjusted.get("payoff_intensity", 0.7)) + 0.03)

    adjusted["tension_target"] = target
    adjusted["tension_band"] = band
    return adjusted


def update_tension_wave(
    state: Dict[str, Any],
    episode: int,
    score_obj: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    tension = prepare_tension_wave(state, episode)
    score_obj = dict(score_obj or {})
    event_plan = dict(event_plan or {})

    achieved = (
        float(score_obj.get("hook_score", 0.0) or 0.0) * 0.4
        + float(score_obj.get("escalation", 0.0) or 0.0) * 0.4
        + float(score_obj.get("emotion_density", 0.0) or 0.0) * 0.2
    )
    current = _clamp_int(round(achieved * 10))
    tension["current_tension"] = current

    if current >= 8:
        tension["peak_count"] = _clamp_int(tension.get("peak_count", 0) + 1)
        tension["release_debt"] = _clamp_int(tension.get("release_debt", 0) + 1)
        tension["spike_debt"] = 0
    elif current <= 5:
        tension["spike_debt"] = _clamp_int(tension.get("spike_debt", 0) + 1)
        tension["release_debt"] = max(0, int(tension.get("release_debt", 0)) - 1)

    if str(event_plan.get("type", "")) in {"loss", "betrayal", "arrival"}:
        tension["peak_count"] = _clamp_int(tension.get("peak_count", 0) + 1)

    state["tension_wave"] = tension
    return tension


def tension_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    tension = state.get("tension_wave", {})
    return {
        "target_tension": tension.get("target_tension", 7),
        "current_tension": tension.get("current_tension", 6),
        "peak_count": tension.get("peak_count", 0),
        "release_debt": tension.get("release_debt", 0),
        "spike_debt": tension.get("spike_debt", 0),
        "band": tension.get("band", "pressure"),
    }
