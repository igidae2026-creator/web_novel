from __future__ import annotations

import streamlit as st

from engine.runtime_config import list_latest_episodes, read_json_file, read_recent_metrics, summarize_hidden_reader_risk


def render(system_status_path: str, metrics_path: str, tracks_root: str, standalone_out_dir: str, limit: int = 5) -> None:
    st.subheader("Runtime Control Panel")
    system_status = read_json_file(system_status_path)
    if system_status:
        st.json(system_status)
    else:
        st.info("No system_status.json yet.")

    metrics_rows = read_recent_metrics(metrics_path, limit=limit)
    if metrics_rows:
        with st.expander("Recent metrics.jsonl", expanded=False):
            st.json(metrics_rows)
    else:
        st.caption("No metrics.jsonl records yet.")

    hidden_risk_summary = summarize_hidden_reader_risk(tracks_root=tracks_root, limit=limit)
    st.subheader("Hidden Reader Risk")
    if hidden_risk_summary["tracks"]:
        c1, c2, c3 = st.columns(3)
        c1.metric("Mean hidden-risk trend", f"{float(hidden_risk_summary.get('mean_hidden_reader_risk_trend', 0.0) or 0.0):.2f}")
        c2.metric("Critical tracks", int(hidden_risk_summary.get("critical_tracks", 0) or 0))
        c3.metric("Mean reader-signal trend", f"{float(hidden_risk_summary.get('mean_heavy_reader_signal_trend', 0.0) or 0.0):.2f}")
        st.caption(f"Weak signal tracks: {int(hidden_risk_summary.get('weak_signal_tracks', 0) or 0)}")
        with st.expander("Track risk summary", expanded=False):
            st.json(hidden_risk_summary["tracks"])
    else:
        st.caption("No final-threshold risk summaries yet.")

    latest_episodes = list_latest_episodes(tracks_root=tracks_root, standalone_out_dir=standalone_out_dir, limit=limit)
    st.subheader("Latest Episodes")
    if not latest_episodes:
        st.caption("No generated episodes yet.")
        return
    for item in latest_episodes:
        label = f"{item.get('track')} / {item.get('name')}"
        with st.expander(label, expanded=False):
            st.caption(item.get("path"))
            st.text(item.get("preview", ""))
