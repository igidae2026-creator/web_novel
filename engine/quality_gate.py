from __future__ import annotations

from typing import Any, Dict

from .cliffhanger_engine import validate_cliffhanger
from .prose_guard import evaluate_prose_readability
from .regression_guard import PROTECTED_AXES, evaluate_total_profile


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _count_open_conflict_threads(
    conflict: Dict[str, Any],
    story_state: Dict[str, Any],
) -> int:
    explicit = conflict.get("open_thread_count")
    if explicit is not None:
        try:
            return max(0, int(explicit))
        except (TypeError, ValueError):
            pass

    threads = conflict.get("threads", []) or []
    open_from_conflict = sum(1 for thread in threads if thread.get("status") != "resolved")
    if open_from_conflict:
        return open_from_conflict

    unresolved_threads = story_state.get("unresolved_threads", []) or []
    return len(unresolved_threads)


def _protagonist_momentum(story_state: Dict[str, Any]) -> float:
    protagonist = dict((story_state.get("cast", {}) or {}).get("protagonist", {}) or {})
    rival = dict((story_state.get("cast", {}) or {}).get("rival", {}) or {})

    progress = _as_float(protagonist.get("progress"), 0.0)
    backlash = _as_float(protagonist.get("backlash"), 0.0)
    decision_pressure = _as_float(protagonist.get("decision_pressure"), 0.0)
    urgency = _as_float(protagonist.get("urgency"), 0.0)
    rival_progress = _as_float(rival.get("progress"), 0.0)

    momentum = 0.52
    momentum += min(0.24, progress * 0.08)
    momentum += min(0.1, decision_pressure * 0.01)
    momentum += min(0.06, urgency * 0.006)
    momentum -= min(0.38, backlash * 0.11)
    momentum -= min(0.14, max(0.0, rival_progress - progress) * 0.05)
    return max(0.0, min(1.0, momentum))


def quality_gate_report(
    scores: Dict[str, Any],
    thresholds: Dict[str, Any],
    *,
    episode_text: str | None = None,
    cliffhanger: str | None = None,
    cliffhanger_plan: Dict[str, Any] | None = None,
    retention_state: Dict[str, Any] | None = None,
    predicted_retention: float | None = None,
    content_ceiling: Dict[str, Any] | None = None,
    causal_report: Dict[str, Any] | None = None,
    story_state: Dict[str, Any] | None = None,
    objective_scores: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    scores = dict(scores or {})
    thresholds = dict(thresholds or {})
    cliffhanger_plan = dict(cliffhanger_plan or {})
    retention_state = dict(retention_state or {})
    content_ceiling = dict(content_ceiling or {})
    causal_report = dict(causal_report or {})
    story_state = dict(story_state or {})
    objective_scores = dict(objective_scores or {})
    prose_report = {}

    checks = {
        "hook_score": _as_float(scores.get("hook_score"), 0.0) >= _as_float(thresholds.get("hook_score_min"), 0.0),
        "paywall_score": _as_float(scores.get("paywall_score"), 1.0) >= _as_float(thresholds.get("paywall_score_min"), 0.0),
        "emotion_density": _as_float(scores.get("emotion_density"), 0.0) >= _as_float(thresholds.get("emotion_density_min"), 0.0),
        "escalation": _as_float(scores.get("escalation"), 0.0) >= _as_float(thresholds.get("escalation_min"), 0.0),
        "repetition_score": _as_float(scores.get("repetition_score"), 1.0) <= _as_float(thresholds.get("repetition_max"), 1.0),
    }

    optional_min_checks = {
        "character_score": "character_score_min",
        "payoff_score": "payoff_score_min",
        "pacing_score": "pacing_score_min",
        "chemistry_score": "chemistry_score_min",
    }
    for score_key, threshold_key in optional_min_checks.items():
        if threshold_key in thresholds:
            checks[score_key] = _as_float(scores.get(score_key), 0.0) >= _as_float(thresholds.get(threshold_key), 0.0)

    cliffhanger_required = thresholds.get("cliffhanger_valid_required")
    if cliffhanger_required:
        checks["cliffhanger_valid"] = validate_cliffhanger(
            {"cliffhanger": cliffhanger or ""},
            cliffhanger_plan,
        )[0]

    min_cliffhanger_pressure = thresholds.get("cliffhanger_carryover_pressure_min")
    if min_cliffhanger_pressure is not None:
        checks["cliffhanger_carryover_pressure"] = _as_float(
            cliffhanger_plan.get("carryover_pressure"),
            0.0,
        ) >= _as_float(min_cliffhanger_pressure, 0.0)

    min_retention = thresholds.get("predicted_retention_min")
    if min_retention is not None and predicted_retention is not None:
        checks["predicted_retention"] = _as_float(predicted_retention, 0.0) >= _as_float(min_retention, 0.0)

    min_prose_readability = thresholds.get("prose_readability_min")
    if min_prose_readability is not None:
        prose_report = evaluate_prose_readability(episode_text or "")
        checks["prose_readability"] = _as_float(
            prose_report.get("score"),
            0.0,
        ) >= _as_float(min_prose_readability, 0.0)

    min_thread_pressure = thresholds.get("thread_pressure_min")
    if min_thread_pressure is not None:
        checks["thread_pressure"] = _as_float(
            retention_state.get("unresolved_thread_pressure"),
            0.0,
        ) >= _as_float(min_thread_pressure, 0.0)

    min_curiosity_debt = thresholds.get("curiosity_debt_min")
    if min_curiosity_debt is not None:
        checks["curiosity_debt"] = _as_float(retention_state.get("curiosity_debt"), 0.0) >= _as_float(min_curiosity_debt, 0.0)

    retention_min_checks = {
        "threat_proximity": "threat_proximity_min",
        "payoff_debt": "payoff_debt_min",
        "fallout_pressure": "fallout_pressure_min",
        "chemistry_pressure": "chemistry_pressure_min",
        "information_gap": "information_gap_min",
        "sustainability": "retention_sustainability_min",
    }
    for retention_key, threshold_key in retention_min_checks.items():
        if threshold_key in thresholds:
            checks[retention_key] = _as_float(
                retention_state.get(retention_key),
                0.0,
            ) >= _as_float(thresholds.get(threshold_key), 0.0)

    min_ceiling = thresholds.get("ceiling_total_min")
    if min_ceiling is not None:
        checks["ceiling_total"] = _as_float(content_ceiling.get("ceiling_total"), 0.0) >= _as_float(min_ceiling, 0.0)

    min_causal_score = thresholds.get("causal_score_min")
    if min_causal_score is not None:
        checks["causal_score"] = _as_float(causal_report.get("score"), 0.0) >= _as_float(min_causal_score, 0.0)

    max_causal_issues = thresholds.get("causal_issues_max")
    if max_causal_issues is not None:
        checks["causal_issues"] = len(causal_report.get("issues", []) or []) <= int(max_causal_issues)

    promise_graph = dict(story_state.get("promise_graph", {}) or {})
    min_payoff_integrity = thresholds.get("payoff_integrity_min")
    if min_payoff_integrity is not None:
        checks["payoff_integrity"] = _as_float(
            promise_graph.get("payoff_integrity"),
            0.0,
        ) >= _as_float(min_payoff_integrity, 0.0)

    max_payoff_corruption_flags = thresholds.get("payoff_corruption_flags_max")
    if max_payoff_corruption_flags is not None:
        checks["payoff_corruption_flags"] = len(
            promise_graph.get("payoff_corruption_flags", []) or []
        ) <= int(max_payoff_corruption_flags)

    world = dict(story_state.get("world", {}) or {})
    max_world_instability = thresholds.get("world_instability_max")
    if max_world_instability is not None:
        checks["world_instability"] = _as_float(
            world.get("instability"),
            10.0,
        ) <= _as_float(max_world_instability, 10.0)

    pacing = dict(story_state.get("pacing", {}) or {})
    max_pacing_release_debt = thresholds.get("pacing_release_debt_max")
    if max_pacing_release_debt is not None:
        checks["pacing_release_debt"] = _as_float(
            pacing.get("release_debt"),
            10.0,
        ) <= _as_float(max_pacing_release_debt, 10.0)

    max_pacing_spike_debt = thresholds.get("pacing_spike_debt_max")
    if max_pacing_spike_debt is not None:
        checks["pacing_spike_debt"] = _as_float(
            pacing.get("spike_debt"),
            10.0,
        ) <= _as_float(max_pacing_spike_debt, 10.0)

    pattern_memory = dict(story_state.get("pattern_memory", {}) or {})
    max_overused_events = thresholds.get("pattern_overused_events_max")
    if max_overused_events is not None:
        checks["pattern_overused_events"] = len(
            pattern_memory.get("overused_events", []) or []
        ) <= int(max_overused_events)

    portfolio_metrics = dict(story_state.get("portfolio_metrics", {}) or {})
    max_pattern_crowding = thresholds.get("pattern_crowding_max")
    if max_pattern_crowding is not None:
        checks["pattern_crowding"] = _as_float(
            portfolio_metrics.get("pattern_crowding"),
            10.0,
        ) <= _as_float(max_pattern_crowding, 10.0)

    max_novelty_debt = thresholds.get("novelty_debt_max")
    if max_novelty_debt is not None:
        checks["novelty_debt"] = _as_float(
            portfolio_metrics.get("novelty_debt"),
            10.0,
        ) <= _as_float(max_novelty_debt, 10.0)

    portfolio_memory = dict(story_state.get("portfolio_memory", {}) or {})
    min_novelty_guard = thresholds.get("novelty_guard_min")
    if min_novelty_guard is not None:
        checks["novelty_guard"] = _as_float(
            portfolio_memory.get("novelty_guard"),
            0.0,
        ) >= _as_float(min_novelty_guard, 0.0)

    conflict = dict(story_state.get("conflict", {}) or {})
    min_conflict_threat_pressure = thresholds.get("conflict_threat_pressure_min")
    if min_conflict_threat_pressure is not None:
        checks["conflict_threat_pressure"] = _as_float(
            conflict.get("threat_pressure"),
            0.0,
        ) >= _as_float(min_conflict_threat_pressure, 0.0)

    min_conflict_consequence = thresholds.get("conflict_consequence_level_min")
    if min_conflict_consequence is not None:
        checks["conflict_consequence_level"] = _as_float(
            conflict.get("consequence_level"),
            0.0,
        ) >= _as_float(min_conflict_consequence, 0.0)

    min_conflict_open_threads = thresholds.get("conflict_open_threads_min")
    if min_conflict_open_threads is not None:
        checks["conflict_open_threads"] = _count_open_conflict_threads(
            conflict,
            story_state,
        ) >= int(min_conflict_open_threads)

    protagonist = dict((story_state.get("cast", {}) or {}).get("protagonist", {}) or {})
    min_protagonist_decision_pressure = thresholds.get("protagonist_decision_pressure_min")
    if min_protagonist_decision_pressure is not None:
        checks["protagonist_decision_pressure"] = _as_float(
            protagonist.get("decision_pressure"),
            0.0,
        ) >= _as_float(min_protagonist_decision_pressure, 0.0)

    min_protagonist_momentum = thresholds.get("protagonist_momentum_min")
    if min_protagonist_momentum is not None:
        checks["protagonist_momentum"] = _protagonist_momentum(story_state) >= _as_float(
            min_protagonist_momentum,
            0.0,
        )

    objective_profile = None
    if objective_scores:
        objective_profile = evaluate_total_profile(objective_scores)

    min_balanced_objective = thresholds.get("balanced_objective_min")
    if min_balanced_objective is not None:
        if objective_profile is None:
            objective_profile = evaluate_total_profile(objective_scores)
        checks["balanced_objective"] = _as_float(
            objective_profile.get("balanced_total"),
            0.0,
        ) >= _as_float(min_balanced_objective, 0.0)

    max_objective_variance = thresholds.get("objective_variance_max")
    if max_objective_variance is not None:
        if objective_profile is None:
            objective_profile = evaluate_total_profile(objective_scores)
        checks["objective_variance"] = _as_float(
            objective_profile.get("variance_penalty"),
            1.0,
        ) <= _as_float(max_objective_variance, 1.0)

    min_weakest_objective_axis = thresholds.get("weakest_objective_axis_min")
    if min_weakest_objective_axis is not None:
        weakest_axis_value = min(
            (_as_float(objective_scores.get(axis), 0.0) for axis in PROTECTED_AXES),
            default=0.0,
        )
        checks["weakest_objective_axis"] = weakest_axis_value >= _as_float(
            min_weakest_objective_axis,
            0.0,
        )

    failed = [name for name, passed in checks.items() if not passed]
    return {
        "passed": not failed,
        "checks": checks,
        "failed_checks": failed,
        "objective_profile": objective_profile or {},
        "prose_report": prose_report,
    }


def quality_gate(
    scores: Dict[str, Any],
    thresholds: Dict[str, Any],
    *,
    episode_text: str | None = None,
    cliffhanger: str | None = None,
    cliffhanger_plan: Dict[str, Any] | None = None,
    retention_state: Dict[str, Any] | None = None,
    predicted_retention: float | None = None,
    content_ceiling: Dict[str, Any] | None = None,
    causal_report: Dict[str, Any] | None = None,
    story_state: Dict[str, Any] | None = None,
    objective_scores: Dict[str, Any] | None = None,
) -> bool:
    report = quality_gate_report(
        scores,
        thresholds,
        episode_text=episode_text,
        cliffhanger=cliffhanger,
        cliffhanger_plan=cliffhanger_plan,
        retention_state=retention_state,
        predicted_retention=predicted_retention,
        content_ceiling=content_ceiling,
        causal_report=causal_report,
        story_state=story_state,
        objective_scores=objective_scores,
    )
    return bool(report["passed"])
