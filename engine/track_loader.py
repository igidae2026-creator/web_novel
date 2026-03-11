from __future__ import annotations
import os, json
from typing import Dict, Any

def list_track_dirs(tracks_root: str) -> list[str]:
    out=[]
    if not os.path.exists(tracks_root):
        return out
    for d in sorted(os.listdir(tracks_root)):
        p=os.path.join(tracks_root,d)
        if os.path.isdir(p) and os.path.exists(os.path.join(p,"track.json")):
            out.append(p)
    return out

def load_track(track_dir: str) -> Dict[str, Any]:
    path = os.path.join(track_dir, "track.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
