from __future__ import annotations
from dataclasses import asdict
from typing import Dict, Any, List
import statistics

from .event_extractor import extract_events
from .emotional_curve import compute_curve
from .cognitive_rhythm import compute_rhythm
from .cliffhanger import classify
from .axes import compute_axes
from .human_guidance import generate
from engine.regression_guard import evaluate_total_profile

def _safe_mean(xs: List[int]) -> float:
    return float(statistics.mean(xs)) if xs else 0.0

def _safe_std(xs: List[int]) -> float:
    return float(statistics.pstdev(xs)) if len(xs) > 1 else 0.0

def evaluate_episode(text: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    meta = dict(meta or {})
    events = extract_events(text, meta)
    curve = compute_curve(text)
    rhythm = compute_rhythm(text)
    cliff = classify(text, meta)
    axes = compute_axes(text)
    retention = meta.get("retention", {}) or {}
    tension = meta.get("tension", {}) or {}
    story_state = meta.get("story_state", {}) or {}
    objective = meta.get("multi_objective", {}) or {}
    world = story_state.get("world", {}) or {}
    serialization = story_state.get("serialization", {}) or {}
    rewards = story_state.get("rewards", {}) or {}

    reward_mean = _safe_mean(events.reward_intervals)
    status_mean = _safe_mean(events.status_intervals)

    structural_profile = {
        "fun": float(objective.get("fun", 0.5) or 0.5),
        "coherence": float(objective.get("coherence", 0.5) or 0.5),
        "character_persuasiveness": float(objective.get("character_persuasiveness", 0.5) or 0.5),
        "pacing": float(objective.get("pacing", 0.5) or 0.5),
        "retention": float(objective.get("retention", 0.5) or 0.5),
        "emotional_payoff": float(objective.get("emotional_payoff", 0.5) or 0.5),
        "long_run_sustainability": float(objective.get("long_run_sustainability", float(serialization.get("sustainability", 5)) / 10.0) or 0.5),
        "world_logic": float(objective.get("world_logic", (10 - float(world.get("instability", 5))) / 10.0) or 0.5),
        "chemistry": float(objective.get("chemistry", float(serialization.get("chemistry_signal", 5)) / 10.0) or 0.5),
        "stability": float(objective.get("stability", 0.5) or 0.5),
    }
    profile_eval = evaluate_total_profile(structural_profile)

    total = 0
    total += min(12, axes.risk_intensity * 2)
    total += min(10, axes.character_agency * 2)
    total += min(10, axes.meaning_depth * 2)
    total += min(8, axes.sensory_density * 2)
    total += min(10, int(rhythm.std_len))
    total += min(8, int(curve.peaks * 4))
    total += min(10, int(events.escalation_steps * 6))
    total += min(8, int(retention.get("unresolved_thread_pressure", 0) or 0))
    total += min(6, int(retention.get("curiosity_debt", 0) or 0))
    total += min(5, int(tension.get("target_tension", 0) or 0))
    total += min(5, int(events.carryover_pressure))
    total += int(profile_eval["balanced_total"] * 28)
    total = int(min(100, total))

    stats = {
        "ceiling_total": total,
        "events": asdict(events),
        "curve": asdict(curve),
        "rhythm": asdict(rhythm),
        "cliff": asdict(cliff),
        "axes": asdict(axes),
        "reward_interval_mean": reward_mean,
        "status_rise_interval_mean": status_mean,
        "genre_bucket": meta.get("genre_bucket", "UNKNOWN"),
        "platform": meta.get("platform", "UNKNOWN"),
        "retention": retention,
        "tension": tension,
        "multi_objective": structural_profile,
        "profile_eval": profile_eval,
        "world_state": {
            "instability": world.get("instability"),
            "change_rate": world.get("change_rate"),
            "reward_density": rewards.get("reward_density"),
            "sustainability": serialization.get("sustainability"),
        },
    }
    guide = generate(stats)
    stats["human_guidance"] = asdict(guide)
    return stats

def aggregate_series(episode_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    totals = [int(r.get("ceiling_total", 0)) for r in episode_results]
    return {
        "episodes": len(totals),
        "mean_ceiling": float(statistics.mean(totals)) if totals else 0.0,
        "min_ceiling": min(totals) if totals else 0,
        "max_ceiling": max(totals) if totals else 0,
    }
