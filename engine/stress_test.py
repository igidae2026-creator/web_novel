from __future__ import annotations
import os, json, time, random
from typing import Dict, Any, Tuple
from engine.safe_guard import require_safe_mode
from engine.track_queue import load_queue_state, start_queue, advance, save_queue_state

def run_stress_test(cfg: Dict[str, Any], steps: int = 100) -> Dict[str, Any]:
    require_safe_mode(cfg)
    q = load_queue_state()
    if q.get("status") != "running":
        q = start_queue(cfg=cfg)
    ok = 0
    err = 0
    start = time.time()
    for i in range(int(steps)):
        # randomly simulate an error at low rate
        if random.random() < 0.01:
            err += 1
            q["status"] = "paused"
            q["last_error"] = "simulated_error"
            save_queue_state(q)
            break
        ok += 1
        advance(q)
        if q.get("status") == "done":
            break
    dur = time.time() - start
    return {"steps_requested": int(steps), "ok_steps": ok, "error_steps": err, "duration_sec": round(dur, 4), "queue_status": q.get("status")}
