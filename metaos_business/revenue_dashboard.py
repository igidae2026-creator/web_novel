from __future__ import annotations
import csv, os
import streamlit as st
from typing import List, Dict
from .revenue_funnel import compute_funnel, merge_funnels
from .kpi_engine import compute_kpi

def _read_csv(path: str) -> List[Dict]:
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r)

def render(revenue_csv_path: str):
    st.subheader("Revenue Funnel (Exposure → Click → Purchase → Repurchase)")
    rows = _read_csv(revenue_csv_path)
    if not rows:
        st.info("No revenue inputs. Upload/prepare revenue_input.csv (template provided).")
        return

    # filter controls
    platforms = sorted(set(r.get("platform","") for r in rows if r.get("platform","")))
    platform = st.selectbox("Platform filter", ["(all)"] + platforms, index=0)
    if platform != "(all)":
        rows = [r for r in rows if r.get("platform","") == platform]

    # aggregate
    total_f = None
    total_rev = 0.0
    total_pu = 0
    retention = None
    for r in rows:
        f = compute_funnel(r)
        total_f = f if total_f is None else merge_funnels(total_f, f)
        try: total_rev += float(r.get("revenue",0) or 0)
        except Exception: pass
        try: total_pu += int(float(r.get("paying_users",0) or 0))
        except Exception: pass
        if r.get("retention_d7") not in (None, ""):
            try: retention = float(r.get("retention_d7"))
            except Exception: pass

    if total_f is None:
        st.warning("No valid rows.")
        return

    kpi = compute_kpi(total_f, total_rev, total_pu, retention_d7=retention)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Exposures", total_f.exposures)
    c2.metric("CTR", f"{kpi.ctr*100:.2f}%")
    c3.metric("CVR", f"{kpi.cvr*100:.2f}%")
    c4.metric("Repurchase", f"{total_f.repurchase_rate*100:.2f}%")

    c5, c6, c7 = st.columns(3)
    c5.metric("Revenue", f"{total_rev:,.0f}")
    c6.metric("ARPPU", f"{kpi.arppu:,.2f}")
    c7.metric("LTV (proxy)", f"{kpi.ltv:,.2f}")

    st.caption("Note: LTV here is a simple proxy based on repurchase rate. Replace with your true cohort LTV if available.")
