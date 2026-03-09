from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .business_operator import build_business_action_recommendations
from .regression_guard import PROTECTED_AXES, evaluate_total_profile
from .story_state import ensure_story_state, sync_story_state


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return 0.0 if not values else sum(values) / len(values)


def detect_quality_drift(
    balanced_history: List[float],
    lookback: int = 5,
    warning_drop: float = 0.025,
    rollback_drop: float = 0.05,
) -> Dict[str, Any]:
    history = [float(item) for item in list(balanced_history or [])]
    if len(history) < max(3, lookback):
        return {"drift_detected": False, "warning": False, "rollback_signal": False, "drop": 0.0}
    baseline_window = history[-lookback * 2:-lookback] or history[:-lookback]
    recent_window = history[-lookback:]
    baseline = _mean(baseline_window)
    recent = _mean(recent_window)
    drop = baseline - recent
    return {
        "drift_detected": drop >= warning_drop,
        "warning": drop >= warning_drop,
        "rollback_signal": drop >= rollback_drop,
        "drop": round(drop, 4),
        "baseline_window_mean": round(baseline, 4),
        "recent_window_mean": round(recent, 4),
    }


def detect_axis_drift(
    axis_history: Dict[str, List[float]],
    lookback: int = 5,
    warning_drop: float = 0.04,
) -> Dict[str, Any]:
    history = {axis: [float(item) for item in list(values or [])] for axis, values in dict(axis_history or {}).items()}
    drifted_axes = []
    details: Dict[str, Any] = {}
    for axis, values in history.items():
        if len(values) < max(3, lookback):
            continue
        baseline_window = values[-lookback * 2:-lookback] or values[:-lookback]
        recent_window = values[-lookback:]
        baseline = _mean(baseline_window)
        recent = _mean(recent_window)
        drop = baseline - recent
        details[axis] = {
            "drop": round(drop, 4),
            "baseline_window_mean": round(baseline, 4),
            "recent_window_mean": round(recent, 4),
            "warning": drop >= warning_drop,
        }
        if drop >= warning_drop:
            drifted_axes.append(axis)
    return {"drifted_axes": drifted_axes, "details": details}


def update_system_status(
    state: Dict[str, Any],
    episode: int,
    objective_scores: Dict[str, Any],
    portfolio_signals: Dict[str, Any] | None = None,
    runtime_cfg: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    control = story_state.setdefault("control", {})
    repair = dict(control.get("causal_repair", {}) or {})
    runtime_release = dict(control.get("runtime_release", {}) or {})
    portfolio_memory = dict(story_state.get("portfolio_memory", {}) or {})
    system_status = state.setdefault(
        "system_status",
        {
            "iteration_state": "idle",
            "balanced_total_history": [],
            "axis_history": {},
            "repair_rate_history": [],
            "portfolio_signal_history": [],
            "drift": {},
            "axis_drift": {},
            "warnings": [],
            "rollback_signal": False,
        },
    )
    profile = evaluate_total_profile(objective_scores)
    attempts_used = int(repair.get("attempts_used", 0) or 0)
    retry_budget = max(1, int(repair.get("retry_budget", 1) or 1))
    repair_rate = _clamp(1.0 - attempts_used / retry_budget)
    portfolio_snapshot = {
        "episode": int(episode),
        "release_guard": int(portfolio_memory.get("release_guard", 0) or 0),
        "coordination_health": int(portfolio_memory.get("coordination_health", 0) or 0),
        "platform_slot_pressure": int(portfolio_memory.get("platform_slot_pressure", 0) or 0),
        "long_horizon_pressure": int(portfolio_memory.get("long_horizon_pressure", 0) or 0),
    }
    system_status["iteration_state"] = str(repair.get("status", runtime_release.get("action", "running")) or "running")
    system_status["balanced_total_history"] = (list(system_status.get("balanced_total_history", []) or []) + [round(profile["balanced_total"], 4)])[-24:]
    axis_history = dict(system_status.get("axis_history", {}) or {})
    for axis in PROTECTED_AXES:
        axis_history[axis] = (list(axis_history.get(axis, []) or []) + [round(float(profile.get(axis, 0.0) or 0.0), 4)])[-24:]
    system_status["axis_history"] = axis_history
    system_status["repair_rate_history"] = (list(system_status.get("repair_rate_history", []) or []) + [round(repair_rate, 4)])[-24:]
    system_status["portfolio_signal_history"] = (list(system_status.get("portfolio_signal_history", []) or []) + [portfolio_snapshot])[-24:]
    drift = detect_quality_drift(system_status["balanced_total_history"])
    axis_drift = detect_axis_drift(system_status["axis_history"])
    warnings = list(system_status.get("warnings", []) or [])
    if drift.get("warning"):
        warnings.append({"episode": int(episode), "type": "quality_drift", "drop": drift.get("drop", 0.0)})
    if axis_drift.get("drifted_axes"):
        warnings.append({"episode": int(episode), "type": "axis_drift", "axes": list(axis_drift.get("drifted_axes", []))[:4]})
    latest_business = {
        "title_fitness": float(((story_state.get("title", {}) or {}).get("best_title", {}) or {}).get("title_fitness", 0.0) or 0.0),
        "milestone_readiness": float((story_state.get("milestones", {}) or {}).get("milestone_readiness", 0.0) or 0.0),
        "conversion_readiness": float((story_state.get("monetization", {}) or {}).get("conversion_readiness", 0.0) or 0.0),
        "protagonist_sovereignty": float((story_state.get("protagonist_guard", {}) or {}).get("protagonist_sovereignty", 0.0) or 0.0),
        "narrative_debt_score": float((story_state.get("narrative_debt", {}) or {}).get("narrative_debt_score", 0.0) or 0.0),
        "emotion_wave_balance": float((story_state.get("emotion_wave", {}) or {}).get("emotion_wave_balance", 0.0) or 0.0),
        "ip_readiness": float((story_state.get("ip_readiness", {}) or {}).get("ip_readiness", 0.0) or 0.0),
    }
    low_business_axes = []
    if latest_business["title_fitness"] < 0.62:
        low_business_axes.append("title_fitness")
    if latest_business["milestone_readiness"] < 0.64:
        low_business_axes.append("milestone_compliance")
    if latest_business["conversion_readiness"] < 0.64:
        low_business_axes.append("conversion_readiness")
    if latest_business["protagonist_sovereignty"] < 0.66:
        low_business_axes.append("protagonist_sovereignty")
    if (1.0 - latest_business["narrative_debt_score"]) < 0.58:
        low_business_axes.append("narrative_debt_health")
    if latest_business["emotion_wave_balance"] < 0.58:
        low_business_axes.append("emotion_wave_health")
    if latest_business["ip_readiness"] < 0.55:
        low_business_axes.append("ip_readiness")
    if low_business_axes:
        warnings.append({"episode": int(episode), "type": "business_axis", "axes": low_business_axes[:5]})
    system_status["warnings"] = warnings[-8:]
    system_status["drift"] = drift
    system_status["axis_drift"] = axis_drift
    system_status["rollback_signal"] = bool(drift.get("rollback_signal")) or bool(axis_drift.get("drifted_axes"))
    if portfolio_signals:
        system_status["latest_portfolio_signals"] = dict(portfolio_signals)
    system_status["latest_business_signals"] = latest_business
    system_status["latest_title_state"] = dict(story_state.get("title", {}) or {})
    system_status["latest_revision_triggers"] = list((((story_state.get("control", {}) or {}).get("causal_repair", {}) or {}).get("revision_triggers", []) or []))
    system_status["latest_business_recommendations"] = build_business_action_recommendations(system_status, runtime_cfg=runtime_cfg)[:5]
    state["system_status"] = system_status
    sync_story_state(state)
    return system_status


def simulate_long_run(
    objective_scores: Dict[str, Any],
    story_state: Dict[str, Any],
    horizons: Iterable[int] = (30, 60, 120),
) -> Dict[str, Any]:
    base_profile = evaluate_total_profile(objective_scores)
    portfolio_memory = dict((story_state or {}).get("portfolio_memory", {}) or {})
    repair = dict(((story_state or {}).get("control", {}) or {}).get("causal_repair", {}) or {})
    promise_graph = dict((story_state or {}).get("promise_graph", {}) or {})
    monetization = dict((story_state or {}).get("monetization", {}) or {})
    emotion_wave = dict((story_state or {}).get("emotion_wave", {}) or {})
    narrative_debt = dict((story_state or {}).get("narrative_debt", {}) or {})
    ip_state = dict((story_state or {}).get("ip_readiness", {}) or {})
    simulation_runs: Dict[str, Any] = {}
    release_guard = int(portfolio_memory.get("release_guard", 5) or 5)
    coordination_health = int(portfolio_memory.get("coordination_health", 5) or 5)
    payoff_integrity = float(promise_graph.get("payoff_integrity", 0.5) or 0.5)
    closure_score = float(repair.get("closure_score", 0.5) or 0.5)
    conversion_readiness = float(monetization.get("conversion_readiness", 0.5) or 0.5)
    fatigue_projection = float(emotion_wave.get("fatigue_projection", 0.5) or 0.5)
    debt_score = float(narrative_debt.get("narrative_debt_score", 0.5) or 0.5)
    ip_axis = float(ip_state.get("ip_readiness", 0.5) or 0.5)
    for horizon in horizons:
        history: List[float] = []
        repair_rate_history: List[float] = []
        for episode in range(1, int(horizon) + 1):
            cycle = ((episode - 1) % 6) / 10.0
            quality = _clamp(
                base_profile["balanced_total"]
                + (release_guard / 10.0) * 0.015
                + (coordination_health / 10.0) * 0.012
                + payoff_integrity * 0.01
                + closure_score * 0.008
                + conversion_readiness * 0.01
                + ip_axis * 0.005
                - cycle * 0.018
                - fatigue_projection * 0.012
                - debt_score * 0.012
            )
            repair_rate = _clamp(0.76 + closure_score * 0.12 - cycle * 0.08)
            history.append(round(quality, 4))
            repair_rate_history.append(round(repair_rate, 4))
        drift = detect_quality_drift(history, lookback=min(8, max(4, int(horizon) // 10)))
        simulation_runs[str(horizon)] = {
            "episodes": int(horizon),
            "balanced_total_history": history,
            "final_balanced_total": history[-1],
            "mean_balanced_total": round(_mean(history), 4),
            "min_balanced_total": min(history),
            "repair_rate_mean": round(_mean(repair_rate_history), 4),
            "drift": drift,
        }
    return {"baseline_balanced_total": round(base_profile["balanced_total"], 4), "runs": simulation_runs}
