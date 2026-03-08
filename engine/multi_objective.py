from __future__ import annotations

from typing import Any, Dict

from .regression_guard import evaluate_total_profile


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def build_multi_objective_scores(
    scores: Dict[str, Any],
    retention_state: Dict[str, Any] | None = None,
    story_state: Dict[str, Any] | None = None,
    causal_report: Dict[str, Any] | None = None,
) -> Dict[str, float]:
    retention_state = dict(retention_state or {})
    story_state = dict(story_state or {})
    causal_report = dict(causal_report or {})
    world = story_state.get("world", {})
    serialization = story_state.get("serialization", {})
    rewards = story_state.get("rewards", {})
    information = story_state.get("information", {})
    antagonist = story_state.get("antagonist", {})
    pattern_memory = story_state.get("pattern_memory", {})
    market = story_state.get("market", {})
    control = story_state.get("control", {})
    portfolio_memory = story_state.get("portfolio_memory", {})
    causal_score = float(causal_report.get("score", 0.6) or 0.6)
    foresight = float(antagonist.get("foresight", 5) or 5) / 10.0
    pressure_clock = float(antagonist.get("pressure_clock", 5) or 5) / 10.0
    exploration_bias = float(pattern_memory.get("exploration_bias", 5) or 5) / 10.0
    market_resonance = float(pattern_memory.get("market_resonance", 5) or 5) / 10.0
    reader_trust = float(market.get("reader_trust", 5) or 5) / 10.0
    bingeability = float(market.get("bingeability", 5) or 5) / 10.0
    release_confidence = float(market.get("release_confidence", 5) or 5) / 10.0
    repair = control.get("causal_repair", {}) or {}
    repair_confidence = float(repair.get("repair_confidence", 5) or 5) / 10.0
    repair_penalty = min(0.12, len(repair.get("critical_issues", []) or []) * 0.04)
    closure_score = float(repair.get("closure_score", 0.0) or 0.0)
    overused_penalty = min(0.15, len(pattern_memory.get("overused_events", []) or []) * 0.04)
    portfolio_fit = float(portfolio_memory.get("portfolio_fit", 5) or 5) / 10.0
    diversity_pressure = float(portfolio_memory.get("diversity_pressure", 5) or 5) / 10.0
    shared_risk_alert = float(portfolio_memory.get("shared_risk_alert", 3) or 3) / 10.0

    base_coherence = scores.get("coherence", scores.get("logic_score", 0.55)) * 0.7 + causal_score * 0.3
    base_pacing = scores.get("pacing_score", 0.5) * 0.7 + scores.get("hook_score", 0.5) * 0.3
    base_retention = scores.get("hook_score", 0.5) * 0.3 + float(retention_state.get("curiosity_debt", 5)) / 10.0 * 0.35 + float(retention_state.get("unresolved_thread_pressure", 5)) / 10.0 * 0.35
    base_world_logic = scores.get("world_logic", 0.5) * 0.5 + (10 - float(world.get("instability", 5))) / 10.0 * 0.25 + causal_report.get("checks", {}).get("world_consequence", 0.0) * 0.25
    base_stability = (1.0 - scores.get("repetition_score", 0.2)) * 0.35 + float(information.get("dramatic_irony", 5)) / 10.0 * 0.1 + float(serialization.get("novelty_budget", 5)) / 10.0 * 0.1 + scores.get("coherence", scores.get("logic_score", 0.55)) * 0.2 + causal_score * 0.25

    objective = {
        "fun": _clamp(scores.get("hook_score", 0.5) * 0.55 + scores.get("escalation", 0.5) * 0.45),
        "coherence": _clamp(base_coherence + foresight * 0.05 + market_resonance * 0.02 + repair_confidence * 0.03 + closure_score * 0.05 + portfolio_fit * 0.03 - repair_penalty),
        "character_persuasiveness": _clamp(scores.get("character_score", 0.5) * 0.60 + scores.get("emotion_density", 0.5) * 0.18 + causal_report.get("checks", {}).get("goal_pressure", 0.0) * 0.12 + repair_confidence * 0.04 + closure_score * 0.06),
        "pacing": _clamp(base_pacing + pressure_clock * 0.05 + exploration_bias * 0.03 + bingeability * 0.03 + repair_confidence * 0.02 + closure_score * 0.04 + diversity_pressure * 0.05),
        "retention": _clamp(base_retention + pressure_clock * 0.05 + market_resonance * 0.05 + exploration_bias * 0.02 + bingeability * 0.03 + reader_trust * 0.03 + portfolio_fit * 0.06),
        "emotional_immersion": _clamp(scores.get("emotion_density", 0.5) * 0.7 + causal_report.get("checks", {}).get("emotional_trace", 0.0) * 0.3),
        "information_design": _clamp(float(information.get("dramatic_irony", 5)) / 10.0 * 0.20 + float(retention_state.get("information_gap", 5)) / 10.0 * 0.14 + causal_report.get("checks", {}).get("cliffhanger_alignment", 0.0) * 0.15 + exploration_bias * 0.08 + market_resonance * 0.16 + repair_confidence * 0.10 + closure_score * 0.10 + portfolio_fit * 0.08 - repair_penalty * 0.5),
        "emotional_payoff": _clamp(scores.get("emotion_density", 0.5) * 0.75 + scores.get("payoff_score", 0.5) * 0.25),
        "long_run_sustainability": _clamp(float(serialization.get("sustainability", 5)) / 10.0 * 0.52 + float(rewards.get("expectation_alignment", 5)) / 10.0 * 0.18 + reader_trust * 0.10 + release_confidence * 0.06 + portfolio_fit * 0.12 + (1.0 - shared_risk_alert) * 0.04),
        "world_logic": _clamp(base_world_logic + foresight * 0.05),
        "chemistry": _clamp(float(serialization.get("chemistry_signal", 5)) / 10.0 * 0.6 + scores.get("chemistry_score", 0.5) * 0.4),
        "stability": _clamp(base_stability + foresight * 0.05 + market_resonance * 0.05 + exploration_bias * 0.04 + release_confidence * 0.04 + repair_confidence * 0.03 + closure_score * 0.05 + portfolio_fit * 0.05 - overused_penalty - repair_penalty - shared_risk_alert * 0.05),
    }
    return objective


def multi_objective_balance(
    scores: Dict[str, Any],
    retention_state: Dict[str, Any] | None = None,
    story_state: Dict[str, Any] | None = None,
    causal_report: Dict[str, Any] | None = None,
) -> float:
    objective = build_multi_objective_scores(scores, retention_state=retention_state, story_state=story_state, causal_report=causal_report)
    profile = evaluate_total_profile(objective)
    return _clamp(profile["balanced_total"])
