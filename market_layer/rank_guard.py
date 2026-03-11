from __future__ import annotations
import csv, os, math
from datetime import datetime
from dateutil.parser import parse as dt_parse
from typing import Dict, List, Optional, Tuple

def _to_int(v, default=0):
    try: return int(float(v))
    except Exception: return default

def _to_float(v, default=0.0):
    try: return float(v)
    except Exception: return default

def _read_rows(path: str) -> List[Dict]:
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def _filter(rows: List[Dict], platform: str, bucket: str) -> List[Dict]:
    # supports both platform-only and platform+genre_bucket rows
    exact = [r for r in rows if r.get("platform","")==platform and r.get("genre_bucket","")==bucket]
    if exact: return exact
    plat = [r for r in rows if r.get("platform","")==platform]
    return plat if plat else rows

def top_percent_from_rank(rank: int, chart_size: int) -> float:
    n = max(1, int(chart_size))
    r = max(1, int(rank))
    return (r / n) * 100.0

def compute_stats(rank_signals_csv: str, platform: str, bucket: str, window: int = 7, out_of_chart_policy: str = "HOLD_LAST") -> Dict:
    rows = _filter(_read_rows(rank_signals_csv), platform, bucket)
    if not rows:
        return {"available": False}
    # sort by date
    def key(r):
        try: return dt_parse(r.get("date","1970-01-01")).timestamp()
        except Exception: return 0
    rows = sorted(rows, key=key)[-max(2, window):]
    tops=[]
    last_valid=None
    policy=str(out_of_chart_policy or "HOLD_LAST").upper().strip()
    for r in rows:
        N=_to_int(r.get("chart_size",0),0)
        rk=_to_int(r.get("rank",0),0)
        if N>0 and rk>0:
            tp=top_percent_from_rank(rk,N)
            tops.append(tp)
            last_valid=tp
        else:
            # Out-of-chart / missing
            if policy == "NA":
                continue
            if policy == "SET_101":
                if N>0:
                    tp=top_percent_from_rank(N+1, N)
                    tops.append(tp)
                    last_valid=tp
                continue
            # HOLD_LAST (default)
            if last_valid is not None:
                tops.append(last_valid)
    if not tops:
        return {"available": False}
    mean = sum(tops)/len(tops)
    var = sum((x-mean)**2 for x in tops)/max(1,len(tops)-1)
    std = math.sqrt(var)
    slope = (tops[-1]-tops[0])/(len(tops)-1) if len(tops)>1 else 0.0
    latest = tops[-1]
    return {
        "available": True,
        "latest_top_percent": latest,
        "mean_top_percent": mean,
        "std_top_percent": std,
        "slope_top_percent": slope,
        "n_points": len(tops),
        "policy_used": policy,

    }

def market_band(stats: Dict, bands: dict | None = None) -> str:
    if not stats.get("available"):
        return "UNKNOWN"
    lp = stats["latest_top_percent"]
    b = bands or {}
    t3 = float(b.get('top3', 3.0))
    t5 = float(b.get('top5', 5.0))
    t10 = float(b.get('top10', 10.0))
    t20 = float(b.get('top20', 20.0))
    if lp <= t3: return "TOP3"
    if lp <= t5: return "TOP5"
    if lp <= t10: return "TOP10"
    if lp <= t20: return "TOP20"
    return "20+"

def market_top3_achieved(stats: Dict, bands: dict | None = None, max_std: float = 1.2) -> bool:
    if not stats.get("available"):
        return False
    # 조건: 최신<=3 AND 평균<=3.5 AND slope<=0.0 (상승/유지)
    b = bands or {}
    t3 = float(b.get('top3', 3.0))
    return (stats["latest_top_percent"] <= t3 and stats["mean_top_percent"] <= (t3 + 0.5) and stats["slope_top_percent"] <= 0.0 and float(stats.get('std_top_percent',999.0)) <= float(max_std))
