from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from .track_loader import list_track_dirs


def _load_json(path: str) -> Dict[str, Any]:
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


def build_cross_track_release_plan(tracks_root: str, last_n: int = 8) -> Dict[str, Any]:
    tracks: List[Dict[str, Any]] = []
    for track_dir in list_track_dirs(tracks_root):
        track = _load_json(os.path.join(track_dir, "track.json"))
        rows = _load_jsonl(os.path.join(track_dir, "outputs", "metrics.jsonl"))[-last_n:]
        if rows:
            mean_retention = sum(float((row.get("retention", {}) or {}).get("predicted_next_episode", 0.0) or 0.0) for row in rows) / len(rows)
            mean_repetition = sum(float((row.get("scores", {}) or {}).get("repetition_score", 0.0) or 0.0) for row in rows) / len(rows)
        else:
            mean_retention = 0.0
            mean_repetition = 0.0
        tracks.append(
            {
                "track": os.path.basename(track_dir),
                "platform": (track.get("project", {}) or {}).get("platform", "UNKNOWN"),
                "bucket": (track.get("project", {}) or {}).get("genre_bucket", "UNKNOWN"),
                "mean_retention": mean_retention,
                "fatigue": mean_repetition,
            }
        )
    tracks.sort(key=lambda item: (item["platform"], -item["mean_retention"], item["fatigue"], item["track"]))
    per_platform_slot: Dict[str, int] = {}
    release_plan: List[Dict[str, Any]] = []
    interference = 0
    for track in tracks:
        platform = str(track["platform"])
        slot = per_platform_slot.get(platform, 0)
        per_platform_slot[platform] = slot + 1
        if track["fatigue"] >= 0.24:
            action = "hold"
        elif slot == 0 and track["mean_retention"] >= 0.68:
            action = "accelerate"
        else:
            action = "stagger"
        if slot >= 1:
            interference += 1
        release_plan.append(
            {
                "track": track["track"],
                "platform": platform,
                "slot_offset": slot,
                "action": action,
            }
        )
    return {
        "release_plan": release_plan,
        "interference_pressure": min(10, interference * 2),
        "platform_clusters": {platform: count for platform, count in per_platform_slot.items()},
    }


def refresh_queue_release_runtime(queue_state: Dict[str, Any], tracks_root: str) -> Dict[str, Any]:
    queue_state = dict(queue_state or {})
    plan = build_cross_track_release_plan(tracks_root)
    runtime: Dict[str, Dict[str, Any]] = {}
    for item in plan.get("release_plan", []) or []:
        runtime[str(item.get("track"))] = {
            "action": str(item.get("action", "stagger") or "stagger"),
            "slot_offset": int(item.get("slot_offset", 0) or 0),
            "hold_budget": 1 if item.get("action") == "hold" else 0,
            "accelerate_budget": 1 if item.get("action") == "accelerate" else 0,
            "executed": 0,
        }
    queue_state["release_runtime"] = runtime
    queue_state["release_runtime_meta"] = {
        "interference_pressure": int(plan.get("interference_pressure", 0) or 0),
        "platform_clusters": dict(plan.get("platform_clusters", {}) or {}),
    }
    return queue_state


def resolve_queue_release_action(queue_state: Dict[str, Any], track_dir: str) -> Dict[str, Any]:
    queue_state = dict(queue_state or {})
    runtime = dict(queue_state.get("release_runtime", {}) or {})
    entry = dict(runtime.get(os.path.basename(track_dir), {}) or {})
    if not entry:
        return {"action": "stagger", "slot_offset": 0, "hold_budget": 0, "accelerate_budget": 0}
    if int(entry.get("hold_budget", 0) or 0) > 0:
        return entry
    if int(entry.get("accelerate_budget", 0) or 0) > 0:
        return entry
    entry["action"] = "stagger"
    return entry


def apply_queue_release_outcome(queue_state: Dict[str, Any], track_dir: str, executed: bool) -> Dict[str, Any]:
    queue_state = dict(queue_state or {})
    runtime = dict(queue_state.get("release_runtime", {}) or {})
    key = os.path.basename(track_dir)
    entry = dict(runtime.get(key, {}) or {})
    action = str(entry.get("action", "stagger") or "stagger")
    should_advance = True
    alignment = 0.55
    if action == "hold":
        entry["hold_budget"] = max(0, int(entry.get("hold_budget", 0) or 0) - 1)
        should_advance = True
        alignment = 0.78
    elif action == "accelerate" and executed and int(entry.get("accelerate_budget", 0) or 0) > 0:
        entry["accelerate_budget"] = max(0, int(entry.get("accelerate_budget", 0) or 0) - 1)
        entry["executed"] = int(entry.get("executed", 0) or 0) + 1
        should_advance = False
        alignment = 0.9
    elif action == "accelerate":
        should_advance = True
        alignment = 0.75
    else:
        alignment = 0.7
    runtime[key] = entry
    queue_state["release_runtime"] = runtime
    queue_state["last_release_action"] = {
        "track": key,
        "action": action,
        "alignment": alignment,
        "executed": bool(executed),
        "slot_offset": int(entry.get("slot_offset", 0) or 0),
    }
    return {"queue_state": queue_state, "should_advance": should_advance, "runtime_action": queue_state["last_release_action"]}


def apply_runtime_release_to_state(state_data: Dict[str, Any], runtime_action: Dict[str, Any]) -> Dict[str, Any]:
    story_state = state_data.setdefault("story_state_v2", {})
    control = story_state.setdefault("control", {})
    runtime = control.setdefault("runtime_release", {
        "action": "balanced",
        "alignment": 0.0,
        "slot_offset": 0,
        "hold_budget": 0,
        "accelerate_budget": 0,
        "history": [],
    })
    memory = story_state.setdefault("portfolio_memory", {})
    runtime.update(
        {
            "action": str(runtime_action.get("action", "balanced") or "balanced"),
            "alignment": float(runtime_action.get("alignment", 0.0) or 0.0),
            "slot_offset": int(runtime_action.get("slot_offset", 0) or 0),
            "hold_budget": int(runtime_action.get("hold_budget", 0) or 0),
            "accelerate_budget": int(runtime_action.get("accelerate_budget", 0) or 0),
            "history": (list(runtime.get("history", []) or []) + [dict(runtime_action)])[-6:],
        }
    )
    memory["release_strategy"] = "focused" if runtime["action"] == "accelerate" else "staggered" if runtime["action"] == "hold" else memory.get("release_strategy", "balanced")
    memory["release_guard"] = min(10, max(0, int(memory.get("release_guard", 5) or 5) + int(runtime["alignment"] >= 0.75)))
    return runtime
