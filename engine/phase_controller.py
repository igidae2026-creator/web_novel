
from __future__ import annotations
from engine.event_log import log_event
from typing import Dict

DEFAULT_COOLDOWN = 7  # 최소 7회차 유지

def apply_phase_hysteresis(state: Dict, new_phase: str) -> str:
    current = state.get("phase", "STABILIZE")
    cooldown = state.get("phase_cooldown", 0)

    if cooldown > 0:
        state["phase_cooldown"] = cooldown - 1
        return current

    if new_phase != current:
        state["phase"] = new_phase
        try:
            log_event(state.get("out_dir","."), "phase_changed", {"phase": new_phase}, safe_mode=True)
        except Exception:
            pass
        state["phase_cooldown"] = DEFAULT_COOLDOWN
        return new_phase

    return current
