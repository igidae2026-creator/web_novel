from __future__ import annotations

import json
import os
import re
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List

from .config import load_config
from .cross_track_release import build_cross_track_release_plan
from .reliability import detect_axis_drift, detect_quality_drift
from .runtime_config import (
    DEFAULT_RUNTIME_CONFIG_PATH,
    DEFAULT_SYSTEM_STATUS_PATH,
    configured_loop_steps,
    configured_track_count,
    load_runtime_config,
    load_runtime_config_into_cfg,
    read_json_file,
    read_recent_metrics,
    save_runtime_config,
)
from .safe_io import safe_write_text
from .track_loader import list_track_dirs

POLICY_ACTION_PATH = os.path.join("outputs", "policy_action.json")

PROJECT_PRESETS: Dict[str, Dict[str, Any]] = {
    "Steady Series": {
        "project_setup": {"target_total_episodes": 300, "early_focus_episodes": 3},
        "track_count": 6,
        "portfolio": {"mode": "balanced"},
        "release_cadence": {"mode": "queue_loop", "steps_per_run": 1},
    },
    "Launch Sprint": {
        "project_setup": {"target_total_episodes": 180, "early_focus_episodes": 5},
        "track_count": 9,
        "portfolio": {"mode": "focused"},
        "release_cadence": {"mode": "queue_loop", "steps_per_run": 2},
    },
    "Portfolio Expansion": {
        "project_setup": {"target_total_episodes": 360, "early_focus_episodes": 3},
        "track_count": 12,
        "portfolio": {"mode": "explore"},
        "release_cadence": {"mode": "queue_loop", "steps_per_run": 3},
    },
}

PLATFORM_PRESETS: Dict[str, Dict[str, Any]] = {
    "Munpia Standard": {"project_setup": {"platform": "Munpia"}, "release_cadence": {"steps_per_run": 1}},
    "KakaoPage Velocity": {"project_setup": {"platform": "KakaoPage"}, "release_cadence": {"steps_per_run": 2}},
    "NaverSeries Stability": {"project_setup": {"platform": "NaverSeries"}, "release_cadence": {"steps_per_run": 1}},
    "Novelpia Discovery": {"project_setup": {"platform": "Novelpia"}, "release_cadence": {"steps_per_run": 2}},
}

GENRE_PRESETS: Dict[str, Dict[str, Any]] = {
    "A": {"label": "High-drama hook", "evaluation": {"viral_required": True}},
    "B": {"label": "Character tension", "evaluation": {"viral_required": True}},
    "C": {"label": "Progression grind", "evaluation": {"viral_required": False}},
    "D": {"label": "Dark inversion", "evaluation": {"viral_required": False}},
    "E": {"label": "Mystery serialization", "evaluation": {"viral_required": True}},
    "F": {"label": "Romance escalation", "evaluation": {"viral_required": True}},
    "G": {"label": "Worldbuilding density", "evaluation": {"viral_required": False}},
    "H": {"label": "Comedy pressure", "evaluation": {"viral_required": False}},
    "I": {"label": "Experimental pacing", "evaluation": {"viral_required": False}},
}

SIMPLE_MODE_FIELDS = [
    "project_name",
    "platform",
    "genre_bucket",
    "generation_enabled",
    "track_count",
    "steps_per_run",
    "portfolio_mode",
]
ADVANCED_MODE_FIELDS = SIMPLE_MODE_FIELDS + [
    "sub_engine",
    "target_total_episodes",
    "early_focus_episodes",
    "revision_passes",
    "repair_budget",
    "viral_required",
    "window_count",
    "drift_check_enabled",
    "simulation_horizons",
    "operator_overrides",
]
HIGH_IMPACT_ACTIONS = {"auto_loop", "release_plan", "reliability_check", "pause"}
OPERATOR_OVERRIDE_ACTIONS = {
    "hold_track",
    "boost_track",
    "resume_generation",
    "ignore_release_once",
    "mark_review",
    "mark_hold",
    "mark_approve",
}


def _ensure_parent_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(name or "").strip().lower()).strip("._")
    return slug or "project"


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = deepcopy(base)
    for key, value in dict(override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def get_project_paths(project_name: str) -> Dict[str, str]:
    slug = _slugify(project_name)
    return {
        "tracks_root": os.path.join("domains", "webnovel", "projects", slug, "tracks"),
        "system_status_path": os.path.join("outputs", "projects", slug, "system_status.json"),
        "policy_action_path": os.path.join("outputs", "projects", slug, "policy_action.json"),
        "project_output_dir": os.path.join("outputs", "projects", slug),
        "project_metrics_path": os.path.join("outputs", "projects", slug, "metrics.jsonl"),
    }


def get_console_mode_fields(mode: str) -> List[str]:
    return list(ADVANCED_MODE_FIELDS if str(mode or "simple") == "advanced" else SIMPLE_MODE_FIELDS)


def load_policy_action(path: str = POLICY_ACTION_PATH) -> Dict[str, Any]:
    default_action = {
        "requested_at": None,
        "action": "idle",
        "status": "idle",
        "result": {},
        "history": [],
        "latest_error": None,
        "latest_warning": None,
        "last_failed_action": None,
    }
    if not os.path.exists(path):
        return default_action
    loaded = read_json_file(path)
    if not loaded:
        return default_action
    return _deep_merge(default_action, loaded)


def save_policy_action(payload: Dict[str, Any], path: str = POLICY_ACTION_PATH) -> Dict[str, Any]:
    existing = load_policy_action(path)
    merged = _deep_merge(existing, dict(payload or {}))
    if "result" in payload:
        merged["result"] = deepcopy(payload.get("result", {}))
    if "payload" in payload:
        merged["payload"] = deepcopy(payload.get("payload", {}))
    entry = {
        "ts": merged.get("executed_at") or merged.get("requested_at") or _now(),
        "action": merged.get("action"),
        "status": merged.get("status"),
        "error": ((merged.get("result", {}) or {}).get("error")),
        "warning": ((merged.get("result", {}) or {}).get("warning")),
    }
    history = list(existing.get("history", []) or [])
    if merged.get("action") and merged.get("status") != "idle":
        history.append(entry)
    merged["history"] = history[-24:]
    if entry.get("error"):
        merged["latest_error"] = entry["error"]
        merged["last_failed_action"] = {"action": entry.get("action"), "ts": entry.get("ts"), "error": entry.get("error")}
    if entry.get("warning"):
        merged["latest_warning"] = entry["warning"]
    _ensure_parent_dir(path)
    safe_write_text(path, json.dumps(merged, ensure_ascii=False, indent=2), safe_mode=False, project_dir_for_backup=os.path.dirname(path) or None)
    return merged


def _project_names(runtime_cfg: Dict[str, Any]) -> List[str]:
    projects = dict(runtime_cfg.get("projects", {}) or {})
    names = sorted(projects.keys())
    project_setup_name = str((runtime_cfg.get("project_setup", {}) or {}).get("name", "") or "")
    if project_setup_name and project_setup_name not in names:
        names.append(project_setup_name)
    return names or ["METAOS_Project"]


def apply_console_presets(runtime_cfg: Dict[str, Any]) -> Dict[str, Any]:
    runtime_cfg = deepcopy(dict(runtime_cfg or {}))
    runtime_cfg.setdefault("console", {})
    runtime_cfg.setdefault("projects", {})
    preset_state = dict(runtime_cfg.get("presets", {}) or {})
    project_preset = PROJECT_PRESETS.get(str(preset_state.get("project", "Steady Series")), {})
    platform_preset = PLATFORM_PRESETS.get(str(preset_state.get("platform", "Munpia Standard")), {})
    genre_key = str(preset_state.get("genre", "A"))
    genre_preset = GENRE_PRESETS.get(genre_key, GENRE_PRESETS["A"])

    merged = deepcopy(runtime_cfg)
    for patch in (
        project_preset,
        platform_preset,
        {"project_setup": {"genre_bucket": genre_key}, "evaluation": genre_preset.get("evaluation", {})},
    ):
        merged = _deep_merge(merged, patch)

    merged.setdefault("project_setup", {})
    project_name = str(merged["project_setup"].get("name", merged.get("console", {}).get("current_project", "METAOS_Project")))
    merged["console"]["current_project"] = project_name
    merged["project_setup"]["name"] = project_name
    merged["project_setup"]["genre_bucket"] = genre_key
    merged["paths"] = _deep_merge(get_project_paths(project_name), dict(merged.get("paths", {}) or {}))
    project_entry = _deep_merge(
        {
            "project_setup": dict(merged.get("project_setup", {}) or {}),
            "paths": get_project_paths(project_name),
        },
        dict((merged.get("projects", {}) or {}).get(project_name, {}) or {}),
    )
    project_entry["project_setup"] = _deep_merge(project_entry.get("project_setup", {}), dict(merged.get("project_setup", {}) or {}))
    project_entry["paths"] = _deep_merge(get_project_paths(project_name), dict(project_entry.get("paths", {}) or {}))
    merged["projects"][project_name] = project_entry
    return merged


def build_confirmation_summary(runtime_cfg: Dict[str, Any], action: str, target_track: str | None = None) -> Dict[str, Any]:
    runtime_cfg = apply_console_presets(runtime_cfg)
    project_setup = dict(runtime_cfg.get("project_setup", {}) or {})
    return {
        "action": action,
        "project": str(project_setup.get("name", "METAOS_Project")),
        "track_scope": target_track or f"{configured_track_count(runtime_cfg, 1)} tracks",
        "release_cadence": f"{runtime_cfg.get('release_cadence', {}).get('mode', 'queue_loop')} / {configured_loop_steps(runtime_cfg, 1)} steps",
        "repair_budget": int((runtime_cfg.get("evaluation", {}) or {}).get("causal_repair_retry_budget", 2) or 2),
        "revision_passes": int((runtime_cfg.get("evaluation", {}) or {}).get("max_revision_passes", 2) or 2),
        "portfolio_mode": str((runtime_cfg.get("portfolio", {}) or {}).get("mode", "balanced")),
        "generation_enabled": bool(runtime_cfg.get("generation_enabled", True)),
    }


def requires_confirmation(action: str, loop_active: bool = False) -> bool:
    if action == "pause":
        return bool(loop_active)
    return action in HIGH_IMPACT_ACTIONS


def save_runtime_snapshot(runtime_cfg: Dict[str, Any], snapshot_name: str) -> Dict[str, Any]:
    runtime_cfg = apply_console_presets(runtime_cfg)
    snapshots = dict(runtime_cfg.get("snapshots", {}) or {})
    saved = dict(snapshots.get("saved", {}) or {})
    saved[str(snapshot_name)] = {
        "saved_at": _now(),
        "runtime_config": deepcopy(runtime_cfg),
    }
    snapshots["saved"] = saved
    if not snapshots.get("last_stable"):
        snapshots["last_stable"] = saved[str(snapshot_name)]
    runtime_cfg["snapshots"] = snapshots
    return runtime_cfg


def load_runtime_snapshot(runtime_cfg: Dict[str, Any], snapshot_name: str) -> Dict[str, Any]:
    snapshots = dict((runtime_cfg.get("snapshots", {}) or {}).get("saved", {}) or {})
    snap = dict(snapshots.get(str(snapshot_name), {}) or {})
    return apply_console_presets(dict(snap.get("runtime_config", runtime_cfg)))


def restore_last_stable_config(runtime_cfg: Dict[str, Any]) -> Dict[str, Any]:
    snap = dict((runtime_cfg.get("snapshots", {}) or {}).get("last_stable", {}) or {})
    return apply_console_presets(dict(snap.get("runtime_config", runtime_cfg)))


def initialize_console_state(
    runtime_config_path: str = DEFAULT_RUNTIME_CONFIG_PATH,
    system_status_path: str = DEFAULT_SYSTEM_STATUS_PATH,
    policy_action_path: str = POLICY_ACTION_PATH,
) -> Dict[str, Any]:
    runtime_cfg = apply_console_presets(load_runtime_config(runtime_config_path))
    save_runtime_config(runtime_cfg, path=runtime_config_path)
    paths = dict(runtime_cfg.get("paths", {}) or {})
    system_status_path = str(paths.get("system_status_path", system_status_path))
    policy_action_path = str(paths.get("policy_action_path", policy_action_path))
    if not os.path.exists(system_status_path):
        _ensure_parent_dir(system_status_path)
        safe_write_text(
            system_status_path,
            json.dumps({"updated_at": _now(), "system_status": {}, "runtime_config": runtime_cfg}, ensure_ascii=False, indent=2),
            safe_mode=False,
            project_dir_for_backup=os.path.dirname(system_status_path) or None,
        )
    if not os.path.exists(policy_action_path):
        save_policy_action({}, path=policy_action_path)
    return {
        "runtime_config": runtime_cfg,
        "system_status": read_json_file(system_status_path),
        "policy_action": load_policy_action(policy_action_path),
    }


def _resolve_output_dir(cfg: Dict[str, Any]) -> str:
    track_dir = str(((cfg.get("track", {}) or {}).get("dir", "")) or "")
    if track_dir:
        path = os.path.join(track_dir, "outputs")
    else:
        project_name = str(((cfg.get("project", {}) or {}).get("name", "project")) or "project")
        path = get_project_paths(project_name)["project_output_dir"]
    os.makedirs(path, exist_ok=True)
    return path


def _latest_metrics_across_outputs(tracks_root: str, standalone_out_dir: str | None = None, limit: int = 10) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    output_dirs: List[str] = []
    if standalone_out_dir and os.path.isdir(standalone_out_dir):
        output_dirs.append(standalone_out_dir)
    if os.path.isdir(tracks_root):
        for track_dir in list_track_dirs(tracks_root):
            output_dirs.append(os.path.join(track_dir, "outputs"))
    seen = set()
    for output_dir in output_dirs:
        metrics_path = os.path.join(output_dir, "metrics.jsonl")
        if metrics_path in seen:
            continue
        seen.add(metrics_path)
        for row in read_recent_metrics(metrics_path, limit=limit):
            row = dict(row)
            row["_output_dir"] = output_dir
            records.append(row)
    records.sort(key=lambda item: str(item.get("ts", "")), reverse=True)
    return records[:limit]


def build_reliability_report(runtime_cfg: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, Any]:
    runtime_cfg = apply_console_presets(runtime_cfg)
    paths = dict(runtime_cfg.get("paths", {}) or {})
    out_dir = _resolve_output_dir(cfg)
    system_status = read_json_file(paths["system_status_path"]).get("system_status", {})
    balanced_history = list(system_status.get("balanced_total_history", []) or [])
    axis_history = dict(system_status.get("axis_history", {}) or {})
    latest_metrics = _latest_metrics_across_outputs(paths["tracks_root"], standalone_out_dir=out_dir, limit=12)
    last_simulation = {}
    if latest_metrics:
        last_simulation = dict((latest_metrics[0].get("simulation", {}) or {}))
    drift = detect_quality_drift(balanced_history, lookback=min(5, len(balanced_history) or 1))
    axis_drift = detect_axis_drift(axis_history, lookback=min(5, max([len(v) for v in axis_history.values()] or [1])))
    return {
        "checked_at": _now(),
        "system_status_available": bool(system_status),
        "balanced_total_history_size": len(balanced_history),
        "quality_drift": drift,
        "axis_drift": axis_drift,
        "warnings": list(system_status.get("warnings", []) or []),
        "rollback_signal": bool(system_status.get("rollback_signal", False)),
        "latest_simulation": last_simulation,
        "latest_metrics_count": len(latest_metrics),
    }


def build_error_warning_panel(system_status_payload: Dict[str, Any], policy_action_payload: Dict[str, Any]) -> Dict[str, Any]:
    system_status = dict(system_status_payload.get("system_status", system_status_payload) or {})
    warnings = list(system_status.get("warnings", []) or [])
    drift = dict(system_status.get("drift", {}) or {})
    axis_drift = dict(system_status.get("axis_drift", {}) or {})
    latest_warning = warnings[-1] if warnings else policy_action_payload.get("latest_warning")
    latest_error = policy_action_payload.get("latest_error")
    return {
        "latest_warning": latest_warning,
        "latest_error": latest_error,
        "rollback_signal": bool(system_status.get("rollback_signal", False)),
        "drift_status": {
            "quality": drift,
            "axis": axis_drift,
        },
        "last_failed_action": policy_action_payload.get("last_failed_action"),
    }


def build_history_trends(system_status_payload: Dict[str, Any], policy_action_payload: Dict[str, Any]) -> Dict[str, Any]:
    system_status = dict(system_status_payload.get("system_status", system_status_payload) or {})
    release_history = [
        item for item in list(policy_action_payload.get("history", []) or [])
        if item.get("action") in {"release_plan", "auto_loop", "generate", "pause", "resume_generation", "ignore_release_once"}
    ]
    drift_history = []
    drift = dict(system_status.get("drift", {}) or {})
    if drift:
        drift_history.append({"ts": system_status_payload.get("updated_at"), "drop": drift.get("drop", 0.0), "warning": drift.get("warning", False)})
    return {
        "balanced_total_trend": list(system_status.get("balanced_total_history", []) or []),
        "repair_rate_trend": list(system_status.get("repair_rate_history", []) or []),
        "drift_history": drift_history,
        "release_decision_history": release_history,
        "portfolio_signal_trend": list(system_status.get("portfolio_signal_history", []) or []),
    }


def build_operator_overrides(runtime_cfg: Dict[str, Any], action: str, target_track: str | None = None, note: str | None = None) -> Dict[str, Any]:
    runtime_cfg = apply_console_presets(runtime_cfg)
    overrides = dict(runtime_cfg.get("operator_overrides", {}) or {})
    if action == "hold_track" and target_track:
        overrides["held_tracks"] = sorted(set(list(overrides.get("held_tracks", []) or []) + [target_track]))
    elif action == "boost_track" and target_track:
        overrides["boosted_tracks"] = sorted(set(list(overrides.get("boosted_tracks", []) or []) + [target_track]))
    elif action == "ignore_release_once" and target_track:
        overrides["ignored_recommendations"] = (list(overrides.get("ignored_recommendations", []) or []) + [{"track": target_track, "ts": _now(), "note": note or ""}])[-12:]
    elif action == "resume_generation":
        runtime_cfg["generation_enabled"] = True
    elif action == "pause":
        runtime_cfg["generation_enabled"] = False
    runtime_cfg["operator_overrides"] = overrides
    return runtime_cfg


def build_episode_review_items(tracks_root: str, limit: int = 8) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if not os.path.isdir(tracks_root):
        return items
    for track_dir in list_track_dirs(tracks_root):
        output_dir = os.path.join(track_dir, "outputs")
        if not os.path.isdir(output_dir):
            continue
        episode_files = [name for name in os.listdir(output_dir) if name.startswith("episode_") and name.endswith(".txt")]
        for name in sorted(episode_files):
            path = os.path.join(output_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception:
                text = ""
            stem = name.replace(".txt", "")
            base_episode = stem.split("_v")[0]
            items.append(
                {
                    "track": os.path.basename(track_dir),
                    "name": name,
                    "base_episode": base_episode,
                    "path": path,
                    "preview": text[:500],
                    "modified_ts": os.path.getmtime(path),
                }
            )
    items.sort(key=lambda item: float(item.get("modified_ts", 0.0)), reverse=True)
    grouped: Dict[tuple[str, str], List[Dict[str, Any]]] = {}
    for item in items:
        grouped.setdefault((item["track"], item["base_episode"]), []).append(item)
    review_items: List[Dict[str, Any]] = []
    for (_track, _base), versions in grouped.items():
        versions.sort(key=lambda item: item["name"])
        latest = versions[-1]
        previous = versions[-2] if len(versions) >= 2 else None
        review_items.append(
            {
                "track": latest["track"],
                "episode": latest["base_episode"],
                "latest": latest,
                "previous": previous,
                "has_repaired_version": previous is not None,
            }
        )
    review_items.sort(key=lambda item: float(item["latest"].get("modified_ts", 0.0)), reverse=True)
    return review_items[:limit]


def build_home_dashboard(runtime_cfg: Dict[str, Any], system_status_payload: Dict[str, Any], policy_action_payload: Dict[str, Any]) -> Dict[str, Any]:
    runtime_cfg = apply_console_presets(runtime_cfg)
    system_status = dict(system_status_payload.get("system_status", system_status_payload) or {})
    error_panel = build_error_warning_panel(system_status_payload, policy_action_payload)
    track_root = str((runtime_cfg.get("paths", {}) or {}).get("tracks_root", ""))
    track_count = len(list_track_dirs(track_root)) if os.path.isdir(track_root) else 0
    return {
        "current_project": str((runtime_cfg.get("project_setup", {}) or {}).get("name", "METAOS_Project")),
        "current_mode": str((runtime_cfg.get("console", {}) or {}).get("mode", "simple")),
        "loop_status": str(system_status.get("iteration_state", "idle") or "idle"),
        "active_tracks": track_count,
        "balanced_total": (list(system_status.get("balanced_total_history", []) or [])[-1] if system_status.get("balanced_total_history") else None),
        "drift": dict(system_status.get("drift", {}) or {}),
        "latest_warning": error_panel.get("latest_warning"),
        "latest_error": error_panel.get("latest_error"),
        "next_recommended_action": "pause" if error_panel.get("rollback_signal") else "release_plan" if track_count else "generate",
    }


def request_policy_action(action: str, payload: Dict[str, Any] | None = None, path: str = POLICY_ACTION_PATH) -> Dict[str, Any]:
    return save_policy_action(
        {
            "requested_at": _now(),
            "action": action,
            "status": "requested",
            "payload": dict(payload or {}),
            "result": {},
        },
        path=path,
    )


def execute_policy_action(
    config_path: str = "config.yaml",
    runtime_config_path: str = DEFAULT_RUNTIME_CONFIG_PATH,
    policy_action_path: str = POLICY_ACTION_PATH,
) -> Dict[str, Any]:
    action_state = load_policy_action(policy_action_path)
    action = str(action_state.get("action", "idle") or "idle")
    payload = dict(action_state.get("payload", {}) or {})
    runtime_cfg = apply_console_presets(load_runtime_config(runtime_config_path))
    save_runtime_config(runtime_cfg, path=runtime_config_path)
    cfg, runtime_cfg = load_runtime_config_into_cfg(load_config(config_path), runtime_config_path)
    cfg["safe_mode"] = bool(cfg.get("safe_mode", True))
    paths = dict(runtime_cfg.get("paths", {}) or {})
    tracks_root = str(paths.get("tracks_root", get_project_paths((runtime_cfg.get("project_setup", {}) or {}).get("name", "METAOS_Project"))["tracks_root"]))
    out_dir = _resolve_output_dir(cfg)

    result: Dict[str, Any] = {"action": action, "executed_at": _now()}
    status = "completed"
    warning = None
    try:
        if action == "generate":
            from .state import StateStore
            from .track_loop import run_queue_loop
            from .track_queue import start_queue

            track_dirs = list_track_dirs(tracks_root)
            limited = track_dirs[: configured_track_count(runtime_cfg, len(track_dirs) or 1)]
            if limited:
                start_queue(track_dirs=limited, cfg=cfg)
                ok, message = run_queue_loop(cfg, max_steps=1)
                result["queue"] = {"ok": ok, "message": message}
            else:
                from .cost import CostTracker
                from .external_rank import ExternalRankSignals
                from .openai_client import LLM
                from .pipeline import generate_episode

                state = StateStore(os.path.join(out_dir, "state.json"), safe_mode=bool(cfg.get("safe_mode", False)), project_dir_for_backup=out_dir)
                state.load()
                llm = LLM(cfg)
                cost = CostTracker(cfg, out_dir)
                ext = ExternalRankSignals(cfg)
                episode = int(state.get("next_episode", 1) or 1)
                record = generate_episode(cfg, state, llm, cost, ext, episode)
                state.save()
                cost.write_summary()
                result["episode"] = {"episode": episode, "record_keys": sorted(record.keys())}
        elif action == "auto_loop":
            from .state import StateStore
            from .track_loop import run_queue_loop
            from .track_queue import start_queue

            track_dirs = list_track_dirs(tracks_root)
            limited = track_dirs[: configured_track_count(runtime_cfg, len(track_dirs) or 1)]
            if limited:
                start_queue(track_dirs=limited, cfg=cfg)
                ok, message = run_queue_loop(cfg, max_steps=configured_loop_steps(runtime_cfg, default_steps=1))
                result["queue"] = {"ok": ok, "message": message}
            else:
                from .cost import CostTracker
                from .external_rank import ExternalRankSignals
                from .openai_client import LLM
                from .pipeline import generate_episode

                state = StateStore(os.path.join(out_dir, "state.json"), safe_mode=bool(cfg.get("safe_mode", False)), project_dir_for_backup=out_dir)
                state.load()
                llm = LLM(cfg)
                cost = CostTracker(cfg, out_dir)
                ext = ExternalRankSignals(cfg)
                ran = []
                for _ in range(configured_loop_steps(runtime_cfg, default_steps=1)):
                    episode = int(state.get("next_episode", 1) or 1)
                    generate_episode(cfg, state, llm, cost, ext, episode)
                    ran.append(episode)
                    state.save()
                cost.write_summary()
                result["episodes"] = ran
        elif action == "release_plan":
            result["release_plan"] = build_cross_track_release_plan(tracks_root)
        elif action == "reliability_check":
            result["reliability"] = build_reliability_report(runtime_cfg, cfg)
        elif action == "restore_last_stable":
            restored = restore_last_stable_config(runtime_cfg)
            save_runtime_config(restored, path=runtime_config_path)
            result["runtime_config"] = restored
        elif action == "load_snapshot":
            snapshot_name = str(payload.get("snapshot_name", "") or "")
            restored = load_runtime_snapshot(runtime_cfg, snapshot_name)
            save_runtime_config(restored, path=runtime_config_path)
            result["runtime_config"] = restored
        elif action == "save_snapshot":
            snapshot_name = str(payload.get("snapshot_name", "manual_snapshot") or "manual_snapshot")
            saved_runtime = save_runtime_snapshot(runtime_cfg, snapshot_name)
            save_runtime_config(saved_runtime, path=runtime_config_path)
            result["runtime_config"] = saved_runtime
        elif action in {"pause", "stop"}:
            from .track_queue import pause_queue

            runtime_cfg["generation_enabled"] = False
            save_runtime_config(runtime_cfg, path=runtime_config_path)
            paused = pause_queue()
            result["queue"] = paused
        elif action in OPERATOR_OVERRIDE_ACTIONS:
            updated_runtime = build_operator_overrides(runtime_cfg, action, target_track=payload.get("track"), note=payload.get("note"))
            if action == "resume_generation":
                warning = "Queue resume is requested through control-plane state."
            if action == "mark_review":
                review_state = dict(updated_runtime.get("review_state", {}) or {})
                review_state["review_queue"] = (list(review_state.get("review_queue", []) or []) + [payload])[-24:]
                updated_runtime["review_state"] = review_state
            elif action == "mark_hold":
                review_state = dict(updated_runtime.get("review_state", {}) or {})
                review_state["held_episodes"] = (list(review_state.get("held_episodes", []) or []) + [payload])[-24:]
                updated_runtime["review_state"] = review_state
            elif action == "mark_approve":
                review_state = dict(updated_runtime.get("review_state", {}) or {})
                review_state["approved_episodes"] = (list(review_state.get("approved_episodes", []) or []) + [payload])[-24:]
                updated_runtime["review_state"] = review_state
            save_runtime_config(updated_runtime, path=runtime_config_path)
            result["runtime_config"] = updated_runtime
            result["warning"] = warning
        else:
            result["message"] = "No executable action requested."
    except Exception as exc:
        status = "failed"
        result["error"] = repr(exc)

    return save_policy_action(
        {
            "action": action,
            "status": status,
            "executed_at": _now(),
            "result": result,
        },
        path=policy_action_path,
    )
