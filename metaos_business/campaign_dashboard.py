from __future__ import annotations
import csv, os
import streamlit as st
from typing import List, Dict
from .roi_optimizer import compute_roi, select_best_campaign

def _read_csv(path: str) -> List[Dict]:
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r)

def render(campaign_csv_path: str):
    st.subheader("Campaign ROI")
    rows = _read_csv(campaign_csv_path)
    if not rows:
        st.info("No campaign inputs. Upload/prepare campaign_input.csv (template provided).")
        return
    for r in rows:
        res = compute_roi(r.get("spend",0), r.get("revenue",0))
        r["roi"] = res.roi
    best = select_best_campaign(rows)
    if best:
        st.metric("Best campaign ROI", f"{best['roi']*100:.2f}%")
        st.caption(f"Best: {best.get('campaign')}  spend={best.get('spend')}  revenue={best.get('revenue')}")
    st.dataframe(rows, use_container_width=True)
