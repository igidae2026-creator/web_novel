from __future__ import annotations
import os, importlib
from typing import Dict, Any, List

REQUIRED = [
    "engine.phase",
    "engine.phase_controller",
    "engine.boost_controller",
    "engine.intensity_lock",
    "engine.damping_controller",
    "engine.phase_grade_link",
]

def check() -> Dict[str, Any]:
    out = {"ok": True, "missing": [], "errors": [], "present": []}
    for mod in REQUIRED:
        try:
            m = importlib.import_module(mod)
            out["present"].append(mod)
        except Exception as e:
            out["ok"] = False
            out["errors"].append({"module": mod, "error": repr(e)})
    # function sanity checks
    try:
        from engine.phase import get_phase
        from engine.boost_controller import apply_boost
        from engine.intensity_lock import clamp_knobs, apply_freeze
        from engine.damping_controller import damp_knobs
        from engine.phase_controller import apply_phase_hysteresis
        # basic calls
        cfg={"phase":"STABILIZE"}
        state={}
        knobs={"hook_intensity":0.7,"payoff_intensity":0.7,"compression":0.6,"novelty_boost":0.5}
        _ = get_phase(cfg)
        _ = clamp_knobs(cfg, dict(knobs))
        _ = damp_knobs(cfg, dict(knobs), dict(knobs))
        _ = apply_freeze(cfg, state, dict(knobs))
        _ = apply_phase_hysteresis(state, "STABILIZE")
        cfg["phase"]="BOOST"
        _ = apply_boost(cfg, state, dict(knobs))
    except Exception as e:
        out["ok"]=False
        out["errors"].append({"module":"sanity", "error": repr(e)})
    return out
