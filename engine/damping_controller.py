from __future__ import annotations
from .phase import get_phase

GLOBAL_DAMPING = 0.4  # STABILIZE only

def damp_knobs(cfg: dict, knobs: dict, original: dict) -> dict:
    if get_phase(cfg) != "STABILIZE":
        return knobs
    for k in list(knobs.keys()):
        if k in original:
            try:
                delta = float(knobs[k]) - float(original[k])
                knobs[k] = float(original[k]) + delta * GLOBAL_DAMPING
            except Exception:
                pass
    return knobs
