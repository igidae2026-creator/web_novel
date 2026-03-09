import streamlit as st

from engine.control_console import (
    build_episode_review_items,
    build_error_warning_panel,
    build_history_trends,
    build_home_dashboard,
    get_console_mode_fields,
    initialize_console_state,
)
from engine.runtime_config import DEFAULT_RUNTIME_CONFIG_PATH, read_json_file
from .panels import dashboard, generation_control, outputs_viewer, project_setup, quality_reliability, release_scheduler, track_portfolio
from .panels.shared import (
    build_runtime_payload,
    initialize_session_state,
    load_snapshot_to_session,
    persist_runtime_config,
    request_or_execute_action,
    restore_stable_to_session,
    save_snapshot_from_session,
    t,
)
from engine.control_console import load_policy_action


def main():
    st.set_page_config(page_title="웹소설 운영 콘솔", layout="wide")
    state_bundle = initialize_console_state(DEFAULT_RUNTIME_CONFIG_PATH)
    runtime_cfg = state_bundle["runtime_config"]
    initialize_session_state(runtime_cfg)

    lang = st.sidebar.selectbox(
        "언어 / Language",
        ["ko", "en"],
        index=["ko", "en"].index(str(st.session_state.get("console_language", "ko")) if str(st.session_state.get("console_language", "ko")) in ["ko", "en"] else "ko"),
        key="console_language",
    )
    console_mode = st.sidebar.radio(
        t("mode", lang),
        ["simple", "advanced"],
        format_func=lambda item: t(item, lang),
        index=["simple", "advanced"].index(str(st.session_state.get("console_mode", "simple")) if str(st.session_state.get("console_mode", "simple")) in ["simple", "advanced"] else "simple"),
        key="console_mode",
    )

    runtime_payload = build_runtime_payload(runtime_cfg)
    runtime_payload["console"]["language"] = lang
    runtime_payload["console"]["mode"] = console_mode
    persisted_runtime = persist_runtime_config(runtime_payload)
    paths = dict(persisted_runtime.get("paths", {}) or {})
    system_status_payload = read_json_file(paths["system_status_path"])
    policy_action_payload = load_policy_action(paths["policy_action_path"])
    review_items = build_episode_review_items(paths["tracks_root"], limit=8)
    dashboard_data = build_home_dashboard(persisted_runtime, system_status_payload, policy_action_payload)
    error_panel = build_error_warning_panel(system_status_payload, policy_action_payload)
    history = build_history_trends(system_status_payload, policy_action_payload)
    visible_fields = set(get_console_mode_fields(console_mode))

    st.title(t("title", lang))
    st.caption(t("korean_first", lang))

    with st.sidebar:
        st.header(t("dashboard", lang))
        st.metric(t("project", lang), dashboard_data["current_project"])
        st.metric(t("loop_status", lang), dashboard_data["loop_status"])
        st.metric(t("active_tracks", lang), dashboard_data["active_tracks"])
        st.metric(t("balanced_total", lang), dashboard_data["balanced_total"] if dashboard_data["balanced_total"] is not None else "-")
        st.metric(t("drift", lang), dashboard_data["drift"].get("drop", "-") if isinstance(dashboard_data.get("drift"), dict) else "-")
        if st.button(t("save_config", lang), use_container_width=True):
            persist_runtime_config(build_runtime_payload(persisted_runtime))
            st.success("runtime_config.json 저장 완료" if lang == "ko" else "Saved runtime_config.json")
        st.text_input("스냅샷 이름" if lang == "ko" else "Snapshot name", key="snapshot_name")
        if st.button(t("save_snapshot", lang), use_container_width=True):
            save_snapshot_from_session(persisted_runtime)
            st.success("스냅샷 저장 완료" if lang == "ko" else "Snapshot saved")
        snapshot_keys = ["(none)"] + sorted(dict((persisted_runtime.get("snapshots", {}) or {}).get("saved", {}) or {}).keys())
        if st.session_state.get("selected_snapshot", "(none)") not in snapshot_keys:
            st.session_state["selected_snapshot"] = "(none)"
        st.selectbox("스냅샷 선택" if lang == "ko" else "Select snapshot", snapshot_keys, key="selected_snapshot")
        if st.button(t("load_snapshot", lang), use_container_width=True, disabled=st.session_state.get("selected_snapshot") == "(none)"):
            load_snapshot_to_session(persisted_runtime)
            st.rerun()
        if st.button(t("restore_stable", lang), use_container_width=True):
            restore_stable_to_session(persisted_runtime)
            st.rerun()
        st.divider()
        loop_active = str(dashboard_data.get("loop_status", "idle")) not in {"idle", "paused", "done"}
        if st.button(t("one_click_generate", lang), use_container_width=True):
            request_or_execute_action("generate", build_runtime_payload(persisted_runtime) | {"generation_enabled": True}, False, paths["policy_action_path"])
        if st.button(t("one_click_auto_loop", lang), use_container_width=True):
            request_or_execute_action("auto_loop", build_runtime_payload(persisted_runtime) | {"generation_enabled": True}, loop_active, paths["policy_action_path"])
        if st.button(t("one_click_release_plan", lang), use_container_width=True):
            request_or_execute_action("release_plan", build_runtime_payload(persisted_runtime), loop_active, paths["policy_action_path"])
        if st.button(t("one_click_reliability", lang), use_container_width=True):
            request_or_execute_action("reliability_check", build_runtime_payload(persisted_runtime), loop_active, paths["policy_action_path"])
        if st.button(t("one_click_pause", lang), use_container_width=True):
            request_or_execute_action("pause", build_runtime_payload(persisted_runtime) | {"generation_enabled": False}, loop_active, paths["policy_action_path"])

    tabs = st.tabs(
        [
            t("dashboard", lang),
            t("project_setup", lang),
            t("generation", lang),
            t("portfolio", lang),
            t("release", lang),
            t("quality", lang),
            t("outputs", lang),
        ]
    )

    with tabs[0]:
        dashboard.render(lang, dashboard_data, error_panel)
    with tabs[1]:
        project_setup.render(lang, dict(persisted_runtime.get("project_setup", {}) or {}), dict(persisted_runtime.get("presets", {}) or {}), visible_fields)
    with tabs[2]:
        generation_control.render(lang, persisted_runtime, dict(persisted_runtime.get("evaluation", {}) or {}), visible_fields)
    with tabs[3]:
        track_portfolio.render(
            lang,
            paths,
            dict(persisted_runtime.get("portfolio", {}) or {}),
            lambda action, payload, loop_active, extra=None: request_or_execute_action(action, payload, loop_active, paths["policy_action_path"], extra),
            build_runtime_payload(persisted_runtime),
        )
    with tabs[4]:
        release_scheduler.render(lang, dict(persisted_runtime.get("release_cadence", {}) or {}), dict(persisted_runtime.get("release_scheduler", {}) or {}), visible_fields)
    with tabs[5]:
        quality_reliability.render(lang, dict(persisted_runtime.get("reliability", {}) or {}), history, visible_fields)
    with tabs[6]:
        outputs_viewer.render(
            lang,
            policy_action_payload,
            review_items,
            lambda action, payload, loop_active, extra=None: request_or_execute_action(action, payload, loop_active, paths["policy_action_path"], extra),
            build_runtime_payload(persisted_runtime),
        )

    if st.session_state.get("last_action_result"):
        st.subheader("최근 실행 결과" if lang == "ko" else "Last action result")
        st.json(st.session_state["last_action_result"])
