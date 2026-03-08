from __future__ import annotations

from typing import Any, Dict

from .story_state import ensure_story_state, sync_story_state


ISSUE_DIRECTIVES = {
    "event_presence": "핵심 사건 타입이 본문에 명시적으로 드러나도록 장면을 추가하라.",
    "causal_link": "선택과 결과를 이어주는 인과 문장을 반드시 넣어라.",
    "goal_pressure": "주인공의 현재 목표가 장면 행동을 직접 밀도록 수정하라.",
    "cost_payment": "대가 지불 장면을 구체화하라.",
    "relationship_fallout": "관계 후폭풍이 대사나 선택으로 드러나게 하라.",
    "world_consequence": "세계 규칙 또는 세력 변화가 사건의 결과로 보이게 하라.",
    "cliffhanger_alignment": "마지막 질문과 실제 장면 압박이 맞물리게 결말을 고쳐라.",
    "emotional_trace": "감정 흔적이 신체 반응 또는 감각으로 남게 하라.",
}


def _priority(issue: str) -> int:
    if issue in {"causal_link", "goal_pressure", "cost_payment"}:
        return 3
    if issue in {"event_presence", "world_consequence", "relationship_fallout"}:
        return 2
    return 1


def build_causal_repair_plan(
    causal_report: Dict[str, Any],
    story_state: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
    cliffhanger_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    causal_report = dict(causal_report or {})
    story_state = dict(story_state or {})
    event_plan = dict(event_plan or {})
    cliffhanger_plan = dict(cliffhanger_plan or {})

    issues = list(causal_report.get("issues", []) or [])
    critical = sorted([issue for issue in issues if _priority(issue) >= 2], key=_priority, reverse=True)
    directives = [ISSUE_DIRECTIVES[issue] for issue in sorted(issues, key=_priority, reverse=True) if issue in ISSUE_DIRECTIVES][:4]
    repair_confidence = max(
        1,
        min(
            10,
            8
            - len(critical)
            + int(bool(event_plan.get("type")))
            + int(bool(cliffhanger_plan.get("open_question")))
            + int(bool(story_state.get("information", {}).get("hidden_truths"))),
        ),
    )
    return {
        "critical_issues": critical[:3],
        "directives": directives,
        "repair_confidence": repair_confidence,
        "target_event": event_plan.get("type"),
        "target_cliffhanger_mode": cliffhanger_plan.get("mode"),
    }


def store_causal_repair_plan(state: Dict[str, Any], repair_plan: Dict[str, Any]) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    story_state["control"]["causal_repair"] = {
        "critical_issues": list(repair_plan.get("critical_issues", []) or []),
        "directives": list(repair_plan.get("directives", []) or []),
        "repair_confidence": int(repair_plan.get("repair_confidence", 5) or 5),
    }
    state["story_state_v2"] = story_state
    sync_story_state(state)
    return story_state["control"]["causal_repair"]


def repair_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    return dict(story_state.get("control", {}).get("causal_repair", {}) or {})
