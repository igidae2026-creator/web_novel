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
    title_state = story_state.get("title", {})
    milestones = story_state.get("milestones", {})
    monetization = story_state.get("monetization", {})
    protagonist_guard = story_state.get("protagonist_guard", {})
    narrative_debt = story_state.get("narrative_debt", {})
    emotion_wave = story_state.get("emotion_wave", {})
    ip_readiness = story_state.get("ip_readiness", {})
    portfolio_memory = story_state.get("portfolio_memory", {})
    portfolio_metrics = story_state.get("portfolio_metrics", {})
    promise_graph = story_state.get("promise_graph", {})
    causal_score = float(causal_report.get("score", 0.6) or 0.6)
    foresight = float(antagonist.get("foresight", 5) or 5) / 10.0
    pressure_clock = float(antagonist.get("pressure_clock", 5) or 5) / 10.0
    exploration_bias = float(pattern_memory.get("exploration_bias", 5) or 5) / 10.0
    market_resonance = float(pattern_memory.get("market_resonance", 5) or 5) / 10.0
    reader_trust = float(market.get("reader_trust", 5) or 5) / 10.0
    bingeability = float(market.get("bingeability", 5) or 5) / 10.0
    release_confidence = float(market.get("release_confidence", 5) or 5) / 10.0
    title_fitness = float((title_state.get("best_title", {}) or {}).get("title_fitness", 0.5) or 0.5)
    milestone_readiness = float(milestones.get("milestone_readiness", 0.5) or 0.5)
    conversion_readiness = float(monetization.get("conversion_readiness", 0.5) or 0.5)
    protagonist_sovereignty = float(protagonist_guard.get("protagonist_sovereignty", 0.5) or 0.5)
    protagonist_agency = float(protagonist_guard.get("protagonist_agency_score", 0.5) or 0.5)
    secondary_takeover_risk = float(protagonist_guard.get("secondary_takeover_risk", 0.3) or 0.3)
    reward_loop_integrity = float(protagonist_guard.get("reward_loop_integrity", 0.5) or 0.5)
    narrative_debt_score = float(narrative_debt.get("narrative_debt_score", 0.5) or 0.5)
    payoff_recovery_rate = float(narrative_debt.get("payoff_recovery_rate", 0.5) or 0.5)
    expansion_friction_risk = float(narrative_debt.get("expansion_friction_risk", 0.5) or 0.5)
    emotion_wave_balance = float(emotion_wave.get("emotion_wave_balance", 0.5) or 0.5)
    emotion_fatigue_projection = float(emotion_wave.get("fatigue_projection", 0.5) or 0.5)
    ip_axis = float(ip_readiness.get("ip_readiness", 0.5) or 0.5)
    canon_consistency = float(ip_readiness.get("canon_consistency", 0.5) or 0.5)
    franchise_expandability = float(ip_readiness.get("franchise_expandability", 0.5) or 0.5)
    repair = control.get("causal_repair", {}) or {}
    runtime_release = control.get("runtime_release", {}) or {}
    repair_confidence = float(repair.get("repair_confidence", 5) or 5) / 10.0
    repair_penalty = min(0.12, len(repair.get("critical_issues", []) or []) * 0.04)
    closure_score = float(repair.get("closure_score", 0.0) or 0.0)
    strategy_coverage = float(repair.get("strategy_coverage", 0.0) or 0.0)
    defect_resolution_score = float(repair.get("defect_resolution_score", 0.0) or 0.0)
    semantic_audit = dict(repair.get("semantic_audit", {}) or {})
    intent_preservation_score = float(semantic_audit.get("intent_preservation_score", 0.0) or 0.0)
    semantic_repair_effectiveness = float(semantic_audit.get("semantic_repair_effectiveness", 0.0) or 0.0)
    semantic_failure_penalty = min(0.12, len(list(semantic_audit.get("semantic_failure_types", []) or [])) * 0.025)
    overused_penalty = min(0.15, len(pattern_memory.get("overused_events", []) or []) * 0.04)
    portfolio_fit = float(portfolio_memory.get("portfolio_fit", 5) or 5) / 10.0
    diversity_pressure = float(portfolio_memory.get("diversity_pressure", 5) or 5) / 10.0
    shared_risk_alert = float(portfolio_memory.get("shared_risk_alert", 3) or 3) / 10.0
    learning_confidence = float(portfolio_memory.get("learning_confidence", 0) or 0) / 10.0
    coordination_health = float(portfolio_memory.get("coordination_health", 5) or 5) / 10.0
    novelty_guard = float(portfolio_memory.get("novelty_guard", 5) or 5) / 10.0
    cadence_guard = float(portfolio_memory.get("cadence_guard", 5) or 5) / 10.0
    release_guard = float(portfolio_memory.get("release_guard", 5) or 5) / 10.0
    release_strategy = str(portfolio_memory.get("release_strategy", "balanced") or "balanced")
    release_plan = list(portfolio_memory.get("release_plan", []) or [])
    window_reservations = list(portfolio_memory.get("window_reservations", []) or [])
    long_horizon_pressure = float(portfolio_memory.get("long_horizon_pressure", 0) or 0) / 10.0
    platform_slot_pressure = float(portfolio_memory.get("platform_slot_pressure", 0) or 0) / 10.0
    slot_policy_clarity = _clamp(len(list(portfolio_memory.get("slot_policy_directives", []) or [])) / 4.0)
    runtime_release_alignment = float(runtime_release.get("alignment", 0.0) or 0.0)
    runtime_learning = dict(portfolio_memory.get("runtime_release_learning", {}) or {})
    runtime_outcomes = dict(portfolio_memory.get("runtime_outcome_memory", {}) or {})
    episode_attribution_memory = dict(portfolio_memory.get("episode_attribution_memory", {}) or {})
    runtime_retention_signal = float(runtime_outcomes.get("retention_signal", 0.0) or 0.0)
    runtime_pacing_signal = float(runtime_outcomes.get("pacing_signal", 0.0) or 0.0)
    runtime_trust_signal = float(runtime_outcomes.get("trust_signal", 0.0) or 0.0)
    runtime_fatigue_signal = float(runtime_outcomes.get("fatigue_signal", 0.0) or 0.0)
    runtime_coordination_signal = float(runtime_outcomes.get("coordination_signal", 0.0) or 0.0)
    runtime_policy_confidence = _clamp(float(runtime_learning.get("observed", 0) or 0) / 8.0)
    episode_attr_retention = float(episode_attribution_memory.get("retention_signal", 0.0) or 0.0)
    episode_attr_pacing = float(episode_attribution_memory.get("pacing_signal", 0.0) or 0.0)
    episode_attr_fatigue = float(episode_attribution_memory.get("fatigue_signal", 0.0) or 0.0)
    episode_attr_payoff = float(episode_attribution_memory.get("payoff_signal", 0.0) or 0.0)
    latest_episode_attr = dict((control.get("episode_attribution", {}) or {}).get("latest", {}) or {})
    latest_fine_grained = dict(latest_episode_attr.get("fine_grained", {}) or {})
    latest_scene_signal = float(latest_fine_grained.get("scene_signal", 0.0) or 0.0)
    promise_resolution_rate = float(promise_graph.get("resolution_rate", 0.0) or 0.0)
    payoff_integrity = float(promise_graph.get("payoff_integrity", 0.0) or 0.0)
    unresolved_promises = min(1.0, float(promise_graph.get("unresolved_count", 0) or 0) / 6.0)
    payoff_corruption_penalty = min(0.12, len(list(promise_graph.get("payoff_corruption_flags", []) or [])) * 0.03)
    character_promises = dict(promise_graph.get("character_promises", {}) or {})
    dependency_edges = list(promise_graph.get("dependency_edges", []) or [])
    weighted_dependency_graph = dict(promise_graph.get("weighted_dependency_graph", {}) or {})
    if not character_promises and not dependency_edges:
        character_dependency_health = 0.0
    else:
        character_dependency_health = _clamp(
            0.35
            + min(0.24, len(character_promises) * 0.06)
            + min(0.16, len(dependency_edges) * 0.04)
            + min(0.14, sum(max(0.0, float(item.get("weight", 0.0) or 0.0)) for item in weighted_dependency_graph.values()) * 0.06)
            - unresolved_promises * 0.08
            - payoff_corruption_penalty * 0.5
        )
    pattern_crowding = float(portfolio_metrics.get("pattern_crowding", 0) or 0) / 10.0
    cross_track_risk = float(portfolio_metrics.get("shared_risk", 0) or 0) / 10.0
    novelty_debt = float(portfolio_metrics.get("novelty_debt", 0) or 0) / 10.0
    cadence_pressure = float(portfolio_metrics.get("cadence_pressure", 0) or 0) / 10.0
    market_overlap = float(portfolio_metrics.get("market_overlap", 0) or 0) / 10.0
    release_interference = float(portfolio_metrics.get("release_timing_interference", 0) or 0) / 10.0
    portfolio_coordination = _clamp(
        coordination_health * 0.45
        + novelty_guard * 0.20
        + cadence_guard * 0.15
        + release_guard * 0.10
        + (1.0 - cross_track_risk) * 0.10
    )
    release_schedule_health = _clamp(
        release_guard * 0.55
        + (0.20 if release_strategy == "staggered" else 0.15 if release_strategy == "focused" else 0.10)
        + min(0.20, len(release_plan) * 0.03)
        + min(0.10, len(window_reservations) * 0.015)
        + (1.0 - platform_slot_pressure) * 0.15
        + slot_policy_clarity * 0.10
        - long_horizon_pressure * 0.08
    )

    base_coherence = scores.get("coherence", scores.get("logic_score", 0.55)) * 0.7 + causal_score * 0.3
    base_pacing = scores.get("pacing_score", 0.5) * 0.7 + scores.get("hook_score", 0.5) * 0.3
    base_retention = scores.get("hook_score", 0.5) * 0.3 + float(retention_state.get("curiosity_debt", 5)) / 10.0 * 0.35 + float(retention_state.get("unresolved_thread_pressure", 5)) / 10.0 * 0.35
    base_world_logic = scores.get("world_logic", 0.5) * 0.5 + (10 - float(world.get("instability", 5))) / 10.0 * 0.25 + causal_report.get("checks", {}).get("world_consequence", 0.0) * 0.25
    base_stability = (1.0 - scores.get("repetition_score", 0.2)) * 0.35 + float(information.get("dramatic_irony", 5)) / 10.0 * 0.1 + float(serialization.get("novelty_budget", 5)) / 10.0 * 0.1 + scores.get("coherence", scores.get("logic_score", 0.55)) * 0.2 + causal_score * 0.25

    objective = {
        "fun": _clamp(scores.get("hook_score", 0.5) * 0.55 + scores.get("escalation", 0.5) * 0.45),
        "coherence": _clamp(base_coherence + foresight * 0.05 + market_resonance * 0.02 + repair_confidence * 0.03 + closure_score * 0.05 + defect_resolution_score * 0.05 + strategy_coverage * 0.05 + intent_preservation_score * 0.04 + semantic_repair_effectiveness * 0.04 + latest_scene_signal * 0.03 + portfolio_fit * 0.03 + learning_confidence * 0.03 + slot_policy_clarity * 0.02 + portfolio_coordination * 0.03 - repair_penalty - semantic_failure_penalty),
        "character_persuasiveness": _clamp(scores.get("character_score", 0.5) * 0.60 + scores.get("emotion_density", 0.5) * 0.18 + causal_report.get("checks", {}).get("goal_pressure", 0.0) * 0.12 + repair_confidence * 0.04 + closure_score * 0.06 + defect_resolution_score * 0.03 + strategy_coverage * 0.04 + intent_preservation_score * 0.05 + semantic_repair_effectiveness * 0.02 + character_dependency_health * 0.05 - semantic_failure_penalty * 0.5),
        "pacing": _clamp(base_pacing + pressure_clock * 0.05 + exploration_bias * 0.03 + bingeability * 0.03 + repair_confidence * 0.02 + closure_score * 0.04 + diversity_pressure * 0.04 + cadence_guard * 0.03 + release_schedule_health * 0.05 + slot_policy_clarity * 0.03 + runtime_release_alignment * 0.04 + runtime_pacing_signal * 0.04 + episode_attr_pacing * 0.04 + latest_scene_signal * 0.03 + runtime_policy_confidence * 0.02 + portfolio_coordination * 0.03 - runtime_fatigue_signal * 0.03 - episode_attr_fatigue * 0.03 - max(0.0, cadence_pressure - 0.6) * 0.01),
        "retention": _clamp(base_retention + pressure_clock * 0.05 + market_resonance * 0.05 + exploration_bias * 0.02 + bingeability * 0.03 + reader_trust * 0.03 + portfolio_fit * 0.05 + learning_confidence * 0.03 + release_guard * 0.03 + release_schedule_health * 0.075 + slot_policy_clarity * 0.06 + runtime_release_alignment * 0.05 + runtime_retention_signal * 0.05 + episode_attr_retention * 0.04 + runtime_trust_signal * 0.03 + runtime_policy_confidence * 0.02 + promise_resolution_rate * 0.03 + payoff_integrity * 0.03 + portfolio_coordination * 0.04 - unresolved_promises * 0.03 - runtime_fatigue_signal * 0.04 - episode_attr_fatigue * 0.03 - max(0.0, release_interference - 0.6) * 0.01),
        "emotional_immersion": _clamp(scores.get("emotion_density", 0.5) * 0.7 + causal_report.get("checks", {}).get("emotional_trace", 0.0) * 0.3 + defect_resolution_score * 0.03 + strategy_coverage * 0.06 + intent_preservation_score * 0.03),
        "information_design": _clamp(float(information.get("dramatic_irony", 5)) / 10.0 * 0.18 + float(retention_state.get("information_gap", 5)) / 10.0 * 0.13 + causal_report.get("checks", {}).get("cliffhanger_alignment", 0.0) * 0.14 + exploration_bias * 0.08 + market_resonance * 0.15 + repair_confidence * 0.09 + closure_score * 0.09 + defect_resolution_score * 0.05 + strategy_coverage * 0.11 + intent_preservation_score * 0.05 + semantic_repair_effectiveness * 0.04 + portfolio_fit * 0.05 + learning_confidence * 0.08 + novelty_guard * 0.04 + slot_policy_clarity * 0.03 + portfolio_coordination * 0.04 - repair_penalty * 0.5 - semantic_failure_penalty * 0.4),
        "emotional_payoff": _clamp(scores.get("emotion_density", 0.5) * 0.75 + scores.get("payoff_score", 0.5) * 0.25 + episode_attr_payoff * 0.06 + payoff_integrity * 0.08 + promise_resolution_rate * 0.04 + portfolio_coordination * 0.02 - payoff_corruption_penalty),
        "long_run_sustainability": _clamp(float(serialization.get("sustainability", 5)) / 10.0 * 0.46 + float(rewards.get("expectation_alignment", 5)) / 10.0 * 0.15 + reader_trust * 0.10 + release_confidence * 0.07 + portfolio_fit * 0.07 + portfolio_coordination * 0.06 + release_schedule_health * 0.075 + slot_policy_clarity * 0.11 + runtime_release_alignment * 0.05 + runtime_trust_signal * 0.03 + runtime_coordination_signal * 0.03 + runtime_policy_confidence * 0.02 + promise_resolution_rate * 0.05 + payoff_integrity * 0.04 + character_dependency_health * 0.02 + strategy_coverage * 0.06 + cadence_guard * 0.02 + release_guard * 0.02 + (1.0 - shared_risk_alert) * 0.02 + (1.0 - novelty_debt) * 0.02 - unresolved_promises * 0.03 - runtime_fatigue_signal * 0.04 - payoff_corruption_penalty * 0.5 - max(0.0, cross_track_risk - 0.7) * 0.01),
        "world_logic": _clamp(base_world_logic + foresight * 0.05 + latest_scene_signal * 0.03),
        "chemistry": _clamp(float(serialization.get("chemistry_signal", 5)) / 10.0 * 0.6 + scores.get("chemistry_score", 0.5) * 0.4 + character_dependency_health * 0.06),
        "stability": _clamp(base_stability + foresight * 0.05 + market_resonance * 0.05 + exploration_bias * 0.03 + release_confidence * 0.04 + repair_confidence * 0.03 + closure_score * 0.05 + defect_resolution_score * 0.05 + strategy_coverage * 0.04 + intent_preservation_score * 0.03 + semantic_repair_effectiveness * 0.03 + portfolio_fit * 0.04 + learning_confidence * 0.05 + release_schedule_health * 0.06 + slot_policy_clarity * 0.06 + runtime_release_alignment * 0.05 + runtime_trust_signal * 0.03 + runtime_coordination_signal * 0.03 + runtime_policy_confidence * 0.02 + portfolio_coordination * 0.06 - overused_penalty - repair_penalty - semantic_failure_penalty - runtime_fatigue_signal * 0.05 - shared_risk_alert * 0.03 - max(0.0, cross_track_risk - 0.6) * 0.02 - max(0.0, pattern_crowding - 0.6) * 0.01 - max(0.0, market_overlap - 0.6) * 0.01),
        "title_fitness": _clamp(title_fitness),
        "milestone_compliance": _clamp(milestone_readiness * 0.72 + conversion_readiness * 0.10 + release_schedule_health * 0.08 + promise_resolution_rate * 0.10),
        "conversion_readiness": _clamp(conversion_readiness * 0.72 + title_fitness * 0.04 + promise_resolution_rate * 0.08 + payoff_integrity * 0.08 + release_schedule_health * 0.08),
        "protagonist_sovereignty": _clamp(protagonist_sovereignty * 0.64 + protagonist_agency * 0.16 + reward_loop_integrity * 0.20 - secondary_takeover_risk * 0.10),
        "narrative_debt_health": _clamp((1.0 - narrative_debt_score) * 0.56 + payoff_recovery_rate * 0.22 + (1.0 - expansion_friction_risk) * 0.22),
        "emotion_wave_health": _clamp(emotion_wave_balance * 0.66 + (1.0 - emotion_fatigue_projection) * 0.20 + release_schedule_health * 0.06 + (1.0 - runtime_fatigue_signal) * 0.08),
        "ip_readiness": _clamp(ip_axis * 0.56 + canon_consistency * 0.20 + franchise_expandability * 0.20 + title_fitness * 0.04),
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
