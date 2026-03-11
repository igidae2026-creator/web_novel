from __future__ import annotations
import os, json
from typing import Dict, Any, List
from engine.track_loader import list_track_dirs
from engine.event_log import read_recent

def summarize_portfolio(tracks_root: str = os.path.join("domains","webnovel","tracks")) -> Dict[str, Any]:
    track_dirs = list_track_dirs(tracks_root)
    by_platform: Dict[str, Dict[str, Any]] = {}
    total = 0
    for td in track_dirs:
        total += 1
        try:
            tj = json.load(open(os.path.join(td, "track.json"), "r", encoding="utf-8"))
        except Exception:
            continue
        plat = tj.get("project", {}).get("platform", "UNKNOWN")
        bucket = tj.get("project", {}).get("genre_bucket", "UNKNOWN")
        phase = str(tj.get("phase", "STABILIZE")).upper()
        out = by_platform.setdefault(plat, {"tracks":0, "BOOST":0, "STABILIZE":0, "buckets":{}, "downgrades":0})
        out["tracks"] += 1
        out[phase] = out.get(phase, 0) + 1
        out["buckets"][bucket] = out["buckets"].get(bucket, 0) + 1
        # count recent downgrade events
        ev = read_recent(os.path.join(td, "outputs"), n=50)
        out["downgrades"] += sum(1 for e in ev if e.get("type")=="boost_downgraded")
    return {"total_tracks": total, "platforms": by_platform}
