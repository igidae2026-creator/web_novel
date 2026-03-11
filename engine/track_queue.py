from __future__ import annotations
import os, json
from engine.safe_io import safe_write_text
from engine.queue_sanity import validate_queue_state, repair_queue_state
from engine.portfolio_guard import enforce_boost_cap_with_priority
from engine.cannibalization_guard import enforce_boost_cap_platform_bucket
from engine.model_config import load_models, get_model
from engine.event_log import log_event
from engine.job_queue import sync_track_queue_to_job_queue
from engine.runtime_supervisor import update_supervisor_from_queue
from typing import Dict, Any, List, Optional
from engine.safe_io import safe_write_text
from engine.queue_sanity import validate_queue_state, repair_queue_state
from engine.portfolio_guard import enforce_boost_cap_with_priority
from engine.cannibalization_guard import enforce_boost_cap_platform_bucket
from engine.model_config import load_models, get_model
from engine.event_log import log_event

QUEUE_STATE_PATH = os.path.join("domains", "webnovel", "tracks", "queue_state.json")
CRITICAL_BUNDLES = {"truth_capability", "recovery_capability"}
CAUTION_BUNDLES = {"judgment_capability", "operations_capability", "generation_capability", "self_evolution_capability"}

def _ensure_dir(p: str):
    os.makedirs(os.path.dirname(p), exist_ok=True)

def load_queue_state(path: str = QUEUE_STATE_PATH) -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
            ok, _ = validate_queue_state(state)
            if not ok:
                state = repair_queue_state(state)
            return state
    return {
        "status": "idle",   # idle|running|paused|done
        "track_dirs": [],
        "current_index": 0,
        "last_error": None,
    }

def save_queue_state(state: Dict[str, Any], path: str = QUEUE_STATE_PATH) -> None:
    _ensure_dir(path)
    safe_write_text(path, json.dumps(state, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup=os.path.dirname(path))


def _sync_runtime_sidecars(state: Dict[str, Any], safe_mode: bool = True) -> None:
    try:
        job_queue_state = sync_track_queue_to_job_queue(state, safe_mode=safe_mode)
        update_supervisor_from_queue(job_queue_state, safe_mode=safe_mode)
    except Exception:
        pass

def _load_failed_bundles(track_dir: str) -> List[str]:
    path = os.path.join(track_dir, "outputs", "final_threshold_eval.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return []
    return list(payload.get("failed_bundles", []) or [])


def _load_failed_criteria(track_dir: str) -> List[str]:
    path = os.path.join(track_dir, "outputs", "final_threshold_eval.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return []
    return list(payload.get("failed_criteria", []) or [])


def _load_hidden_reader_risk(track_dir: str) -> float:
    path = os.path.join(track_dir, "outputs", "final_threshold_eval.json")
    if not os.path.exists(path):
        return 0.0
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return 0.0
    criteria = dict(payload.get("criteria") or {})
    risk_total = 0.0
    for criterion_name in ("reader_retention_stability", "serialization_fatigue_control"):
        details = dict((criteria.get(criterion_name) or {}).get("details") or {})
        debt = dict(details.get("reader_quality_debt") or {})
        for key in ("thinness_debt", "repetition_debt", "deja_vu_debt", "fake_urgency_debt", "compression_debt"):
            try:
                risk_total += float(debt.get(key, 0.0) or 0.0)
            except Exception:
                continue
    return round(risk_total, 4)


def _load_hidden_reader_risk_trend(track_dir: str) -> float:
    path = os.path.join(track_dir, "outputs", "final_threshold_eval.json")
    if not os.path.exists(path):
        return 0.0
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return 0.0
    details = dict((((payload.get("criteria", {}) or {}).get("autonomous_convergence_trend", {}) or {}).get("details", {}) or {}))
    if "hidden_reader_risk_trend" in details:
        return float(details.get("hidden_reader_risk_trend", 0.0) or 0.0)
    return float((payload.get("threshold_history", {}) or {}).get("hidden_reader_risk_trend", 0.0) or 0.0)


def _track_priority_key(track_dir: str) -> tuple:
    bundles = _load_failed_bundles(track_dir)
    criteria = _load_failed_criteria(track_dir)
    hidden_reader_risk = _load_hidden_reader_risk(track_dir)
    hidden_reader_risk_trend = _load_hidden_reader_risk_trend(track_dir)
    critical_count = sum(1 for bundle in bundles if bundle in CRITICAL_BUNDLES)
    caution_count = sum(1 for bundle in bundles if bundle in CAUTION_BUNDLES)
    reader_quality_count = sum(
        1
        for criterion in criteria
        if criterion in {
            "early_hook_strength",
            "episode_end_hook_strength",
            "long_arc_payoff_stability",
            "protagonist_fantasy_persistence",
            "reader_retention_stability",
            "serialization_fatigue_control",
        }
    )
    other_count = max(0, len(bundles) - critical_count - caution_count)
    has_eval = os.path.exists(os.path.join(track_dir, "outputs", "final_threshold_eval.json"))
    hidden_reader_risk_band = 1 if hidden_reader_risk >= 0.45 else 0
    hidden_reader_risk_trend_band = 1 if hidden_reader_risk_trend >= 0.35 else 0
    return (
        -critical_count,
        -caution_count,
        -reader_quality_count,
        -hidden_reader_risk_trend_band,
        -hidden_reader_risk_trend,
        -hidden_reader_risk_band,
        -hidden_reader_risk,
        -other_count,
        0 if has_eval else 1,
        os.path.basename(track_dir),
    )


def build_track_dirs(tracks_root: str = os.path.join("domains","webnovel","tracks")) -> List[str]:
    out=[]
    if not os.path.exists(tracks_root):
        return out
    for d in sorted(os.listdir(tracks_root)):
        p=os.path.join(tracks_root,d)
        if os.path.isdir(p) and os.path.exists(os.path.join(p,"track.json")):
            out.append(p)
    return sorted(out, key=_track_priority_key)

def start_queue(track_dirs: Optional[List[str]] = None, cfg: Optional[dict] = None) -> Dict[str, Any]:
    state = load_queue_state()
    state["track_dirs"] = track_dirs or build_track_dirs()
    state["current_index"] = 0
    state["status"] = "running" if state["track_dirs"] else "done"
    state["last_error"] = None
    save_queue_state(state)
    _sync_runtime_sidecars(state)
        # Enforce BOOST cap safety
    try:
        tracks = []
        for td in state.get('track_dirs', []):
            try:
                tj = json.load(open(os.path.join(td,'track.json'),'r',encoding='utf-8'))
                tracks.append({'dir': td, 'platform': tj.get('project',{}).get('platform'), 'phase': tj.get('phase','STABILIZE')})
            except Exception:
                continue
        capped = enforce_boost_cap(tracks)
        for item in capped:
            if item.get('phase') == 'STABILIZE':
                # write back to track.json if downgraded
                try:
                    tj = json.load(open(os.path.join(item['dir'],'track.json'),'r',encoding='utf-8'))
                    tj['phase'] = 'STABILIZE'
                    open(os.path.join(item['dir'],'track.json'),'w',encoding='utf-8').write(json.dumps(tj,ensure_ascii=False,indent=2))
                except Exception:
                    pass
    except Exception:
        pass
    return state

def pause_queue() -> Dict[str, Any]:
    state = load_queue_state()
    if state.get("status") == "running":
        state["status"] = "paused"
        save_queue_state(state)
        _sync_runtime_sidecars(state)
        # Enforce BOOST cap safety
    try:
        tracks = []
        for td in state.get('track_dirs', []):
            try:
                tj = json.load(open(os.path.join(td,'track.json'),'r',encoding='utf-8'))
                tracks.append({'dir': td, 'platform': tj.get('project',{}).get('platform'), 'phase': tj.get('phase','STABILIZE')})
            except Exception:
                continue
        capped = enforce_boost_cap(tracks)
        for item in capped:
            if item.get('phase') == 'STABILIZE':
                # write back to track.json if downgraded
                try:
                    tj = json.load(open(os.path.join(item['dir'],'track.json'),'r',encoding='utf-8'))
                    tj['phase'] = 'STABILIZE'
                    open(os.path.join(item['dir'],'track.json'),'w',encoding='utf-8').write(json.dumps(tj,ensure_ascii=False,indent=2))
                except Exception:
                    pass
    except Exception:
        pass
    return state

def resume_queue(cfg: Optional[dict] = None) -> Dict[str, Any]:
    state = load_queue_state()
    if state.get("status") == "paused":
        state["status"] = "running"
        save_queue_state(state)
        _sync_runtime_sidecars(state)
        # Enforce BOOST cap safety
    try:
        tracks = []
        for td in state.get('track_dirs', []):
            try:
                tj = json.load(open(os.path.join(td,'track.json'),'r',encoding='utf-8'))
                tracks.append({'dir': td, 'platform': tj.get('project',{}).get('platform'), 'phase': tj.get('phase','STABILIZE')})
            except Exception:
                continue
        capped = enforce_boost_cap(tracks)
        for item in capped:
            if item.get('phase') == 'STABILIZE':
                # write back to track.json if downgraded
                try:
                    tj = json.load(open(os.path.join(item['dir'],'track.json'),'r',encoding='utf-8'))
                    tj['phase'] = 'STABILIZE'
                    open(os.path.join(item['dir'],'track.json'),'w',encoding='utf-8').write(json.dumps(tj,ensure_ascii=False,indent=2))
                except Exception:
                    pass
    except Exception:
        pass
    return state

def mark_done() -> Dict[str, Any]:
    state = load_queue_state()
    state["status"] = "done"
    save_queue_state(state)
    _sync_runtime_sidecars(state)
        # Enforce BOOST cap safety
    try:
        tracks = []
        for td in state.get('track_dirs', []):
            try:
                tj = json.load(open(os.path.join(td,'track.json'),'r',encoding='utf-8'))
                tracks.append({'dir': td, 'platform': tj.get('project',{}).get('platform'), 'phase': tj.get('phase','STABILIZE')})
            except Exception:
                continue
        capped = enforce_boost_cap(tracks)
        for item in capped:
            if item.get('phase') == 'STABILIZE':
                # write back to track.json if downgraded
                try:
                    tj = json.load(open(os.path.join(item['dir'],'track.json'),'r',encoding='utf-8'))
                    tj['phase'] = 'STABILIZE'
                    open(os.path.join(item['dir'],'track.json'),'w',encoding='utf-8').write(json.dumps(tj,ensure_ascii=False,indent=2))
                except Exception:
                    pass
    except Exception:
        pass
    return state

def current_track_dir(state: Dict[str, Any]) -> Optional[str]:
    dirs = state.get("track_dirs", [])
    idx = int(state.get("current_index", 0) or 0)
    if 0 <= idx < len(dirs):
        return dirs[idx]
    return None

def advance(state: Dict[str, Any]) -> Dict[str, Any]:
    idx = int(state.get("current_index", 0) or 0) + 1
    state["current_index"] = idx
    if idx >= len(state.get("track_dirs", [])):
        state["status"] = "done"
    save_queue_state(state)
    _sync_runtime_sidecars(state)
        # Enforce BOOST cap safety
    try:
        tracks = []
        for td in state.get('track_dirs', []):
            try:
                tj = json.load(open(os.path.join(td,'track.json'),'r',encoding='utf-8'))
                tracks.append({'dir': td, 'platform': tj.get('project',{}).get('platform'), 'phase': tj.get('phase','STABILIZE')})
            except Exception:
                continue
        capped = enforce_boost_cap(tracks)
        for item in capped:
            if item.get('phase') == 'STABILIZE':
                # write back to track.json if downgraded
                try:
                    tj = json.load(open(os.path.join(item['dir'],'track.json'),'r',encoding='utf-8'))
                    tj['phase'] = 'STABILIZE'
                    open(os.path.join(item['dir'],'track.json'),'w',encoding='utf-8').write(json.dumps(tj,ensure_ascii=False,indent=2))
                except Exception:
                    pass
    except Exception:
        pass
    return state


def progress_info(state: dict) -> dict:
    total = len(state.get("track_dirs", []))
    idx = int(state.get("current_index", 0) or 0)
    return {
        "total_tracks": total,
        "current_index": idx,
        "remaining": max(0, total - idx),
        "status": state.get("status"),
        "last_error": state.get("last_error"),
    }


def enforce_portfolio_caps(cfg: dict, state: dict) -> dict:
    # Build track list with priority signals
    tracks = []
    for td in state.get("track_dirs", []):
        try:
            tj = json.load(open(os.path.join(td, "track.json"), "r", encoding="utf-8"))
        except Exception:
            continue
        plat = tj.get("project", {}).get("platform", "")
        bucket = tj.get("project", {}).get("genre_bucket", "")
        desired = str(tj.get("phase", "STABILIZE")).upper()
        if desired not in ["BOOST","STABILIZE"]:
            desired = "STABILIZE"
        # grade + latest_top_percent
        grade = None
        latest_tp = 999.0
        gs_path = os.path.join(td, "outputs", "grade_state.json")
        if os.path.exists(gs_path):
            try:
                gs = json.load(open(gs_path, "r", encoding="utf-8"))
                grade = gs.get("grade")
            except Exception:
                pass
        cert_path = os.path.join(td, "outputs", "certification_report.json")
        if os.path.exists(cert_path):
            try:
                cr = json.load(open(cert_path, "r", encoding="utf-8"))
                stats = cr.get("market", {}).get("stats", {})
                latest_tp = float(stats.get("latest_top_percent", latest_tp) or latest_tp)
            except Exception:
                pass
        tracks.append({
            "dir": td,
            "platform": plat,
            "bucket": bucket,
            "desired_phase": desired,
            "grade": grade or "D",
            "latest_top_percent": latest_tp,
            "priority_score": latest_tp,
        })

    models = load_models(cfg)
    pm = get_model(cfg, models, 'portfolio')
    port = pm if isinstance(pm, dict) else {}
    max_boost = int(port.get("max_boost_per_platform", 1) or 1)
    priority = str(port.get("boost_priority", "top_percent"))
    capped = enforce_boost_cap_with_priority(tracks, max_per_platform=max_boost, priority=priority)

    # Write back downgraded phases safely (no direct open write)
    for item in capped:
        if item.get("desired_phase") == "STABILIZE" and item.get("downgraded"):
            try:
                tj = json.load(open(os.path.join(item["dir"], "track.json"), "r", encoding="utf-8"))
                tj["phase"] = "STABILIZE"
                safe_write_text(
                    os.path.join(item["dir"], "track.json"),
                    json.dumps(tj, ensure_ascii=False, indent=2),
                    safe_mode=bool(cfg.get("safe_mode", False)),
                    project_dir_for_backup=item["dir"],
                )
                try:
                    log_event(os.path.join(item['dir'],'outputs'), 'boost_downgraded', {'platform': item.get('platform'), 'bucket': item.get('bucket')}, safe_mode=bool(cfg.get('safe_mode', False)))
                except Exception:
                    pass
            except Exception:
                pass

    return state
