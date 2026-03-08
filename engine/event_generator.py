from __future__ import annotations

from typing import Any, Dict, List

from .story_state import EVENT_TYPES, ensure_story_state, open_threads, sync_story_state
from .pattern_memory import choose_event_with_memory


def _recent_events(state: Dict[str, Any]) -> List[str]:
    return list(state.get("story_events", []) or [])[-3:]


def _choose_type(state: Dict[str, Any], episode: int) -> str:
    story_state = ensure_story_state(state)
    conflict = story_state.get("conflict", {})
    character = story_state.get("cast", {}).get("protagonist", {})
    world = story_state.get("world", {})
    rewards = story_state.get("rewards", {})
    antagonist = story_state.get("antagonist", {})
    recent = _recent_events(state)
    consequence = int(conflict.get("consequence_level", 5) or 5)
    urgency = int(character.get("urgency", 6) or 6)
    mode = str(conflict.get("escalation_mode", "complication"))
    instability = int(world.get("instability", 4) or 4)
    reward_density = int(rewards.get("reward_density", 5) or 5)
    next_move = str(antagonist.get("next_move", ""))

    preferred = ""
    if mode in {"irreversible_stakes", "sacrifice"} and "sacrifice" not in recent:
        preferred = "sacrifice"
    elif "불신" in next_move and "misunderstanding" not in recent:
        preferred = "misunderstanding"
    elif "타이머" in next_move and "timer" not in recent:
        preferred = "timer"
    elif "주도권" in next_move and "power_shift" not in recent:
        preferred = "power_shift"
    elif mode in {"sacrifice", "collateral_damage"} and "loss" not in recent:
        preferred = "loss"
    elif mode == "power_reversal" and "reversal" not in recent:
        preferred = "reversal"
    elif urgency >= 8 and "betrayal" not in recent:
        preferred = "betrayal"
    elif instability >= 8 and "collapse" not in recent:
        preferred = "collapse"
    elif consequence >= 7 and "arrival" not in recent:
        preferred = "arrival"
    elif reward_density <= 4 and "false_victory" not in recent:
        preferred = "false_victory"
    elif episode % 6 == 0 and "timer" not in recent:
        preferred = "timer"
    elif episode % 5 == 0 and "reveal" not in recent:
        preferred = "reveal"
    elif consequence >= 6 and "misunderstanding" not in recent and urgency <= 7:
        preferred = "misunderstanding"

    for event_type in EVENT_TYPES:
        if event_type not in recent:
            fallback = event_type
            break
    else:
        fallback = EVENT_TYPES[episode % len(EVENT_TYPES)]
    return choose_event_with_memory(state, preferred, fallback)


def generate_event_plan(state: Dict[str, Any], episode: int) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    conflict = story_state.get("conflict", {})
    character = story_state.get("cast", {}).get("protagonist", {})
    threads = open_threads(story_state)
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
    consequence_level = int(conflict.get("consequence_level", 5) or 5)
    threat_pressure = int(conflict.get("threat_pressure", 5) or 5)
    urgency = int(character.get("urgency", 6) or 6)
    chemistry = int(story_state.get("serialization", {}).get("chemistry_signal", 5) or 5)
    antagonist_move = str(story_state.get("antagonist", {}).get("next_move", "") or "")

    consequence_map = {
        "reveal": "숨겨진 정보가 드러나며 기존 선택의 비용이 올라간다",
        "betrayal": "믿었던 축이 무너지며 다음 회차의 의사결정 비용이 급등한다",
        "reversal": "우세하던 쪽이 불리해지며 규칙이 뒤집힌다",
        "loss": "지켜야 할 것을 잃고 즉시 복구할 수 없는 손실이 남는다",
        "arrival": "새 인물 또는 세력이 도착해 판의 규모와 위험을 키운다",
        "sacrifice": "얻는 대신 돌이킬 수 없는 무언가를 버려야 한다",
        "timer": "남은 시간이 줄어들며 선택지가 급격히 닫힌다",
        "power_shift": "힘의 우위가 이동해 기존 질서가 재편된다",
        "false_victory": "승리처럼 보이지만 더 큰 함정이 뒤에 열린다",
        "collapse": "세계 또는 관계 구조 일부가 실제로 무너진다",
        "misunderstanding": "엇갈린 정보가 관계와 판단을 동시에 왜곡한다",
    }
    trigger_map = {
        "reveal": "주인공이 감추려던 사실이 더 이상 숨겨지지 않는다",
        "betrayal": "관계 압박이 임계점을 넘으며 내부에서 칼이 나온다",
        "reversal": "기존 우위가 함정으로 바뀌며 판이 뒤집힌다",
        "loss": "지연 또는 오판의 대가가 회수된다",
        "arrival": "바깥에서 더 큰 압력이 본편 갈등 안으로 진입한다",
        "sacrifice": "살리기 위해 반드시 다른 것을 버려야 하는 순간이 온다",
        "timer": "기회가 닫히기 전 행동해야 하는 시한이 걸린다",
        "power_shift": "기존 규칙의 소유권이 다른 손으로 넘어간다",
        "false_victory": "부분 승리가 더 큰 포획 장치였음이 드러난다",
        "collapse": "유지되던 구조가 더 이상 버티지 못하고 붕괴한다",
        "misunderstanding": "의도와 정보가 어긋나며 관계 압박이 폭증한다",
    }

    plan = {
        "type": event_type,
        "trigger": trigger_map[event_type],
        "target_thread": target_thread.get("id"),
        "target_label": target_thread.get("label"),
        "stakes": target_thread.get("stake"),
        "consequence": consequence_map[event_type],
        "carryover_pressure": min(10, max(consequence_level, threat_pressure, urgency, chemistry)),
        "heat": min(10, int(target_thread.get("heat", 5) or 5) + 1),
        "irreversible_if_lost": target_thread.get("irreversible_if_lost", "핵심 관계 또는 세계 질서가 변형된다"),
        "antagonist_move": antagonist_move,
    }

    state["event_plan"] = plan
    return plan


def register_story_event(state: Dict[str, Any], event_plan: Dict[str, Any]) -> None:
    story_state = ensure_story_state(state)
    history = list(state.get("story_events", []) or [])
    event_type = str((event_plan or {}).get("type", "")).strip()
    if event_type:
        history.append(event_type)
    state["story_events"] = history[-8:]
    story_state["history"]["events"] = state["story_events"]
    story_state["control"]["last_event_type"] = event_type
    state["story_state_v2"] = story_state
    sync_story_state(state)


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
        "irreversible_if_lost": event_plan.get("irreversible_if_lost"),
    }
