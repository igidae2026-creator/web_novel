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
    payoff_score = float(score_obj.get("payoff_score", 0.5) or 0.5)
    hook_score = float(score_obj.get("hook_score", 0.5) or 0.5)

    if event_type in PROMISE_SETUP_EVENTS:
        label = _promise_label(event_type, rewards)
        if not any(item.get("label") == label and item.get("status") == "open" and item.get("event_type") == event_type for item in active):
            active.append(
                {
                    "id": f"promise-{episode}-{len(active)+1}",
                    "label": label,
                    "setup_episode": int(episode),
                    "event_type": event_type,
                    "status": "open",
                }
            )

    if event_type in PROMISE_PAYOFF_EVENTS and active:
        target = dict(active.pop(0))
        target["status"] = "resolved"
        target["payoff_episode"] = int(episode)
        target["payoff_event_type"] = event_type
        resolved.append(target)

    corruption_flags: List[Dict[str, Any]] = []
    oldest_age = max([int(episode) - int(item.get("setup_episode", episode) or episode) for item in active], default=0)
    if oldest_age >= 3 and payoff_score < 0.6:
        corruption_flags.append({"episode": int(episode), "type": "overdue_payoff", "severity": round(oldest_age / 6.0, 4)})
    if pending_promises and delivered_rewards and payoff_score < 0.52 and hook_score > 0.68:
        corruption_flags.append({"episode": int(episode), "type": "hook_without_payoff", "severity": 0.62})

    total_seen = len(active) + len(resolved)
    resolution_rate = 0.0 if total_seen == 0 else len(resolved) / total_seen
    integrity_penalty = min(0.35, len(corruption_flags) * 0.12 + max(0, oldest_age - 2) * 0.05)
    payoff_integrity = _clamp(0.48 + resolution_rate * 0.28 + payoff_score * 0.18 + min(0.08, len(delivered_rewards[-3:]) * 0.02) - integrity_penalty)

    graph.update(
        {
            "active_promises": active[-10:],
            "resolved_promises": resolved[-10:],
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
        "unresolved_count": graph.get("unresolved_count", 0),
        "resolution_rate": graph.get("resolution_rate", 0.0),
        "payoff_integrity": graph.get("payoff_integrity", 0.0),
        "payoff_corruption_flags": graph.get("payoff_corruption_flags", [])[:4],
    }
