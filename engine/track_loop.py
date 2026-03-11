from __future__ import annotations
import os, json, time
from typing import Dict, Any, Tuple
from engine.safe_guard import require_safe_mode
from engine.safe_io import safe_write_text
from engine.final_threshold import ensure_final_threshold_repairs
from engine.track_queue import load_queue_state, save_queue_state
from engine.track_runner import run_queue_step
from engine.portfolio_orchestrator import rebalance_platform
from engine.cross_track_release import refresh_queue_release_runtime
from engine.final_threshold_runtime import capability_budget_severity
from engine.job_queue import JOB_QUEUE_PATH, load_job_queue_state
from engine.runtime_config import capability_generation_cap, generation_enabled, load_runtime_config

LOCK_PATH = os.path.join("domains","webnovel","tracks",".queue_lock")
LOCK_TTL_SECONDS = 600  # 10 minutes
HISTORY_PATH = os.path.join("domains","webnovel","tracks","queue_history.json")


def _hidden_reader_risk_trend_summary(track_dirs: list[str]) -> Dict[str, Any]:
    values = []
    critical_tracks = []
    caution_tracks = []
    for track_dir in track_dirs:
        path = os.path.join(track_dir, "outputs", "final_threshold_eval.json")
        if not os.path.exists(path):
            continue
        try:
            payload = json.load(open(path, "r", encoding="utf-8"))
        except Exception:
            continue
        criteria = dict(payload.get("criteria") or {})
        convergence_details = dict((((criteria.get("autonomous_convergence_trend", {}) or {}).get("details", {}) or {})))
        try:
            trend = float(
                convergence_details.get(
                    "hidden_reader_risk_trend",
                    (payload.get("threshold_history", {}) or {}).get("hidden_reader_risk_trend", 0.0),
                )
                or 0.0
            )
        except Exception:
            trend = 0.0
        if trend <= 0.0:
            continue
        track_id = os.path.basename(track_dir.rstrip(os.sep)) or track_dir
        values.append({"track": track_id, "trend": round(trend, 4)})
        if trend >= 0.5:
            critical_tracks.append(track_id)
        elif trend >= 0.35:
            caution_tracks.append(track_id)
    ordered = sorted(values, key=lambda item: (-float(item.get("trend", 0.0) or 0.0), str(item.get("track") or "")))
    trends = [float(item["trend"]) for item in ordered]
    if not trends:
        return {
            "track_count": 0,
            "mean": 0.0,
            "max": 0.0,
            "critical_tracks": [],
            "caution_tracks": [],
            "top_tracks": [],
        }
    return {
        "track_count": len(ordered),
        "mean": round(sum(trends) / len(trends), 4),
        "max": round(max(trends), 4),
        "critical_tracks": critical_tracks[:5],
        "caution_tracks": caution_tracks[:5],
        "top_tracks": ordered[:3],
    }


def _heavy_reader_signal_trend_summary(track_dirs: list[str]) -> Dict[str, Any]:
    values = []
    critical_tracks = []
    caution_tracks = []
    for track_dir in track_dirs:
        path = os.path.join(track_dir, "outputs", "final_threshold_eval.json")
        if not os.path.exists(path):
            continue
        try:
            payload = json.load(open(path, "r", encoding="utf-8"))
        except Exception:
            continue
        criteria = dict(payload.get("criteria") or {})
        convergence_details = dict((((criteria.get("autonomous_convergence_trend", {}) or {}).get("details", {}) or {})))
        try:
            trend = float(
                convergence_details.get(
                    "heavy_reader_signal_trend",
                    (payload.get("threshold_history", {}) or {}).get("heavy_reader_signal_trend", 1.0),
                )
                or 1.0
            )
        except Exception:
            trend = 1.0
        track_id = os.path.basename(track_dir.rstrip(os.sep)) or track_dir
        values.append({"track": track_id, "trend": round(trend, 4)})
        if 0.0 < trend < 0.62:
            critical_tracks.append(track_id)
        elif 0.0 < trend < 0.72:
            caution_tracks.append(track_id)
    if not values:
        return {
            "track_count": 0,
            "mean": 0.0,
            "min": 0.0,
            "critical_tracks": [],
            "caution_tracks": [],
            "weakest_tracks": [],
        }
    ordered = sorted(values, key=lambda item: (float(item.get("trend", 1.0) or 1.0), str(item.get("track") or "")))
    trends = [float(item["trend"]) for item in ordered]
    return {
        "track_count": len(ordered),
        "mean": round(sum(trends) / len(trends), 4),
        "min": round(min(trends), 4),
        "critical_tracks": critical_tracks[:5],
        "caution_tracks": caution_tracks[:5],
        "weakest_tracks": ordered[:3],
    }


def _platform_soak_stress_summary(track_dirs: list[str]) -> Dict[str, Any]:
    values = []
    critical_tracks = []
    caution_tracks = []
    for track_dir in track_dirs:
        metrics_path = os.path.join(track_dir, "outputs", "metrics.jsonl")
        if not os.path.exists(metrics_path):
            continue
        try:
            with open(metrics_path, "r", encoding="utf-8") as handle:
                rows = [json.loads(line) for line in handle if line.strip()]
        except Exception:
            continue
        reports = []
        for row in rows[-8:]:
            soak_report = dict(row.get("soak_report") or (row.get("meta", {}) or {}).get("soak_report") or {})
            if soak_report.get("tested"):
                reports.append(soak_report)
        if not reports:
            continue
        steady_noop_ratio = sum(float(report.get("steady_noop_ratio", 0.0) or 0.0) for report in reports) / len(reports)
        heavy_reader_signal_floor_mean = sum(float(report.get("heavy_reader_signal_floor_mean", 0.0) or 0.0) for report in reports) / len(reports)
        repair_rate_mean = sum(float(report.get("repair_rate_mean", 0.0) or 0.0) for report in reports) / len(reports)
        dominant_mode = str(reports[-1].get("dominant_mode") or "unknown")
        pressure = max(
            0.0,
            min(
                1.0,
                max(0.0, 0.76 - steady_noop_ratio) * 0.55
                + max(0.0, 0.72 - heavy_reader_signal_floor_mean) * 0.95
                + max(0.0, 0.78 - repair_rate_mean) * 0.35
                + (0.12 if dominant_mode == "volatile" else 0.05 if dominant_mode == "noop" else 0.0),
            ),
        )
        track_id = os.path.basename(track_dir.rstrip(os.sep)) or track_dir
        values.append({"track": track_id, "pressure": round(pressure, 4)})
        if pressure >= 0.34:
            critical_tracks.append(track_id)
        elif pressure >= 0.22:
            caution_tracks.append(track_id)
    if not values:
        return {
            "track_count": 0,
            "mean": 0.0,
            "max": 0.0,
            "critical_tracks": [],
            "caution_tracks": [],
            "top_tracks": [],
        }
    ordered = sorted(values, key=lambda item: (-float(item.get("pressure", 0.0) or 0.0), str(item.get("track") or "")))
    pressures = [float(item["pressure"]) for item in ordered]
    return {
        "track_count": len(ordered),
        "mean": round(sum(pressures) / len(pressures), 4),
        "max": round(max(pressures), 4),
        "critical_tracks": critical_tracks[:5],
        "caution_tracks": caution_tracks[:5],
        "top_tracks": ordered[:3],
    }


def _queue_bundle_severity(track_dirs: list[str]) -> str:
    severities = []
    for track_dir in track_dirs:
        path = os.path.join(track_dir, "outputs", "final_threshold_eval.json")
        if not os.path.exists(path):
            continue
        try:
            payload = json.load(open(path, "r", encoding="utf-8"))
        except Exception:
            continue
        severities.append(capability_budget_severity(list(payload.get("failed_bundles", []) or [])))
        reader_quality_count = sum(
            1
            for criterion in list(payload.get("failed_criteria", []) or [])
            if criterion
            in {
                "early_hook_strength",
                "episode_end_hook_strength",
                "long_arc_payoff_stability",
                "protagonist_fantasy_persistence",
                "reader_retention_stability",
                "serialization_fatigue_control",
            }
        )
        if reader_quality_count >= 2:
            severities.append("caution")
        criteria = dict(payload.get("criteria") or {})
        hidden_reader_risk = 0.0
        for criterion_name in ("reader_retention_stability", "serialization_fatigue_control"):
            details = dict((criteria.get(criterion_name) or {}).get("details") or {})
            debt = dict(details.get("reader_quality_debt") or {})
            for key in ("thinness_debt", "repetition_debt", "deja_vu_debt", "fake_urgency_debt", "compression_debt"):
                try:
                    hidden_reader_risk += float(debt.get(key, 0.0) or 0.0)
                except Exception:
                    continue
        if hidden_reader_risk >= 0.55:
            severities.append("caution")
        convergence_details = dict((((criteria.get("autonomous_convergence_trend", {}) or {}).get("details", {}) or {})))
        hidden_reader_risk_trend = 0.0
        try:
            hidden_reader_risk_trend = float(convergence_details.get("hidden_reader_risk_trend", (payload.get("threshold_history", {}) or {}).get("hidden_reader_risk_trend", 0.0)) or 0.0)
        except Exception:
            hidden_reader_risk_trend = 0.0
        if hidden_reader_risk_trend >= 0.5:
            severities.append("critical")
        elif hidden_reader_risk_trend >= 0.35:
            severities.append("caution")
        metrics_path = os.path.join(track_dir, "outputs", "metrics.jsonl")
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, "r", encoding="utf-8") as handle:
                    rows = [json.loads(line) for line in handle if line.strip()]
            except Exception:
                rows = []
            reports = []
            for row in rows[-8:]:
                soak_report = dict(row.get("soak_report") or (row.get("meta", {}) or {}).get("soak_report") or {})
                if soak_report.get("tested"):
                    reports.append(soak_report)
            if reports:
                steady_noop_ratio = sum(float(report.get("steady_noop_ratio", 0.0) or 0.0) for report in reports) / len(reports)
                heavy_reader_signal_floor_mean = sum(float(report.get("heavy_reader_signal_floor_mean", 0.0) or 0.0) for report in reports) / len(reports)
                repair_rate_mean = sum(float(report.get("repair_rate_mean", 0.0) or 0.0) for report in reports) / len(reports)
                dominant_mode = str(reports[-1].get("dominant_mode") or "unknown")
                platform_soak_pressure = max(
                    0.0,
                    min(
                        1.0,
                        max(0.0, 0.76 - steady_noop_ratio) * 0.55
                        + max(0.0, 0.72 - heavy_reader_signal_floor_mean) * 0.95
                        + max(0.0, 0.78 - repair_rate_mean) * 0.35
                        + (0.12 if dominant_mode == "volatile" else 0.05 if dominant_mode == "noop" else 0.0),
                    ),
                )
                if platform_soak_pressure >= 0.34:
                    severities.append("critical")
                elif platform_soak_pressure >= 0.22:
                    severities.append("caution")
    if "critical" in severities:
        return "critical"
    if "caution" in severities:
        return "caution"
    return "stable"


def _ensure_queue_repair_work(track_dirs: list[str], queue_path: str = JOB_QUEUE_PATH) -> int:
    queued = 0
    for track_dir in track_dirs:
        path = os.path.join(track_dir, "outputs", "final_threshold_eval.json")
        if not os.path.exists(path):
            continue
        try:
            report = json.load(open(path, "r", encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(report, dict):
            continue
        report = dict(report)
        report.setdefault("track_id", os.path.basename(track_dir.rstrip(os.sep)) or "unknown_track")
        report.setdefault("out_dir", os.path.join(track_dir, "outputs"))
        before = len(load_job_queue_state(queue_path).get("jobs", []))
        ensure_final_threshold_repairs(report, queue_path=queue_path, safe_mode=True)
        after = len(load_job_queue_state(queue_path).get("jobs", []))
        queued += max(0, after - before)
    return queued

def _lock_acquire() -> bool:
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
    if os.path.exists(LOCK_PATH):
        try:
            # stale lock recovery
            age = time.time() - float(open(LOCK_PATH,'r',encoding='utf-8').read().strip() or 0)
            if age > LOCK_TTL_SECONDS:
                os.remove(LOCK_PATH)
            else:
                return False
        except Exception:
            return False
    safe_write_text(LOCK_PATH, str(time.time()), safe_mode=True, project_dir_for_backup=os.path.dirname(LOCK_PATH))
    return True

def _lock_release():
    try:
        if os.path.exists(LOCK_PATH):
            os.remove(LOCK_PATH)
    except Exception:
        pass

def _load_history() -> Dict[str, Any]:
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"total_steps": 0, "ok_steps": 0, "error_steps": 0, "last_msg": None, "last_ts": None}

def _save_history(h: Dict[str, Any]):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    safe_write_text(HISTORY_PATH, json.dumps(h, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup=os.path.dirname(HISTORY_PATH))

def run_queue_loop(cfg: Dict[str, Any], max_steps: int = 1) -> Tuple[bool, str]:
    require_safe_mode(cfg)
    runtime_cfg = load_runtime_config()
    if not generation_enabled(runtime_cfg):
        q = load_queue_state()
        if q.get("status") == "running":
            q["status"] = "paused"
            q["last_error"] = "Generation disabled in runtime_config.json"
            save_queue_state(q)
        return False, "Generation disabled in runtime_config.json"
    if not _lock_acquire():
        return False, "Queue loop already running (lock present)."
    try:
        h = _load_history()
        msg_last = None
        ok_any = False
        q0 = load_queue_state()
        track_dirs = list(q0.get("track_dirs", []) or [])
        severity = _queue_bundle_severity(track_dirs)
        hidden_reader_risk_summary = _hidden_reader_risk_trend_summary(track_dirs)
        heavy_reader_signal_summary = _heavy_reader_signal_trend_summary(track_dirs)
        platform_soak_summary = _platform_soak_stress_summary(track_dirs)
        generation_cap = capability_generation_cap(runtime_cfg, severity)
        steps_budget = min(max(1, int(max_steps)), max(0, generation_cap))
        h["bundle_budgeting"] = {
            "severity": severity,
            "generation_cap": generation_cap,
            "requested_steps": int(max_steps),
            "hidden_reader_risk_trend_summary": hidden_reader_risk_summary,
            "heavy_reader_signal_trend_summary": heavy_reader_signal_summary,
            "platform_soak_summary": platform_soak_summary,
        }
        if steps_budget <= 0:
            queued_repairs = _ensure_queue_repair_work(track_dirs)
            h["last_msg"] = f"Generation budget exhausted for bundle severity={severity}"
            if queued_repairs:
                h["last_msg"] += f"; queued_repairs={queued_repairs}"
            if hidden_reader_risk_summary.get("max", 0.0):
                h["last_msg"] += f"; hidden_reader_risk_trend_max={hidden_reader_risk_summary['max']}"
            if heavy_reader_signal_summary.get("min", 0.0):
                h["last_msg"] += f"; heavy_reader_signal_trend_min={heavy_reader_signal_summary['min']}"
            if platform_soak_summary.get("max", 0.0):
                h["last_msg"] += f"; platform_soak_pressure_max={platform_soak_summary['max']}"
            if severity == "critical":
                q0["status"] = "blocked"
            elif severity == "caution" and q0.get("status") == "running":
                q0["status"] = "paused"
            q0["last_error"] = h["last_msg"]
            q0["bundle_budgeting"] = dict(h["bundle_budgeting"])
            save_queue_state(q0)
            h["last_ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
            _save_history(h)
            return False, h["last_msg"]
        for _ in range(steps_budget):
            runtime_cfg = load_runtime_config()
            if not generation_enabled(runtime_cfg):
                msg_last = "Generation disabled in runtime_config.json"
                break
            q = load_queue_state()
            if q.get("status") != "running":
                msg_last = f"Queue not running (status={q.get('status')})"
                break
            q = refresh_queue_release_runtime(q, os.path.join("domains", "webnovel", "tracks"))
            save_queue_state(q)
            ok, msg = run_queue_step(cfg)
            msg_last = msg
            h["total_steps"] += 1
            h["last_msg"] = msg
            h["last_ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
            if ok:
                h["ok_steps"] += 1
                ok_any = True
            else:
                h["error_steps"] += 1
                break
        _save_history(h)
                # After loop steps, auto-rebalance portfolio
        try:
            rebalance_platform(cfg, os.path.join('domains','webnovel','tracks'))
        except Exception:
            pass
        return ok_any, (msg_last or "done")
    finally:
        _lock_release()
