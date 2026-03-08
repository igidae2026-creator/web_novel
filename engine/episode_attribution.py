from __future__ import annotations

from typing import Any, Dict

from .causal_attribution import build_scene_event_attribution
from .story_state import ensure_story_state, sync_story_state


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def build_episode_attribution(
    episode: int,
    episode_text: str,
    event_plan: Dict[str, Any] | None,
    cliffhanger_plan: Dict[str, Any] | None,
    score_obj: Dict[str, Any],
    retention_state: Dict[str, Any],
    story_state: Dict[str, Any],
    content_ceiling: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    content_ceiling = dict(content_ceiling or {})
    rewards = dict(story_state.get("rewards", {}) or {})
    promise_graph = dict(story_state.get("promise_graph", {}) or {})
    repetition = float(score_obj.get("repetition_score", 0.2) or 0.2)
    payoff_score = float(score_obj.get("payoff_score", 0.5) or 0.5)
    hook_score = float(score_obj.get("hook_score", 0.5) or 0.5)
    pacing_score = float(score_obj.get("pacing_score", 0.5) or 0.5)
    ceiling_total = float(content_ceiling.get("ceiling_total", 60) or 60) / 100.0
    unresolved_pressure = float(retention_state.get("unresolved_thread_pressure", 5) or 5) / 10.0
    payoff_debt = float(retention_state.get("payoff_debt", 5) or 5) / 10.0
    reward_density = float(rewards.get("reward_density", 5) or 5) / 10.0
    expectation_alignment = float(rewards.get("expectation_alignment", 5) or 5) / 10.0
    payoff_integrity = float(promise_graph.get("payoff_integrity", 0.5) or 0.5)
    unresolved_promises = min(1.0, float(promise_graph.get("unresolved_count", 0) or 0) / 6.0)
    fine_grained = build_scene_event_attribution(episode_text, event_plan=event_plan, cliffhanger_plan=cliffhanger_plan)
    retention_signal = _clamp(hook_score * 0.32 + unresolved_pressure * 0.22 + payoff_score * 0.16 + payoff_integrity * 0.12 + ceiling_total * 0.10 + reward_density * 0.08)
    event_chain_strength = float(fine_grained.get("event_chain_strength", 0.0) or 0.0)
    pacing_signal = _clamp(pacing_score * 0.56 + (1.0 - repetition) * 0.18 + expectation_alignment * 0.14 + max(0.0, 1.0 - abs(unresolved_pressure - 0.6)) * 0.12 + float(fine_grained.get("scene_signal", 0.0) or 0.0) * 0.04 + event_chain_strength * 0.03)
    fatigue_signal = _clamp(repetition * 0.48 + payoff_debt * 0.18 + unresolved_promises * 0.12 + max(0.0, reward_density - 0.75) * 0.22)
    payoff_signal = _clamp(payoff_score * 0.46 + payoff_integrity * 0.34 + expectation_alignment * 0.12 + max(0.0, 1.0 - unresolved_promises) * 0.08 + float(fine_grained.get("scene_signal", 0.0) or 0.0) * 0.03 + event_chain_strength * 0.02)
    return {
        "episode": int(episode),
        "retention_signal": round(retention_signal, 4),
        "pacing_signal": round(pacing_signal, 4),
        "fatigue_signal": round(fatigue_signal, 4),
        "payoff_signal": round(payoff_signal, 4),
        "ceiling_signal": round(ceiling_total, 4),
        "fine_grained": fine_grained,
    }


def record_episode_attribution(
    state: Dict[str, Any],
    episode: int,
    episode_text: str,
    event_plan: Dict[str, Any] | None,
    cliffhanger_plan: Dict[str, Any] | None,
    score_obj: Dict[str, Any],
    retention_state: Dict[str, Any],
    content_ceiling: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    attribution = build_episode_attribution(
        episode=episode,
        episode_text=episode_text,
        event_plan=event_plan,
        cliffhanger_plan=cliffhanger_plan,
        score_obj=score_obj,
        retention_state=retention_state,
        story_state=story_state,
        content_ceiling=content_ceiling,
    )
    control = story_state.setdefault("control", {})
    episode_memory = control.setdefault("episode_attribution", {"latest": {}, "history": []})
    episode_memory["latest"] = dict(attribution)
    episode_memory["history"] = (list(episode_memory.get("history", []) or []) + [dict(attribution)])[-12:]
    portfolio_memory = story_state.setdefault("portfolio_memory", {})
    memory = dict(portfolio_memory.get("episode_attribution_memory", {}) or {})
    observed = int(memory.get("observed", 0) or 0) + 1
    blend = 0.0 if observed == 1 else 0.7
    portfolio_memory["episode_attribution_memory"] = {
        "observed": observed,
        "retention_signal": round(float(memory.get("retention_signal", 0.0) or 0.0) * blend + float(attribution["retention_signal"]) * (1.0 - blend), 4),
        "pacing_signal": round(float(memory.get("pacing_signal", 0.0) or 0.0) * blend + float(attribution["pacing_signal"]) * (1.0 - blend), 4),
        "fatigue_signal": round(float(memory.get("fatigue_signal", 0.0) or 0.0) * blend + float(attribution["fatigue_signal"]) * (1.0 - blend), 4),
        "payoff_signal": round(float(memory.get("payoff_signal", 0.0) or 0.0) * blend + float(attribution["payoff_signal"]) * (1.0 - blend), 4),
    }
    state["story_state_v2"] = story_state
    sync_story_state(state)
    return attribution
