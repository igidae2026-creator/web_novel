import streamlit as st

from engine.control_console import build_confirmation_summary
from .shared import execute_pending_action, t


def render(lang: str, dashboard: dict, error_panel: dict):
    st.subheader(t("dashboard", lang))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("project", lang), dashboard["current_project"])
    c2.metric(t("mode", lang), dashboard["current_mode"])
    c3.metric(t("loop_status", lang), dashboard["loop_status"])
    c4.metric(t("active_tracks", lang), dashboard["active_tracks"])
    c5, c6, c7, c8 = st.columns(4)
    c5.metric(t("balanced_total", lang), dashboard["balanced_total"] if dashboard["balanced_total"] is not None else "-")
    c6.metric(t("drift", lang), dashboard["drift"].get("drop", "-") if isinstance(dashboard.get("drift"), dict) else "-")
    c7.metric(t("latest_warning", lang), "Y" if dashboard["latest_warning"] else "N")
    c8.metric(t("latest_error", lang), "Y" if dashboard["latest_error"] else "N")
    st.info(f"{t('next_action', lang)}: {dashboard['next_recommended_action']}")

    st.subheader(t("warning_panel", lang))
    st.json(error_panel)

    st.subheader(t("confirm", lang))
    pending = st.session_state.get("pending_action")
    if pending:
        summary = build_confirmation_summary(pending["runtime_payload"], pending["action"], target_track=pending["extra_payload"].get("track"))
        st.json(summary)
        confirm = st.checkbox("이 실행을 확인합니다." if lang == "ko" else "I confirm this action.", key="confirm_pending_action")
        if st.button(t("execute", lang), key="execute_confirmed_action", use_container_width=True, disabled=not confirm):
            execute_pending_action()
            st.rerun()
    else:
        st.caption(t("no_data", lang))
