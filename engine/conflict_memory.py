from __future__ import annotations

from typing import Any, Dict, List

from .story_state import ensure_story_state, open_threads, sync_story_state


ESCALATION_MODES = [
    "complication",
    "exposure",
    "sacrifice",
    "race_against_time",
    "collateral_damage",
    "power_reversal",
]


def _clamp(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def _ensure_conflict_engine(state: Dict[str, Any]) -> Dict[str, Any]:
    ensure_story_state(state)
    return state["conflict_engine"]


def _open_threads(engine: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [thread for thread in engine.get("threads", []) if thread.get("status") != "resolved"]


def prepare_conflict_memory(state: Dict[str, Any], episode: int) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    engine = story_state["conflict"]
    open_threads_list = open_threads(story_state)
    score_history = state.get("score_history", [])[-3:]
    weak_episodes = sum(
        1
        for score in score_history
        if float(score.get("hook_score", 0.0)) < 0.72 or float(score.get("escalation", 0.0)) < 0.68
    )
    protagonist = story_state["cast"]["protagonist"]
    relationships = story_state["relationships"]
    world = story_state["world"]
    antagonist = story_state.get("antagonist", {})
    pressure_seed = int(protagonist.get("urgency", 5) >= 8)

    engine["threat_pressure"] = _clamp(4 + len(open_threads_list) + weak_episodes + pressure_seed + int(world.get("instability", 4) >= 6) + int(antagonist.get("pressure_clock", 4) >= 6))
    engine["consequence_level"] = _clamp(3 + max((thread.get("heat", 0) for thread in open_threads_list), default=3) // 2 + int(world.get("change_rate", 3) >= 5))
    recent_losses = sum(1 for event in story_state["history"]["events"][-5:] if event in {"loss", "collapse", "sacrifice"})
    engine["opposition_advantage"] = _clamp(3 + weak_episodes + recent_losses + max(0, -relationships["protagonist:rival"]["charge"]) // 4 + int(antagonist.get("foresight", 5) >= 7))
    engine["payoff_debt"] = _clamp(engine.get("payoff_debt", 3) + max(0, len(open_threads_list) - 1))
    engine["risk_distribution"]["social"] = _clamp(relationships["protagonist:ally"]["relationship_debt"] + 3)
    engine["risk_distribution"]["strategic"] = _clamp(engine["opposition_advantage"] + 2)

    mode_index = min(
        len(ESCALATION_MODES) - 1,
        max(0, engine["consequence_level"] - 3 + min(2, episode // 15)),
    )
    engine["escalation_mode"] = ESCALATION_MODES[mode_index]
    if engine["consequence_level"] >= 8:
        engine["escalation_mode"] = "irreversible_stakes"
    engine["open_thread_count"] = len(open_threads_list)
    story_state["unresolved_threads"] = [
        {
            "id": thread.get("id"),
            "question": f"{thread.get('label')}은 어떤 대가로 회수될까",
            "pressure": min(10, int(thread.get("heat", 5) or 5) + int(engine["consequence_level"] >= 7)),
            "promised_payoff": thread.get("consequence"),
        }
        for thread in open_threads_list[:4]
    ]
    state["story_state_v2"] = story_state
    sync_story_state(state)
    state["conflict_memory"] = engine["threat_pressure"]
    return state["conflict_engine"]


def update_conflict_memory(
    state: Dict[str, Any],
    episode: int,
    score_obj: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    engine = story_state["conflict"]
    score_obj = dict(score_obj or {})
    event_plan = dict(event_plan or {})
    event_type = str(event_plan.get("type", "")).strip().lower()

    open_threads_list = open_threads(story_state)
    active_thread = open_threads_list[0] if open_threads_list else None

    if active_thread:
        active_thread["heat"] = _clamp(active_thread.get("heat", 5) + 1)

    hook = float(score_obj.get("hook_score", 0.0) or 0.0)
    escalation = float(score_obj.get("escalation", 0.0) or 0.0)

    if hook < 0.72 or escalation < 0.68:
        engine["payoff_debt"] = _clamp(engine.get("payoff_debt", 0) + 1)
        if active_thread and active_thread.get("heat", 0) >= 7:
            active_thread["status"] = "pressured"

    if event_type in {"loss", "betrayal", "collapse", "sacrifice"}:
        story_state["history"]["events"].extend([event_type, event_type])
        story_state["history"]["events"] = story_state["history"]["events"][-8:]
        engine["consequence_level"] = _clamp(engine.get("consequence_level", 4) + 2)
        engine["threads"].append(
            {
                "id": f"thread-{episode}-{event_type}",
                "label": "새로운 후폭풍 갈등",
                "heat": 7,
                "stake": "신뢰와 생존",
                "consequence": "즉시 보복 또는 붕괴",
                "status": "open",
                "irreversible_if_lost": "주요 관계와 세계 질서가 함께 악화된다",
            }
        )
        story_state["world"]["instability"] = _clamp(story_state["world"].get("instability", 4) + 2)
        story_state["world"]["change_rate"] = _clamp(story_state["world"].get("change_rate", 3) + 1)
    elif event_type in {"reveal", "reversal", "arrival", "power_shift", "false_victory", "timer"}:
        if active_thread:
            active_thread["status"] = "reshaped"
            active_thread["consequence"] = "기존 판이 뒤집히며 더 큰 대가가 요구됨"
        story_state["world"]["change_rate"] = _clamp(story_state["world"].get("change_rate", 3) + 1)
    if event_type == "timer":
        story_state["world"]["active_timers"].append({"episode": episode, "label": "마감 압박", "ttl": 2})
        story_state["world"]["active_timers"] = story_state["world"]["active_timers"][-4:]

    prepare_conflict_memory(state, episode)
    story_state["control"]["last_event_type"] = event_type
    state["story_state_v2"] = story_state
    sync_story_state(state)
    return state["conflict_engine"]


def conflict_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    ensure_story_state(state)
    engine = state["conflict_engine"]
    return {
        "threat_pressure": engine.get("threat_pressure", 0),
        "consequence_level": engine.get("consequence_level", 0),
        "opposition_advantage": engine.get("opposition_advantage", 0),
        "payoff_debt": engine.get("payoff_debt", 0),
        "escalation_mode": engine.get("escalation_mode", "complication"),
        "recent_losses": engine.get("recent_losses", 0),
        "recent_reversals": engine.get("recent_reversals", 0),
        "threads": [
            {
                "id": thread.get("id"),
                "label": thread.get("label"),
                "heat": thread.get("heat"),
                "stake": thread.get("stake"),
                "consequence": thread.get("consequence"),
                "status": thread.get("status"),
                "irreversible_if_lost": thread.get("irreversible_if_lost"),
            }
            for thread in _open_threads(engine)[:3]
        ],
    }
