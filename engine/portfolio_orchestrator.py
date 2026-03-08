from __future__ import annotations
import os, json
from typing import Dict, Any, List
from engine.safe_io import safe_write_text
from engine.event_log import log_event
from engine.track_loader import list_track_dirs
from engine.cannibalization_scheduler import schedule_boost_assignments, record_boost_history

def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def rebalance_platform(cfg: dict, tracks_root: str) -> Dict[str, Any]:
    # build track descriptors
    tdirs = list_track_dirs(tracks_root)
    tracks: List[Dict[str, Any]] = []
    for td in tdirs:
        tj_path = os.path.join(td, "track.json")
        tj = _load_json(tj_path)
        plat = tj.get("project", {}).get("platform", "UNKNOWN")
        bucket = tj.get("project", {}).get("genre_bucket", "UNKNOWN")
        # grade
        gs_path = os.path.join(td, "outputs", "grade_state.json")
        grade = _load_json(gs_path).get("grade", "D") if os.path.exists(gs_path) else "D"
        # latest top percent
        latest_tp = 999.0
        cert_path = os.path.join(td, "outputs", "certification_report.json")
        if os.path.exists(cert_path):
            cr = _load_json(cert_path)
            stats = (cr.get("market", {}) or {}).get("stats", {}) or {}
            try:
                latest_tp = float(stats.get("latest_top_percent", latest_tp) or latest_tp)
            except Exception:
                pass
        tracks.append({
            "dir": td,
            "platform": plat,
            "bucket": bucket,
            "grade": grade,
            "latest_top_percent": latest_tp,
        })

    assigned = schedule_boost_assignments(cfg, tracks)

    # write back
    results: Dict[str, Dict[str, int]] = {}
    for t in assigned:
        td = t["dir"]
        tj_path = os.path.join(td, "track.json")
        tj = _load_json(tj_path)
        prev = str(tj.get("phase", "STABILIZE")).upper()
        tj["phase"] = t["assigned_phase"]
        safe_write_text(
            tj_path,
            json.dumps(tj, ensure_ascii=False, indent=2),
            safe_mode=bool(cfg.get("safe_mode", False)),
            project_dir_for_backup=td,
        )
        record_boost_history(td, t["assigned_phase"], safe_mode=bool(cfg.get("safe_mode", False)))
        if prev != t["assigned_phase"]:
            try:
                log_event(os.path.join(td, "outputs"), "portfolio_rebalance",
                          {"platform": t["platform"], "bucket": t["bucket"], "grade": t["grade"], "from": prev, "to": t["assigned_phase"]},
                          safe_mode=bool(cfg.get("safe_mode", False)))
            except Exception:
                pass
        plat = t["platform"]
        results.setdefault(plat, {"total": 0, "boost_assigned": 0})
        results[plat]["total"] += 1
        if t["assigned_phase"] == "BOOST":
            results[plat]["boost_assigned"] += 1

    return {"ok": True, "platforms": results, "assigned_count": len(assigned)}
