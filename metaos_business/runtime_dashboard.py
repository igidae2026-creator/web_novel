from __future__ import annotations

import streamlit as st

from engine.runtime_config import list_latest_episodes, read_json_file, read_recent_metrics


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
