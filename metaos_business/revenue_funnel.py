from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class FunnelMetrics:
    exposures: int
    clicks: int
    purchases: int
    repurchases: int

    @property
    def ctr(self) -> float:
        return (self.clicks / self.exposures) if self.exposures else 0.0

    @property
    def cvr(self) -> float:
        return (self.purchases / self.clicks) if self.clicks else 0.0

    @property
    def repurchase_rate(self) -> float:
        return (self.repurchases / self.purchases) if self.purchases else 0.0

def compute_funnel(row: Dict) -> FunnelMetrics:
    """Compute basic funnel metrics from an input row.
    Expected keys (any missing -> 0):
      exposures, clicks, purchases, repurchases
    """
    def i(k: str) -> int:
        try:
            return int(float(row.get(k, 0) or 0))
        except Exception:
            return 0

    return FunnelMetrics(
        exposures=i("exposures"),
        clicks=i("clicks"),
        purchases=i("purchases"),
        repurchases=i("repurchases"),
    )

def merge_funnels(a: FunnelMetrics, b: FunnelMetrics) -> FunnelMetrics:
    return FunnelMetrics(
        exposures=a.exposures + b.exposures,
        clicks=a.clicks + b.clicks,
        purchases=a.purchases + b.purchases,
        repurchases=a.repurchases + b.repurchases,
    )
