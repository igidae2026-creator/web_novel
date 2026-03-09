import streamlit as st

from .shared import t


def render(lang: str, policy_action_payload: dict, review_items: list[dict], request_action, runtime_payload: dict):
    st.subheader("출력 검토" if lang == "ko" else "Outputs Review")
    st.write("정책 액션 상태" if lang == "ko" else "Policy action state")
    st.json(policy_action_payload)
    st.subheader("검토" if lang == "ko" else "Review")
    if review_items:
        labels = [f"{item['track']} / {item['episode']}" for item in review_items]
        st.selectbox("검토 대상 에피소드" if lang == "ko" else "Episode review item", labels, key="review_choice")
        selected = next(item for item in review_items if f"{item['track']} / {item['episode']}" == st.session_state["review_choice"])
        c1, c2 = st.columns(2)
        with c1:
            st.caption("최신 버전" if lang == "ko" else "Latest version")
            st.caption(selected["latest"]["path"])
            st.text(selected["latest"]["preview"])
        with c2:
            st.caption("이전 / 수정 전 버전" if lang == "ko" else "Previous / repaired comparison")
            if selected["previous"]:
                st.caption(selected["previous"]["path"])
                st.text(selected["previous"]["preview"])
            else:
                st.caption(t("no_data", lang))
        payload = {"track": selected["track"], "episode": selected["episode"]}
        c3, c4, c5 = st.columns(3)
        if c3.button("검토 표시" if lang == "ko" else "Mark review", use_container_width=True):
            request_action("mark_review", runtime_payload, False, payload)
        if c4.button("보류 표시" if lang == "ko" else "Mark hold", use_container_width=True):
            request_action("mark_hold", runtime_payload, False, payload)
        if c5.button("승인 표시" if lang == "ko" else "Mark approve", use_container_width=True):
            request_action("mark_approve", runtime_payload, False, payload)
    else:
        st.caption(t("no_data", lang))
