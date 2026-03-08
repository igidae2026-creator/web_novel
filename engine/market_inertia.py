
from __future__ import annotations
import random
from engine.event_log import log_event
from engine.model_config import load_models, get_model

def inertia_adjust(cfg: dict, state: dict, knobs: dict) -> dict:
    models = load_models(cfg)
    cm = get_model(cfg, models, "competition")
    inertia = cm.get("inertia", {})
    platform_hold_strength = inertia.get('platform_hold_strength', {})
    genre_hold_strength = inertia.get('genre_hold_strength', {})
    plat = cfg.get('project', {}).get('platform')
    bucket = cfg.get('project', {}).get('genre_bucket')
    hold = float(platform_hold_strength.get(plat, 0.7)) * float(genre_hold_strength.get(bucket, 1.0))
    
    platform_factor = inertia.get('platform_factor', {})
    plat = cfg.get('project', {}).get('platform')
    pf = float(platform_factor.get(plat, 1.0))

    

    # if top% improving quickly -> risk rebound -> damp boosts
    hist = state.get("top_percent_hist", [])
    if len(hist) >= 3:
        jump = hist[-3] - hist[-1]  # improvement
        jump_base = float(inertia.get('rebound_jump_base', 1.5))
        if jump > (jump_base/pf) and random.random() < rebound:
            knobs['hook_intensity'] *= float(inertia.get('rebound_damp_hook', 0.9))
            knobs['payoff_intensity'] *= float(inertia.get('rebound_damp_payoff', 0.9))
            state["rebound_flag"] = True
            try:
                log_event(state.get('out_dir','.'), 'rebound_damp', {'jump': jump, 'pf': pf}, safe_mode=True)
            except Exception:
                pass
        else:
            state["rebound_flag"] = False

    # holding effect: if already top3/top5 then stabilize by reducing novelty swing
    if state.get("market_mode") == "ATTACK_TOP3":
        pass
    else:
        knobs['novelty_boost'] *= (1.0 - 0.2 * hold)

    return knobs
