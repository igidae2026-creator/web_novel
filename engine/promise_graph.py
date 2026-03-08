from __future__ import annotations

from typing import Any, Dict, List

from .story_state import ensure_story_state, sync_story_state


PROMISE_SETUP_EVENTS = {
    "betrayal": "누가 끝내 등을 돌리는가",
    "reveal": "숨겨진 진실이 어떤 대가를 요구하는가",
    "loss": "잃어버린 것을 어떤 방식으로 되찾는가",
    "arrival": "새 전력이 판을 어떻게 바꾸는가",
    "sacrifice": "희생의 청구서가 누구에게 돌아가는가",
    "collapse": "무너진 질서의 후속 비용을 누가 감당하는가",
    "false_victory": "지금 승리의 숨은 비용이 언제 회수되는가",
    "power_shift": "힘의 재편이 관계와 규칙에 어떤 값을 요구하는가",
}

PROMISE_PAYOFF_EVENTS = {"reveal", "reversal", "power_shift", "arrival", "collapse"}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _promise_label(event_type: str, rewards: Dict[str, Any]) -> str:
    pending = list(rewards.get("pending_promises", []) or [])
    if pending:
        return str(pending[0])
    return PROMISE_SETUP_EVENTS.get(event_type, "현재 갈등의 약속된 회수")


def update_promise_payoff_graph(
    state: Dict[str, Any],
    episode: int,
    event_plan: Dict[str, Any] | None = None,
    score_obj: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    rewards = story_state["rewards"]
    graph = story_state.setdefault(
        "promise_graph",
        {
            "active_promises": [],
            "resolved_promises": [],
            "character_promises": {},
            "dependency_edges": [],
            "payoff_corruption_flags": [],
            "unresolved_count": 0,
            "resolution_rate": 0.0,
            "payoff_integrity": 0.0,
            "episode_history": [],
        },
    )
    event_type = str((event_plan or {}).get("type", "")).strip()
    score_obj = dict(score_obj or {})
    active = list(graph.get("active_promises", []) or [])
    resolved = list(graph.get("resolved_promises", []) or [])
    pending_promises = list(rewards.get("pending_promises", []) or [])
    delivered_rewards = list(rewards.get("delivered_rewards", []) or [])
    cast = dict(story_state.get("cast", {}) or {})
    character_keys = sorted(cast.keys())
    focus_characters = character_keys[:2] if character_keys else ["protagonist"]
    payoff_score = float(score_obj.get("payoff_score", 0.5) or 0.5)
    hook_score = float(score_obj.get("hook_score", 0.5) or 0.5)
    character_promises = dict(graph.get("character_promises", {}) or {})
    dependency_edges = list(graph.get("dependency_edges", []) or [])

    if event_type in PROMISE_SETUP_EVENTS:
        label = _promise_label(event_type, rewards)
        if not any(item.get("label") == label and item.get("status") == "open" and item.get("event_type") == event_type for item in active):
            owners = focus_characters if event_type in {"betrayal", "loss", "sacrifice"} else [focus_characters[0]]
            active.append(
                {
                    "id": f"promise-{episode}-{len(active)+1}",
                    "label": label,
                    "setup_episode": int(episode),
                    "event_type": event_type,
                    "status": "open",
                    "owners": owners,
                }
            )
            for owner in owners:
                bucket = list(character_promises.get(owner, []) or [])
                bucket.append({"id": f"promise-{episode}-{len(active)}", "label": label, "status": "open", "setup_episode": int(episode)})
                character_promises[owner] = bucket[-6:]
            if len(owners) >= 2:
                dependency_edges.append({"from": owners[0], "to": owners[1], "promise": label, "edge_type": "shared_payoff", "episode": int(episode)})

    if event_type in PROMISE_PAYOFF_EVENTS and active:
        target = dict(active.pop(0))
        target["status"] = "resolved"
        target["payoff_episode"] = int(episode)
        target["payoff_event_type"] = event_type
        resolved.append(target)
        for owner in list(target.get("owners", []) or []):
            bucket = []
            for item in list(character_promises.get(owner, []) or []):
                updated = dict(item)
                if updated.get("label") == target.get("label") and updated.get("status") == "open":
                    updated["status"] = "resolved"
                    updated["payoff_episode"] = int(episode)
                bucket.append(updated)
            character_promises[owner] = bucket[-6:]

    corruption_flags: List[Dict[str, Any]] = []
    oldest_age = max([int(episode) - int(item.get("setup_episode", episode) or episode) for item in active], default=0)
    if oldest_age >= 3 and payoff_score < 0.6:
        corruption_flags.append({"episode": int(episode), "type": "overdue_payoff", "severity": round(oldest_age / 6.0, 4)})
    if pending_promises and delivered_rewards and payoff_score < 0.52 and hook_score > 0.68:
        corruption_flags.append({"episode": int(episode), "type": "hook_without_payoff", "severity": 0.62})

    total_seen = len(active) + len(resolved)
    resolution_rate = 0.0 if total_seen == 0 else len(resolved) / total_seen
    integrity_penalty = min(0.35, len(corruption_flags) * 0.12 + max(0, oldest_age - 2) * 0.05)
    dependency_penalty = min(0.18, sum(1 for owner, items in character_promises.items() if any(item.get("status") == "open" for item in items) and len(items) >= 3) * 0.06)
    payoff_integrity = _clamp(0.48 + resolution_rate * 0.28 + payoff_score * 0.18 + min(0.08, len(delivered_rewards[-3:]) * 0.02) - integrity_penalty)
    payoff_integrity = _clamp(payoff_integrity - dependency_penalty)
    character_pressure = {
        owner: sum(1 for item in items if item.get("status") == "open")
        for owner, items in character_promises.items()
    }

    graph.update(
        {
            "active_promises": active[-10:],
            "resolved_promises": resolved[-10:],
            "character_promises": {owner: list(items)[-6:] for owner, items in character_promises.items()},
            "dependency_edges": dependency_edges[-10:],
            "payoff_corruption_flags": (list(graph.get("payoff_corruption_flags", []) or []) + corruption_flags)[-8:],
            "unresolved_count": len(active),
            "resolution_rate": round(resolution_rate, 4),
            "payoff_integrity": round(payoff_integrity, 4),
            "episode_history": (
                list(graph.get("episode_history", []) or [])
                + [
                    {
                        "episode": int(episode),
                        "event_type": event_type,
                        "unresolved_count": len(active),
                        "resolved_total": len(resolved),
                        "payoff_integrity": round(payoff_integrity, 4),
                        "character_pressure": character_pressure,
                        "corruption_flags": corruption_flags,
                    }
                ]
            )[-12:],
        }
    )
    state["story_state_v2"] = story_state
    sync_story_state(state)
    return graph


def promise_graph_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    graph = dict(story_state.get("promise_graph", {}) or {})
    return {
        "active_promises": graph.get("active_promises", [])[:4],
        "resolved_promises": graph.get("resolved_promises", [])[:4],
        "character_promises": graph.get("character_promises", {}),
        "dependency_edges": graph.get("dependency_edges", [])[:6],
        "unresolved_count": graph.get("unresolved_count", 0),
        "resolution_rate": graph.get("resolution_rate", 0.0),
        "payoff_integrity": graph.get("payoff_integrity", 0.0),
        "payoff_corruption_flags": graph.get("payoff_corruption_flags", [])[:4],
    }
