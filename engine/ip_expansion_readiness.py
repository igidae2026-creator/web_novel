from __future__ import annotations

from typing import Any, Dict


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def evaluate_ip_expansion_readiness(
    episode: int,
    story_state: Dict[str, Any],
    title_bundle: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = dict(story_state or {})
    title_bundle = dict(title_bundle or {})
    world = dict(story_state.get("world", {}) or {})
    promise_graph = dict(story_state.get("promise_graph", {}) or {})
    relationships = dict(story_state.get("relationships", {}) or {})
    title_score = float(title_bundle.get("best_title", {}).get("title_fitness", 0.0) or 0.0)
    adaptation_scene_density = _clamp(len(relationships) * 0.12 + len(list(world.get("recent_changes", []) or [])) * 0.08 + float(promise_graph.get("payoff_integrity", 0.0) or 0.0) * 0.34)
    canon_consistency = _clamp(0.88 - int(world.get("instability", 0) or 0) * 0.05 + float(promise_graph.get("resolution_rate", 0.0) or 0.0) * 0.18)
    world_capacity = _clamp(len(list(world.get("factions", []) or [])) * 0.11 + len(list(world.get("power_rules", []) or [])) * 0.08)
    webtoon_adaptability = _clamp(adaptation_scene_density * 0.54 + title_score * 0.20 + float(story_state.get("protagonist_guard", {}).get("protagonist_sovereignty", 0.0) or 0.0) * 0.18)
    franchise_expandability = _clamp(world_capacity * 0.36 + canon_consistency * 0.34 + adaptation_scene_density * 0.18 + float(story_state.get("narrative_debt", {}).get("expansion_friction_risk", 0.0) or 0.0) * -0.18 + 0.20)
    ip_readiness = _clamp((0.18 if episode >= 100 else 0.05) + webtoon_adaptability * 0.32 + franchise_expandability * 0.32 + canon_consistency * 0.24 + title_score * 0.08)
    return {
        "ip_readiness": round(ip_readiness, 4),
        "webtoon_adaptability": round(webtoon_adaptability, 4),
        "franchise_expandability": round(franchise_expandability, 4),
        "canon_consistency": round(canon_consistency, 4),
        "adaptation_scene_density": round(adaptation_scene_density, 4),
        "world_expansion_capacity": round(world_capacity, 4),
    }
