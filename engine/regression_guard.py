from __future__ import annotations

from typing import Any, Dict, Tuple


PROTECTED_AXES = [
    "fun",
    "coherence",
    "character_persuasiveness",
    "pacing",
    "retention",
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
