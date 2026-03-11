from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List

from .config import deep_merge
from .safe_io import safe_write_text

DEFAULT_RUNTIME_CONFIG_PATH = "runtime_config.json"
DEFAULT_SYSTEM_STATUS_PATH = os.path.join("outputs", "system_status.json")

DEFAULT_RUNTIME_CONFIG: Dict[str, Any] = {
    "generation_enabled": True,
    "track_count": 6,
    "release_cadence": {
        "mode": "queue_loop",
        "steps_per_run": 1,
    },
    "portfolio": {
        "mode": "balanced",
        "bundle_budgeting": {
            "enabled": True,
            "critical_generation_cap": 0,
            "caution_generation_cap": 1,
            "stable_generation_cap": 3,
        },
    },
    "evaluation": {
        "max_revision_passes": 2,
        "causal_repair_retry_budget": 2,
        "viral_required": True,
        "preflight_gate": {
            "enabled": True,
        },
        "risk_tiers": {
            "low": {
                "max_revision_passes": 1,
                "causal_repair_retry_budget": 1,
                "request_timeout_seconds": 90,
                "mode": "batch",
            },
            "medium": {
                "max_revision_passes": 2,
                "causal_repair_retry_budget": 2,
                "request_timeout_seconds": 150,
                "mode": "batch",
            },
            "high": {
                "max_revision_passes": 3,
                "causal_repair_retry_budget": 3,
                "request_timeout_seconds": 210,
                "mode": "batch",
            },
            "critical": {
                "max_revision_passes": 3,
                "causal_repair_retry_budget": 3,
                "request_timeout_seconds": 240,
                "mode": "priority",
            },
        },
    },
}


def _ensure_parent_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)


def _normalized_path(path: str) -> str:
    return path if os.path.dirname(path) else os.path.join(".", path)


def runtime_config_defaults() -> Dict[str, Any]:
    return deepcopy(DEFAULT_RUNTIME_CONFIG)


def load_runtime_config(path: str = DEFAULT_RUNTIME_CONFIG_PATH) -> Dict[str, Any]:
    runtime_cfg = runtime_config_defaults()
    if not path or not os.path.exists(path):
        return runtime_cfg
    try:
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
    except Exception:
        return runtime_cfg
    if isinstance(loaded, dict):
        runtime_cfg = deep_merge(runtime_cfg, loaded)
    return runtime_cfg


def save_runtime_config(
    runtime_cfg: Dict[str, Any],
    path: str = DEFAULT_RUNTIME_CONFIG_PATH,
    safe_mode: bool = False,
    project_dir_for_backup: str | None = None,
) -> Dict[str, Any]:
    merged = deep_merge(runtime_config_defaults(), dict(runtime_cfg or {}))
    payload = json.dumps(merged, ensure_ascii=False, indent=2)
    normalized_path = _normalized_path(path)
    _ensure_parent_dir(normalized_path)
    safe_write_text(normalized_path, payload, safe_mode=safe_mode, project_dir_for_backup=project_dir_for_backup)
    return merged


def generation_enabled(runtime_cfg: Dict[str, Any] | None) -> bool:
    if runtime_cfg is None:
        return True
    return bool(runtime_cfg.get("generation_enabled", True))


def configured_track_count(runtime_cfg: Dict[str, Any] | None, default_count: int = 1) -> int:
    runtime_cfg = runtime_cfg or {}
    try:
        return max(1, int(runtime_cfg.get("track_count", default_count) or default_count))
    except Exception:
        return max(1, int(default_count or 1))


def configured_loop_steps(runtime_cfg: Dict[str, Any] | None, default_steps: int = 1) -> int:
    runtime_cfg = runtime_cfg or {}
    cadence = dict(runtime_cfg.get("release_cadence", {}) or {})
    try:
        return max(1, int(cadence.get("steps_per_run", default_steps) or default_steps))
    except Exception:
        return max(1, int(default_steps or 1))


def capability_generation_cap(runtime_cfg: Dict[str, Any] | None, severity: str) -> int:
    runtime_cfg = runtime_cfg or {}
    portfolio = dict(runtime_cfg.get("portfolio", {}) or {})
    budgeting = dict(portfolio.get("bundle_budgeting", {}) or {})
    if not budgeting.get("enabled", True):
        return 999999
    def _as_budget(key: str, default: int) -> int:
        value = budgeting.get(key, default)
        try:
            return int(default if value is None else value)
        except Exception:
            return int(default)
    mapping = {
        "critical": _as_budget("critical_generation_cap", 0),
        "caution": _as_budget("caution_generation_cap", 1),
        "stable": _as_budget("stable_generation_cap", 3),
    }
    return max(0, mapping.get(severity, mapping["stable"]))


def apply_runtime_config(cfg: Dict[str, Any], runtime_cfg: Dict[str, Any] | None) -> Dict[str, Any]:
    runtime_cfg = load_runtime_config() if runtime_cfg is None else dict(runtime_cfg)
    override: Dict[str, Any] = {
        "runtime": {
            "generation_enabled": generation_enabled(runtime_cfg),
            "track_count": configured_track_count(runtime_cfg, default_count=cfg.get("runtime", {}).get("track_count", 1) or 1),
            "release_cadence": dict(runtime_cfg.get("release_cadence", {}) or {}),
        }
    }
    portfolio_cfg = dict(runtime_cfg.get("portfolio", {}) or {})
    if portfolio_cfg:
        override["portfolio"] = portfolio_cfg
    evaluation_cfg = dict(runtime_cfg.get("evaluation", {}) or {})
    if evaluation_cfg:
        override.setdefault("limits", {})
        override.setdefault("quality", {})
        if evaluation_cfg.get("max_revision_passes") is not None:
            override["limits"]["max_revision_passes"] = int(evaluation_cfg["max_revision_passes"])
        if evaluation_cfg.get("causal_repair_retry_budget") is not None:
            override["limits"]["causal_repair_retry_budget"] = int(evaluation_cfg["causal_repair_retry_budget"])
        if evaluation_cfg.get("viral_required") is not None:
            override["quality"]["viral_required"] = bool(evaluation_cfg["viral_required"])
    return deep_merge(cfg, override)


def load_runtime_config_into_cfg(
    cfg: Dict[str, Any],
    path: str = DEFAULT_RUNTIME_CONFIG_PATH,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    runtime_cfg = load_runtime_config(path)
    return apply_runtime_config(cfg, runtime_cfg), runtime_cfg


def write_system_status_snapshot(
    system_status: Dict[str, Any],
    runtime_cfg: Dict[str, Any] | None = None,
    path: str = DEFAULT_SYSTEM_STATUS_PATH,
    out_dir: str | None = None,
    tracks_root: str = os.path.join("domains", "webnovel", "tracks"),
    safe_mode: bool = False,
    project_dir_for_backup: str | None = None,
) -> Dict[str, Any]:
    payload = {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "system_status": dict(system_status or {}),
        "runtime_config": dict(runtime_cfg or load_runtime_config()),
        "hidden_reader_risk_summary": summarize_hidden_reader_risk(tracks_root=tracks_root),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    _ensure_parent_dir(path)
    safe_write_text(path, text, safe_mode=safe_mode, project_dir_for_backup=project_dir_for_backup)
    if out_dir:
        local_path = os.path.join(out_dir, "system_status.json")
        if os.path.abspath(local_path) != os.path.abspath(path):
            safe_write_text(local_path, text, safe_mode=safe_mode, project_dir_for_backup=out_dir)
    return payload


def read_json_file(path: str) -> Dict[str, Any]:
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def read_recent_metrics(path: str, limit: int = 20) -> List[Dict[str, Any]]:
    if not path or not os.path.exists(path):
        return []
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except Exception:
                continue
            if isinstance(record, dict):
                rows.append(record)
    return rows[-max(1, int(limit)) :]


def list_latest_episodes(
    tracks_root: str = os.path.join("domains", "webnovel", "tracks"),
    standalone_out_dir: str | None = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    output_dirs: List[str] = []
    if standalone_out_dir and os.path.isdir(standalone_out_dir):
        output_dirs.append(standalone_out_dir)
    if tracks_root and os.path.isdir(tracks_root):
        for name in sorted(os.listdir(tracks_root)):
            candidate = os.path.join(tracks_root, name, "outputs")
            if os.path.isdir(candidate):
                output_dirs.append(candidate)

    episodes: List[Dict[str, Any]] = []
    for output_dir in output_dirs:
        for name in sorted(os.listdir(output_dir)):
            if not (name.startswith("episode_") and name.endswith(".txt")):
                continue
            path = os.path.join(output_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    preview = f.read(600)
            except Exception:
                preview = ""
            episodes.append(
                {
                    "path": path,
                    "name": name,
                    "track": os.path.basename(os.path.dirname(output_dir)) if os.path.basename(output_dir) == "outputs" else os.path.basename(output_dir),
                    "modified_ts": os.path.getmtime(path),
                    "preview": preview,
                }
            )
    episodes.sort(key=lambda item: float(item.get("modified_ts", 0.0)), reverse=True)
    return episodes[: max(1, int(limit))]


def summarize_hidden_reader_risk(
    tracks_root: str = os.path.join("domains", "webnovel", "tracks"),
    limit: int = 5,
) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "tracks": [],
        "mean_hidden_reader_risk_trend": 0.0,
        "mean_heavy_reader_signal_trend": 0.0,
        "critical_tracks": 0,
        "weak_signal_tracks": 0,
    }
    if not tracks_root or not os.path.isdir(tracks_root):
        return summary
    rows: List[Dict[str, Any]] = []
    for name in sorted(os.listdir(tracks_root)):
        final_path = os.path.join(tracks_root, name, "outputs", "final_threshold_eval.json")
        if not os.path.exists(final_path):
            continue
        payload = read_json_file(final_path)
        details = dict((((payload.get("criteria", {}) or {}).get("autonomous_convergence_trend", {}) or {}).get("details", {}) or {}))
        hidden_reader_risk_trend = float(details.get("hidden_reader_risk_trend", (payload.get("threshold_history", {}) or {}).get("hidden_reader_risk_trend", 0.0)) or 0.0)
        heavy_reader_signal_trend = float(details.get("heavy_reader_signal_trend", (payload.get("threshold_history", {}) or {}).get("heavy_reader_signal_trend", 0.0)) or 0.0)
        rows.append(
            {
                "track": name,
                "hidden_reader_risk_trend": round(hidden_reader_risk_trend, 4),
                "heavy_reader_signal_trend": round(heavy_reader_signal_trend, 4),
                "final_threshold_ready": bool(payload.get("final_threshold_ready")),
                "failed_bundles": list(payload.get("failed_bundles", []) or []),
            }
        )
    if not rows:
        return summary
    rows.sort(key=lambda item: (-float(item.get("hidden_reader_risk_trend", 0.0)), item.get("track", "")))
    summary["tracks"] = rows[: max(1, int(limit))]
    summary["mean_hidden_reader_risk_trend"] = round(
        sum(float(item.get("hidden_reader_risk_trend", 0.0) or 0.0) for item in rows) / len(rows),
        4,
    )
    summary["mean_heavy_reader_signal_trend"] = round(
        sum(float(item.get("heavy_reader_signal_trend", 0.0) or 0.0) for item in rows) / len(rows),
        4,
    )
    summary["critical_tracks"] = sum(1 for item in rows if float(item.get("hidden_reader_risk_trend", 0.0) or 0.0) >= 0.35)
    summary["weak_signal_tracks"] = sum(1 for item in rows if 0.0 < float(item.get("heavy_reader_signal_trend", 0.0) or 0.0) < 0.72)
    return summary
