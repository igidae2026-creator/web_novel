from __future__ import annotations
import os, json, time
from typing import Dict, Any, Tuple
from engine.safe_guard import require_safe_mode
from engine.safe_io import safe_write_text
from engine.track_queue import load_queue_state, save_queue_state
from engine.track_runner import run_queue_step
from engine.portfolio_orchestrator import rebalance_platform
from engine.cross_track_release import refresh_queue_release_runtime

LOCK_PATH = os.path.join("domains","webnovel","tracks",".queue_lock")
LOCK_TTL_SECONDS = 600  # 10 minutes
HISTORY_PATH = os.path.join("domains","webnovel","tracks","queue_history.json")

def _lock_acquire() -> bool:
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
    if os.path.exists(LOCK_PATH):
        try:
            # stale lock recovery
            age = time.time() - float(open(LOCK_PATH,'r',encoding='utf-8').read().strip() or 0)
            if age > LOCK_TTL_SECONDS:
                os.remove(LOCK_PATH)
            else:
                return False
        except Exception:
            return False
    safe_write_text(LOCK_PATH, str(time.time()), safe_mode=True, project_dir_for_backup=os.path.dirname(LOCK_PATH))
    return True

def _lock_release():
    try:
        if os.path.exists(LOCK_PATH):
            os.remove(LOCK_PATH)
    except Exception:
        pass

def _load_history() -> Dict[str, Any]:
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"total_steps": 0, "ok_steps": 0, "error_steps": 0, "last_msg": None, "last_ts": None}

def _save_history(h: Dict[str, Any]):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    safe_write_text(HISTORY_PATH, json.dumps(h, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup=os.path.dirname(HISTORY_PATH))

def run_queue_loop(cfg: Dict[str, Any], max_steps: int = 1) -> Tuple[bool, str]:
    require_safe_mode(cfg)
    if not _lock_acquire():
        return False, "Queue loop already running (lock present)."
    try:
        h = _load_history()
        msg_last = None
        ok_any = False
        for _ in range(max(1, int(max_steps))):
            q = load_queue_state()
            if q.get("status") != "running":
                msg_last = f"Queue not running (status={q.get('status')})"
                break
            q = refresh_queue_release_runtime(q, os.path.join("domains", "webnovel", "tracks"))
            save_queue_state(q)
            ok, msg = run_queue_step(cfg)
            msg_last = msg
            h["total_steps"] += 1
            h["last_msg"] = msg
            h["last_ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
            if ok:
                h["ok_steps"] += 1
                ok_any = True
            else:
                h["error_steps"] += 1
                break
        _save_history(h)
                # After loop steps, auto-rebalance portfolio
        try:
            rebalance_platform(cfg, os.path.join('domains','webnovel','tracks'))
        except Exception:
            pass
        return ok_any, (msg_last or "done")
    finally:
        _lock_release()
