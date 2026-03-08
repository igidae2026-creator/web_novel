
from __future__ import annotations
import os, json
from typing import Dict, Any

def estimate_density(out_dir: str) -> float:
    path = os.path.join(out_dir, "metrics.jsonl")
    if not os.path.exists(path):
        return 0.5
    rows=[]
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except:
                pass
    rows = rows[-20:]
    if not rows:
        return 0.5
    ups=0
    downs=0
    for r in rows:
        tp=r.get("top_percent")
        if tp is None: 
            continue
        if tp < 5: ups+=1
        else: downs+=1
    total=max(1, ups+downs)
    return downs/total
