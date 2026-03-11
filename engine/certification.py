from __future__ import annotations
import os, json, math
from datetime import datetime
from typing import Dict, Any, List, Optional
from engine.safe_io import safe_write_text
from engine.io_utils import append_jsonl
from engine.io_utils import read_text
from market_layer.market_api import compute_market_view
from engine.model_config import load_models, get_model
from engine.grading import maybe_update_grade

def _mean(xs: List[float]) -> float:
    return sum(xs)/len(xs) if xs else 0.0

def _std(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x-m)**2 for x in xs)/(len(xs)-1))

def _p(xs: List[float], q: float) -> float:
    if not xs:
        return 0.0
    xs2 = sorted(xs)
    idx = int(q * (len(xs2)-1))
    return xs2[idx]

def load_metrics_scores(metrics_jsonl_path: str, window_eps: int = 10) -> Dict[str, Any]:
    if not metrics_jsonl_path or not os.path.exists(metrics_jsonl_path):
        return {"available": False}
    rows = []
    with open(metrics_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    if not rows:
        return {"available": False}
    rows = rows[-max(1, int(window_eps)):]
    hooks=[]; emos=[]; escs=[]; reps=[]
    for r in rows:
        s = r.get("scores", {})
        try: hooks.append(float(s.get("hook_score",0.0)))
        except Exception: pass
        try: emos.append(float(s.get("emotion_density",0.0)))
        except Exception: pass
        try: escs.append(float(s.get("escalation",0.0)))
        except Exception: pass
        try: reps.append(float(s.get("repetition_score",0.0)))
        except Exception: pass
    return {
        "available": True,
        "window": len(rows),
        "hook_mean": _mean(hooks), "hook_std": _std(hooks),
        "emotion_mean": _mean(emos), "emotion_std": _std(emos),
        "escalation_mean": _mean(escs), "escalation_std": _std(escs),
        "repetition_mean": _mean(reps), "repetition_std": _std(reps),
    }

def certify(cfg: dict, out_dir: str) -> Dict[str, Any]:
    project_dir = out_dir
    platform = cfg["project"]["platform"]
    bucket = cfg["project"]["genre_bucket"]
    rank_csv = cfg.get("external", {}).get("rank_signals_csv", "data/rank_signals.csv")

    # market stats
    mv = compute_market_view(cfg, rank_csv, platform, bucket)
    stats = mv.get("stats", {})
    band = mv.get("band")
    top3 = mv.get("top3", False)

    models = load_models(cfg)
    mm = get_model(cfg, models, 'market')
    cert_cfg = mm.get('certification', {}) if isinstance(mm.get('certification', {}), dict) else {}
    # cfg.certification overrides
    if isinstance(cfg.get('certification'), dict):
        cert_cfg = {**cert_cfg, **cfg.get('certification')}

    target = str(cert_cfg.get("market_target", "TOP3")).upper()
    max_std = float(cert_cfg.get("max_std_top_percent", 1.2))
    score_window = int(cert_cfg.get("score_window_eps", 10))

    # internal metrics
    metrics_path = os.path.join(project_dir, "metrics.jsonl")
    internal = load_metrics_scores(metrics_path, window_eps=score_window)

    ok_market = False
    if stats.get("available"):
        std_ok = float(stats.get("std_top_percent", 999.0)) <= max_std
        if target == "TOP3":
            ok_market = (band == "TOP3") and std_ok
        elif target == "TOP5":
            ok_market = (band in ["TOP3","TOP5"]) and std_ok
        else:
            ok_market = (band in ["TOP3","TOP5","TOP10"]) and std_ok

    failure_reason = None
    if stats.get("available"):
        if not ok_market:
            if band not in ["TOP3","TOP5","TOP10"]:
                failure_reason = "band_not_reached"
            elif float(stats.get("std_top_percent", 999.0)) > max_std:
                failure_reason = "std_exceeded"
            else:
                failure_reason = "target_not_met"
    else:
        failure_reason = "no_market_data"

    report = {
        "platform": platform,
        "genre_bucket": bucket,
        "market": {
            "available": bool(stats.get("available")),
            "band": band,
            "top3_rule": bool(top3),
            "stats": stats,
            "target": target,
            "max_std_top_percent": max_std,
            "ok": ok_market,
        },
        "internal": internal,
        "failure_reason": failure_reason,
    }
    return report

def save_report(cfg: dict, out_dir: str, report: Dict[str, Any]) -> str:
    path = os.path.join(out_dir, "certification_report.json")

    # Grade state stored per out_dir
    grade_state_path = os.path.join(out_dir, "grade_state.json")
    grade_state = {}
    if os.path.exists(grade_state_path):
        try:
            grade_state = json.load(open(grade_state_path, "r", encoding="utf-8"))
        except Exception:
            grade_state = {}
    today = datetime.now().strftime("%Y-%m-%d")
    # certification counters for phase-grade link
    grade_last = grade_state.get('grade_last_change_ymd')
    if grade_last and today >= grade_last:
        grade_state['cert_count_since_grade_change'] = int(grade_state.get('cert_count_since_grade_change', 0) or 0) + 1
    grade_state['last_cert_date'] = today

    if stats.get("available"):
        latest_tp = float(stats.get("latest_top_percent", 999.0) or 999.0)
        grade = maybe_update_grade(grade_state, latest_tp, today_ymd=today, cooldown_days=7, cfg=cfg)
        report["grade"] = grade
        safe_write_text(grade_state_path, json.dumps(grade_state, ensure_ascii=False, indent=2), safe_mode=bool(cfg.get("safe_mode", False)), project_dir_for_backup=out_dir)

    safe_mode = bool(cfg.get("safe_mode", False))
    txt = json.dumps(report, ensure_ascii=False, indent=2)
    safe_write_text(path, txt, safe_mode=safe_mode, project_dir_for_backup=out_dir)
        # Append certification snapshot to metrics
    try:
        append_jsonl(os.path.join(out_dir, "metrics.jsonl"),
            {"type": "certification", "report": report},
            safe_mode=bool(cfg.get("safe_mode", False)),
            project_dir_for_backup=out_dir)
    except Exception:
        pass

    try:
        if report.get('grade'):
            append_jsonl(os.path.join(out_dir, 'metrics.jsonl'),
                {'type':'grade','grade': report.get('grade'), 'date': datetime.now().strftime('%Y-%m-%d'),
                 'top_percent': report.get('market',{}).get('stats',{}).get('latest_top_percent')},
                safe_mode=bool(cfg.get('safe_mode', False)), project_dir_for_backup=out_dir)
    except Exception:
        pass
    return path


def summarize_cert_trend(out_dir: str, last_n: int = 5):
    path = os.path.join(out_dir, "metrics.jsonl")
    if not os.path.exists(path):
        return {"available": False}
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line.strip())
                if row.get("type") == "certification":
                    records.append(row.get("report", {}))
            except Exception:
                continue
    if not records:
        return {"available": False}
    recent = records[-last_n:]
    ok_count = sum(1 for r in recent if r.get("market", {}).get("ok"))
    fail_count = len(recent) - ok_count
    reasons = {}
    for r in recent:
        fr = r.get("failure_reason")
        if fr:
            reasons[fr] = reasons.get(fr, 0) + 1
    return {
        "available": True,
        "total": len(recent),
        "ok": ok_count,
        "fail": fail_count,
        "failure_breakdown": reasons
    }
