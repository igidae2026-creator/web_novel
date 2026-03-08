from __future__ import annotations
import os, json
from datetime import datetime
from typing import Dict, Any, List, Tuple
from engine.safe_io import safe_write_text

def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def _load_json(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_json(path: str, obj: dict, safe_mode: bool, backup_dir: str):
    safe_write_text(path, json.dumps(obj, ensure_ascii=False, indent=2), safe_mode=safe_mode, project_dir_for_backup=backup_dir)

def _grade_rank(g: str) -> int:
    g = (g or "D").upper()
    return {"A":0,"B":1,"C":2,"D":3}.get(g, 3)

def schedule_boost_assignments(cfg: dict, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    port = cfg.get("portfolio", {}) if isinstance(cfg.get("portfolio"), dict) else {}
    rotation_cfg = port.get('rotation', {}) if isinstance(port.get('rotation', {}), dict) else {}
    max_per_platform = int(port.get("max_boost_per_platform", 1) or 1)
    max_per_platform_bucket = int(port.get("max_boost_per_platform_bucket", 1) or 1)

    for t in tracks:
        bh_path = os.path.join(t["dir"], "outputs", "boost_history.json")
        bh = _load_json(bh_path)
        t["last_boost_date"] = bh.get("last_boost_date") or "0000-00-00"
        t["boost_count"] = int(bh.get("boost_count", 0) or 0)

    # Sort candidates: grade, top_percent, least recently boosted, least boosted count
    
    # rotation configuration
    min_days = int(rotation_cfg.get("min_days_between_boost", 0) or 0)

    def _eligible(t):
        if not min_days:
            return True
        last = t.get("last_boost_date")
        if not last or last == "0000-00-00":
            return True
        try:
            d0 = datetime.strptime(last, "%Y-%m-%d").date()
            d1 = datetime.now().date()
            return (d1 - d0).days >= min_days
        except:
            return True

    tracks = [t for t in tracks if _eligible(t)]
    candidates = sorted(

        tracks,
        key=lambda x: (
            _grade_rank(x.get("grade","D")),
            float(x.get("latest_top_percent", 999.0)),
            -float(x.get("portfolio_score", 0.0) or 0.0),
            float(x.get("fatigue_score", 999.0) or 999.0),
            x.get("last_boost_date"),
            int(x.get("boost_count", 0)),
        )
    )

    selected=set()
    plat_counts={}
    pb_counts={}

    for t in candidates:
        g=(t.get("grade","D") or "D").upper()
        if g not in ["A","B"]:
            continue
        plat=t.get("platform","")
        bucket=t.get("bucket","")
        if plat_counts.get(plat,0) >= max_per_platform:
            continue
        if pb_counts.get((plat,bucket),0) >= max_per_platform_bucket:
            continue
        if float(t.get("fatigue_score", 0.0) or 0.0) >= 0.24:
            continue
        selected.add(id(t))
        plat_counts[plat]=plat_counts.get(plat,0)+1
        pb_counts[(plat,bucket)]=pb_counts.get((plat,bucket),0)+1

    out=[]
    for t in tracks:
        y=dict(t)
        y["assigned_phase"]="BOOST" if id(t) in selected else "STABILIZE"
        out.append(y)
    return out

def record_boost_history(track_dir: str, assigned_phase: str, safe_mode: bool):
    out_dir=os.path.join(track_dir,"outputs")
    os.makedirs(out_dir, exist_ok=True)
    path=os.path.join(out_dir,"boost_history.json")
    bh=_load_json(path)
    if assigned_phase=="BOOST":
        bh["last_boost_date"]= _today()
        bh["boost_count"]= int(bh.get("boost_count",0) or 0)+1
    _save_json(path, bh, safe_mode=safe_mode, backup_dir=out_dir)
