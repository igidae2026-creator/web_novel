from __future__ import annotations

from typing import Any, Dict, Tuple


PROTECTED_AXES = [
    "fun",
    "coherence",
    "character_persuasiveness",
    "pacing",
    "retention",
    "emotional_immersion",
    "information_design",
    "emotional_payoff",
    "long_run_sustainability",
    "world_logic",
    "chemistry",
    "stability",
]


def evaluate_total_profile(scores: Dict[str, Any]) -> Dict[str, float]:
    values = {axis: float(scores.get(axis, 0.0) or 0.0) for axis in PROTECTED_AXES}
    values["total"] = sum(values.values()) / len(PROTECTED_AXES)
    values["variance_penalty"] = max(0.0, max(values[axis] for axis in PROTECTED_AXES) - min(values[axis] for axis in PROTECTED_AXES))
    values["balanced_total"] = max(0.0, values["total"] - values["variance_penalty"] * 0.15)
    return values


def regression_decision(before: Dict[str, Any], after: Dict[str, Any], tolerance: float = 0.05) -> Tuple[bool, Dict[str, Any]]:
    prev = evaluate_total_profile(before)
    nxt = evaluate_total_profile(after)
    dropped_axes = [
        axis for axis in PROTECTED_AXES
        if nxt[axis] + tolerance < prev[axis]
    ]
    improved_total = nxt["balanced_total"] > prev["balanced_total"] + 0.01
    accepted = improved_total and len(dropped_axes) == 0
    return accepted, {
        "accepted": accepted,
        "before": prev,
        "after": nxt,
        "dropped_axes": dropped_axes,
    }


def portfolio_signal_decision(before: Dict[str, Any], after: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    improving = ["pattern_crowding", "shared_risk", "novelty_debt", "cadence_pressure", "market_overlap", "release_timing_interference"]
    deltas = {key: float(after.get(key, 0) or 0) - float(before.get(key, 0) or 0) for key in improving}
    regressed = [key for key, delta in deltas.items() if delta > 0.5]
    accepted = len(regressed) == 0
    return accepted, {"accepted": accepted, "regressed_signals": regressed, "deltas": deltas}


def release_policy_decision(before: Dict[str, Any], after: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    deltas = {
        "platform_slot_pressure": float(after.get("platform_slot_pressure", 0) or 0) - float(before.get("platform_slot_pressure", 0) or 0),
        "release_guard": float(before.get("release_guard", 0) or 0) - float(after.get("release_guard", 0) or 0),
    }
    regressed = [key for key, delta in deltas.items() if delta > 0.5]
    accepted = len(regressed) == 0
    return accepted, {"accepted": accepted, "regressed_signals": regressed, "deltas": deltas}
