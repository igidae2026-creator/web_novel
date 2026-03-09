import streamlit as st

from .shared import t


AXIS_LABELS = {
    "title_fitness": "제목 적합도",
    "milestone_compliance": "마일스톤 준수",
    "conversion_readiness": "유료 전환 준비도",
    "protagonist_sovereignty": "주인공 주권",
    "narrative_debt_health": "내러티브 부채 건강도",
    "emotion_wave_health": "감정 파형 건강도",
    "ip_readiness": "IP 확장 준비도",
}


def render(lang: str, studio_os: dict, visible_fields: set[str], request_action=None, runtime_payload: dict | None = None):
    st.subheader("스튜디오 OS 신호" if lang == "ko" else "Studio OS Signals")
    cards = list(studio_os.get("cards", []) or [])
    if not cards:
        st.caption(t("no_data", lang))
        return

    cols = st.columns(4)
    for index, card in enumerate(cards):
        label = AXIS_LABELS.get(card["axis"], card["axis"]) if lang == "ko" else card["axis"]
        value = card.get("value")
        suffix = "경고" if card.get("status") == "warning" and lang == "ko" else "warning" if card.get("status") == "warning" else ""
        cols[index % 4].metric(label, "-" if value is None else round(float(value), 4), suffix)

    st.write("최신 사업 신호" if lang == "ko" else "Latest business signals")
    st.json(studio_os.get("latest_business_signals", {}))

    title_state = dict(studio_os.get("latest_title_state", {}) or {})
    st.write("제목 / 런치 패키지" if lang == "ko" else "Title / Launch Package")
    st.json(
        {
            "selected_title": title_state.get("selected_title"),
            "rationale": title_state.get("selected_title_rationale", []),
            "launch_recommendation": title_state.get("launch_recommendation", {}),
            "ranked_candidates": title_state.get("ranked_candidates", []),
        }
    )

    st.write("최근 개정 트리거" if lang == "ko" else "Latest revision triggers")
    st.json(studio_os.get("latest_revision_triggers", []))

    st.write("권장 운영 액션" if lang == "ko" else "Recommended operator actions")
    recommendations = list(studio_os.get("recommendations", []) or [])
    if recommendations:
        for item in recommendations:
            st.json(item)
            if request_action and runtime_payload is not None:
                label = f"권장 액션 적용: {item['action_type']}" if lang == "ko" else f"Apply: {item['action_type']}"
                if st.button(label, key=f"apply_{item['id']}", use_container_width=True):
                    request_action("apply_business_adjustment", runtime_payload, False, {"recommendation_id": item["id"]})
    else:
        st.caption(t("no_data", lang))

    st.write("축별 추세" if lang == "ko" else "Axis trends")
    trend_cols = st.columns(2)
    for index, card in enumerate(cards):
        target = trend_cols[index % 2]
        target.caption(AXIS_LABELS.get(card["axis"], card["axis"]) if lang == "ko" else card["axis"])
        if card.get("trend"):
            target.line_chart(card["trend"])
        else:
            target.caption(t("no_data", lang))

    st.write("사업 축 경고" if lang == "ko" else "Business warnings")
    st.json(studio_os.get("warnings", []))
    st.write("조정 학습" if lang == "ko" else "Adjustment learning")
    st.json(studio_os.get("business_learning", {}))
    if "simulation_horizons" in visible_fields:
        st.caption("고급 모드에서는 품질/신뢰성 탭과 함께 사업 축 추세를 병행 확인한다." if lang == "ko" else "In advanced mode, review these alongside the Quality/Reliability tab.")
