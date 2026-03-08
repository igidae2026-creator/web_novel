from __future__ import annotations
from datetime import datetime
from typing import Dict, Any
from engine.model_config import load_models, get_model

PROMOTE = {"A": 3.0, "B": 5.0, "C": 10.0}  # fallback
DEMOTE  = {"A": 3.5, "B": 6.0, "C": 12.0}  # fallback
COOLDOWN_DAYS_DEFAULT = 7

def compute_grade(latest_top_percent: float) -> str:
    p = float(latest_top_percent)
    if p <= 3.0: return "A"
    if p <= 5.0: return "B"
    if p <= 10.0: return "C"
    return "D"

def maybe_update_grade(state: Dict[str, Any], latest_top_percent: float, today_ymd: str, cooldown_days: int = COOLDOWN_DAYS_DEFAULT, cfg: Dict[str, Any] | None = None) -> str:
    cur = state.get("grade", "D")
    if cfg is not None:
        models = load_models(cfg)
        gm = get_model(cfg, models, 'grading')
        prom = (gm.get('promote', {}) if isinstance(gm.get('promote'), dict) else {})
        dem = (gm.get('demote', {}) if isinstance(gm.get('demote'), dict) else {})
        try:
            PROMOTE.update({k: float(v) for k,v in prom.items()})
            DEMOTE.update({k: float(v) for k,v in dem.items()})
            cooldown_days = int(gm.get('cooldown_days', cooldown_days))
        except Exception:
            pass
    cd = int(state.get("grade_cooldown_days", 0) or 0)
    last = state.get("grade_last_change_ymd")
    if cd > 0 and last:
        try:
            d_last = datetime.strptime(last, "%Y-%m-%d").date()
            d_today = datetime.strptime(today_ymd, "%Y-%m-%d").date()
            diff = (d_today - d_last).days
            if diff <= 0:
                return cur
            state["grade_cooldown_days"] = max(0, cd - diff)
            if state["grade_cooldown_days"] > 0:
                return cur
        except Exception:
            state["grade_cooldown_days"] = max(0, cd - 1)
            if state["grade_cooldown_days"] > 0:
                return cur

    desired = compute_grade(latest_top_percent)
    order = ["D","C","B","A"]
    p = float(latest_top_percent)

    if order.index(desired) > order.index(cur):
        # promotion
        if desired == "A" and p <= PROMOTE["A"]:
            cur = "A"
        elif desired == "B" and p <= PROMOTE["B"]:
            cur = "B"
        elif desired == "C" and p <= PROMOTE["C"]:
            cur = "C"
    elif order.index(desired) < order.index(cur):
        # demotion
        if cur == "A" and p > DEMOTE["A"]:
            cur = desired
        elif cur == "B" and p > DEMOTE["B"]:
            cur = desired
        elif cur == "C" and p > DEMOTE["C"]:
            cur = desired

    if cur != state.get("grade", "D"):
        state["grade"] = cur
        state["grade_last_change_ymd"] = today_ymd
        state["grade_cooldown_days"] = cooldown_days
        state.setdefault("grade_events", []).append({"date": today_ymd, "grade": cur, "top_percent": p})
    return cur