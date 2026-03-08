from __future__ import annotations

from typing import Any, Dict

from .regression_guard import evaluate_total_profile


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def build_multi_objective_scores(
    scores: Dict[str, Any],
    retention_state: Dict[str, Any] | None = None,
    story_state: Dict[str, Any] | None = None,
) -> Dict[str, float]:
    retention_state = dict(retention_state or {})
    story_state = dict(story_state or {})
    world = story_state.get("world", {})
    serialization = story_state.get("serialization", {})
    rewards = story_state.get("rewards", {})
    information = story_state.get("information", {})

    objective = {
        "fun": _clamp(scores.get("hook_score", 0.5) * 0.55 + scores.get("escalation", 0.5) * 0.45),
        "coherence": _clamp(scores.get("coherence", scores.get("logic_score", 0.55))),
        "character_persuasiveness": _clamp(scores.get("character_score", 0.5) * 0.7 + scores.get("emotion_density", 0.5) * 0.3),
        "pacing": _clamp(scores.get("pacing_score", 0.5) * 0.7 + scores.get("hook_score", 0.5) * 0.3),
        "retention": _clamp(scores.get("hook_score", 0.5) * 0.3 + float(retention_state.get("curiosity_debt", 5)) / 10.0 * 0.35 + float(retention_state.get("unresolved_thread_pressure", 5)) / 10.0 * 0.35),
        "emotional_payoff": _clamp(scores.get("emotion_density", 0.5) * 0.75 + scores.get("payoff_score", 0.5) * 0.25),
        "long_run_sustainability": _clamp(float(serialization.get("sustainability", 5)) / 10.0 * 0.7 + float(rewards.get("expectation_alignment", 5)) / 10.0 * 0.3),
        "world_logic": _clamp(scores.get("world_logic", 0.5) * 0.6 + (10 - float(world.get("instability", 5))) / 10.0 * 0.4),
        "chemistry": _clamp(float(serialization.get("chemistry_signal", 5)) / 10.0 * 0.6 + scores.get("chemistry_score", 0.5) * 0.4),
        "stability": _clamp((1.0 - scores.get("repetition_score", 0.2)) * 0.4 + float(information.get("dramatic_irony", 5)) / 10.0 * 0.15 + float(serialization.get("novelty_budget", 5)) / 10.0 * 0.15 + scores.get("coherence", scores.get("logic_score", 0.55)) * 0.3),
    }
    return objective


def multi_objective_balance(
    scores: Dict[str, Any],
    retention_state: Dict[str, Any] | None = None,
    story_state: Dict[str, Any] | None = None,
) -> float:
    objective = build_multi_objective_scores(scores, retention_state=retention_state, story_state=story_state)
    profile = evaluate_total_profile(objective)
    return _clamp(profile["balanced_total"])
