from __future__ import annotations

from typing import Any, Dict, List


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def evaluate_narrative_debt(story_state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = dict(story_state or {})
    promise_graph = dict(story_state.get("promise_graph", {}) or {})
    rewards = dict(story_state.get("rewards", {}) or {})
    world = dict(story_state.get("world", {}) or {})
    history = dict(story_state.get("history", {}) or {})
    debt_sources: List[str] = []
    unresolved = int(promise_graph.get("unresolved_count", 0) or 0)
    resolution_rate = float(promise_graph.get("resolution_rate", 0.0) or 0.0)
    if unresolved >= 5:
        debt_sources.append("unresolved_setup_overload")
    if resolution_rate <= 0.3:
        debt_sources.append("low_payoff_recovery_rate")
    if len(list(world.get("power_rules", []) or [])) >= 4:
        debt_sources.append("overextended_world_rules")
    if len(list(rewards.get("pending_promises", []) or [])) >= 5:
        debt_sources.append("too_many_dangling_promises")
    recent_events = list(history.get("events", []) or [])[-6:]
    if sum(1 for event in recent_events if event in {"power_shift", "collapse", "false_victory"}) >= 4:
        debt_sources.append("repeated_shortcut_escalation")
    debt_score = _clamp(
        unresolved * 0.08
        + (1.0 - resolution_rate) * 0.28
        + len(list(world.get("power_rules", []) or [])) * 0.03
        + len(list(rewards.get("pending_promises", []) or [])) * 0.04
        + len(debt_sources) * 0.06
    )
    return {
        "narrative_debt_score": round(debt_score, 4),
        "debt_sources": debt_sources,
        "payoff_recovery_rate": round(resolution_rate, 4),
        "expansion_friction_risk": round(_clamp(debt_score * 0.74 + len(debt_sources) * 0.04), 4),
    }
