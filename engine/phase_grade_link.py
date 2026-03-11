from __future__ import annotations
from engine.event_log import log_event
from typing import Dict

GRADE_PHASE_POLICY = {
    'A': {'phase': 'BOOST', 'intensity': 1.0},
    'B': {'phase': 'BOOST', 'intensity': 0.6},
    'C': {'phase': 'STABILIZE', 'intensity': 0.0},
    'D': {'phase': 'STABILIZE', 'intensity': 0.0},
}

GRADE_TO_PHASE = {
    "A": "BOOST",
    "B": "BOOST",
    "C": "STABILIZE",
    "D": "STABILIZE",
}

def desired_phase_from_grade(grade: str) -> str:
    # 기본 phase 결정

    g = (grade or "D").upper()
    return GRADE_TO_PHASE.get(g, "STABILIZE")

def maybe_set_pending_phase(state: Dict, grade: str) -> None:
    # only set pending; actual phase change controlled by phase_controller hysteresis
    desired = desired_phase_from_grade(grade)
    cur = state.get("phase", "STABILIZE")
    if desired != cur:
        state["pending_phase"] = desired
    else:
        state.pop("pending_phase", None)

def can_apply_pending(state: Dict) -> bool:
    # require at least 1 certification ok/record after grade change
    # and respect grade cooldown and phase cooldown
    if state.get("pending_phase") is None:
        return False
    # grade cooldown must be 0
    if int(state.get("grade_cooldown_days", 0) or 0) > 0:
        return False
    # phase cooldown must be 0
    if int(state.get("phase_cooldown", 0) or 0) > 0:
        return False
    # require last certification snapshot date to match or exceed grade_last_change_ymd
    glast = state.get("grade_last_change_ymd")
    clast = state.get("last_cert_date")
    if glast and clast and clast < glast:
        return False
    # require at least one cert record after grade change (tracked by cert_count_since_grade_change)
    if int(state.get("cert_count_since_grade_change", 0) or 0) < 1:
        return False
    return True

def apply_pending_phase(state: Dict) -> str:
    p = state.get("pending_phase")
    if not p:
        return state.get("phase", "STABILIZE")
    state["phase"] = p
    try:
        log_event(state.get("out_dir","."), "pending_phase_applied", {"phase": p}, safe_mode=True)
    except Exception:
        pass
    state.pop("pending_phase", None)
    # set a small cooldown to prevent immediate flip
    state["phase_cooldown"] = max(int(state.get("phase_cooldown", 0) or 0), 3)
    return p

def phase_intensity_from_grade(grade: str) -> float:
    g = (grade or "D").upper()
    return GRADE_PHASE_POLICY.get(g, {}).get("intensity", 0.0)
