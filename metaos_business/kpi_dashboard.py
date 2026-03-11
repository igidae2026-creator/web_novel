from __future__ import annotations
import csv, os
import streamlit as st
from typing import List, Dict
from .kpi_engine import cohort_retention

def _read_csv(path: str) -> List[Dict]:
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r)

def render_cohort(cohort_csv_path: str):
    st.subheader("Cohort Retention")
    rows = _read_csv(cohort_csv_path)
    if not rows:
        st.info("No cohort file provided. You can create your own CSV with columns day, active_users, cohort_size(optional).")
        return
    curve = cohort_retention(rows)
    if not curve:
        st.warning("Could not compute retention.")
        return
    st.json(curve)
