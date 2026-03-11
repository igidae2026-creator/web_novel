from __future__ import annotations
import os, json, math
from datetime import datetime
from typing import Dict, Any, List, Optional
from engine.safe_io import safe_write_text
from engine.io_utils import append_jsonl
from engine.io_utils import read_text
from market_layer.market_api import compute_market_view
from engine.final_threshold import evaluate_final_threshold_bundle
from engine.model_config import load_models, get_model
from engine.grading import maybe_update_grade
import csv

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


def load_business_feedback_summary(
    revenue_csv_path: str = os.path.join("data", "revenue_input.csv"),
    campaign_csv_path: str = os.path.join("data", "campaign_input.csv"),
) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "available": False,
        "revenue_rows": 0,
        "campaign_rows": 0,
        "total_revenue": 0.0,
        "total_campaign_spend": 0.0,
        "best_campaign_roi": 0.0,
    }

    def _read_rows(path: str) -> List[Dict[str, Any]]:
        if not path or not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return list(csv.DictReader(handle))
        except Exception:
            return []

    revenue_rows = _read_rows(revenue_csv_path)
    campaign_rows = _read_rows(campaign_csv_path)
    summary["revenue_rows"] = len(revenue_rows)
    summary["campaign_rows"] = len(campaign_rows)
    summary["available"] = bool(revenue_rows or campaign_rows)

    for row in revenue_rows:
        try:
            summary["total_revenue"] += float(row.get("revenue", 0.0) or 0.0)
        except Exception:
            continue
    best_roi = 0.0
    for row in campaign_rows:
        try:
            spend = float(row.get("spend", 0.0) or 0.0)
        except Exception:
            spend = 0.0
        try:
            revenue = float(row.get("revenue", 0.0) or 0.0)
        except Exception:
            revenue = 0.0
        summary["total_campaign_spend"] += spend
        if spend > 0:
            best_roi = max(best_roi, (revenue - spend) / spend)
    summary["best_campaign_roi"] = round(best_roi, 4)
    summary["total_revenue"] = round(float(summary["total_revenue"]), 4)
    summary["total_campaign_spend"] = round(float(summary["total_campaign_spend"]), 4)
    return summary


def _hidden_reader_risk_from_state(state: Dict[str, Any]) -> float:
    story_state = dict(state.get("story_state_v2", {}) or {})
    reader_quality = dict((story_state.get("control", {}) or {}).get("reader_quality", {}) or {})
    threshold_history = dict((story_state.get("control", {}) or {}).get("final_threshold_history", {}) or {})
    total = 0.0
    for key in ("thinness_debt", "repetition_debt", "deja_vu_debt", "fake_urgency_debt", "compression_debt"):
        try:
            total += float(reader_quality.get(key, 0.0) or 0.0)
        except Exception:
            continue
    total += float(threshold_history.get("hidden_reader_risk_trend", 0.0) or 0.0)
    return round(total, 4)


def _heavy_reader_signal_from_state(state: Dict[str, Any]) -> float:
    story_state = dict(state.get("story_state_v2", {}) or {})
    threshold_history = dict((story_state.get("control", {}) or {}).get("final_threshold_history", {}) or {})
    try:
        return round(float(threshold_history.get("heavy_reader_signal_trend", 1.0) or 1.0), 4)
    except Exception:
        return 1.0


def _platform_soak_pressure_from_state(state: Dict[str, Any]) -> float:
    story_state = dict(state.get("story_state_v2", {}) or {})
    soak_history = dict((story_state.get("control", {}) or {}).get("soak_history", {}) or {})
    history = list(soak_history.get("history", []) or [])
    recent = history[-4:]
    if recent:
        values = []
        for item in recent:
            steady = float(item.get("steady_noop_ratio", 0.0) or 0.0)
            heavy_reader_signal = float(item.get("heavy_reader_signal", 0.0) or 0.0)
            values.append(
                max(0.0, min(1.0, max(0.0, 0.76 - steady) * 0.55 + max(0.0, 0.72 - heavy_reader_signal) * 0.95))
            )
        return round(_mean(values), 4)
    steady = float(soak_history.get("steady_noop_ratio", 0.0) or 0.0)
    heavy_reader_signal = float(soak_history.get("heavy_reader_signal_trend", 0.0) or 0.0)
    return round(max(0.0, min(1.0, max(0.0, 0.76 - steady) * 0.55 + max(0.0, 0.72 - heavy_reader_signal) * 0.95)), 4)

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

    stats = report.get("market", {}).get("stats", {}) if isinstance(report.get("market", {}), dict) else {}
    if stats.get("available"):
        latest_tp = float(stats.get("latest_top_percent", 999.0) or 999.0)
        grade = maybe_update_grade(grade_state, latest_tp, today_ymd=today, cooldown_days=7, cfg=cfg)
        report["grade"] = grade
        safe_write_text(grade_state_path, json.dumps(grade_state, ensure_ascii=False, indent=2), safe_mode=bool(cfg.get("safe_mode", False)), project_dir_for_backup=out_dir)

    safe_mode = bool(cfg.get("safe_mode", False))
    business_feedback = load_business_feedback_summary()
    state_path = os.path.join(os.path.dirname(out_dir), "state.json")
    state = {}
    if os.path.exists(state_path):
        try:
            state = json.load(open(state_path, "r", encoding="utf-8"))
        except Exception:
            state = {}
    hidden_reader_risk = _hidden_reader_risk_from_state(state)
    heavy_reader_signal_trend = _heavy_reader_signal_from_state(state)
    platform_soak_pressure = _platform_soak_pressure_from_state(state)
    promotion_guidance = {
        "verdict": "promote" if report.get("market", {}).get("ok") and hidden_reader_risk < 0.35 and heavy_reader_signal_trend >= 0.62 and platform_soak_pressure < 0.34 else "hold",
        "reason": (
            "market_ok_and_reader_quality_bounded"
            if report.get("market", {}).get("ok") and hidden_reader_risk < 0.35 and heavy_reader_signal_trend >= 0.62 and platform_soak_pressure < 0.34
            else "hidden_reader_risk_requires_hold"
            if hidden_reader_risk >= 0.35
            else "heavy_reader_signal_requires_hold"
            if heavy_reader_signal_trend < 0.62
            else "platform_soak_pressure_requires_hold"
            if platform_soak_pressure >= 0.34
            else "hidden_reader_risk_requires_hold"
        ),
        "hidden_reader_risk": hidden_reader_risk,
        "heavy_reader_signal_trend": heavy_reader_signal_trend,
        "platform_soak_pressure": platform_soak_pressure,
    }
    report["business_feedback"] = business_feedback
    report["promotion_guidance"] = promotion_guidance
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
        append_jsonl(
            os.path.join(out_dir, "metrics.jsonl"),
            {"type": "business_feedback", "summary": business_feedback},
            safe_mode=bool(cfg.get("safe_mode", False)),
            project_dir_for_backup=out_dir,
        )
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

    evaluate_final_threshold_bundle(
        cfg,
        out_dir,
        cycle_context={
            "action": "certify",
            "task_generated": True,
            "execution_recorded": True,
            "next_step_recorded": True,
            "market_feedback_handled": True,
            "business_feedback_handled": bool(business_feedback.get("available")),
            "scope_authority_policy_ok": True,
            "policy_decision": promotion_guidance["verdict"],
            "quality_lift_if_human_intervenes": grade_state.get("quality_lift_if_human_intervenes", 1.0),
        },
        safe_mode=safe_mode,
    )
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
