from __future__ import annotations

from typing import Any, Dict, List


def _contains_any(text: str, tokens: List[str]) -> bool:
    return any(token and token in text for token in tokens)


def validate_scene_causality(
    episode_text: str,
    story_state: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
    cliffhanger_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    text = str(episode_text or "")
    story_state = dict(story_state or {})
    event_plan = dict(event_plan or {})
    cliffhanger_plan = dict(cliffhanger_plan or {})

    cast = story_state.get("cast", {}) or {}
    relationships = story_state.get("relationships", {}) or {}
    world = story_state.get("world", {}) or {}
    conflict = story_state.get("conflict", {}) or {}

    protagonist = cast.get("protagonist", {}) or {}
    rival = cast.get("rival", {}) or {}
    event_type = str(event_plan.get("type", "")).strip()
    event_tokens = {
        "reveal": ["진실", "드러", "밝혀", "정체"],
        "betrayal": ["배신", "등을 돌", "속였", "칼끝"],
        "reversal": ["뒤집", "역전", "반전"],
        "loss": ["잃", "사라", "무너", "놓쳤"],
        "arrival": ["도착", "나타났", "들이닥"],
        "sacrifice": ["희생", "포기", "대가", "버렸다"],
        "timer": ["시간", "마감", "카운트", "남은"],
        "power_shift": ["힘", "권한", "우위", "주도권"],
        "false_victory": ["승리", "이긴", "함정", "덫"],
        "collapse": ["붕괴", "무너", "파열", "붕락"],
        "misunderstanding": ["오해", "엇갈", "착각", "오판"],
    }
    cause_tokens = ["때문", "그래서", "결국", "대가", "그 탓", "그 순간", "그 결과"]
    emotion_tokens = ["숨", "떨", "울", "분노", "차갑", "뜨겁", "심장", "목이", "시선"]
    world_tokens = ["규칙", "질서", "세력", "세계", "계약", "법칙", "문", "의식"]

    checks = {
        "event_presence": 1.0 if _contains_any(text, event_tokens.get(event_type, [])) else 0.0,
        "causal_link": 1.0 if _contains_any(text, cause_tokens) else 0.0,
        "goal_pressure": 1.0 if _contains_any(text, [str(protagonist.get("surface_goal", ""))[:8], "주도권", "지키", "복수", "선택"]) else 0.0,
        "cost_payment": 1.0 if _contains_any(text, ["대가", "잃", "포기", "상처", "희생", "무너"]) else 0.0,
        "relationship_fallout": 1.0 if _contains_any(text, [relationships.get("protagonist:rival", {}).get("label", ""), relationships.get("protagonist:ally", {}).get("label", ""), "신뢰", "배신", "동맹"]) else 0.0,
        "world_consequence": 1.0 if _contains_any(text, world_tokens + [str(world.get("power_rules", [""])[0])[:6], str(conflict.get("threads", [{}])[0].get("stake", ""))[:6]]) else 0.0,
        "cliffhanger_alignment": 1.0 if _contains_any(text[-220:], [str(cliffhanger_plan.get("open_question", ""))[:6], str(cliffhanger_plan.get("target", ""))[:6], "누가", "무엇", "다음"]) else 0.0,
        "emotional_trace": 1.0 if _contains_any(text, emotion_tokens) else 0.0,
    }
    score = sum(checks.values()) / len(checks)
    issues = []
    for key, passed in checks.items():
        if passed < 1.0:
            issues.append(key)

    return {
        "score": score,
        "checks": checks,
        "issues": issues,
        "passes": len(checks) - len(issues),
    }
