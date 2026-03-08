import os, csv
from datetime import datetime
from dateutil.parser import parse as dt_parse
from .ceiling import top_percent_from_rank

def _to_bool(v) -> bool:
    s = str(v).strip().lower()
    return s in ["1","true","yes","y","t"]

def _to_int(v, default=0) -> int:
    try:
        return int(float(v))
    except Exception:
        return default

def _to_float(v, default=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default

class ExternalRankSignals:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.path = cfg.get("external", {}).get("rank_signals_csv", "")
        self.rows = []
        self.ts = datetime.now().isoformat(timespec="seconds")
        self.load()

    def load(self):
        self.ts = datetime.now().isoformat(timespec="seconds")
        self.rows = []
        if self.path and os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8-sig", newline="") as f:
                r = csv.DictReader(f)
                self.rows = list(r)

    def snapshot(self) -> dict:
        return {"ts": self.ts, "rows": self.rows}

    def _filter(self, platform: str, genre_bucket: str):
        rows = self.rows
        exact = [x for x in rows if x.get("platform","") == platform and x.get("genre_bucket","") == genre_bucket]
        if exact:
            return exact
        plat = [x for x in rows if x.get("platform","") == platform]
        return plat if plat else rows

    def latest(self, platform: str, genre_bucket: str):
        self.load()
        rows = self._filter(platform, genre_bucket)
        if not rows:
            return None
        # sort by date if present
        def key(row):
            try:
                return dt_parse(row.get("date","1970-01-01")).timestamp()
            except Exception:
                return 0
        rows = sorted(rows, key=key)
        row = rows[-1]
        N = _to_int(row.get("chart_size", 0), 0)
        r = _to_int(row.get("rank", 0), 0)
        out = {
            "date": row.get("date",""),
            "platform": row.get("platform",""),
            "genre_bucket": row.get("genre_bucket",""),
            "chart_size": N,
            "rank": r,
            "event_flag": _to_bool(row.get("event_flag","false")),
            "notes": row.get("notes","")
        }
        if N > 0 and r > 0:
            out["top_percent"] = top_percent_from_rank(r, N)
        return out

    def slope(self, platform: str, genre_bucket: str, window: int = 5) -> float:
        self.load()
        rows = self._filter(platform, genre_bucket)
        if len(rows) < 2:
            return 0.0
        def key(row):
            try:
                return dt_parse(row.get("date","1970-01-01")).timestamp()
            except Exception:
                return 0
        rows = sorted(rows, key=key)[-max(2, int(window)):]
        pts = []
        for i, row in enumerate(rows):
            N = _to_int(row.get("chart_size", 0), 0)
            r = _to_int(row.get("rank", 0), 0)
            if N > 0 and r > 0:
                pts.append((i, top_percent_from_rank(r, N)))
        if len(pts) < 2:
            return 0.0
        # simple linear slope
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x_mean = sum(xs)/len(xs)
        y_mean = sum(ys)/len(ys)
        num = sum((x-x_mean)*(y-y_mean) for x,y in pts)
        den = sum((x-x_mean)**2 for x in xs) or 1e-9
        return num/den
