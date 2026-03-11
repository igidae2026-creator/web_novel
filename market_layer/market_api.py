from __future__ import annotations
from typing import Dict
from .rank_guard import compute_stats, market_band, market_top3_achieved
from engine.model_config import load_models, get_model

def compute_market_view(cfg: dict, rank_signals_csv: str, platform: str, bucket: str) -> Dict:
    models = load_models(cfg)
    mm = get_model(cfg, models, 'market')
    market_cfg = (mm if isinstance(mm, dict) else {})
    # cfg.market (if provided) overrides yaml
    if isinstance(cfg.get('market'), dict):
        market_cfg = {**market_cfg, **cfg.get('market')}

    policy = str(market_cfg.get("out_of_chart_policy", market_cfg.get('out_of_chart_policy', 'HOLD_LAST')))
    window = int(market_cfg.get('certification', {}).get('window_days', market_cfg.get('window_days', 7)))
    stats = compute_stats(rank_signals_csv, platform, bucket, window=window, out_of_chart_policy=policy)
    bands_cfg = (market_cfg.get('bands', {}) if isinstance(market_cfg.get('bands', {}), dict) else {})
    max_std = float(market_cfg.get('certification', {}).get('max_std_top_percent', 1.2))
    return {
        "stats": stats,
        "band": market_band(stats, bands=bands_cfg),
        "top3": market_top3_achieved(stats, bands=bands_cfg, max_std=max_std),
    }
