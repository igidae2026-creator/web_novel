from __future__ import annotations

from typing import Any, Dict

from .story_state import ensure_story_state, sync_story_state


def prepare_information_emotion(state: Dict[str, Any], episode: int, event_plan: Dict[str, Any] | None = None) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    information = story_state["information"]
    event_plan = dict(event_plan or {})

    hidden = list(information.get("hidden_truths", []) or [])
    foreshadow = list(information.get("foreshadow_queue", []) or [])
    event_type = str(event_plan.get("type", "")).strip()

    if event_type in {"reveal", "betrayal", "power_shift"} and hidden:
        revealed = hidden.pop(0)
        information.setdefault("revealed_truths", []).append(revealed)
        information["revealed_truths"] = information["revealed_truths"][-6:]
    if event_type in {"loss", "sacrifice", "collapse"}:
        information["emotional_reservoir"] = min(10, int(information.get("emotional_reservoir", 5) or 5) + 2)
    else:
        information["emotional_reservoir"] = min(10, int(information.get("emotional_reservoir", 5) or 5) + 1)

    if episode % 3 == 0:
        foreshadow.append(f"{episode}화 시점의 압박이 다음 관계 파열의 씨앗이 된다")
    information["hidden_truths"] = hidden
    information["foreshadow_queue"] = foreshadow[-6:]
    information["dramatic_irony"] = min(10, len(hidden) + len(foreshadow))

    state["story_state_v2"] = story_state
    sync_story_state(state)
    return information


def information_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    information = story_state["information"]
    return {
        "hidden_truths": information.get("hidden_truths", [])[:3],
        "revealed_truths": information.get("revealed_truths", [])[-3:],
        "foreshadow_queue": information.get("foreshadow_queue", [])[-3:],
        "dramatic_irony": information.get("dramatic_irony", 0),
        "emotional_reservoir": information.get("emotional_reservoir", 0),
    }
