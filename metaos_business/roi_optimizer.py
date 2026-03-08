from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ROIResult:
    spend: float
    revenue: float
    roi: float   # (revenue - spend) / spend

def compute_roi(spend: float, revenue: float) -> ROIResult:
    spend = float(spend or 0.0)
    revenue = float(revenue or 0.0)
    roi = ((revenue - spend) / spend) if spend > 0 else 0.0
    return ROIResult(spend=spend, revenue=revenue, roi=roi)

def select_best_campaign(campaigns: List[Dict]) -> Optional[Dict]:
    """Pick the campaign with max ROI. Expected keys: spend, revenue."""
    best = None
    best_roi = None
    for c in campaigns:
        r = compute_roi(c.get("spend", 0), c.get("revenue", 0))
        if best is None or r.roi > best_roi:
            best = {**c, "roi": r.roi}
            best_roi = r.roi
    return best
