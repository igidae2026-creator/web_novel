from __future__ import annotations

from typing import Any, Dict

from .story_state import ensure_story_state, sync_story_state


def _clamp_float(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _clamp_int(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def prepare_tension_wave(state: Dict[str, Any], episode: int) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    tension = story_state.get("pacing", {})

    recent_events = list(state.get("story_events", []) or [])[-3:]
    recent_scores = state.get("score_history", [])[-3:]
    avg_escalation = (
        sum(float(score.get("escalation", 0.0) or 0.0) for score in recent_scores) / len(recent_scores)
        if recent_scores
        else 0.7
    )
    conflict = story_state.get("conflict", {})
    serialization = story_state.get("serialization", {})
    pressure = int(conflict.get("threat_pressure", 5) or 5)
    consequence = int(conflict.get("consequence_level", 5) or 5)
    sustainability = int(serialization.get("sustainability", 6) or 6)

    cycle = episode % 4
    base_target = 8 if cycle in (0, 3) else 6
    if "loss" in recent_events or "betrayal" in recent_events:
        base_target += 1
    if avg_escalation < 0.7:
        base_target += 1
    if tension.get("release_debt", 0) >= 2:
        base_target -= 1
    if sustainability <= 4:
        base_target -= 1

    target_tension = _clamp_int(base_target + max(0, pressure - 6) + max(0, consequence - 6))
    band = "spike" if target_tension >= 8 else "release" if target_tension <= 5 else "pressure"

    tension["target_tension"] = target_tension
    tension["target_band"] = band
    state["story_state_v2"] = story_state
    sync_story_state(state)
    return state["tension_wave"]


def apply_tension_wave(knobs: Dict[str, Any], tension: Dict[str, Any]) -> Dict[str, Any]:
    adjusted = dict(knobs)
    target = int(tension.get("target_tension", 7) or 7)
    band = str(tension.get("band", tension.get("target_band", "pressure")))

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
    story_state = ensure_story_state(state)
    tension = story_state.get("pacing", {})
    prepare_tension_wave(state, episode)
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

    band = tension.get("target_band", "pressure")
    rhythm_window = list(tension.get("rhythm_window", []) or [])
    rhythm_window.append(band)
    tension["rhythm_window"] = rhythm_window[-6:]
    state["story_state_v2"] = story_state
    sync_story_state(state)
    return state["tension_wave"]


def tension_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    ensure_story_state(state)
    tension = state.get("tension_wave", {})
    return {
        "target_tension": tension.get("target_tension", 7),
        "current_tension": tension.get("current_tension", 6),
        "peak_count": tension.get("peak_count", 0),
        "release_debt": tension.get("release_debt", 0),
        "spike_debt": tension.get("spike_debt", 0),
        "band": tension.get("band", "pressure"),
    }
