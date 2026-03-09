import streamlit as st

from engine.control_console import GENRE_PRESETS, PLATFORM_PRESETS, PROJECT_PRESETS


def render(lang: str, project_setup: dict, presets: dict, visible_fields: set[str]):
    st.subheader("프로젝트 설정" if lang == "ko" else "Project Setup")
    st.selectbox("프로젝트 프리셋" if lang == "ko" else "Project preset", list(PROJECT_PRESETS.keys()), key="project_preset", index=list(PROJECT_PRESETS.keys()).index(str(presets.get("project", "Steady Series"))))
    st.selectbox("플랫폼 프리셋" if lang == "ko" else "Platform preset", list(PLATFORM_PRESETS.keys()), key="platform_preset", index=list(PLATFORM_PRESETS.keys()).index(str(presets.get("platform", "Munpia Standard"))))
    st.selectbox("장르 프리셋" if lang == "ko" else "Genre preset", list(GENRE_PRESETS.keys()), key="genre_preset", index=list(GENRE_PRESETS.keys()).index(str(presets.get("genre", "A"))))
    c1, c2, c3 = st.columns(3)
    c1.text_input("프로젝트 이름" if lang == "ko" else "Project name", key="project_name", value=str(project_setup.get("name", "METAOS_Project")))
    c2.selectbox("플랫폼" if lang == "ko" else "Platform", ["Joara", "Munpia", "NaverSeries", "KakaoPage", "Ridibooks", "Novelpia"], key="platform_name", index=["Joara", "Munpia", "NaverSeries", "KakaoPage", "Ridibooks", "Novelpia"].index(str(project_setup.get("platform", "Munpia"))))
    c3.selectbox("장르 버킷" if lang == "ko" else "Genre bucket", list(GENRE_PRESETS.keys()), key="genre_bucket", index=list(GENRE_PRESETS.keys()).index(str(project_setup.get("genre_bucket", "A"))))
    if "sub_engine" in visible_fields:
        st.text_input("서브 엔진" if lang == "ko" else "Sub-engine", key="sub_engine", value=str(project_setup.get("sub_engine", "AUTO")))
    if "target_total_episodes" in visible_fields:
        c4, c5 = st.columns(2)
        c4.number_input("목표 총 화수" if lang == "ko" else "Target episodes", min_value=1, max_value=2000, key="target_total_episodes", value=int(project_setup.get("target_total_episodes", 300)), step=10)
        c5.number_input("초반 집중 화수" if lang == "ko" else "Early focus episodes", min_value=1, max_value=20, key="early_focus_episodes", value=int(project_setup.get("early_focus_episodes", 3)), step=1)
