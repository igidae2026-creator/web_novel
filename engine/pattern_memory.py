from __future__ import annotations

from typing import Any, Dict

from .story_state import EVENT_TYPES, ensure_story_state, sync_story_state


def update_pattern_memory(
    state: Dict[str, Any],
    episode: int,
    event_plan: Dict[str, Any] | None = None,
    cliffhanger_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    memory = story_state["pattern_memory"]
    serialization = story_state["serialization"]
    rewards = story_state["rewards"]
    event_plan = dict(event_plan or {})
    cliffhanger_plan = dict(cliffhanger_plan or {})

    event_type = str(event_plan.get("type", "")).strip()
    cliff_mode = str(cliffhanger_plan.get("mode", "")).strip()

    recent_events = list(memory.get("recent_event_types", []) or [])
    recent_modes = list(memory.get("recent_cliffhanger_modes", []) or [])
    event_counts = dict(memory.get("event_counts", {}) or {})

    if event_type:
        recent_events.append(event_type)
        event_counts[event_type] = int(event_counts.get(event_type, 0) or 0) + 1
    if cliff_mode:
        recent_modes.append(cliff_mode)

    recent_events = recent_events[-6:]
    recent_modes = recent_modes[-6:]
    overused = sorted({evt for evt in recent_events if recent_events.count(evt) >= 2})
    novelty_budget = int(serialization.get("novelty_budget", 5) or 5)
    reward_density = int(rewards.get("reward_density", 5) or 5)

    memory["recent_event_types"] = recent_events
    memory["recent_cliffhanger_modes"] = recent_modes
    memory["event_counts"] = event_counts
    memory["overused_events"] = overused
    memory["exploration_bias"] = min(10, max(1, novelty_budget + (2 if overused else 0) + (1 if reward_density <= 4 else 0)))
    memory["market_resonance"] = min(10, max(1, rewards.get("expectation_alignment", 5) + serialization.get("market_fit", 5) // 3))

    state["story_state_v2"] = story_state
    sync_story_state(state)
    return memory


def choose_event_with_memory(state: Dict[str, Any], preferred: str, fallback: str) -> str:
    story_state = ensure_story_state(state)
    memory = story_state["pattern_memory"]
    portfolio_memory = story_state.get("portfolio_memory", {})
    overused = set(memory.get("overused_events", []) or [])
    overused.update(portfolio_memory.get("crowded_patterns", []) or [])
    exploration_bias = int(memory.get("exploration_bias", 4) or 4)
    fatigue_patterns = set(portfolio_memory.get("fatigue_patterns", []) or [])
    portfolio_metrics = story_state.get("portfolio_metrics", {})
    coordination_health = int(portfolio_memory.get("coordination_health", 5) or 5)
    cadence_guard = int(portfolio_memory.get("cadence_guard", 5) or 5)
    release_guard = int(portfolio_memory.get("release_guard", 5) or 5)
    hidden_reader_risk = float(portfolio_memory.get("hidden_reader_risk", 0.0) or 0.0)
    if int(portfolio_metrics.get("novelty_debt", 0) or 0) >= 6:
        exploration_bias = max(exploration_bias, 7)
    if coordination_health <= 4:
        exploration_bias = max(exploration_bias, 6)
    if cadence_guard <= 4 or release_guard <= 4:
        exploration_bias = max(4, exploration_bias - 1)
    if hidden_reader_risk >= 0.35:
        exploration_bias = max(exploration_bias, 7)

    if preferred and preferred not in overused and preferred not in fatigue_patterns:
        return preferred
    if exploration_bias >= 6:
        for event_type in EVENT_TYPES:
            if event_type not in overused and event_type not in fatigue_patterns and event_type != preferred:
                return event_type
    return fallback


def pattern_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    memory = story_state["pattern_memory"]
    return {
        "recent_event_types": memory.get("recent_event_types", [])[-4:],
        "recent_cliffhanger_modes": memory.get("recent_cliffhanger_modes", [])[-4:],
        "overused_events": memory.get("overused_events", []),
        "exploration_bias": memory.get("exploration_bias", 0),
        "market_resonance": memory.get("market_resonance", 0),
        "design_guardrails": (story_state.get("portfolio_memory", {}) or {}).get("design_guardrails", [])[:4],
    }
