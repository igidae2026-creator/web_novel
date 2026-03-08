from __future__ import annotations

from typing import Any, Dict

from .story_state import chemistry_pressure, ensure_story_state, sync_story_state


def update_reward_serialization(state: Dict[str, Any], episode: int, event_plan: Dict[str, Any] | None = None) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    rewards = story_state["rewards"]
    serialization = story_state["serialization"]
    event_plan = dict(event_plan or {})
    event_type = str(event_plan.get("type", "")).strip()

    delivered = list(rewards.get("delivered_rewards", []) or [])
    pending = list(rewards.get("pending_promises", []) or [])

    if event_type in {"reveal", "reversal", "power_shift", "arrival"} and pending:
        delivered.append(pending.pop(0))
    if event_type in {"false_victory", "collapse"}:
        pending.append("방금 얻은 이득의 숨은 비용 회수")
    if event_type in {"loss", "sacrifice"}:
        pending.append("잃어버린 대가의 정산")

    rewards["delivered_rewards"] = delivered[-8:]
    rewards["pending_promises"] = pending[-8:]
    rewards["reward_density"] = min(10, max(1, len(delivered[-3:]) + (1 if event_type in {"reveal", "power_shift", "arrival"} else 0) + 3))
    rewards["expectation_alignment"] = min(10, max(1, rewards["reward_density"] + (1 if pending else -1)))
    rewards["power_integrity"] = min(10, max(1, int(rewards.get("power_integrity", 7) or 7) + (1 if event_type in {"power_shift", "sacrifice"} else 0) - (1 if event_type == "false_victory" else 0)))

    serialization["chemistry_signal"] = chemistry_pressure(story_state)
    serialization["retention_pressure"] = min(10, len(pending[:3]) + int(rewards["reward_density"] >= 6) + 4)
    serialization["sustainability"] = min(10, max(1, 7 - max(0, rewards["reward_density"] - 7) + min(2, len(pending))))
    serialization["novelty_budget"] = min(10, max(1, int(serialization.get("novelty_budget", 5) or 5) + (1 if event_type in {"arrival", "power_shift", "collapse"} else 0) - (1 if event_type in {"misunderstanding"} else 0)))

    state["story_state_v2"] = story_state
    sync_story_state(state)
    return {
        "rewards": rewards,
        "serialization": serialization,
    }
