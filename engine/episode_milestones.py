from __future__ import annotations

from typing import Any, Dict, List


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _has_win_signal(story_state: Dict[str, Any]) -> bool:
    rewards = dict(story_state.get("rewards", {}) or {})
    delivered = list(rewards.get("delivered_rewards", []) or [])
    return bool(delivered) or int(rewards.get("reward_density", 0) or 0) >= 6


def _has_hook_signal(event_plan: Dict[str, Any], score_obj: Dict[str, Any]) -> bool:
    return bool(event_plan.get("type")) and float(score_obj.get("hook_score", 0.0) or 0.0) >= 0.62


def evaluate_episode_milestones(
    episode: int,
    story_state: Dict[str, Any],
    platform_spec: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
    score_obj: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = dict(story_state or {})
    platform_spec = dict(platform_spec or {})
    event_plan = dict(event_plan or {})
    score_obj = dict(score_obj or {})
    rewards = dict(story_state.get("rewards", {}) or {})
    market = dict(story_state.get("market", {}) or {})
    promise_graph = dict(story_state.get("promise_graph", {}) or {})
    pacing = dict(story_state.get("pacing", {}) or {})

    checks: List[Dict[str, Any]] = []
    missing: List[str] = []
    directives: List[str] = []

    def add_check(name: str, required: bool, passed: bool, directive: str) -> None:
        checks.append({"name": name, "required": required, "passed": passed, "directive": directive})
        if required and not passed:
            missing.append(name)
            directives.append(directive)

    add_check("episode_1_hook", episode == 1, _has_hook_signal(event_plan, score_obj), "Episode 1 must open on an immediate hook and visible destabilization.")
    add_check("episode_3_first_win", episode >= 3, _has_win_signal(story_state), "By episode 3 the protagonist needs a meaningful visible win or reward.")
    major_payoff_episode = int(platform_spec.get("major_payoff_timing_target", 10) or 10)
    add_check(
        "episode_10_value_jump",
        episode >= major_payoff_episode,
        int(rewards.get("reward_density", 0) or 0) >= 6 and float(promise_graph.get("payoff_integrity", 0.0) or 0.0) >= 0.45,
        "Around episode 10 the value proposition must materially jump through payoff, status gain, or premise expansion.",
    )
    conversion_zone = list(platform_spec.get("conversion_zone_timing_target", [20, 25]) or [20, 25])
    zone_start = int(conversion_zone[0] if conversion_zone else 20)
    zone_end = int(conversion_zone[1] if len(conversion_zone) > 1 else zone_start + 5)
    add_check(
        "conversion_zone_trigger",
        zone_start <= episode <= zone_end,
        int(market.get("paywall_pressure", 0) or 0) >= 7 and float(promise_graph.get("payoff_integrity", 0.0) or 0.0) >= 0.5,
        "The free-to-paid zone needs high pressure, unfinished reward appetite, and premise expansion energy.",
    )
    variation_due = episode >= 15 and episode % 15 == 0
    add_check(
        "structural_variation_checkpoint",
        variation_due,
        len(list(story_state.get("pattern_memory", {}).get("overused_events", []) or [])) == 0 and int(story_state.get("serialization", {}).get("novelty_budget", 0) or 0) >= 5,
        "Every ~15 episodes introduce meaningful structural variation instead of repeating the same event rhythm.",
    )
    reset_due = 40 <= episode <= 60
    add_check(
        "reset_refresh_zone",
        reset_due,
        int(pacing.get("release_debt", 0) or 0) <= 2 and int(story_state.get("information", {}).get("emotional_reservoir", 0) or 0) >= 4,
        "Episodes 40-60 should include refresh, reset, or re-centering to avoid stamina collapse.",
    )
    scale_due = episode >= 100
    add_check(
        "scale_up_assetization_zone",
        scale_due,
        int(promise_graph.get("unresolved_count", 0) or 0) <= 5 and float(promise_graph.get("resolution_rate", 0.0) or 0.0) >= 0.35,
        "After episode 100 the story should show scalable payoff management and franchise-ready structure.",
    )
    passed_required = sum(1 for item in checks if item["required"] and item["passed"])
    total_required = sum(1 for item in checks if item["required"])
    readiness = 1.0 if total_required == 0 else passed_required / total_required
    return {
        "episode": int(episode),
        "checks": checks,
        "milestone_directives": directives[:5],
        "missing_milestones": missing,
        "milestone_readiness": round(_clamp(readiness), 4),
    }
