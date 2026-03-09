import streamlit as st


def render(lang: str, runtime_cfg: dict, evaluation: dict, visible_fields: set[str]):
    st.subheader("생성 제어" if lang == "ko" else "Generation Control")
    c1, c2 = st.columns(2)
    c1.toggle("생성 활성화" if lang == "ko" else "Generation enabled", key="generation_enabled", value=bool(runtime_cfg.get("generation_enabled", True)))
    c2.number_input("트랙 수" if lang == "ko" else "Track count", min_value=1, max_value=54, key="track_count", value=int(runtime_cfg.get("track_count", 6)), step=1)
    if "revision_passes" in visible_fields:
        c3, c4, c5 = st.columns(3)
        c3.slider("수정 패스" if lang == "ko" else "Revision passes", 1, 3, key="revision_passes", value=int(evaluation.get("max_revision_passes", 2)), step=1)
        c4.slider("수정 예산" if lang == "ko" else "Repair budget", 1, 4, key="repair_budget", value=int(evaluation.get("causal_repair_retry_budget", 2)), step=1)
        c5.toggle("바이럴 강제" if lang == "ko" else "Viral required", key="viral_required", value=bool(evaluation.get("viral_required", True)))
