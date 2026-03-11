from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .regression_guard import PROTECTED_AXES, evaluate_total_profile
from .story_state import ensure_story_state, sync_story_state
from .strategy import PLATFORM_STRATEGY


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return 0.0 if not values else sum(values) / len(values)


def _platform_soak_profile(platform: str | None) -> Dict[str, float]:
    name = str(platform or "DEFAULT")
    profile = dict(PLATFORM_STRATEGY.get(name, {}) or {})
    pacing = str(profile.get("pacing") or "balanced")
    if pacing == "aggressive":
        return {"cycle_penalty": 1.18, "signal_penalty": 1.15, "repair_bonus": 0.0}
    if pacing == "spiky":
        return {"cycle_penalty": 1.24, "signal_penalty": 1.2, "repair_bonus": -0.01}
    if pacing == "character":
        return {"cycle_penalty": 0.94, "signal_penalty": 0.9, "repair_bonus": 0.01}
    return {"cycle_penalty": 1.0, "signal_penalty": 1.0, "repair_bonus": 0.0}


def _heavy_reader_signal(objective_scores: Dict[str, Any], story_state: Dict[str, Any] | None = None) -> float:
    scores = dict(objective_scores or {})
    story = dict(story_state or {})
    promise_graph = dict(story.get("promise_graph", {}) or {})
    cast = dict(story.get("cast", {}) or {})
    protagonist = dict(cast.get("protagonist", {}) or {})
    control = dict(story.get("control", {}) or {})
    reader_quality = dict(control.get("reader_quality", {}) or {})
    arc_pressure = dict(control.get("arc_pressure", {}) or {})

    hook = float(scores.get("fun", 0.0) or 0.0)
    retention = float(scores.get("retention", 0.0) or 0.0)
    pacing = float(scores.get("pacing", 0.0) or 0.0)
    sustainability = float(scores.get("long_run_sustainability", 0.0) or 0.0)
    fantasy = min(
        1.0,
        max(
            0.0,
            float(protagonist.get("urgency", 0.0) or 0.0) / 10.0 * 0.45
            + float(protagonist.get("progress", 0.0) or 0.0) * 0.12
            - float(protagonist.get("backlash", 0.0) or 0.0) * 0.08,
        ),
    )
    payoff_integrity = float(promise_graph.get("payoff_integrity", 0.0) or 0.0)
    hidden_reader_risk = (
        float(reader_quality.get("thinness_debt", 0.0) or 0.0)
        + float(reader_quality.get("repetition_debt", 0.0) or 0.0)
        + float(reader_quality.get("deja_vu_debt", 0.0) or 0.0)
        + float(reader_quality.get("fake_urgency_debt", 0.0) or 0.0)
        + float(reader_quality.get("compression_debt", 0.0) or 0.0)
    ) / 5.0
    arc_drag = (
        float(arc_pressure.get("momentum_debt", 0.0) or 0.0)
        + float(arc_pressure.get("payoff_debt", 0.0) or 0.0)
    ) / 2.0
    return round(
        _clamp(
            hook * 0.24
            + retention * 0.24
            + pacing * 0.15
            + sustainability * 0.13
            + fantasy * 0.14
            + payoff_integrity * 0.10
            - min(0.22, hidden_reader_risk * 0.32)
            - min(0.14, arc_drag * 0.2)
        ),
        4,
    )


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
    system_status["warnings"] = warnings[-8:]
    system_status["drift"] = drift
    system_status["axis_drift"] = axis_drift
    system_status["rollback_signal"] = bool(drift.get("rollback_signal")) or bool(axis_drift.get("drifted_axes"))
    if portfolio_signals:
        system_status["latest_portfolio_signals"] = dict(portfolio_signals)
    state["system_status"] = system_status
    sync_story_state(state)
    return system_status


def simulate_long_run(
    objective_scores: Dict[str, Any],
    story_state: Dict[str, Any],
    horizons: Iterable[int] = (30, 60, 120),
    platform: str | None = None,
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
    heavy_reader_baseline = _heavy_reader_signal(objective_scores, story_state)
    platform_profile = _platform_soak_profile(platform)
    for horizon in horizons:
        history: List[float] = []
        repair_rate_history: List[float] = []
        heavy_reader_signal_history: List[float] = []
        for episode in range(1, int(horizon) + 1):
            cycle = ((episode - 1) % 6) / 10.0
            quality = _clamp(
                base_profile["balanced_total"]
                + (release_guard / 10.0) * 0.015
                + (coordination_health / 10.0) * 0.012
                + payoff_integrity * 0.01
                + closure_score * 0.008
                + float(platform_profile.get("repair_bonus", 0.0) or 0.0)
                - cycle * 0.018 * float(platform_profile.get("cycle_penalty", 1.0) or 1.0)
            )
            repair_rate = _clamp(
                0.76
                + closure_score * 0.12
                + float(platform_profile.get("repair_bonus", 0.0) or 0.0)
                - cycle * 0.08 * float(platform_profile.get("cycle_penalty", 1.0) or 1.0)
            )
            heavy_reader_signal = _clamp(
                heavy_reader_baseline
                + (release_guard / 10.0) * 0.02
                + (coordination_health / 10.0) * 0.016
                + payoff_integrity * 0.01
                - cycle * 0.02 * float(platform_profile.get("signal_penalty", 1.0) or 1.0)
            )
            history.append(round(quality, 4))
            repair_rate_history.append(round(repair_rate, 4))
            heavy_reader_signal_history.append(round(heavy_reader_signal, 4))
        drift = detect_quality_drift(history, lookback=min(8, max(4, int(horizon) // 10)))
        heavy_reader_drift = detect_quality_drift(heavy_reader_signal_history, lookback=min(8, max(4, int(horizon) // 10)), warning_drop=0.03, rollback_drop=0.06)
        simulation_runs[str(horizon)] = {
            "episodes": int(horizon),
            "balanced_total_history": history,
            "final_balanced_total": history[-1],
            "mean_balanced_total": round(_mean(history), 4),
            "min_balanced_total": min(history),
            "repair_rate_mean": round(_mean(repair_rate_history), 4),
            "heavy_reader_signal_history": heavy_reader_signal_history,
            "heavy_reader_signal_mean": round(_mean(heavy_reader_signal_history), 4),
            "heavy_reader_signal_floor": min(heavy_reader_signal_history),
            "heavy_reader_signal_drift": heavy_reader_drift,
            "drift": drift,
        }
    return {
        "baseline_balanced_total": round(base_profile["balanced_total"], 4),
        "baseline_heavy_reader_signal": round(heavy_reader_baseline, 4),
        "platform": str(platform or "DEFAULT"),
        "platform_profile": platform_profile,
        "runs": simulation_runs,
    }


def summarize_soak_report(simulation: Dict[str, Any]) -> Dict[str, Any]:
    runs = dict((simulation or {}).get("runs", {}) or {})
    if not runs:
        return {"tested": False, "steady_noop_ratio": 0.0, "dominant_mode": "unknown"}
    drift_flags = []
    repair_rates = []
    balanced_floors = []
    heavy_reader_floors = []
    heavy_reader_drift_flags = []
    for run in runs.values():
        drift = dict(run.get("drift", {}) or {})
        heavy_reader_drift = dict(run.get("heavy_reader_signal_drift", {}) or {})
        drift_flags.append(0.0 if drift.get("drift_detected") else 1.0)
        heavy_reader_drift_flags.append(0.0 if heavy_reader_drift.get("drift_detected") else 1.0)
        repair_rates.append(float(run.get("repair_rate_mean", 0.0) or 0.0))
        balanced_floors.append(float(run.get("min_balanced_total", 0.0) or 0.0))
        heavy_reader_floors.append(float(run.get("heavy_reader_signal_floor", 0.0) or 0.0))
    steady_noop_ratio = _clamp(
        _mean(drift_flags) * 0.45
        + _mean(repair_rates) * 0.2
        + _mean(balanced_floors) * 0.15
        + _mean(heavy_reader_drift_flags) * 0.1
        + _mean(heavy_reader_floors) * 0.1
    )
    dominant_mode = "steady" if steady_noop_ratio >= 0.72 else "noop" if steady_noop_ratio >= 0.5 else "volatile"
    return {
        "tested": True,
        "steady_noop_ratio": round(steady_noop_ratio, 4),
        "dominant_mode": dominant_mode,
        "run_count": len(runs),
        "drift_free_run_ratio": round(_mean(drift_flags), 4),
        "repair_rate_mean": round(_mean(repair_rates), 4),
        "balanced_floor_mean": round(_mean(balanced_floors), 4),
        "heavy_reader_signal_floor_mean": round(_mean(heavy_reader_floors), 4),
        "heavy_reader_drift_free_run_ratio": round(_mean(heavy_reader_drift_flags), 4),
    }


def record_soak_history(
    state: Dict[str, Any],
    *,
    episode: int,
    soak_report: Dict[str, Any],
    quality_lift_if_human_intervenes: float,
    objective_scores: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    control = story_state.setdefault("control", {})
    reader_quality = dict(control.get("reader_quality", {}) or {})
    soak_state = control.setdefault(
        "soak_history",
        {
            "observed": 0,
            "steady_noop_ratio": 0.0,
            "dominant_mode": "unknown",
            "quality_lift_trend": 1.0,
            "hidden_reader_risk_trend": 1.0,
            "heavy_reader_signal_trend": 0.0,
            "history": [],
        },
    )
    hidden_reader_risk = round(
        min(
            1.0,
            (
                float(reader_quality.get("thinness_debt", 0.0) or 0.0)
                + float(reader_quality.get("repetition_debt", 0.0) or 0.0)
                + float(reader_quality.get("deja_vu_debt", 0.0) or 0.0)
                + float(reader_quality.get("fake_urgency_debt", 0.0) or 0.0)
                + float(reader_quality.get("compression_debt", 0.0) or 0.0)
            )
            / 5.0,
        ),
        4,
    )
    heavy_reader_signal = _heavy_reader_signal(objective_scores or {}, story_state)
    snapshot = {
        "episode": int(episode),
        "steady_noop_ratio": round(float(soak_report.get("steady_noop_ratio", 0.0) or 0.0), 4),
        "dominant_mode": str(soak_report.get("dominant_mode") or "unknown"),
        "quality_lift_if_human_intervenes": round(float(quality_lift_if_human_intervenes or 0.0), 4),
        "hidden_reader_risk": hidden_reader_risk,
        "heavy_reader_signal": heavy_reader_signal,
    }
    history = (list(soak_state.get("history", []) or []) + [snapshot])[-12:]
    observed = int(soak_state.get("observed", 0) or 0) + 1
    blend = 0.0 if observed == 1 else 0.74
    soak_state["history"] = history
    soak_state["observed"] = observed
    soak_state["steady_noop_ratio"] = round(float(soak_state.get("steady_noop_ratio", 0.0) or 0.0) * blend + snapshot["steady_noop_ratio"] * (1.0 - blend), 4)
    soak_state["dominant_mode"] = snapshot["dominant_mode"] if observed <= 2 else (
        "steady" if sum(1 for item in history if item.get("dominant_mode") == "steady") >= max(1, len(history) // 2)
        else "noop" if sum(1 for item in history if item.get("dominant_mode") == "noop") >= max(1, len(history) // 2)
        else snapshot["dominant_mode"]
    )
    soak_state["quality_lift_trend"] = round(
        float(soak_state.get("quality_lift_trend", 1.0) or 1.0) * blend + snapshot["quality_lift_if_human_intervenes"] * (1.0 - blend),
        4,
    )
    soak_state["hidden_reader_risk_trend"] = round(
        float(soak_state.get("hidden_reader_risk_trend", hidden_reader_risk) or hidden_reader_risk) * blend + hidden_reader_risk * (1.0 - blend),
        4,
    )
    soak_state["heavy_reader_signal_trend"] = round(
        float(soak_state.get("heavy_reader_signal_trend", heavy_reader_signal) or heavy_reader_signal) * blend + heavy_reader_signal * (1.0 - blend),
        4,
    )
    state["story_state_v2"] = story_state
    sync_story_state(state)
    return soak_state


def estimate_human_quality_lift(
    *,
    objective_scores: Dict[str, Any],
    system_status: Dict[str, Any] | None = None,
    repair_plan: Dict[str, Any] | None = None,
    gate_passed: bool = False,
    story_state: Dict[str, Any] | None = None,
) -> float:
    profile = evaluate_total_profile(objective_scores)
    balanced_total = float(profile.get("balanced_total", 0.0) or 0.0)
    repair = dict(repair_plan or {})
    critical_issues = list(repair.get("critical_issues", []) or [])
    strategy = list(repair.get("recommended_strategies", []) or [])
    status = dict(system_status or {})
    drift = dict(status.get("drift", {}) or {})
    rollback = bool(status.get("rollback_signal"))
    story_state = dict(story_state or {})
    soak_history = dict(((story_state.get("control", {}) or {}).get("soak_history", {}) or {}))
    soak_observed = int(soak_history.get("observed", 0) or 0)
    soak_ratio = float(soak_history.get("steady_noop_ratio", 0.0) or 0.0)
    soak_lift_trend = float(soak_history.get("quality_lift_trend", 1.0) or 1.0)
    hidden_reader_risk_trend = float(soak_history.get("hidden_reader_risk_trend", 0.0) or 0.0)
    heavy_reader_signal_trend = float(soak_history.get("heavy_reader_signal_trend", 0.0) or 0.0)

    lift = 0.16
    lift -= min(0.1, balanced_total * 0.1)
    lift -= 0.03 if gate_passed else 0.0
    lift += min(0.08, len(critical_issues) * 0.012)
    lift += min(0.04, len(strategy) * 0.008)
    lift += min(0.04, float(drift.get("drop", 0.0) or 0.0))
    lift += 0.03 if rollback else 0.0
    if soak_observed:
        lift -= min(0.05, soak_ratio * 0.06)
        lift -= min(0.03, max(0.0, 0.2 - soak_lift_trend))
        lift += min(0.05, max(0.0, hidden_reader_risk_trend - 0.24) * 0.18)
        lift += min(0.05, max(0.0, 0.72 - heavy_reader_signal_trend) * 0.18)
    return round(_clamp(lift, 0.0, 1.0), 4)
