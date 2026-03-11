from __future__ import annotations
from typing import Dict, Tuple

DEFAULT_THRESHOLD = 0.60
DEFAULT_STREAK = 3
DEFAULT_COOLDOWN = 5

def update_decline_streak(state: Dict, score_obj: Dict) -> int:
    # Track consecutive declines in hook_score (or fitness if absent)
    prev = state.get("prev_hook_score")
    cur = float(score_obj.get("hook_score", score_obj.get("hook", 0.0)) or 0.0)
    streak = int(state.get("decline_streak", 0) or 0)

    if prev is None:
        streak = 0
    else:
        if cur < float(prev):
            streak += 1
        else:
            streak = 0

    state["prev_hook_score"] = cur
    state["decline_streak"] = streak
    return streak

def can_rebuild(state: Dict) -> bool:
    cd = int(state.get("rebuild_cooldown", 0) or 0)
    return cd <= 0

def tick_cooldowns(state: Dict):
    cd = int(state.get("rebuild_cooldown", 0) or 0)
    if cd > 0:
        state["rebuild_cooldown"] = cd - 1

def maybe_trigger_rebuild(
    cfg: Dict,
    state: Dict,
    score_obj: Dict,
) -> Tuple[bool, str]:
    threshold = float(cfg.get("rebuild", {}).get("hook_threshold", DEFAULT_THRESHOLD))
    need_streak = int(cfg.get("rebuild", {}).get("decline_streak", DEFAULT_STREAK))
    streak = int(state.get("decline_streak", 0) or 0)
    hook = float(score_obj.get("hook_score", score_obj.get("hook", 0.0)) or 0.0)

    if not can_rebuild(state):
        return False, "cooldown"

    if hook < threshold and streak >= need_streak:
        # arm cooldown
        state["rebuild_cooldown"] = int(cfg.get("rebuild", {}).get("cooldown", DEFAULT_COOLDOWN))
        level = int(state.get("rebuild_level", 0) or 0)
        level = min(3, level + 1)
        state["rebuild_level"] = level
        return True, f"hook<{threshold} streak={streak} level={level}"
    return False, "no_trigger"

def apply_rebuild(knobs: Dict, level: int) -> Dict:
    # staged rebuild: gentle -> stronger
    if level <= 1:
        knobs["compression"] = min(0.90, float(knobs.get("compression", 0.6)) + 0.03)
        knobs["hook_intensity"] = min(0.95, float(knobs.get("hook_intensity", 0.7)) + 0.03)
    elif level == 2:
        knobs["payoff_intensity"] = min(0.96, float(knobs.get("payoff_intensity", 0.7)) + 0.04)
        knobs["novelty_boost"] = min(0.90, float(knobs.get("novelty_boost", 0.5)) + 0.04)
    else:
        knobs["hook_intensity"] = min(0.97, float(knobs.get("hook_intensity", 0.7)) + 0.05)
        knobs["payoff_intensity"] = min(0.97, float(knobs.get("payoff_intensity", 0.7)) + 0.05)
        knobs["compression"] = min(0.92, float(knobs.get("compression", 0.6)) + 0.05)
        knobs["novelty_boost"] = min(0.92, float(knobs.get("novelty_boost", 0.5)) + 0.05)
    return knobs
