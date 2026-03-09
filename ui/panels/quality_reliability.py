import streamlit as st

from .shared import t


def render(lang: str, reliability: dict, history: dict, visible_fields: set[str]):
    st.subheader("품질 / 신뢰성" if lang == "ko" else "Quality / Reliability")
    st.toggle("드리프트 감지" if lang == "ko" else "Drift detection", key="drift_check_enabled", value=bool(reliability.get("drift_check_enabled", True)))
    if "simulation_horizons" in visible_fields:
        st.text_input("시뮬레이션 구간" if lang == "ko" else "Simulation horizons", key="horizons_text", value=",".join(str(item) for item in reliability.get("simulation_horizons", [30, 60, 120])))
    st.subheader("이력 / 추세" if lang == "ko" else "History / Trends")
    c1, c2 = st.columns(2)
    if history["balanced_total_trend"]:
        c1.line_chart(history["balanced_total_trend"])
    else:
        c1.caption(t("no_data", lang))
    if history["repair_rate_trend"]:
        c2.line_chart(history["repair_rate_trend"])
    else:
        c2.caption(t("no_data", lang))
    st.write("드리프트 이력" if lang == "ko" else "Drift history")
    st.json(history["drift_history"])
    st.write("릴리즈 결정 이력" if lang == "ko" else "Release decision history")
    st.json(history["release_decision_history"])
    st.write("포트폴리오 신호 추세" if lang == "ko" else "Portfolio signal trend")
    st.json(history["portfolio_signal_trend"])
