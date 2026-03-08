
from __future__ import annotations
import random, os, json
from datetime import datetime

def simulate_rank_signals(path: str, platform: str, bucket: str, days: int = 30, chart_size: int = 100):
    # generate synthetic rank series with noise
    rows=["date,platform,genre_bucket,chart_size,rank\n"]
    r = random.randint(10, 80)
    for i in range(days):
        r += random.randint(-5,5)
        r = max(1, min(chart_size+1, r))
        dt = (datetime.now()).strftime("%Y-%m-%d")
        rows.append(f"{dt},{platform},{bucket},{chart_size},{r}\n")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path,"w",encoding="utf-8").write("".join(rows))
    return path
