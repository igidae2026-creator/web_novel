from __future__ import annotations
import os, yaml, datetime, shutil
from typing import Dict, Any, Tuple
from engine.safe_io import safe_write_text

CALIBRATION_FILE = "config/models/calibration_input.yaml"
HISTORY_DIR = "config/models/calibration_history"

MODEL_FILES = {
    "market": "config/models/market_model.yaml",
    "grading": "config/models/grading_model.yaml",
    "portfolio": "config/models/portfolio_model.yaml",
    "competition": "config/models/competition_model.yaml",
}

def load_yaml(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    return yaml.safe_load(open(path,"r",encoding="utf-8")) or {}

def save_yaml(path: str, data: dict):
    safe_write_text(path, yaml.safe_dump(data, allow_unicode=True), safe_mode=True)

def snapshot_calibration(tag: str = "cal") -> str:
    os.makedirs(HISTORY_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(HISTORY_DIR, f"{ts}_{tag}.yaml")
    if os.path.exists(CALIBRATION_FILE):
        shutil.copy2(CALIBRATION_FILE, dest)
    return dest

def list_snapshots() -> list[str]:
    if not os.path.exists(HISTORY_DIR):
        return []
    return sorted([os.path.basename(p) for p in glob.glob(os.path.join(HISTORY_DIR, "*.yaml"))])

def diff_yaml(before: dict, after: dict) -> str:
    b = yaml.safe_dump(before, allow_unicode=True).splitlines()
    a = yaml.safe_dump(after, allow_unicode=True).splitlines()
    import difflib
    return "\n".join(difflib.unified_diff(b, a, fromfile="before", tofile="after", lineterm=""))

def deep_merge(dst: dict, src: dict) -> dict:
    for k,v in (src or {}).items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst

def apply_calibration(calib: dict) -> Dict[str, str]:
    """Apply calibration sections to corresponding model yamls. Returns diff per model key."""
    diffs = {}
    for key, path in MODEL_FILES.items():
        before = load_yaml(path)
        after = dict(before) if isinstance(before, dict) else {}
        section = calib.get(key, {})
        if isinstance(section, dict) and section:
            deep_merge(after, section)
            save_yaml(path, after)
            diffs[key] = diff_yaml(before, after)
        else:
            diffs[key] = ""
    return diffs

def rollback_from_snapshot(snapshot_filename: str) -> Tuple[bool, str]:
    path = os.path.join(HISTORY_DIR, snapshot_filename)
    if not os.path.exists(path):
        return False, "snapshot not found"
    # rollback means: replace calibration_input.yaml with snapshot and re-apply
    shutil.copy2(path, CALIBRATION_FILE)
    calib = load_yaml(CALIBRATION_FILE)
    apply_calibration(calib)
    return True, "rolled back and re-applied"
