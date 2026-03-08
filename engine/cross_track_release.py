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
