from __future__ import annotations
from typing import Dict, List
from .kpi_engine import cohort_retention

def summarize_cohort(cohort_rows: List[Dict]) -> Dict:
    curve = cohort_retention(cohort_rows)
    d0 = curve.get(0, 1.0)
    d1 = curve.get(1, 0.0)
    d7 = curve.get(7, 0.0)
    return {
        "curve": curve,
        "d1": d1,
        "d7": d7,
    }
