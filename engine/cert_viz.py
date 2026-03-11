from __future__ import annotations
import os, json, math
from typing import Dict, Any, List

def _mean(xs: List[float]) -> float:
    return sum(xs)/len(xs) if xs else 0.0

def _std(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x-m)**2 for x in xs)/(len(xs)-1))

def load_cert_series(metrics_jsonl_path: str, last_n: int = 20) -> Dict[str, Any]:
    if not metrics_jsonl_path or not os.path.exists(metrics_jsonl_path):
        return {"available": False}
    records = []
    with open(metrics_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if row.get("type") == "certification":
                rep = row.get("report", {})
                records.append(rep)
    if not records:
        return {"available": False}
    rec = records[-max(1,int(last_n)):]
    # Extract time series
    ok = []
    latest_tp = []
    std_tp = []
    band = []
    for r in rec:
        m = r.get("market", {})
        ok.append(bool(m.get("ok")))
        stats = m.get("stats", {}) if isinstance(m.get("stats", {}), dict) else {}
        latest_tp.append(float(stats.get("latest_top_percent", 0.0) or 0.0))
        std_tp.append(float(stats.get("std_top_percent", 0.0) or 0.0))
        band.append(str(m.get("band", "UNKNOWN")))
    return {
        "available": True,
        "count": len(rec),
        "ok": ok,
        "latest_top_percent": latest_tp,
        "std_top_percent": std_tp,
        "band": band,
    }

def stability_score(series: Dict[str, Any]) -> Dict[str, Any]:
    if not series.get("available"):
        return {"available": False}
    ok = series["ok"]
    latest = series["latest_top_percent"]
    stds = series["std_top_percent"]
    # Success rate
    ok_rate = sum(1 for x in ok if x) / len(ok)
    # Stability: lower std better; map to 0..1 with soft clamp at 2.0
    std_mean = _mean(stds)
    std_score = max(0.0, min(1.0, 1.0 - (std_mean/2.0)))
    # Band score: TOP3=1, TOP5=0.8, TOP10=0.6, else 0.3
    band_last = series["band"][-1] if series["band"] else "UNKNOWN"
    band_score = {"TOP3":1.0,"TOP5":0.8,"TOP10":0.6}.get(band_last, 0.3)
    score = ok_rate*0.5 + std_score*0.3 + band_score*0.2
    stable_window = (len(ok) >= 5 and sum(1 for x in ok[-5:] if x) >= 4 and std_mean <= 1.2)
    return {
        "available": True,
        "score": score,
        "ok_rate": ok_rate,
        "std_mean": std_mean,
        "band_last": band_last,
        "stable_window": stable_window,
    }
