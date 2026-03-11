from __future__ import annotations

from typing import Any, Dict

from .story_state import ensure_story_state, sync_story_state


PHASES = ["probing", "positioning", "constriction", "domination", "collapse_harvest"]


def _clamp(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def prepare_antagonist_plan(
    state: Dict[str, Any],
    episode: int,
    event_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    antagonist = story_state["antagonist"]
    conflict = story_state["conflict"]
    world = story_state["world"]
    relationships = story_state["relationships"]
    event_plan = dict(event_plan or {})

    threat = int(conflict.get("threat_pressure", 5) or 5)
    consequence = int(conflict.get("consequence_level", 5) or 5)
    instability = int(world.get("instability", 4) or 4)
    ally_trust = int(relationships.get("protagonist:ally", {}).get("trust", 5) or 5)
    chemistry = int(relationships.get("protagonist:rival", {}).get("chemistry", 5) or 5)
    event_type = str(event_plan.get("type", "")).strip()

    phase_idx = min(len(PHASES) - 1, max(0, (threat + consequence + instability - 12) // 3))
    antagonist["campaign_phase"] = PHASES[phase_idx]
    antagonist["pressure_clock"] = _clamp(3 + phase_idx + int(event_type in {"loss", "collapse", "betrayal"}))
    antagonist["foresight"] = _clamp(5 + phase_idx + chemistry // 4)

    if ally_trust <= 4:
        antagonist["next_move"] = "조력자와 주인공의 불신을 증폭시킨다"
        antagonist["contingency"] = "불신이 실패하면 공개 망신으로 압박을 전환한다"
    elif instability >= 7:
        antagonist["next_move"] = "무너진 질서를 이용해 힘의 규칙을 재편한다"
        antagonist["contingency"] = "질서 재편이 지연되면 타이머를 걸어 선택지를 닫는다"
    elif consequence >= 7:
        antagonist["next_move"] = "주인공이 구할 수 없는 두 선택지를 동시에 강요한다"
        antagonist["contingency"] = "정면 압박이 먹히지 않으면 조력자를 미끼로 쓴다"
    else:
        antagonist["next_move"] = "주인공의 약점을 시험하며 작은 승리를 함정으로 바꾼다"
        antagonist["contingency"] = "탐색이 실패하면 정보를 흘려 관계를 갈라놓는다"

    antagonist["horizon_beats"] = [
        antagonist["next_move"],
        antagonist["contingency"],
        "결정적 순간에 주도권을 탈취한다",
    ]

    state["story_state_v2"] = story_state
    sync_story_state(state)
    return antagonist


def antagonist_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    antagonist = story_state["antagonist"]
    return {
        "master_intent": antagonist.get("master_intent"),
        "campaign_phase": antagonist.get("campaign_phase"),
        "next_move": antagonist.get("next_move"),
        "contingency": antagonist.get("contingency"),
        "pressure_clock": antagonist.get("pressure_clock"),
        "foresight": antagonist.get("foresight"),
        "horizon_beats": antagonist.get("horizon_beats", [])[:3],
    }
