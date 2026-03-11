from __future__ import annotations
import os, yaml
from typing import Dict, Any
from engine.model_config import load_models, get_model
from market_layer.market_api import compute_market_view
from engine.event_log import log_event

def decide_market_mode(cfg: dict) -> str:
    models = load_models(cfg)
    mp = models.get("market_policy", {})
    if not mp:
        return "ATTACK_TOP3"

    # fetch current market status
    platform = cfg["project"]["platform"]
    bucket = cfg["project"]["genre_bucket"]
    rank_csv = cfg.get("external", {}).get("rank_signals_csv", "data/rank_signals.csv")
    mv = compute_market_view(cfg, rank_csv, platform, bucket)
    stats = mv.get("stats", {}) if mv else {}
    band = mv.get("band")
    std = float(stats.get("std_top_percent", 0.0) or 0.0)

    rules = mp.get("switch_rules", {})
    if std > float(rules.get("to_defend_if_std_above", 1.5)):
        return "DEFEND_TOP10"
    if band not in ["TOP3","TOP5","TOP10"]:
        return "DEFEND_TOP10"
    if band in ["TOP3","TOP5"]:
        return "ATTACK_TOP3"
    return "DEFEND_TOP10"

def apply_market_policy(cfg: dict, state: dict):
    mode = decide_market_mode(cfg)
    prev_mode = state.get('market_mode')
    state["market_mode"] = mode
    if prev_mode and prev_mode != mode:
        try:
            log_event(state.get('out_dir','.'), 'market_mode_changed', {'from': prev_mode, 'to': mode}, safe_mode=True)
        except Exception:
            pass
    # boost allowed / not allowed
    models = load_models(cfg)
    mp = models.get("market_policy", {})
    mcfg = mp.get("modes", {}).get(mode, {})
    state["boost_allowed"] = bool(mcfg.get("boost_allowed", True))
    return state
