from __future__ import annotations

from typing import Any, Dict

from .story_state import chemistry_pressure, ensure_story_state, sync_story_state


CHARACTER_DEFAULTS = {
    "A": {
        "desire": "압도적인 힘으로 자신의 자리를 증명한다",
        "fear": "무력하다는 낙인이 다시 찍힌다",
        "weakness": "힘으로만 해결하려는 조급함",
        "misbelief": "정상에 오르면 누구도 자신을 버리지 못한다",
    },
    "B": {
        "desire": "숨겨진 진실을 파헤쳐 잃은 것을 되찾는다",
        "fear": "진실이 자신을 먼저 무너뜨린다",
        "weakness": "사람을 시험하고 밀어내는 습관",
        "misbelief": "누구도 믿지 않아야 살아남는다",
    },
    "default": {
        "desire": "소중한 것을 지키며 더 큰 자리를 차지한다",
        "fear": "가장 중요한 사람과 기회를 동시에 잃는다",
        "weakness": "불안이 커질수록 무리수를 둔다",
        "misbelief": "먼저 상처 주지 않으면 결국 당한다",
    },
}


def _clamp(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def _pick_defaults(bucket: str | None) -> Dict[str, str]:
    return dict(CHARACTER_DEFAULTS.get(str(bucket or "").upper(), CHARACTER_DEFAULTS["default"]))


def _infer_anchor(outline: str) -> str:
    lines = (outline or "").strip().splitlines()
    if not lines:
        return "주인공"
    line = lines[0].strip()
    return line[:80] if line else "주인공"


def _ensure_roster(state: Dict[str, Any], cfg: Dict[str, Any] | None = None, outline: str = "") -> Dict[str, Any]:
    arcs = state.get("character_arcs")
    if isinstance(arcs, dict) and arcs.get("protagonist") and arcs.get("rival"):
        return arcs

    bucket = None
    if isinstance(cfg, dict):
        bucket = cfg.get("project", {}).get("genre_bucket")
    defaults = _pick_defaults(bucket)
    anchor = _infer_anchor(outline)
    arcs = {
        "anchor": anchor,
        "protagonist": {
            "label": "protagonist",
            "anchor": anchor,
            "core_desire": defaults["desire"],
            "surface_goal": "이번 회차에서 밀린 주도권을 되찾는다",
            "fear_trigger": defaults["fear"],
            "weakness": defaults["weakness"],
            "misbelief": defaults["misbelief"],
            "urgency": 6,
            "relationship_pressure": 3,
            "progress": 0,
            "backlash": 0,
            "decision_pressure": 6,
            "dominant_need": "주도권 회복",
            "last_outcome": "unresolved",
        },
        "rival": {
            "label": "rival",
            "anchor": "주인공이 가장 경계해야 할 상대",
            "core_desire": "주인공보다 먼저 판을 지배한다",
            "surface_goal": "주인공의 약점을 공개적으로 드러낸다",
            "fear_trigger": "주인공의 성장으로 입지를 잃는다",
            "weakness": "상대를 과소평가하며 조급하게 압박한다",
            "misbelief": "상처를 깊게 주면 복종이 따라온다",
            "urgency": 5,
            "relationship_pressure": 4,
            "progress": 0,
            "backlash": 0,
            "decision_pressure": 5,
            "dominant_need": "지배력 유지",
            "last_outcome": "pressing",
        },
    }
    state["character_arcs"] = arcs
    return arcs


def prepare_character_arc(
    state: Dict[str, Any],
    cfg: Dict[str, Any] | None = None,
    outline: str = "",
    episode: int = 1,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state, cfg=cfg, outline=outline)
    cast = story_state["cast"]
    relationships = story_state["relationships"]
    world = story_state["world"]
    conflict = story_state["conflict"]
    recent_scores = state.get("score_history", [])[-3:]
    weak_finish = sum(
        1
        for score in recent_scores
        if float(score.get("hook_score", 0.0)) < 0.72 or float(score.get("escalation", 0.0)) < 0.68
    )

    protagonist = cast["protagonist"]
    rival = cast["rival"]
    ally = cast["ally"]
    rival_edge = relationships["protagonist:rival"]
    ally_edge = relationships["protagonist:ally"]
    pressure = int(conflict.get("threat_pressure", 5) or 5)
    unresolved = len([thread for thread in conflict.get("threads", []) if thread.get("status") != "resolved"])
    chemistry = chemistry_pressure(story_state)
    instability = int(world.get("instability", 4) or 4)

    protagonist["urgency"] = _clamp(4 + pressure + unresolved + weak_finish + instability // 2)
    protagonist["decision_pressure"] = _clamp(
        protagonist["urgency"]
        + rival_edge.get("relationship_debt", 0)
        + ally_edge.get("dependency", 0) // 2
        - protagonist.get("progress", 0) // 2
    )
    protagonist["surface_goal"] = (
        "이번 회차 안에 손실을 막고 관계 붕괴를 지연시키며 주도권을 일부라도 회복한다"
        if protagonist["urgency"] >= 8
        else "상대보다 먼저 움직여 판의 규칙을 자기 쪽으로 기울인다"
    )
    protagonist["inner_need"] = (
        "힘의 과시보다 누구를 지킬지 선택한다"
        if ally_edge.get("trust", 0) <= 5
        else "통제 대신 신뢰를 받아들인다"
    )
    protagonist["emotion"] = "cornered" if protagonist["urgency"] >= 8 else "strained"

    rival["urgency"] = _clamp(4 + pressure + chemistry // 2 + episode // 10)
    rival["decision_pressure"] = _clamp(rival["urgency"] + rival_edge.get("chemistry", 0) // 2 + unresolved)
    rival["surface_goal"] = (
        "주인공이 관계와 힘 사이에서 틀린 선택을 하게 만든다"
        if unresolved
        else "주인공의 약점을 다시 시험해 공개적으로 무너뜨린다"
    )
    rival["emotion"] = "obsessive" if rival_edge.get("chemistry", 0) >= 6 else "predatory"

    ally["urgency"] = _clamp(3 + instability + ally_edge.get("dependency", 0) // 2)
    ally["decision_pressure"] = _clamp(ally["urgency"] + ally_edge.get("relationship_debt", 0))
    ally["surface_goal"] = (
        "주인공을 돕되 돌이킬 수 없는 손실은 피한다"
        if world.get("order", 5) >= 5
        else "곧 올 붕괴를 대비해 숨은 출구를 마련한다"
    )

    state["character_arcs"]["episode_focus"] = {
        "pressure_sources": unresolved,
        "weak_finish_count": weak_finish,
        "episode": episode,
        "chemistry_pressure": chemistry,
    }
    state["story_state_v2"] = story_state
    sync_story_state(state)
    return state["character_arcs"]


def update_character_arc(
    state: Dict[str, Any],
    episode: int,
    score_obj: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    protagonist = story_state["cast"]["protagonist"]
    rival = story_state["cast"]["rival"]
    ally = story_state["cast"]["ally"]
    relationships = story_state["relationships"]
    score_obj = dict(score_obj or {})
    event_plan = dict(event_plan or {})

    hook = float(score_obj.get("hook_score", 0.0) or 0.0)
    escalation = float(score_obj.get("escalation", 0.0) or 0.0)
    event_type = str(event_plan.get("type", "")).strip().lower()

    if hook >= 0.75 and escalation >= 0.70:
        protagonist["progress"] = _clamp(protagonist.get("progress", 0) + 1)
        outcome = "advance"
    else:
        protagonist["backlash"] = _clamp(protagonist.get("backlash", 0) + 1)
        outcome = "setback"

    if event_type in {"loss", "betrayal", "collapse"}:
        protagonist["backlash"] = _clamp(protagonist.get("backlash", 0) + 2)
        rival["progress"] = _clamp(rival.get("progress", 0) + 1)
        relationships["protagonist:rival"]["relationship_debt"] = _clamp(relationships["protagonist:rival"].get("relationship_debt", 0) + 2)
    elif event_type in {"reveal", "reversal", "arrival", "power_shift", "false_victory"}:
        protagonist["progress"] = _clamp(protagonist.get("progress", 0) + 1)
        relationships["protagonist:rival"]["chemistry"] = _clamp(relationships["protagonist:rival"].get("chemistry", 0) + 1)
    if event_type in {"sacrifice", "misunderstanding"}:
        ally["backlash"] = _clamp(ally.get("backlash", 0) + 1)
        relationships["protagonist:ally"]["trust"] = _clamp(relationships["protagonist:ally"].get("trust", 0) - 1)

    protagonist["urgency"] = _clamp(
        protagonist.get("urgency", 6) + protagonist.get("backlash", 0) - protagonist.get("progress", 0) // 2
    )
    protagonist["decision_pressure"] = _clamp(
        protagonist.get("decision_pressure", 6) + protagonist.get("backlash", 0) - protagonist.get("progress", 0)
    )
    rival["urgency"] = _clamp(rival.get("urgency", 5) + episode // 20 + rival.get("progress", 0))
    story_state["history"]["outcomes"].append(outcome)
    story_state["history"]["outcomes"] = story_state["history"]["outcomes"][-12:]
    state["story_state_v2"] = story_state
    sync_story_state(state)
    return state["character_arcs"]


def character_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    ensure_story_state(state)
    arcs = state["character_arcs"]
    protagonist = arcs["protagonist"]
    rival = arcs["rival"]
    cast = state["story_state_v2"]["cast"]
    relationships = state["story_state_v2"]["relationships"]
    return {
        "anchor": arcs.get("anchor", "주인공"),
        "protagonist": {
            "core_desire": protagonist["core_desire"],
            "surface_goal": protagonist["surface_goal"],
            "fear_trigger": protagonist["fear_trigger"],
            "weakness": protagonist["weakness"],
            "misbelief": protagonist["misbelief"],
            "dominant_need": protagonist["dominant_need"],
            "wound": cast["protagonist"]["wound"],
            "moral_limit": cast["protagonist"]["moral_limit"],
            "obsession": cast["protagonist"]["obsession"],
            "contradiction": cast["protagonist"]["contradiction"],
            "urgency": protagonist["urgency"],
            "decision_pressure": protagonist["decision_pressure"],
            "relationship_pressure": protagonist["relationship_pressure"],
            "progress": protagonist["progress"],
            "backlash": protagonist["backlash"],
            "last_outcome": protagonist["last_outcome"],
        },
        "rival": {
            "core_desire": rival["core_desire"],
            "surface_goal": rival["surface_goal"],
            "fear_trigger": rival["fear_trigger"],
            "weakness": rival["weakness"],
            "urgency": rival["urgency"],
            "decision_pressure": rival["decision_pressure"],
            "progress": rival["progress"],
        },
        "relationships": {
            "protagonist_rival": relationships["protagonist:rival"],
            "protagonist_ally": relationships["protagonist:ally"],
        },
        "antagonist_pressure": state["story_state_v2"].get("antagonist", {}),
        "episode_focus": arcs.get("episode_focus", {}),
    }
