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

def _safe_mean(xs: List[int]) -> float:
    return float(statistics.mean(xs)) if xs else 0.0

def _safe_std(xs: List[int]) -> float:
    return float(statistics.pstdev(xs)) if len(xs) > 1 else 0.0

def evaluate_episode(text: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    meta = dict(meta or {})
    events = extract_events(text)
    curve = compute_curve(text)
    rhythm = compute_rhythm(text)
    cliff = classify(text)
    axes = compute_axes(text)

    reward_mean = _safe_mean(events.reward_intervals)
    status_mean = _safe_mean(events.status_intervals)

    # total ceiling score (0~100) — weighted, content-only
    total = 0
    total += min(20, axes.risk_intensity * 2)
    total += min(15, axes.character_agency * 2)
    total += min(15, axes.meaning_depth * 2)
    total += min(10, axes.sensory_density * 2)
    total += min(15, int(rhythm.std_len))  # rhythm variation
    total += min(10, int(curve.peaks * 4))
    total += min(15, int(events.escalation_steps * 6))
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
