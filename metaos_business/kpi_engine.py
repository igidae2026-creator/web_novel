from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple
from .revenue_funnel import FunnelMetrics

@dataclass
class KPI:
    arppu: float          # Average Revenue Per Paying User
    ltv: float            # Lifetime Value (simple proxy)
    cvr: float            # Conversion rate clicks->purchase
    ctr: float            # Click-through rate
    retention_d7: float   # 7-day retention proxy (manual input supported)

def compute_arppu(total_revenue: float, paying_users: int) -> float:
    return (total_revenue / paying_users) if paying_users else 0.0

def compute_ltv(arppu: float, avg_repurchase: float) -> float:
    # Simple LTV proxy: ARPPU * (1 + avg_repurchase)
    return arppu * (1.0 + max(0.0, avg_repurchase))

def compute_kpi(
    funnel: FunnelMetrics,
    total_revenue: float,
    paying_users: int,
    retention_d7: Optional[float] = None,
) -> KPI:
    arppu = compute_arppu(total_revenue, paying_users)
    ltv = compute_ltv(arppu, funnel.repurchase_rate)
    return KPI(
        arppu=arppu,
        ltv=ltv,
        cvr=funnel.cvr,
        ctr=funnel.ctr,
        retention_d7=float(retention_d7) if retention_d7 is not None else 0.0,
    )

def cohort_retention(cohort: List[Dict], day_key: str = "day", active_key: str = "active_users") -> Dict[int, float]:
    """Return retention curve {day: retention_rate}, where day0=1.0 if provided.
    cohort rows expected: day(int), active_users(int), cohort_size(int optional)
    """
    if not cohort:
        return {}
    def to_int(v, d=0):
        try: return int(float(v))
        except Exception: return d

    # cohort_size: prefer explicit else use day 0 active_users
    cohort_size = None
    for r in cohort:
        if "cohort_size" in r and r["cohort_size"] not in (None, ""):
            cohort_size = to_int(r["cohort_size"], 0)
            break
    if cohort_size is None:
        day0 = next((r for r in cohort if to_int(r.get(day_key,0),0)==0), None)
        cohort_size = to_int(day0.get(active_key, 0), 0) if day0 else max(to_int(r.get(active_key,0),0) for r in cohort)

    out = {}
    for r in cohort:
        day = to_int(r.get(day_key, 0), 0)
        active = to_int(r.get(active_key, 0), 0)
        out[day] = (active / cohort_size) if cohort_size else 0.0
    return dict(sorted(out.items()))
