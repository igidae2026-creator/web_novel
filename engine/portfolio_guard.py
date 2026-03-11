from __future__ import annotations
from typing import List, Dict, Tuple

GRADE_RANK = {"A": 0, "B": 1, "C": 2, "D": 3}

def _grade_key(g: str) -> int:
    return GRADE_RANK.get((g or "D").upper(), 3)

def enforce_boost_cap_with_priority(
    tracks: List[Dict],
    max_per_platform: int = 1,
    priority: str = "top_percent",
) -> List[Dict]:
    """tracks items expected keys:
    - dir, platform, desired_phase, grade(optional), latest_top_percent(optional)
    Returns updated items where desired_phase may be downgraded to STABILIZE if over cap.
    """
    pr = (priority or "top_percent").lower().strip()
    by_plat: Dict[str, List[Dict]] = {}
    for t in tracks:
        by_plat.setdefault(t.get("platform",""), []).append(t)

    out: List[Dict] = []
    for plat, items in by_plat.items():
        boost_items = [x for x in items if x.get("desired_phase") == "BOOST"]
        keep = set()
        if max_per_platform <= 0:
            keep = set()
        else:
            if pr == "grade":
                boost_items_sorted = sorted(
                    boost_items,
                    key=lambda x: (_grade_key(x.get("grade","D")), float(x.get("latest_top_percent", 999.0)))
                )
            else:
                boost_items_sorted = sorted(
                    boost_items,
                    key=lambda x: (float(x.get("latest_top_percent", 999.0)), _grade_key(x.get("grade","D")))
                )
            keep = set(id(x) for x in boost_items_sorted[:max_per_platform])

        for x in items:
            y = dict(x)
            if y.get("desired_phase") == "BOOST" and id(x) not in keep:
                y["desired_phase"] = "STABILIZE"
                y["downgraded"] = True
            out.append(y)
    return out
