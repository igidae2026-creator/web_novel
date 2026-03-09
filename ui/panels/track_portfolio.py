import os

import streamlit as st


def render(lang: str, paths: dict, portfolio: dict, request_action, runtime_payload: dict):
    st.subheader("트랙 / 포트폴리오" if lang == "ko" else "Track / Portfolio")
    st.selectbox("포트폴리오 모드" if lang == "ko" else "Portfolio mode", ["balanced", "focused", "explore"], key="portfolio_mode", index=["balanced", "focused", "explore"].index(str(portfolio.get("mode", "balanced")) if str(portfolio.get("mode", "balanced")) in ["balanced", "focused", "explore"] else "balanced"))
    track_dirs = sorted(os.listdir(paths["tracks_root"])) if os.path.isdir(paths["tracks_root"]) else []
    st.metric("트랙 수" if lang == "ko" else "Tracks", len(track_dirs))
    if track_dirs:
        st.dataframe([{"track": item} for item in track_dirs], use_container_width=True)
    st.subheader("운영자 오버라이드" if lang == "ko" else "Operator Override")
    st.selectbox("대상 트랙" if lang == "ko" else "Target track", ["(none)"] + track_dirs, key="override_track")
    st.text_input("메모" if lang == "ko" else "Note", key="override_note", value=st.session_state.get("override_note", ""))
    c1, c2, c3, c4, c5 = st.columns(5)
    disabled = st.session_state.get("override_track") == "(none)"
    if c1.button("트랙 보류" if lang == "ko" else "Hold track", use_container_width=True, disabled=disabled):
        request_action("hold_track", runtime_payload, False, {"track": st.session_state["override_track"], "note": st.session_state["override_note"]})
    if c2.button("트랙 부스트" if lang == "ko" else "Boost track", use_container_width=True, disabled=disabled):
        request_action("boost_track", runtime_payload, False, {"track": st.session_state["override_track"], "note": st.session_state["override_note"]})
    if c3.button("릴리즈 1회 무시" if lang == "ko" else "Ignore release once", use_container_width=True, disabled=disabled):
        request_action("ignore_release_once", runtime_payload, False, {"track": st.session_state["override_track"], "note": st.session_state["override_note"]})
    if c4.button("안전 일시정지" if lang == "ko" else "Safe pause", use_container_width=True):
        request_action("pause", dict(runtime_payload, generation_enabled=False), True, {"note": st.session_state["override_note"]})
    if c5.button("생성 재개" if lang == "ko" else "Resume generation", use_container_width=True):
        request_action("resume_generation", dict(runtime_payload, generation_enabled=True), False, {"note": st.session_state["override_note"]})
