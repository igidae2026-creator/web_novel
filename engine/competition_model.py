from __future__ import annotations
from typing import Dict, Any
from engine.model_config import load_models, get_model
from engine.event_log import log_event

def update_competition_state(state: Dict[str, Any], latest_top_percent: float | None) -> Dict[str, Any]:
    # track recent top% for fat-tail detection
    hist = state.get("top_percent_hist", [])
    if latest_top_percent is not None:
        try:
            hist.append(float(latest_top_percent))
        except Exception:
            pass
    if len(hist) > 10:
        hist = hist[-10:]
    state["top_percent_hist"] = hist
    # load thresholds once per run if cfg supplied via state
    try:
        cfg = state.get('_cfg_for_models')
        if cfg:
            models = load_models(cfg)
            cm = get_model(cfg, models, 'competition')
            state['fat_tail_jump_threshold'] = float(cm.get('fat_tail_jump_threshold', 2.0))
            state['fat_tail_damp_factor'] = float(cm.get('fat_tail_damp_factor', 0.90))
            state['boost_streak_limit'] = int(cm.get('boost_streak_limit', 3))
            state['force_stabilize_cooldown'] = int(cm.get('force_stabilize_cooldown', 3))
    except Exception:
        pass
    return state

def fat_tail_flag(state: Dict[str, Any]) -> bool:
    hist = state.get("top_percent_hist", [])
    if len(hist) < 3:
        return False
    # if improvement jump too large (e.g., 2%+ within 2 steps), treat as fat-tail spike (risk of rebound)
    a, b, c = hist[-3], hist[-2], hist[-1]
    # smaller is better: improvement means decrease
    jump = (a - c)
    return jump >= float(state.get('fat_tail_jump_threshold', 2.0))

def update_boost_streak(state: Dict[str, Any], phase: str) -> int:
    streak = int(state.get("boost_streak", 0) or 0)
    if str(phase).upper() == "BOOST":
        streak += 1
    else:
        streak = 0
    state["boost_streak"] = streak
    return streak

def apply_competition_safety(cfg: Dict[str, Any], state: Dict[str, Any], knobs: Dict[str, Any]) -> Dict[str, Any]:
    # 1) Fat-tail spike dampening: reduce boost intensity if spike detected
    if fat_tail_flag(state):
        knobs["hook_intensity"] = float(knobs.get("hook_intensity", 0.7)) * float(state.get('fat_tail_damp_factor', 0.90))
        knobs["payoff_intensity"] = float(knobs.get("payoff_intensity", 0.7)) * float(state.get('fat_tail_damp_factor', 0.90))
        knobs["compression"] = float(knobs.get("compression", 0.6)) * 0.92
        state["fat_tail_flag"] = True
        try:
            log_event(state.get('out_dir','.'), 'fat_tail_damp', {'reason':'spike_detected'}, safe_mode=True)
        except Exception:
            pass
    else:
        state["fat_tail_flag"] = False

    # 2) BOOST streak fatigue: after 3 consecutive boosts, enforce stabilize for next run via pending_phase
    streak = int(state.get("boost_streak", 0) or 0)
    if streak >= int(state.get('boost_streak_limit', 3)):
        state["pending_phase"] = "STABILIZE"
        state["boost_streak"] = 0
        state["competition_fatigue_triggered"] = True
        try:
            log_event(state.get('out_dir','.'), 'boost_fatigue', {'action':'force_stabilize'}, safe_mode=True)
        except Exception:
            pass
    else:
        state["competition_fatigue_triggered"] = False

    return knobs
