from __future__ import annotations

from typing import Any, Dict, List


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
    engine = state.get("conflict_engine")
    if isinstance(engine, dict) and "threads" in engine:
        return engine

    engine = {
        "threads": [
            {
                "id": "main-survival-thread",
                "label": "주인공이 밀리면 판 전체를 잃는 주 갈등",
                "heat": 5,
                "stake": "지위와 생존",
                "consequence": "주도권 상실",
                "status": "open",
            }
        ],
        "threat_pressure": 5,
        "consequence_level": 4,
        "recent_losses": 0,
        "recent_reversals": 0,
        "opposition_advantage": 4,
        "payoff_debt": 3,
        "escalation_mode": "complication",
        "last_event_type": "",
    }
    state["conflict_engine"] = engine
    return engine


def _open_threads(engine: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [thread for thread in engine.get("threads", []) if thread.get("status") != "resolved"]


def prepare_conflict_memory(state: Dict[str, Any], episode: int) -> Dict[str, Any]:
    engine = _ensure_conflict_engine(state)
    open_threads = _open_threads(engine)
    score_history = state.get("score_history", [])[-3:]
    weak_episodes = sum(
        1
        for score in score_history
        if float(score.get("hook_score", 0.0)) < 0.72 or float(score.get("escalation", 0.0)) < 0.68
    )
    character = state.get("character_arcs", {}).get("protagonist", {})
    pressure_seed = int(character.get("urgency", 5) >= 8)

    engine["threat_pressure"] = _clamp(4 + len(open_threads) + weak_episodes + pressure_seed)
    engine["consequence_level"] = _clamp(3 + max((thread.get("heat", 0) for thread in open_threads), default=3) // 2)
    engine["opposition_advantage"] = _clamp(3 + weak_episodes + engine.get("recent_losses", 0))

    mode_index = min(
        len(ESCALATION_MODES) - 1,
        max(0, engine["consequence_level"] - 3 + min(2, episode // 15)),
    )
    engine["escalation_mode"] = ESCALATION_MODES[mode_index]
    engine["open_thread_count"] = len(open_threads)
    state["conflict_engine"] = engine
    state["conflict_memory"] = engine["threat_pressure"]
    return engine


def update_conflict_memory(
    state: Dict[str, Any],
    episode: int,
    score_obj: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    engine = _ensure_conflict_engine(state)
    score_obj = dict(score_obj or {})
    event_plan = dict(event_plan or {})
    event_type = str(event_plan.get("type", "")).strip().lower()

    open_threads = _open_threads(engine)
    active_thread = open_threads[0] if open_threads else None

    if active_thread:
        active_thread["heat"] = _clamp(active_thread.get("heat", 5) + 1)

    hook = float(score_obj.get("hook_score", 0.0) or 0.0)
    escalation = float(score_obj.get("escalation", 0.0) or 0.0)

    if hook < 0.72 or escalation < 0.68:
        engine["recent_losses"] = _clamp(engine.get("recent_losses", 0) + 1)
        engine["payoff_debt"] = _clamp(engine.get("payoff_debt", 0) + 1)
    else:
        engine["recent_reversals"] = _clamp(engine.get("recent_reversals", 0) + 1)
        if active_thread and active_thread.get("heat", 0) >= 7:
            active_thread["status"] = "pressured"

    if event_type in {"loss", "betrayal"}:
        engine["recent_losses"] = _clamp(engine.get("recent_losses", 0) + 2)
        engine["consequence_level"] = _clamp(engine.get("consequence_level", 4) + 2)
        engine["threads"].append(
            {
                "id": f"thread-{episode}-{event_type}",
                "label": "새로운 후폭풍 갈등",
                "heat": 7,
                "stake": "신뢰와 생존",
                "consequence": "즉시 보복 또는 붕괴",
                "status": "open",
            }
        )
    elif event_type in {"reveal", "reversal", "arrival"}:
        engine["recent_reversals"] = _clamp(engine.get("recent_reversals", 0) + 1)
        if active_thread:
            active_thread["status"] = "reshaped"
            active_thread["consequence"] = "기존 판이 뒤집히며 더 큰 대가가 요구됨"

    prepare_conflict_memory(state, episode)
    engine["last_event_type"] = event_type
    return engine


def conflict_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    engine = _ensure_conflict_engine(state)
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
            }
            for thread in _open_threads(engine)[:3]
        ],
    }
