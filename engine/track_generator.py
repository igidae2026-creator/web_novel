from __future__ import annotations
import os, json
from typing import List, Dict
from engine.safe_io import safe_write_text, safe_copy_bytes
from engine.strategy import bootstrap_design_guardrails, pick_bootstrap_subengine

DEFAULT_PLATFORMS = ["Joara","KakaoPage","Munpia","NaverSeries","Ridibooks","Novelpia"]
DEFAULT_BUCKETS = list("ABCDEFGHI")


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _hidden_reader_risk_profile(tracks_dir: str) -> Dict[str, float]:
    profile: Dict[str, list[float]] = {}
    if not os.path.exists(tracks_dir):
        return {}
    for name in os.listdir(tracks_dir):
        track_dir = os.path.join(tracks_dir, name)
        track_json = os.path.join(track_dir, "track.json")
        final_path = os.path.join(track_dir, "outputs", "final_threshold_eval.json")
        if not (os.path.isdir(track_dir) and os.path.exists(track_json) and os.path.exists(final_path)):
            continue
        try:
            track_cfg = json.load(open(track_json, "r", encoding="utf-8"))
            payload = json.load(open(final_path, "r", encoding="utf-8"))
        except Exception:
            continue
        project = dict(track_cfg.get("project", {}) or {})
        key = f"{project.get('platform', 'UNKNOWN')}::{project.get('genre_bucket', 'X')}"
        criteria = dict(payload.get("criteria", {}) or {})
        total = 0.0
        for criterion_name in ("reader_retention_stability", "serialization_fatigue_control"):
            details = dict((criteria.get(criterion_name) or {}).get("details", {}) or {})
            debt = dict(details.get("reader_quality_debt") or {})
            for debt_key in ("thinness_debt", "repetition_debt", "deja_vu_debt", "fake_urgency_debt", "compression_debt"):
                total += _safe_float(debt.get(debt_key), 0.0)
        profile.setdefault(key, []).append(round(total, 4))
    return {key: round(sum(values) / len(values), 4) for key, values in profile.items() if values}

def generate_tracks(root_dir: str, project_name: str, platforms: List[str] = None, buckets: List[str] = None) -> List[Dict]:
    platforms = platforms or DEFAULT_PLATFORMS
    buckets = buckets or DEFAULT_BUCKETS
    tracks_dir = os.path.join(root_dir, "tracks")
    os.makedirs(tracks_dir, exist_ok=True)
    hidden_risk_profile = _hidden_reader_risk_profile(tracks_dir)
    created = []
    for p in platforms:
        for b in buckets:
            track_id = f"{p}_{b}".lower()
            tdir = os.path.join(tracks_dir, track_id)
            os.makedirs(tdir, exist_ok=True)
            profile_key = f"{p}::{b}"
            hidden_reader_risk = _safe_float(hidden_risk_profile.get(profile_key), 0.0)
            bootstrap_sub_engine = pick_bootstrap_subengine(b, hidden_reader_risk).key
            design_guardrails = bootstrap_design_guardrails(hidden_reader_risk)
            # minimal track config
            cfg = {
                "project": {
                    "name": project_name,
                    "platform": p,
                    "genre_bucket": b,
                    "sub_engine": bootstrap_sub_engine,
                    "bootstrap_design_guardrails": design_guardrails,
                    "bootstrap_hidden_reader_risk": round(hidden_reader_risk, 4),
                },
                "track": {"id": track_id},
                "phase": "STABILIZE",
                "bootstrap_strategy": {
                    "hidden_reader_risk": round(hidden_reader_risk, 4),
                    "source_profile_key": profile_key,
                    "selected_sub_engine": bootstrap_sub_engine,
                    "design_guardrails": design_guardrails,
                },
            }
            # write track.json
            safe_write_text(os.path.join(tdir, "track.json"), json.dumps(cfg, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup=tdir)
            # initialize state.json
            safe_write_text(os.path.join(tdir, "state.json"), json.dumps({"next_episode": 1}, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup=tdir)
            created.append({"track_id": track_id, "platform": p, "bucket": b, "dir": tdir, "hidden_reader_risk": round(hidden_reader_risk, 4), "sub_engine": bootstrap_sub_engine})
    # index
    safe_write_text(os.path.join(tracks_dir, "tracks_index.json"), json.dumps(created, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup=tracks_dir)
    return created
