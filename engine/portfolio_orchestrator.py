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


def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return rows
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return rows


def _track_log_snapshot(track_dir: str, last_n: int = 8) -> Dict[str, Any]:
    rows = _load_jsonl(os.path.join(track_dir, "outputs", "metrics.jsonl"))[-last_n:]
    if not rows:
        return {
            "mean_ceiling": 0.0,
            "mean_retention": 0.0,
            "fatigue_score": 0.0,
            "event_crowding": 0,
            "hidden_reader_risk": 0.0,
            "portfolio_score": 0.0,
        }
    retention = [float((row.get("retention", {}) or {}).get("predicted_next_episode", 0.0) or 0.0) for row in rows]
    ceiling = [float((row.get("content_ceiling", {}) or {}).get("ceiling_total", 0.0) or 0.0) for row in rows]
    repetition = [float((row.get("scores", {}) or {}).get("repetition_score", 0.0) or 0.0) for row in rows]
    events = [str((row.get("meta", {}) or {}).get("event_plan", {}).get("type", "")).strip() for row in rows]
    events = [event for event in events if event]
    event_crowding = max((events.count(event) for event in set(events)), default=0)
    mean_ceiling = sum(ceiling) / len(ceiling)
    mean_retention = sum(retention) / len(retention)
    fatigue_score = sum(repetition) / len(repetition) if repetition else 0.0
    hidden_reader_risk = 0.0
    threshold_path = os.path.join(track_dir, "outputs", "final_threshold_eval.json")
    threshold_payload = _load_json(threshold_path) if os.path.exists(threshold_path) else {}
    criteria = dict((threshold_payload or {}).get("criteria", {}) or {})
    for criterion_name in ("reader_retention_stability", "serialization_fatigue_control"):
        details = dict((criteria.get(criterion_name) or {}).get("details", {}) or {})
        debt = dict(details.get("reader_quality_debt") or {})
        for key in ("thinness_debt", "repetition_debt", "deja_vu_debt", "fake_urgency_debt", "compression_debt"):
            try:
                hidden_reader_risk += float(debt.get(key, 0.0) or 0.0)
            except Exception:
                continue
    portfolio_score = (
        mean_retention * 0.45
        + (mean_ceiling / 100.0) * 0.40
        + max(0.0, 1.0 - fatigue_score) * 0.15
        - min(0.18, hidden_reader_risk * 0.12)
    )
    return {
        "mean_ceiling": mean_ceiling,
        "mean_retention": mean_retention,
        "fatigue_score": fatigue_score,
        "event_crowding": event_crowding,
        "hidden_reader_risk": round(hidden_reader_risk, 4),
        "portfolio_score": portfolio_score,
    }


def build_portfolio_runtime_snapshot(tracks_root: str, last_n: int = 8) -> Dict[str, Any]:
    tracks: List[Dict[str, Any]] = []
    for td in list_track_dirs(tracks_root):
        track = _load_json(os.path.join(td, "track.json"))
        log_snapshot = _track_log_snapshot(td, last_n=last_n)
        tracks.append(
            {
                "track": os.path.basename(td),
                "platform": (track.get("project", {}) or {}).get("platform", "UNKNOWN"),
                "bucket": (track.get("project", {}) or {}).get("genre_bucket", "UNKNOWN"),
                **log_snapshot,
            }
        )
    if not tracks:
        return {"tracks": [], "boost_ready_tracks": 0, "stable_tracks": 0, "mean_portfolio_score": 0.0}
    boost_ready = sum(1 for track in tracks if track["portfolio_score"] >= 0.68 and track["fatigue_score"] < 0.24 and track.get("hidden_reader_risk", 0.0) < 0.35)
    stable = sum(1 for track in tracks if track["fatigue_score"] < 0.18 and track["event_crowding"] <= 3 and track.get("hidden_reader_risk", 0.0) < 0.3)
    mean_score = sum(float(track["portfolio_score"]) for track in tracks) / len(tracks)
    return {
        "tracks": tracks,
        "boost_ready_tracks": boost_ready,
        "stable_tracks": stable,
        "mean_portfolio_score": round(mean_score, 4),
    }

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
        log_snapshot = _track_log_snapshot(td)
        tracks.append({
            "dir": td,
            "platform": plat,
            "bucket": bucket,
            "grade": grade,
            "latest_top_percent": latest_tp,
            "mean_ceiling": log_snapshot["mean_ceiling"],
            "mean_retention": log_snapshot["mean_retention"],
            "fatigue_score": log_snapshot["fatigue_score"],
            "event_crowding": log_snapshot["event_crowding"],
            "portfolio_score": log_snapshot["portfolio_score"],
        })

    assigned = schedule_boost_assignments(cfg, tracks)

    # write back
    results: Dict[str, Dict[str, Any]] = {}
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
        results.setdefault(plat, {"total": 0, "boost_assigned": 0, "mean_portfolio_score": 0.0})
        results[plat]["total"] += 1
        results[plat]["mean_portfolio_score"] += float(t.get("portfolio_score", 0.0) or 0.0)
        if t["assigned_phase"] == "BOOST":
            results[plat]["boost_assigned"] += 1
    for plat, payload in results.items():
        total = max(1, int(payload.get("total", 0) or 0))
        payload["mean_portfolio_score"] = round(float(payload.get("mean_portfolio_score", 0.0) or 0.0) / total, 4)

    return {"ok": True, "platforms": results, "assigned_count": len(assigned)}
