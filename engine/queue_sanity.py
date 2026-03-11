from __future__ import annotations
import os, json
from typing import Dict, Any, Tuple

def validate_queue_state(state: Dict[str, Any]) -> Tuple[bool, str]:
    status = state.get("status")
    if status not in ["idle","running","paused","blocked","done"]:
        return False, f"invalid status: {status}"
    dirs = state.get("track_dirs", [])
    if not isinstance(dirs, list):
        return False, "track_dirs not list"
    idx = int(state.get("current_index", 0) or 0)
    if idx < 0:
        return False, "current_index < 0"
    if dirs and idx > len(dirs):
        return False, "current_index > len(track_dirs)"
    return True, "ok"

def repair_queue_state(state: Dict[str, Any]) -> Dict[str, Any]:
    ok, _ = validate_queue_state(state)
    if ok:
        return state
    # minimal repair
    state["status"] = "paused"
    try:
        state["track_dirs"] = list(state.get("track_dirs", [])) if isinstance(state.get("track_dirs", []), list) else []
    except Exception:
        state["track_dirs"] = []
    try:
        state["current_index"] = max(0, int(state.get("current_index", 0) or 0))
    except Exception:
        state["current_index"] = 0
    state["last_error"] = f"queue_state_repaired"
    return state
