from __future__ import annotations
from typing import List, Dict, Tuple

def enforce_boost_cap_platform_bucket(tracks: List[Dict]) -> List[Dict]:
    """tracks items keys: dir, platform, bucket, desired_phase, priority_score (lower is better)
    Keeps 1 BOOST per (platform,bucket) by best priority_score.
    """
    groups: Dict[Tuple[str,str], List[Dict]] = {}
    for t in tracks:
        key=(t.get("platform",""), t.get("bucket",""))
        groups.setdefault(key, []).append(t)

    out=[]
    for key, items in groups.items():
        boost=[x for x in items if x.get("desired_phase")=="BOOST"]
        keep=set()
        if boost:
            boost_sorted=sorted(boost, key=lambda x: float(x.get("priority_score", 999.0)))
            keep.add(id(boost_sorted[0]))
        for x in items:
            y=dict(x)
            if y.get("desired_phase")=="BOOST" and id(x) not in keep:
                y["desired_phase"]="STABILIZE"
                y["downgraded"]=True
            out.append(y)
    return out
