from __future__ import annotations
import os
from typing import Dict, Any
import yaml

def _load_yaml(path: str) -> Dict[str, Any]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def load_models(cfg: Dict[str, Any]) -> Dict[str, Any]:
    files = cfg.get("model_files", {}) if isinstance(cfg.get("model_files"), dict) else {}
    models = {
        "market": _load_yaml(files.get("market","")),
        "grading": _load_yaml(files.get("grading","")),
        "portfolio": _load_yaml(files.get("portfolio","")),
        "competition": _load_yaml(files.get("competition","")),
    }
    return models

def get_model(cfg: Dict[str, Any], models: Dict[str, Any], key: str) -> Dict[str, Any]:
    # cfg overrides yaml if present (for quick experiments)
    if isinstance(cfg.get(key), dict):
        base = dict(models.get(key, {}) or {})
        base.update(cfg.get(key, {}) or {})
        return base
    return models.get(key, {}) or {}
