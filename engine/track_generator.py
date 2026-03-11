from __future__ import annotations
import os, json
from typing import List, Dict
from engine.safe_io import safe_write_text, safe_copy_bytes

DEFAULT_PLATFORMS = ["Joara","KakaoPage","Munpia","NaverSeries","Ridibooks","Novelpia"]
DEFAULT_BUCKETS = list("ABCDEFGHI")

def generate_tracks(root_dir: str, project_name: str, platforms: List[str] = None, buckets: List[str] = None) -> List[Dict]:
    platforms = platforms or DEFAULT_PLATFORMS
    buckets = buckets or DEFAULT_BUCKETS
    tracks_dir = os.path.join(root_dir, "tracks")
    os.makedirs(tracks_dir, exist_ok=True)
    created = []
    for p in platforms:
        for b in buckets:
            track_id = f"{p}_{b}".lower()
            tdir = os.path.join(tracks_dir, track_id)
            os.makedirs(tdir, exist_ok=True)
            # minimal track config
            cfg = {
                "project": {"name": project_name, "platform": p, "genre_bucket": b, "sub_engine": "AUTO"},
                "track": {"id": track_id},
                "phase": "STABILIZE",
            }
            # write track.json
            safe_write_text(os.path.join(tdir, "track.json"), json.dumps(cfg, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup=tdir)
            # initialize state.json
            safe_write_text(os.path.join(tdir, "state.json"), json.dumps({"next_episode": 1}, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup=tdir)
            created.append({"track_id": track_id, "platform": p, "bucket": b, "dir": tdir})
    # index
    safe_write_text(os.path.join(tracks_dir, "tracks_index.json"), json.dumps(created, ensure_ascii=False, indent=2), safe_mode=True, project_dir_for_backup=tracks_dir)
    return created
