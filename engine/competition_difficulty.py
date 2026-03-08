
from __future__ import annotations
from engine.model_config import load_models, get_model

def difficulty_factor(cfg: dict) -> float:
    models = load_models(cfg)
    cm = get_model(cfg, models, "competition")
    diff = cm.get("difficulty", {})

    plat = cfg.get("project", {}).get("platform")
    bucket = cfg.get("project", {}).get("genre_bucket")

    p = diff.get("platform", {}).get(plat, 1.0)
    g = diff.get("genre_bucket", {}).get(bucket, 1.0)

    return float(p) * float(g)
