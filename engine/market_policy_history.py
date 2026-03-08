
from __future__ import annotations
import os, json

def read_history(out_dir: str, n: int = 50):
    path = os.path.join(out_dir, "events.jsonl")
    if not os.path.exists(path):
        return []
    rows=[]
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            try:
                r=json.loads(line)
                if r.get("type")=="market_mode_changed":
                    rows.append(r)
            except:
                pass
    return rows[-n:]
