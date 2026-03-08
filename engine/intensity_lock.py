from __future__ import annotations
from .phase import get_phase

LIMITS = {
    "STABILIZE": {"hook_intensity": 0.92, "payoff_intensity": 0.94, "compression": 0.88, "novelty_boost": 0.85},
    "BOOST": {"hook_intensity": 0.97, "payoff_intensity": 0.98, "compression": 0.92, "novelty_boost": 0.90},
}

def clamp_knobs(cfg: dict, knobs: dict) -> dict:
    lim = LIMITS.get(get_phase(cfg), LIMITS["STABILIZE"])
    for k, maxv in lim.items():
        if k in knobs:
            try:
                knobs[k] = min(float(maxv), float(knobs[k]))
            except Exception:
                pass
    return knobs

def apply_freeze(cfg: dict, state: dict, knobs: dict):
    if get_phase(cfg) != "STABILIZE":
        return knobs
    freeze = int(state.get("freeze_counter", 0) or 0)
    if freeze > 0:
        state["freeze_counter"] = freeze - 1
        return state.get("last_stable_knobs", knobs)
    return knobs

def register_change(cfg: dict, state: dict, knobs: dict):
    if get_phase(cfg) != "STABILIZE":
        return state
    state["last_stable_knobs"] = knobs.copy()
    state["freeze_counter"] = 2
    return state
