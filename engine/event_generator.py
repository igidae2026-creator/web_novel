from __future__ import annotations

from typing import Any, Dict, List


EVENT_TYPES = ["reveal", "betrayal", "reversal", "loss", "arrival"]


def _recent_events(state: Dict[str, Any]) -> List[str]:
    return list(state.get("story_events", []) or [])[-3:]


def _choose_type(state: Dict[str, Any], episode: int) -> str:
    conflict = state.get("conflict_engine", {})
    character = state.get("character_arcs", {}).get("protagonist", {})
    recent = _recent_events(state)
    consequence = int(conflict.get("consequence_level", 4) or 4)
    urgency = int(character.get("urgency", 6) or 6)
    mode = str(conflict.get("escalation_mode", "complication"))

    if mode in {"sacrifice", "collateral_damage"} and "loss" not in recent:
        return "loss"
    if mode == "power_reversal" and "reversal" not in recent:
        return "reversal"
    if urgency >= 8 and "betrayal" not in recent:
        return "betrayal"
    if consequence >= 7 and "arrival" not in recent:
        return "arrival"
    if episode % 5 == 0 and "reveal" not in recent:
        return "reveal"

    for event_type in EVENT_TYPES:
        if event_type not in recent:
            return event_type
    return EVENT_TYPES[episode % len(EVENT_TYPES)]


def generate_event_plan(state: Dict[str, Any], episode: int) -> Dict[str, Any]:
    conflict = state.get("conflict_engine", {})
    character = state.get("character_arcs", {}).get("protagonist", {})
    threads = conflict.get("threads", []) or []
    target_thread = None
    for thread in threads:
        if thread.get("status") != "resolved":
            target_thread = thread
            break
    target_thread = target_thread or {
        "id": "free-thread",
        "label": "새 갈등",
        "stake": "주도권",
        "consequence": "대가 상승",
        "heat": 5,
    }

    event_type = _choose_type(state, episode)
    consequence_level = int(conflict.get("consequence_level", 4) or 4)
    threat_pressure = int(conflict.get("threat_pressure", 5) or 5)
    urgency = int(character.get("urgency", 6) or 6)

    consequence_map = {
        "reveal": "숨겨진 정보가 드러나며 기존 선택의 비용이 올라간다",
        "betrayal": "믿었던 축이 무너지며 다음 회차의 의사결정 비용이 급등한다",
        "reversal": "우세하던 쪽이 불리해지며 규칙이 뒤집힌다",
        "loss": "지켜야 할 것을 잃고 즉시 복구할 수 없는 손실이 남는다",
        "arrival": "새 인물 또는 세력이 도착해 판의 규모와 위험을 키운다",
    }
    trigger_map = {
        "reveal": "주인공이 감추려던 사실이 더 이상 숨겨지지 않는다",
        "betrayal": "관계 압박이 임계점을 넘으며 내부에서 칼이 나온다",
        "reversal": "기존 우위가 함정으로 바뀌며 판이 뒤집힌다",
        "loss": "지연 또는 오판의 대가가 회수된다",
        "arrival": "바깥에서 더 큰 압력이 본편 갈등 안으로 진입한다",
    }

    plan = {
        "type": event_type,
        "trigger": trigger_map[event_type],
        "target_thread": target_thread.get("id"),
        "target_label": target_thread.get("label"),
        "stakes": target_thread.get("stake"),
        "consequence": consequence_map[event_type],
        "carryover_pressure": min(10, max(consequence_level, threat_pressure, urgency)),
        "heat": min(10, int(target_thread.get("heat", 5) or 5) + 1),
    }

    state["event_plan"] = plan
    return plan


def register_story_event(state: Dict[str, Any], event_plan: Dict[str, Any]) -> None:
    history = list(state.get("story_events", []) or [])
    event_type = str((event_plan or {}).get("type", "")).strip()
    if event_type:
        history.append(event_type)
    state["story_events"] = history[-8:]


def event_prompt_payload(event_plan: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": event_plan.get("type"),
        "trigger": event_plan.get("trigger"),
        "target_thread": event_plan.get("target_thread"),
        "target_label": event_plan.get("target_label"),
        "stakes": event_plan.get("stakes"),
        "consequence": event_plan.get("consequence"),
        "carryover_pressure": event_plan.get("carryover_pressure"),
        "heat": event_plan.get("heat"),
    }
