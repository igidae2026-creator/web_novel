from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .regression_guard import evaluate_total_profile
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


def update_system_status(
    state: Dict[str, Any],
    episode: int,
    objective_scores: Dict[str, Any],
    portfolio_signals: Dict[str, Any] | None = None,
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
            "repair_rate_history": [],
            "portfolio_signal_history": [],
            "drift": {},
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
    system_status["repair_rate_history"] = (list(system_status.get("repair_rate_history", []) or []) + [round(repair_rate, 4)])[-24:]
    system_status["portfolio_signal_history"] = (list(system_status.get("portfolio_signal_history", []) or []) + [portfolio_snapshot])[-24:]
    drift = detect_quality_drift(system_status["balanced_total_history"])
    warnings = list(system_status.get("warnings", []) or [])
    if drift.get("warning"):
        warnings.append({"episode": int(episode), "type": "quality_drift", "drop": drift.get("drop", 0.0)})
    system_status["warnings"] = warnings[-8:]
    system_status["drift"] = drift
    system_status["rollback_signal"] = bool(drift.get("rollback_signal"))
    if portfolio_signals:
        system_status["latest_portfolio_signals"] = dict(portfolio_signals)
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
    simulation_runs: Dict[str, Any] = {}
    release_guard = int(portfolio_memory.get("release_guard", 5) or 5)
    coordination_health = int(portfolio_memory.get("coordination_health", 5) or 5)
    payoff_integrity = float(promise_graph.get("payoff_integrity", 0.5) or 0.5)
    closure_score = float(repair.get("closure_score", 0.5) or 0.5)
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
                - cycle * 0.018
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
