from __future__ import annotations
import os, json, time
from typing import Dict, Any
from engine.integrated_validator import run_all
from engine.safe_io import safe_write_text
from engine.queue_sanity import repair_queue_state, validate_queue_state

REPORT_PATH = os.path.join("data", "validation_last.json")
LOCK_PATH = os.path.join("domains","webnovel","tracks",".queue_lock")
QUEUE_STATE_PATH = os.path.join("domains","webnovel","tracks","queue_state.json")

def _ensure_dirs():
    os.makedirs("data", exist_ok=True)
    os.makedirs(os.path.join("domains","webnovel","tracks"), exist_ok=True)

def _clear_stale_lock(ttl_seconds: int = 600) -> bool:
    if not os.path.exists(LOCK_PATH):
        return False
    try:
        ts = float(open(LOCK_PATH,"r",encoding="utf-8").read().strip() or 0)
        if time.time() - ts > ttl_seconds:
            os.remove(LOCK_PATH)
            return True
    except Exception:
        return False
    return False

def _repair_queue_state() -> bool:
    if not os.path.exists(QUEUE_STATE_PATH):
        return False
    try:
        state = json.load(open(QUEUE_STATE_PATH,"r",encoding="utf-8"))
    except Exception:
        return False
    ok,_ = validate_queue_state(state)
    if ok:
        return False
    fixed = repair_queue_state(state)
    safe_write_text(QUEUE_STATE_PATH, json.dumps(fixed, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup=os.path.dirname(QUEUE_STATE_PATH))
    return True

def auto_validate(max_rounds: int = 3) -> Dict[str, Any]:
    _ensure_dirs()
    healed = {"stale_lock_cleared": False, "queue_state_repaired": False}
    rep = run_all(".")
    round_i = 0
    while (not rep.get("ok")) and round_i < max_rounds:
        round_i += 1
        changed = False
        if _clear_stale_lock():
            healed["stale_lock_cleared"] = True
            changed = True
        if _repair_queue_state():
            healed["queue_state_repaired"] = True
            changed = True
        rep = run_all(".")
        if rep.get("ok"):
            break
        if not changed:
            break
    rep["auto_heal"] = healed
    rep["rounds"] = round_i + 1
    safe_write_text(REPORT_PATH, json.dumps(rep, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup="data")
    return rep
