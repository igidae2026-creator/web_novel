from __future__ import annotations
from typing import List, Dict, Tuple
import random

def wave_assign(tracks: List[Dict], seed: int = 0) -> Dict[str, List[Dict]]:
    """Assign tracks into three groups: BOOST, STABILIZE, HOLD.
    Strategy: balance by platform; default 2 platforms BOOST, 2 STABILIZE, rest HOLD.
    Tracks are dicts with keys: platform, genre_bucket, track_id, score(optional).
    """
    random.seed(seed)
    platforms = sorted(set(t.get("platform","") for t in tracks if t.get("platform","")))
    # Pick platforms for waves
    if len(platforms) <= 2:
        boost_plats = platforms
        stab_plats = []
    else:
        boost_plats = platforms[:2]
        stab_plats = platforms[2:4]
    out = {"BOOST": [], "STABILIZE": [], "HOLD": []}
    for t in tracks:
        p = t.get("platform","")
        if p in boost_plats:
            out["BOOST"].append(t)
        elif p in stab_plats:
            out["STABILIZE"].append(t)
        else:
            out["HOLD"].append(t)
    return out
