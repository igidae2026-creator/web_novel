from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterable

from engine.event_log import read_recent
from engine.job_queue import JOB_QUEUE_PATH, load_job_queue_state, mark_job_status, save_job_queue_state
from engine.metaos_recovery import replay_resume_decision
from engine.runtime_supervisor import SUPERVISOR_STATE_PATH, load_supervisor_state

CRITICAL_BUNDLES = {"truth_capability", "recovery_capability"}
CAUTION_BUNDLES = {"judgment_capability", "operations_capability"}


def build_fault_injection_report(
    out_dir: str,
    *,
    queue_path: str = JOB_QUEUE_PATH,
    supervisor_path: str = SUPERVISOR_STATE_PATH,
) -> Dict[str, Any]:
    queue_state = load_job_queue_state(queue_path) if queue_path else {}
    supervisor_state = load_supervisor_state(supervisor_path) if supervisor_path else {}
    events = read_recent(out_dir, n=100)
    decision = replay_resume_decision(
        events=events,
        snapshot=supervisor_state,
        queue_state=queue_state,
        required_snapshot_fields=["schema_version", "mode", "status"],
    )
    verdict = str(decision.get("verdict") or "")
    return {
        "tested": True,
        "scenario": "replay_resume_consistency_probe",
        "recovered": verdict == "resume",
        "safe_blocked": verdict == "recover",
        "verdict": verdict,
        "reason": decision.get("reason"),
        "details": decision.get("details", {}),
    }


def run_final_threshold_repairs(
    *,
    state: Any,
    out_dir: str,
    track_id: str,
    queue_path: str = JOB_QUEUE_PATH,
    safe_mode: bool = True,
) -> Dict[str, Any]:
    queue_state = load_job_queue_state(queue_path)
    repairs = [
        job for job in queue_state.get("jobs", [])
        if job.get("job_type") == "repair_final_threshold"
        and job.get("status") == "queued"
        and str(job.get("payload", {}).get("track_id") or track_id) == track_id
    ]
    if not repairs:
        return {"executed": False, "applied": [], "blocked_generation": False, "failed_bundles": []}

    story_state = state.data.setdefault("story_state_v2", {})
    control = story_state.setdefault("control", {})
    threshold_control = control.setdefault(
        "final_threshold_repairs",
        {"pending": [], "applied": [], "blocked_generation": False, "last_applied_episode": None},
    )
    threshold_control["pending"] = []

    blocked_generation = False
    applied = []
    failed_bundles = _load_failed_bundles(out_dir)
    high_risk = {
        "append_only_truth_lineage_replayability",
        "metaos_identity_priority",
        "control_loop_state_closure",
        "fault_injection_resilience",
    }
    directive_map = {
        "early_hook_strength": {"hook_bias": 0.14, "rewrite_pressure": "high", "reader_quality_priority": "critical"},
        "episode_end_hook_strength": {"hook_bias": 0.1, "payoff_bias": 0.05, "rewrite_pressure": "high", "reader_quality_priority": "critical"},
        "long_arc_payoff_stability": {"payoff_bias": 0.12, "rewrite_pressure": "high", "reader_quality_priority": "high"},
        "protagonist_fantasy_persistence": {"hook_bias": 0.06, "payoff_bias": 0.08, "rewrite_pressure": "high", "reader_quality_priority": "high"},
        "reader_retention_stability": {"hook_bias": 0.12, "payoff_bias": 0.06, "rewrite_pressure": "high"},
        "story_quality_stability": {"world_lock": True, "causal_repair_priority": "critical"},
        "adaptive_edit_governance": {"force_fail_closed": True},
        "market_feedback_autoloop": {"market_rebind_required": True},
        "automatic_scope_authority_policy_handling": {"scope_rebind_required": True},
        "human_quality_lift_near_zero": {"human_lift_sampling_required": True},
        "serialization_fatigue_control": {"world_lock": True, "causal_repair_priority": "high", "reader_quality_priority": "high"},
        "soak_steady_noop_dominance": {"stability_mode": "conservative"},
    }

    for job in repairs:
        payload = dict(job.get("payload") or {})
        criterion = str(payload.get("criterion") or "")
        repair_context = dict(payload.get("repair_context") or {})
        threshold_control["pending"].append(criterion)
        threshold_control.update(directive_map.get(criterion, {}))
        threshold_control.update(repair_context)
        if criterion in high_risk:
            blocked_generation = True
        applied.append(
            {
                "job_id": job.get("job_id"),
                "criterion": criterion,
                "repair_action": payload.get("repair_action"),
                "repair_context": repair_context,
            }
        )
        mark_job_status(queue_state, str(job.get("job_id")), "completed", result={"criterion": criterion, "applied": True})

    if any(bundle in CRITICAL_BUNDLES for bundle in failed_bundles):
        blocked_generation = True
    threshold_control["applied"] = applied
    threshold_control["blocked_generation"] = blocked_generation
    threshold_control["failed_bundles"] = failed_bundles
    if any(
        threshold_control.get(key)
        for key in ("hook_bias", "payoff_bias", "rewrite_pressure", "reader_quality_priority")
    ):
        threshold_control["reader_quality_repair_required"] = True
    threshold_control["bundle_priority_mode"] = (
        "critical_repair"
        if any(bundle in CRITICAL_BUNDLES for bundle in failed_bundles)
        else "caution_repair"
        if any(bundle in CAUTION_BUNDLES for bundle in failed_bundles)
        else "criterion_repair"
    )
    threshold_control["last_applied_episode"] = int(state.get("next_episode", 1) or 1)
    state.data["quality_lift_if_human_intervenes"] = min(
        float(state.data.get("quality_lift_if_human_intervenes", 1.0) or 1.0),
        0.12 if blocked_generation else 0.06 if threshold_control.get("reader_quality_repair_required") else 0.08,
    )
    save_job_queue_state(queue_state, path=queue_path, safe_mode=safe_mode)
    return {
        "executed": True,
        "applied": applied,
        "blocked_generation": blocked_generation,
        "failed_bundles": failed_bundles,
        "bundle_priority_mode": threshold_control["bundle_priority_mode"],
    }


def _load_failed_bundles(out_dir: str) -> list[str]:
    path = os.path.join(out_dir, "final_threshold_eval.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return []
    return list(payload.get("failed_bundles", []) or [])


def capability_budget_severity(failed_bundles: list[str]) -> str:
    if any(bundle in CRITICAL_BUNDLES for bundle in failed_bundles):
        return "critical"
    if any(bundle in CAUTION_BUNDLES for bundle in failed_bundles):
        return "caution"
    return "stable"
