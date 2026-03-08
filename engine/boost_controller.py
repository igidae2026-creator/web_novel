from __future__ import annotations
from .phase import get_phase

def apply_boost(cfg: dict, state: dict, knobs: dict) -> dict:
    if get_phase(cfg) != "BOOST":
        return knobs
    # conservative additive boosts; clamped later by intensity_lock
    knobs["hook_intensity"] = float(knobs.get("hook_intensity", 0.7)) + 0.03
    knobs["payoff_intensity"] = float(knobs.get("payoff_intensity", 0.7)) + 0.04
    knobs["compression"] = float(knobs.get("compression", 0.6)) + 0.03
    knobs["novelty_boost"] = float(knobs.get("novelty_boost", 0.5)) + 0.02
    state["boost_active"] = True
    return knobs
