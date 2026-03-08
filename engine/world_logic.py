from __future__ import annotations

from typing import Any, Dict

from .story_state import ensure_story_state, sync_story_state


def update_world_state(state: Dict[str, Any], episode: int, event_plan: Dict[str, Any] | None = None) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    world = story_state["world"]
    event_plan = dict(event_plan or {})
    event_type = str(event_plan.get("type", "")).strip()

    if event_type in {"arrival", "power_shift", "collapse"}:
        world["change_rate"] = min(10, int(world.get("change_rate", 3) or 3) + 2)
        world["instability"] = min(10, int(world.get("instability", 4) or 4) + 1)
    if event_type in {"loss", "betrayal", "misunderstanding"}:
        world["order"] = max(0, int(world.get("order", 6) or 6) - 1)
    if event_type == "timer":
        world.setdefault("active_timers", []).append({"episode": episode, "label": "긴급 타이머", "ttl": 2})
    for timer in world.get("active_timers", []):
        timer["ttl"] = int(timer.get("ttl", 1)) - 1
    world["active_timers"] = [timer for timer in world.get("active_timers", []) if timer.get("ttl", 0) > 0][-5:]
    world.setdefault("recent_changes", []).append({"episode": episode, "event_type": event_type, "order": world.get("order"), "instability": world.get("instability")})
    world["recent_changes"] = world["recent_changes"][-8:]

    state["story_state_v2"] = story_state
    sync_story_state(state)
    return world


def world_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    world = story_state["world"]
    return {
        "order": world.get("order", 0),
        "instability": world.get("instability", 0),
        "change_rate": world.get("change_rate", 0),
        "active_timers": world.get("active_timers", [])[-3:],
        "power_rules": world.get("power_rules", [])[:3],
        "recent_changes": world.get("recent_changes", [])[-3:],
    }
