from __future__ import annotations

from typing import Any, Dict, List


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def evaluate_monetization_transition(
    episode: int,
    story_state: Dict[str, Any],
    platform_spec: Dict[str, Any] | None = None,
    milestone_report: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = dict(story_state or {})
    platform_spec = dict(platform_spec or {})
    milestone_report = dict(milestone_report or {})
    rewards = dict(story_state.get("rewards", {}) or {})
    market = dict(story_state.get("market", {}) or {})
    promise_graph = dict(story_state.get("promise_graph", {}) or {})
    serialization = dict(story_state.get("serialization", {}) or {})
    free_target = int(platform_spec.get("free_episode_count_target", 22) or 22)
    zone = list(platform_spec.get("conversion_zone_timing_target", [20, 25]) or [20, 25])
    zone_start = int(zone[0] if zone else free_target)
    zone_end = int(zone[1] if len(zone) > 1 else zone_start + 5)

    pressure = _clamp(
        int(market.get("paywall_pressure", 0) or 0) / 10.0 * 0.34
        + int(rewards.get("reward_density", 0) or 0) / 10.0 * 0.16
        + float(promise_graph.get("payoff_integrity", 0.0) or 0.0) * 0.22
        + int(serialization.get("retention_pressure", 0) or 0) / 10.0 * 0.18
        + (0.10 if zone_start <= episode <= zone_end else 0.0)
    )
    readiness = _clamp(
        pressure * 0.52
        + float(milestone_report.get("milestone_readiness", 0.0) or 0.0) * 0.24
        + (0.12 if int(rewards.get("expectation_alignment", 0) or 0) >= 6 else 0.0)
        + (0.12 if int(market.get("reader_trust", 0) or 0) >= 6 else 0.0)
    )
    missing: List[str] = []
    if episode <= free_target and int(rewards.get("reward_density", 0) or 0) <= 4:
        missing.append("free_episodes_wasting_setup")
    if zone_start <= episode <= zone_end and int(market.get("paywall_pressure", 0) or 0) < 7:
        missing.append("low_conversion_pressure")
    if float(promise_graph.get("payoff_integrity", 0.0) or 0.0) < 0.5:
        missing.append("weak_pre_conversion_payoff")
    if int(serialization.get("retention_pressure", 0) or 0) < 6:
        missing.append("must_continue_energy_missing")
    risk = _clamp(1.0 - readiness + min(0.25, len(missing) * 0.08))
    return {
        "conversion_readiness": round(readiness, 4),
        "conversion_pressure": round(pressure, 4),
        "conversion_risk": round(risk, 4),
        "missing_conversion_signals": missing,
    }
