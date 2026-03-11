from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from engine.event_log import log_event
from engine.io_utils import append_jsonl


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _recent_regression_pressure(story_state: Dict[str, Any], episode: int) -> int:
    flags = list((((story_state or {}).get("control", {}) or {}).get("regression_flags", []) or []))
    recent = [item for item in flags if _as_int(item.get("episode"), 0) >= max(1, int(episode) - 2)]
    return len(recent)


def _read_last_final_threshold(state_data: Dict[str, Any]) -> Dict[str, Any]:
    out_dir = str(state_data.get("out_dir") or "")
    if not out_dir:
        return {}
    path = os.path.join(out_dir, "final_threshold_eval.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def assess_preflight_bundle(
    cfg: Dict[str, Any],
    state_data: Dict[str, Any],
    *,
    runtime_cfg: Dict[str, Any] | None = None,
    episode: int,
) -> Dict[str, Any]:
    runtime_cfg = dict(runtime_cfg or {})
    evaluation_cfg = dict(runtime_cfg.get("evaluation", {}) or {})
    preflight_cfg = dict(evaluation_cfg.get("preflight_gate", {}) or {})
    if preflight_cfg.get("enabled") is False:
        return {
            "enabled": False,
            "preflight_ready": True,
            "risk_tier": "medium",
            "risk_score": 0.5,
            "blocking_reasons": [],
            "signals": {},
            "runtime_policy": {},
        }

    story_state = dict(state_data.get("story_state_v2", {}) or {})
    control = dict(story_state.get("control", {}) or {})
    world = dict(story_state.get("world", {}) or {})
    promise_graph = dict(story_state.get("promise_graph", {}) or {})
    portfolio_memory = dict(story_state.get("portfolio_memory", {}) or {})
    reader_quality = dict(control.get("reader_quality", {}) or {})
    arc_pressure = dict(control.get("arc_pressure", {}) or {})
    runtime_repairs = dict(control.get("final_threshold_repairs", {}) or {})
    last_gate = dict(state_data.get("last_quality_gate", {}) or {})
    last_threshold = _read_last_final_threshold(state_data)
    failed_bundles = list(last_threshold.get("failed_bundles", []) or [])
    failed_criteria = list(last_threshold.get("failed_criteria", []) or [])

    predicted_retention = _as_float(state_data.get("predicted_retention", last_gate.get("predicted_retention")), 0.0)
    world_instability = _as_float(world.get("instability"), 0.0)
    release_guard = _as_int(portfolio_memory.get("release_guard"), 5)
    shared_risk_alert = _as_int(portfolio_memory.get("shared_risk_alert"), 3)
    unresolved_promises = _as_int(promise_graph.get("unresolved_count", 0), 0)
    payoff_integrity = _as_float(promise_graph.get("payoff_integrity", 0.75), 0.75)
    regression_pressure = _recent_regression_pressure(story_state, episode)
    blocked_generation = bool(runtime_repairs.get("blocked_generation"))
    capability_pressure = _clamp(len(failed_bundles) / 6.0)
    reader_quality_debt = _clamp(
        (
            _as_float(reader_quality.get("hook_debt"), 0.0)
            + _as_float(reader_quality.get("payoff_debt"), 0.0)
            + _as_float(reader_quality.get("fatigue_debt"), 0.0)
            + _as_float(reader_quality.get("retention_debt"), 0.0)
            + _as_float(reader_quality.get("thinness_debt"), 0.0)
            + _as_float(reader_quality.get("repetition_debt"), 0.0)
            + _as_float(reader_quality.get("deja_vu_debt"), 0.0)
            + _as_float(reader_quality.get("fake_urgency_debt"), 0.0)
            + _as_float(reader_quality.get("compression_debt"), 0.0)
        )
        / 1.6
    )
    arc_debt = _clamp(
        (
            _as_float(arc_pressure.get("payoff_debt"), 0.0)
            + _as_float(arc_pressure.get("momentum_debt"), 0.0)
        )
        / 0.8
    )
    reader_quality_pressure = _clamp(
        sum(
            1
            for criterion in failed_criteria
            if criterion
            in {
                "early_hook_strength",
                "episode_end_hook_strength",
                "long_arc_payoff_stability",
                "protagonist_fantasy_persistence",
                "reader_retention_stability",
                "serialization_fatigue_control",
            }
        )
        / 6.0
    )

    quality_cfg = dict(cfg.get("quality", {}) or {})
    max_world_instability = _as_float(quality_cfg.get("world_instability_max"), 7.0)
    min_retention = _as_float(quality_cfg.get("predicted_retention_min"), 0.62)

    retention_risk = _clamp((min_retention - predicted_retention) / max(0.05, min_retention)) if predicted_retention else 0.75
    world_risk = _clamp(world_instability / max(1.0, max_world_instability))
    promise_risk = _clamp(unresolved_promises / 6.0)
    payoff_risk = _clamp(1.0 - payoff_integrity)
    release_risk = _clamp((6 - release_guard) / 6.0)
    shared_risk = _clamp(shared_risk_alert / 10.0)
    regression_risk = _clamp(regression_pressure / 2.0)

    risk_score = _clamp(
        retention_risk * 0.22
        + world_risk * 0.18
        + promise_risk * 0.14
        + payoff_risk * 0.12
        + release_risk * 0.10
        + shared_risk * 0.10
        + regression_risk * 0.14
        + capability_pressure * 0.18
        + reader_quality_pressure * 0.2
        + reader_quality_debt * 0.16
        + arc_debt * 0.16
    )
    if blocked_generation:
        risk_score = max(risk_score, 0.95)
    if "truth_capability" in failed_bundles or "recovery_capability" in failed_bundles:
        risk_score = max(risk_score, 0.9)
    if runtime_repairs.get("reader_quality_priority") == "critical":
        risk_score = max(risk_score, 0.62)
    elif runtime_repairs.get("reader_quality_repair_required"):
        risk_score = max(risk_score, 0.5)
    if runtime_repairs.get("reader_risk_trend_repair_required"):
        risk_score = max(risk_score, 0.68)
    if runtime_repairs.get("reader_risk_trend_block_required"):
        risk_score = max(risk_score, 0.9)
    if runtime_repairs.get("heavy_reader_signal_repair_required"):
        risk_score = max(risk_score, 0.68)
    if runtime_repairs.get("heavy_reader_signal_block_required"):
        risk_score = max(risk_score, 0.9)
    elif reader_quality_debt >= 0.24:
        risk_score = max(risk_score, 0.5)
    if arc_debt >= 0.3:
        risk_score = max(risk_score, 0.5)

    if risk_score >= 0.85:
        risk_tier = "critical"
    elif risk_score >= 0.62:
        risk_tier = "high"
    elif risk_score >= 0.35:
        risk_tier = "medium"
    else:
        risk_tier = "low"

    blocking_reasons: List[str] = []
    if blocked_generation:
        blocking_reasons.append("final_threshold_repair_block")
    if predicted_retention and predicted_retention < min_retention - 0.08:
        blocking_reasons.append("retention_projection_too_low")
    if world_instability > max_world_instability + 1:
        blocking_reasons.append("world_instability_preflight_block")
    if regression_pressure >= 2:
        blocking_reasons.append("recent_regression_pressure")
    if "truth_capability" in failed_bundles:
        blocking_reasons.append("truth_capability_not_closed")
    if "recovery_capability" in failed_bundles:
        blocking_reasons.append("recovery_capability_not_closed")
    if runtime_repairs.get("reader_risk_trend_block_required"):
        blocking_reasons.append("hidden_reader_risk_trend_block")
    if runtime_repairs.get("heavy_reader_signal_block_required"):
        blocking_reasons.append("heavy_reader_signal_trend_block")

    tier_cfg = dict((evaluation_cfg.get("risk_tiers", {}) or {}).get(risk_tier, {}) or {})
    runtime_policy = {
        "max_revision_passes": _as_int(
            tier_cfg.get(
                "max_revision_passes",
                1 if risk_tier == "low" else 2 if risk_tier == "medium" else 3,
            ),
            2,
        ),
        "causal_repair_retry_budget": _as_int(
            tier_cfg.get(
                "causal_repair_retry_budget",
                1 if risk_tier == "low" else 2 if risk_tier == "medium" else 3,
            ),
            2,
        ),
        "request_timeout_seconds": _as_int(
            tier_cfg.get(
                "request_timeout_seconds",
                90 if risk_tier == "low" else 150 if risk_tier == "medium" else 210,
            ),
            150,
        ),
        "mode": str(tier_cfg.get("mode", cfg.get("model", {}).get("mode", "batch")) or "batch"),
    }
    if risk_tier == "critical":
        runtime_policy["mode"] = str(tier_cfg.get("mode", "priority") or "priority")

    if runtime_repairs.get("business_feedback_rebind_required"):
        runtime_policy["max_revision_passes"] = max(int(runtime_policy.get("max_revision_passes", 2) or 2), 3)
        runtime_policy["causal_repair_retry_budget"] = max(int(runtime_policy.get("causal_repair_retry_budget", 2) or 2), 3)
        runtime_policy["request_timeout_seconds"] = max(int(runtime_policy.get("request_timeout_seconds", 150) or 150), 180)
    if runtime_repairs.get("reader_quality_repair_required") or runtime_repairs.get("reader_quality_priority"):
        runtime_policy["mode"] = "priority"
        runtime_policy["max_revision_passes"] = max(int(runtime_policy.get("max_revision_passes", 2) or 2), 3)
        runtime_policy["causal_repair_retry_budget"] = max(int(runtime_policy.get("causal_repair_retry_budget", 2) or 2), 3)
    if runtime_repairs.get("reader_risk_trend_repair_required"):
        runtime_policy["mode"] = "priority"
        runtime_policy["max_revision_passes"] = max(int(runtime_policy.get("max_revision_passes", 2) or 2), 3)
        runtime_policy["causal_repair_retry_budget"] = max(int(runtime_policy.get("causal_repair_retry_budget", 2) or 2), 3)
        runtime_policy["request_timeout_seconds"] = max(int(runtime_policy.get("request_timeout_seconds", 150) or 150), 180)
    if runtime_repairs.get("heavy_reader_signal_repair_required"):
        runtime_policy["mode"] = "priority"
        runtime_policy["max_revision_passes"] = max(int(runtime_policy.get("max_revision_passes", 2) or 2), 3)
        runtime_policy["causal_repair_retry_budget"] = max(int(runtime_policy.get("causal_repair_retry_budget", 2) or 2), 3)
        runtime_policy["request_timeout_seconds"] = max(int(runtime_policy.get("request_timeout_seconds", 150) or 150), 180)
    if runtime_repairs.get("scope_policy_rebind_required"):
        runtime_policy["mode"] = "priority"
    if runtime_repairs.get("human_lift_sampling_required"):
        runtime_policy["mode"] = "priority"
        runtime_policy["max_revision_passes"] = max(int(runtime_policy.get("max_revision_passes", 2) or 2), 2)

    return {
        "enabled": True,
        "preflight_ready": len(blocking_reasons) == 0,
        "risk_tier": risk_tier,
        "risk_score": round(risk_score, 4),
        "blocking_reasons": blocking_reasons,
        "signals": {
            "predicted_retention": predicted_retention,
            "world_instability": world_instability,
            "unresolved_promises": unresolved_promises,
            "payoff_integrity": payoff_integrity,
            "release_guard": release_guard,
            "shared_risk_alert": shared_risk_alert,
            "regression_pressure": regression_pressure,
            "blocked_generation": blocked_generation,
            "failed_bundles": failed_bundles,
            "failed_criteria": failed_criteria,
            "capability_pressure": round(capability_pressure, 4),
            "reader_quality_pressure": round(reader_quality_pressure, 4),
            "reader_quality_debt": round(reader_quality_debt, 4),
            "arc_debt": round(arc_debt, 4),
            "heavy_reader_signal_trend": round(_as_float(runtime_repairs.get("heavy_reader_signal_trend"), 0.0), 4),
            "runtime_repairs": runtime_repairs,
        },
        "runtime_policy": runtime_policy,
    }


def apply_preflight_runtime_policy(cfg: Dict[str, Any], preflight: Dict[str, Any]) -> Dict[str, Any]:
    adjusted = {
        **cfg,
        "limits": dict(cfg.get("limits", {}) or {}),
        "model": dict(cfg.get("model", {}) or {}),
    }
    policy = dict(preflight.get("runtime_policy", {}) or {})
    if policy.get("max_revision_passes") is not None:
        adjusted["limits"]["max_revision_passes"] = int(policy["max_revision_passes"])
    if policy.get("causal_repair_retry_budget") is not None:
        adjusted["limits"]["causal_repair_retry_budget"] = int(policy["causal_repair_retry_budget"])
    if policy.get("request_timeout_seconds") is not None:
        adjusted["limits"]["request_timeout_seconds"] = int(policy["request_timeout_seconds"])
        adjusted["model"]["request_timeout_seconds"] = int(policy["request_timeout_seconds"])
    if policy.get("mode"):
        adjusted["model"]["mode"] = str(policy["mode"])
    return adjusted


def record_preflight_bundle(
    out_dir: str,
    preflight: Dict[str, Any],
    *,
    episode: int,
    safe_mode: bool,
) -> None:
    record = {
        "type": "preflight_eval",
        "episode": int(episode),
        "risk_tier": preflight.get("risk_tier"),
        "risk_score": preflight.get("risk_score"),
        "preflight_ready": bool(preflight.get("preflight_ready")),
        "blocking_reasons": list(preflight.get("blocking_reasons", []) or []),
    }
    append_jsonl(
        os.path.join(out_dir, "metrics.jsonl"),
        record,
        safe_mode=safe_mode,
        project_dir_for_backup=out_dir,
    )
    log_event(
        out_dir,
        "preflight_evaluated",
        {
            "episode": int(episode),
            "risk_tier": preflight.get("risk_tier"),
            "preflight_ready": bool(preflight.get("preflight_ready")),
        },
        safe_mode=safe_mode,
    )
