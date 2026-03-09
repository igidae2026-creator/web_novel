import streamlit as st


def render(lang: str, release_cadence: dict, release_scheduler: dict, visible_fields: set[str]):
    st.subheader("릴리즈 스케줄러" if lang == "ko" else "Release Scheduler")
    c1, c2 = st.columns(2)
    c1.selectbox("릴리즈 모드" if lang == "ko" else "Release mode", ["queue_loop", "manual"], key="cadence_mode", index=["queue_loop", "manual"].index(str(release_cadence.get("mode", "queue_loop")) if str(release_cadence.get("mode", "queue_loop")) in ["queue_loop", "manual"] else "queue_loop"))
    c2.number_input("루프 스텝" if lang == "ko" else "Loop steps", min_value=1, max_value=20, key="steps_per_run", value=int(release_cadence.get("steps_per_run", 1)), step=1)
    if "window_count" in visible_fields:
        c3, c4 = st.columns(2)
        c3.selectbox("릴리즈 전략" if lang == "ko" else "Release strategy", ["adaptive", "guarded", "balanced"], key="scheduler_strategy", index=["adaptive", "guarded", "balanced"].index(str(release_scheduler.get("strategy", "adaptive")) if str(release_scheduler.get("strategy", "adaptive")) in ["adaptive", "guarded", "balanced"] else "adaptive"))
        c4.slider("예약 윈도우" if lang == "ko" else "Reservation windows", 1, 8, key="window_count", value=int(release_scheduler.get("window_count", 6)), step=1)
