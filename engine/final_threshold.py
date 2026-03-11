from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any, Dict, List, Tuple

from engine.event_log import log_event
from engine.io_utils import append_jsonl
from engine.job_queue import JOB_QUEUE_PATH, load_job_queue_state, save_job_queue_state, upsert_job
from engine.runtime_supervisor import (
    SUPERVISOR_STATE_PATH,
    ADMISSION_STATE_PATH,
    PROMOTION_STATE_PATH,
    load_admission_state,
    load_promotion_state,
    load_supervisor_state,
    save_supervisor_state,
    update_supervisor_from_queue,
)
from engine.safe_io import safe_write_text

FINAL_THRESHOLD_FILENAME = "final_threshold_eval.json"
DEFAULT_HUMAN_LIFT_THRESHOLD = 0.05

CRITERIA_SPECS: Dict[str, Dict[str, Any]] = {
    "closed_loop_cycle_completion": {
        "label": "task generation, execution, failure recording, and next-step progression must stay closed",
        "repair": "repair_closed_loop_progression",
        "priority": 10,
    },
    "quality_gate_fail_closed": {
        "label": "quality gate failures must fail closed and avoid silent acceptance",
        "repair": "repair_fail_closed_quality_gate",
        "priority": 10,
    },
    "append_only_truth_lineage_replayability": {
        "label": "append-only truth, lineage, and replayability must remain intact",
        "repair": "repair_append_only_lineage_replayability",
        "priority": 5,
    },
    "metaos_identity_priority": {
        "label": "MetaOS identity must stay above production convenience",
        "repair": "repair_metaos_identity_guard",
        "priority": 5,
    },
    "story_quality_stability": {
        "label": "planning, world, character, plot, episode quality, and long-arc stability must hold together",
        "repair": "repair_story_quality_stability",
        "priority": 20,
    },
    "early_hook_strength": {
        "label": "the opening must deliver upper-tier early hook pressure for heavy web-novel readers",
        "repair": "repair_early_hook_strength",
        "priority": 20,
    },
    "episode_end_hook_strength": {
        "label": "episode endings must preserve addictive next-episode carryover pressure",
        "repair": "repair_episode_end_hook_strength",
        "priority": 20,
    },
    "long_arc_payoff_stability": {
        "label": "long-arc promise, payoff, and reward integrity must remain stable",
        "repair": "repair_long_arc_payoff_stability",
        "priority": 20,
    },
    "protagonist_fantasy_persistence": {
        "label": "protagonist fantasy and forward momentum must stay persuasive over time",
        "repair": "repair_protagonist_fantasy_persistence",
        "priority": 20,
    },
    "reader_retention_stability": {
        "label": "hook, retention, rhythm, per-episode hook, and fatigue control must remain stable",
        "repair": "repair_reader_retention_stability",
        "priority": 20,
    },
    "serialization_fatigue_control": {
        "label": "serialization rhythm must manage fatigue without collapsing tension or pacing",
        "repair": "repair_serialization_fatigue_control",
        "priority": 20,
    },
    "adaptive_edit_governance": {
        "label": "degradation must trigger automatic hold, reject, rewrite, or promote behavior",
        "repair": "repair_adaptive_edit_governance",
        "priority": 20,
    },
    "soak_steady_noop_dominance": {
        "label": "long soak runs should stay steady with noop dominance",
        "repair": "repair_soak_steady_noop",
        "priority": 40,
    },
    "autonomous_convergence_trend": {
        "label": "recent unattended cycles should show convergence toward steady operation with low human-lift dependence",
        "repair": "repair_autonomous_convergence_trend",
        "priority": 45,
    },
    "fault_injection_resilience": {
        "label": "fault injection must auto-recover or safely block",
        "repair": "repair_fault_injection_resilience",
        "priority": 30,
    },
    "human_quality_lift_near_zero": {
        "label": "human intervention should provide near-zero incremental quality lift",
        "repair": "measure_and_reduce_human_quality_lift",
        "priority": 50,
    },
    "automatic_scope_authority_policy_handling": {
        "label": "new works, arcs, character groups, settings, and reference material must auto-resolve within scope, authority, and policy",
        "repair": "repair_scope_authority_policy_autonomy",
        "priority": 30,
    },
    "control_loop_state_closure": {
        "label": "reports, interventions, control-state, queue, and supervisor transitions must stay closed",
        "repair": "repair_control_loop_state_closure",
        "priority": 15,
    },
    "market_feedback_autoloop": {
        "label": "market and reader signals must feed the next generated work and policy adjustment automatically",
        "repair": "repair_market_feedback_autoloop",
        "priority": 25,
    },
}

CAPABILITY_BUNDLES: Dict[str, Dict[str, Any]] = {
    "generation_capability": {
        "label": "autonomous story generation quality",
        "criteria": [
            "story_quality_stability",
            "early_hook_strength",
            "episode_end_hook_strength",
            "long_arc_payoff_stability",
            "protagonist_fantasy_persistence",
            "reader_retention_stability",
            "quality_gate_fail_closed",
        ],
    },
    "judgment_capability": {
        "label": "quality judgment and fail-closed evaluation",
        "criteria": [
            "quality_gate_fail_closed",
            "adaptive_edit_governance",
            "human_quality_lift_near_zero",
        ],
    },
    "recovery_capability": {
        "label": "automatic recovery and safe blocking",
        "criteria": [
            "closed_loop_cycle_completion",
            "adaptive_edit_governance",
            "fault_injection_resilience",
        ],
    },
    "operations_capability": {
        "label": "serial operations and market-aware portfolio control",
        "criteria": [
            "reader_retention_stability",
            "serialization_fatigue_control",
            "soak_steady_noop_dominance",
            "autonomous_convergence_trend",
            "market_feedback_autoloop",
            "automatic_scope_authority_policy_handling",
        ],
    },
    "truth_capability": {
        "label": "append-only truth and replayable control state",
        "criteria": [
            "append_only_truth_lineage_replayability",
            "metaos_identity_priority",
            "control_loop_state_closure",
        ],
    },
    "self_evolution_capability": {
        "label": "self-improving autonomous system behavior",
        "criteria": [
            "automatic_scope_authority_policy_handling",
            "market_feedback_autoloop",
            "human_quality_lift_near_zero",
            "autonomous_convergence_trend",
        ],
    },
}


def _read_json(path: str, default: Any) -> Any:
    if not path or not os.path.exists(path):
        return deepcopy(default)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return deepcopy(default)


def _read_jsonl(path: str) -> List[Dict[str, Any]]:
    if not path or not os.path.exists(path):
        return []
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _bool_path(path: str) -> bool:
    return bool(path) and os.path.exists(path)


def _criteria_result(passed: bool, evidence: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "passed": bool(passed),
        "evidence": evidence,
        "details": details or {},
    }


def _repair_entry_for_criterion(name: str, criteria: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    spec = CRITERIA_SPECS[name]
    details = dict(criteria.get(name, {}).get("details") or {})
    priority = int(spec["priority"])
    repair_context: Dict[str, Any] = {}

    if name == "market_feedback_autoloop" and bool(details.get("business_feedback_present")):
        priority = max(5, priority - 10)
        repair_context["business_feedback_rebind_required"] = True
    if name == "early_hook_strength":
        repair_context["hook_bias"] = 0.14
        repair_context["rewrite_pressure"] = "high"
    if name == "episode_end_hook_strength":
        repair_context["hook_bias"] = max(float(repair_context.get("hook_bias", 0.0) or 0.0), 0.1)
        repair_context["payoff_bias"] = 0.05
        repair_context["rewrite_pressure"] = "high"
    if name == "long_arc_payoff_stability":
        repair_context["payoff_bias"] = max(float(repair_context.get("payoff_bias", 0.0) or 0.0), 0.12)
        repair_context["rewrite_pressure"] = "high"
    if name == "protagonist_fantasy_persistence":
        repair_context["hook_bias"] = max(float(repair_context.get("hook_bias", 0.0) or 0.0), 0.06)
        repair_context["payoff_bias"] = max(float(repair_context.get("payoff_bias", 0.0) or 0.0), 0.08)
        repair_context["rewrite_pressure"] = "high"
    if name == "reader_retention_stability":
        repair_context["hook_bias"] = max(float(repair_context.get("hook_bias", 0.0) or 0.0), 0.12)
        repair_context["payoff_bias"] = max(float(repair_context.get("payoff_bias", 0.0) or 0.0), 0.06)
        repair_context["rewrite_pressure"] = "high"
    if name == "serialization_fatigue_control":
        repair_context["world_lock"] = True
        repair_context["causal_repair_priority"] = "high"
    if name == "automatic_scope_authority_policy_handling":
        repair_context["scope_policy_rebind_required"] = True
    if name == "human_quality_lift_near_zero":
        repair_context["human_lift_sampling_required"] = True

    return {
        "criterion": name,
        "repair_job_type": "repair_final_threshold",
        "repair_action": spec["repair"],
        "priority": priority,
        "repair_context": repair_context,
        "evidence_details": details,
    }


def _track_id_from_out_dir(out_dir: str) -> str:
    track_root = os.path.dirname(out_dir.rstrip(os.sep))
    return os.path.basename(track_root) or "unknown_track"


def _latest_episode_row(metrics_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    for row in reversed(metrics_rows):
        if row.get("episode") is not None and isinstance(row.get("scores"), dict):
            return row
    return {}


def _latest_rejection(metrics_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    for row in reversed(metrics_rows):
        if row.get("type") == "episode_rejected":
            return row
    return {}


def _latest_metric_by_type(metrics_rows: List[Dict[str, Any]], metric_type: str) -> Dict[str, Any]:
    for row in reversed(metrics_rows):
        if row.get("type") == metric_type:
            return row
    return {}


def _business_feedback_summary() -> Dict[str, Any]:
    summary = {
        "revenue_input_present": False,
        "campaign_input_present": False,
        "business_feedback_present": False,
    }
    for key, path in {
        "revenue_input_present": os.path.join("data", "revenue_input.csv"),
        "campaign_input_present": os.path.join("data", "campaign_input.csv"),
    }.items():
        try:
            summary[key] = os.path.exists(path) and os.path.getsize(path) > 0
        except Exception:
            summary[key] = False
    summary["business_feedback_present"] = bool(summary["revenue_input_present"] or summary["campaign_input_present"])
    return summary


def _story_state_from(state: Dict[str, Any]) -> Dict[str, Any]:
    return dict(state.get("story_state_v2") or {})


def _episode_attribution_from(latest_episode: Dict[str, Any], story_state: Dict[str, Any]) -> Dict[str, Any]:
    latest = dict(latest_episode.get("episode_attribution") or latest_episode.get("meta", {}).get("episode_attribution") or {})
    if latest:
        return latest
    control = dict(story_state.get("control") or {})
    episode_memory = dict(control.get("episode_attribution") or {})
    return dict(episode_memory.get("latest") or {})


def _score_value(latest_episode: Dict[str, Any], cycle_context: Dict[str, Any], key: str, default: float = 0.0) -> float:
    if key in cycle_context:
        return _as_float(cycle_context.get(key), default)
    scores = dict(latest_episode.get("scores") or {})
    return _as_float(scores.get(key), default)


def _runtime_sidecar_evidence(queue_state: Dict[str, Any], supervisor_state: Dict[str, Any]) -> bool:
    queue_last_sync = queue_state.get("last_sync")
    supervisor_last_event = str(supervisor_state.get("last_event_type") or "")
    return bool(queue_last_sync or queue_state.get("jobs") or supervisor_last_event or supervisor_state.get("active_job_id"))


def _repair_jobs_for_track(queue_state: Dict[str, Any], track_id: str) -> List[Dict[str, Any]]:
    prefix = f"repair:{track_id}:"
    return [job for job in queue_state.get("jobs", []) if str(job.get("job_id", "")).startswith(prefix)]


def _infer_policy_decision(
    *,
    gate_passed: bool,
    queued_repairs: List[Dict[str, Any]],
    promotion_state: Dict[str, Any],
    cycle_context: Dict[str, Any],
) -> str:
    explicit = str(cycle_context.get("policy_decision") or "").strip().lower()
    if explicit:
        return explicit
    if not gate_passed:
        if cycle_context.get("rewrite_attempted"):
            return "rewrite"
        return "reject" if queued_repairs else "hold"
    last_promotion = promotion_state.get("last_promotion_decision") or {}
    decision = str(last_promotion.get("decision") or "").strip().lower()
    if decision == "promoted":
        return "promote"
    return "continue"


def _queue_is_consistent(queue_state: Dict[str, Any], supervisor_state: Dict[str, Any]) -> bool:
    queue_status = str(queue_state.get("queue_status") or "")
    supervisor_status = str(supervisor_state.get("status") or "")
    if not queue_status or not supervisor_status:
        return False
    if queue_status == "running":
        return supervisor_status in {"running", "blocked"}
    return queue_status == supervisor_status or supervisor_status == "blocked"


def _capability_bundle_summary(criteria: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    bundles: Dict[str, Any] = {}
    for bundle_id, spec in CAPABILITY_BUNDLES.items():
        bundle_criteria = list(spec.get("criteria", []) or [])
        failed = [criterion for criterion in bundle_criteria if not criteria.get(criterion, {}).get("passed")]
        bundles[bundle_id] = {
            "label": spec.get("label"),
            "passed": len(failed) == 0,
            "criteria": bundle_criteria,
            "failed_criteria": failed,
            "completion_ratio": round((len(bundle_criteria) - len(failed)) / max(1, len(bundle_criteria)), 4),
        }
    return bundles


def _record_final_threshold_history(
    state: Dict[str, Any],
    report: Dict[str, Any],
    *,
    state_path: str,
    safe_mode: bool,
) -> Dict[str, Any]:
    if not isinstance(state, dict):
        return {}
    story_state = dict(state.get("story_state_v2") or {})
    control = dict(story_state.get("control") or {})
    history_state = dict(
        control.get("final_threshold_history")
        or {
            "observed": 0,
            "ready_ratio": 0.0,
            "recent_fail_ratio": 0.0,
            "history": [],
        }
    )
    item = {
        "ready": bool(report.get("final_threshold_ready")),
        "failed_criteria_count": len(list(report.get("failed_criteria", []) or [])),
        "failed_bundle_count": len(list(report.get("failed_bundles", []) or [])),
        "quality_lift_if_human_intervenes": _as_float(report.get("quality_lift_if_human_intervenes"), 1.0),
    }
    history = (list(history_state.get("history", []) or []) + [item])[-12:]
    observed = int(history_state.get("observed", 0) or 0) + 1
    ready_ratio = sum(1 for row in history if row.get("ready")) / max(1, len(history))
    recent = history[-4:]
    recent_fail_ratio = sum(1 for row in recent if not row.get("ready")) / max(1, len(recent))
    history_state.update(
        {
            "observed": observed,
            "ready_ratio": round(ready_ratio, 4),
            "recent_fail_ratio": round(recent_fail_ratio, 4),
            "history": history,
        }
    )
    control["final_threshold_history"] = history_state
    story_state["control"] = control
    state["story_state_v2"] = story_state
    safe_write_text(
        state_path,
        json.dumps(state, ensure_ascii=False, indent=2),
        safe_mode=safe_mode,
        project_dir_for_backup=os.path.dirname(state_path),
    )
    return history_state


def evaluate_final_threshold_bundle(
    cfg: Dict[str, Any],
    out_dir: str,
    *,
    cycle_context: Dict[str, Any] | None = None,
    queue_path: str = JOB_QUEUE_PATH,
    supervisor_path: str = SUPERVISOR_STATE_PATH,
    admission_path: str = ADMISSION_STATE_PATH,
    promotion_path: str = PROMOTION_STATE_PATH,
    safe_mode: bool | None = None,
) -> Dict[str, Any]:
    cycle_context = dict(cycle_context or {})
    safe_mode = bool(cfg.get("safe_mode", False) if safe_mode is None else safe_mode)
    track_id = str(cycle_context.get("track_id") or _track_id_from_out_dir(out_dir))
    metrics_path = os.path.join(out_dir, "metrics.jsonl")
    events_path = os.path.join(out_dir, "events.jsonl")
    state_path = os.path.join(os.path.dirname(out_dir), "state.json")
    final_path = os.path.join(out_dir, FINAL_THRESHOLD_FILENAME)

    metrics_rows = _read_jsonl(metrics_path)
    latest_episode = _latest_episode_row(metrics_rows)
    latest_rejection = _latest_rejection(metrics_rows)
    state = _read_json(state_path, {})
    queue_state = load_job_queue_state(queue_path) if queue_path else {}
    supervisor_state = load_supervisor_state(supervisor_path) if supervisor_path else {}
    admission_state = load_admission_state(admission_path) if admission_path else {}
    promotion_state = load_promotion_state(promotion_path) if promotion_path else {}
    cert_report = _read_json(os.path.join(out_dir, "certification_report.json"), {})
    grade_state = _read_json(os.path.join(out_dir, "grade_state.json"), {})
    latest_eval = _latest_metric_by_type(metrics_rows, "final_threshold_eval")
    latest_certification = _latest_metric_by_type(metrics_rows, "certification")
    story_state = _story_state_from(state)
    control = dict(story_state.get("control") or {})
    reader_quality = dict(control.get("reader_quality") or {})
    episode_attribution = _episode_attribution_from(latest_episode, story_state)
    soak_history = dict((story_state.get("control", {}) or {}).get("soak_history", {}) or {})
    threshold_history = dict((story_state.get("control", {}) or {}).get("final_threshold_history", {}) or {})
    promise_graph = dict(story_state.get("promise_graph") or {})
    cast = dict(story_state.get("cast") or {})
    protagonist = dict(cast.get("protagonist") or {})

    last_quality_gate = dict(state.get("last_quality_gate") or latest_episode.get("meta", {}).get("quality_gate") or {})
    gate_checks = dict(last_quality_gate.get("checks") or {})
    gate_passed = bool(cycle_context.get("gate_passed", last_quality_gate.get("passed", not latest_rejection)))
    predicted_retention = _as_float(
        cycle_context.get("predicted_retention", last_quality_gate.get("predicted_retention", latest_episode.get("retention", {}).get("predicted_next_episode"))),
        0.0,
    )
    content_ceiling_total = _as_float(
        cycle_context.get("content_ceiling_total", last_quality_gate.get("content_ceiling_total", latest_episode.get("content_ceiling", {}).get("ceiling_total"))),
        0.0,
    )
    causal_score = _as_float(
        cycle_context.get("causal_score", last_quality_gate.get("causal_score", latest_episode.get("meta", {}).get("scene_causality", {}).get("score"))),
        0.0,
    )
    quality_thresholds = dict(cfg.get("quality") or {})
    min_retention = _as_float(quality_thresholds.get("predicted_retention_min"), 0.75)
    min_causal = _as_float(quality_thresholds.get("causal_score_min"), 0.72)
    min_ceiling = _as_float(quality_thresholds.get("ceiling_total_min"), 60.0)
    min_early_hook = _as_float(quality_thresholds.get("upper_tier_early_hook_min"), 0.78)
    min_episode_hook = _as_float(quality_thresholds.get("upper_tier_episode_hook_min"), 0.74)
    min_payoff_signal = _as_float(quality_thresholds.get("upper_tier_payoff_signal_min"), 0.72)
    min_protagonist_momentum = _as_float(quality_thresholds.get("upper_tier_protagonist_momentum_min"), 0.58)
    max_fatigue_signal = _as_float(quality_thresholds.get("upper_tier_fatigue_signal_max"), 0.22)
    min_pacing_signal = _as_float(quality_thresholds.get("upper_tier_pacing_signal_min"), 0.70)
    hook_score_value = _score_value(latest_episode, cycle_context, "hook_score", 0.0)
    payoff_score_value = _score_value(latest_episode, cycle_context, "payoff_score", 0.0)
    pacing_score_value = _score_value(latest_episode, cycle_context, "pacing_score", 0.0)
    repetition_score_value = _score_value(latest_episode, cycle_context, "repetition_score", 0.0)
    retention_signal = _as_float(episode_attribution.get("retention_signal"), predicted_retention)
    pacing_signal = _as_float(episode_attribution.get("pacing_signal"), pacing_score_value)
    fatigue_signal = _as_float(episode_attribution.get("fatigue_signal"), repetition_score_value)
    payoff_signal = _as_float(episode_attribution.get("payoff_signal"), payoff_score_value)
    payoff_integrity = _as_float(promise_graph.get("payoff_integrity"), payoff_signal)
    payoff_corruption_flags = list(promise_graph.get("payoff_corruption_flags", []) or [])
    protagonist_progress = _as_float(protagonist.get("progress"), 0.0)
    protagonist_backlash = _as_float(protagonist.get("backlash"), 0.0)
    protagonist_urgency = _as_float(protagonist.get("urgency"), 0.0)
    inferred_protagonist_momentum = max(
        0.0,
        min(
            1.0,
            _score_value(latest_episode, cycle_context, "character_score", 0.0) * 0.38
            + hook_score_value * 0.14
            + payoff_score_value * 0.18
            + predicted_retention * 0.2
            + max(0.0, 1.0 - repetition_score_value) * 0.1,
        ),
    )
    protagonist_momentum = max(
        _as_float(cycle_context.get("protagonist_momentum"), -1.0),
        max(
            0.0,
            min(
                1.0,
                protagonist_progress * 0.18
                + protagonist_urgency / 10.0 * 0.52
                + _as_float(_score_value(latest_episode, cycle_context, "character_score", 0.0), 0.0) * 0.2
                - protagonist_backlash * 0.06,
            ),
        ),
        inferred_protagonist_momentum,
    )
    human_lift = _as_float(
        cycle_context.get(
            "quality_lift_if_human_intervenes",
            state.get(
                "quality_lift_if_human_intervenes",
                soak_history.get("quality_lift_trend", grade_state.get("quality_lift_if_human_intervenes", 1.0)),
            ),
        ),
        1.0,
    )
    queued_repairs = _repair_jobs_for_track(queue_state, track_id)
    next_step_recorded = bool(cycle_context.get("next_step_recorded"))
    if not next_step_recorded:
        next_step_recorded = bool(queued_repairs) or bool(queue_state.get("active_job_id")) or str(queue_state.get("queue_status") or "") in {"running", "done", "paused", "blocked"}
    failure_recorded = bool(cycle_context.get("failure_recorded"))
    if not failure_recorded:
        failure_recorded = bool(queue_state.get("last_error")) or bool(latest_rejection)
    action = str(cycle_context.get("action") or "unknown")
    repair_orchestration = bool(queued_repairs)
    policy_decision = _infer_policy_decision(
        gate_passed=gate_passed,
        queued_repairs=queued_repairs,
        promotion_state=promotion_state,
        cycle_context=cycle_context,
    )

    soak_report = dict(cycle_context.get("soak_report") or latest_episode.get("soak_report") or latest_episode.get("meta", {}).get("soak_report") or {})
    if soak_history and not soak_report.get("tested"):
        soak_report = {
            "tested": bool(soak_history.get("observed")),
            "steady_noop_ratio": soak_history.get("steady_noop_ratio", 0.0),
            "dominant_mode": soak_history.get("dominant_mode", "unknown"),
            "observed": soak_history.get("observed", 0),
            "quality_lift_trend": soak_history.get("quality_lift_trend", 1.0),
        }
    convergence_history = list(soak_history.get("history", []) or [])
    convergence_ready = (
        bool(soak_report.get("tested"))
        and _as_float(soak_report.get("steady_noop_ratio"), 0.0) >= 0.72
        and str(soak_report.get("dominant_mode") or "") in {"steady", "noop"}
        and human_lift <= max(DEFAULT_HUMAN_LIFT_THRESHOLD, 0.08)
    )
    if len(convergence_history) >= 3:
        recent = convergence_history[-3:]
        steady = all(float(item.get("steady_noop_ratio", 0.0) or 0.0) >= 0.68 for item in recent)
        low_lift = all(float(item.get("quality_lift_if_human_intervenes", 1.0) or 1.0) <= 0.08 for item in recent)
        convergence_ready = convergence_ready or (steady and low_lift)
    if not convergence_ready and int(threshold_history.get("observed", 0) or 0) >= 4:
        convergence_ready = (
            _as_float(threshold_history.get("ready_ratio"), 0.0) >= 0.75
            and _as_float(threshold_history.get("recent_fail_ratio"), 1.0) <= 0.25
            and human_lift <= 0.08
        )
    fault_injection = dict(cycle_context.get("fault_injection") or {})
    scope_auto = bool(cycle_context.get("scope_authority_policy_ok"))
    if not scope_auto:
        scope_auto = bool(admission_state.get("last_scope_decision")) and bool(promotion_state.get("last_promotion_decision"))
    market_ok = bool(cert_report.get("market", {}).get("ok"))
    market_data_available = bool(cert_report.get("market", {}).get("available"))
    promotion_recorded = bool(promotion_state.get("last_promotion_decision"))
    certification_recorded = bool(latest_certification)
    business_feedback = _business_feedback_summary()
    market_feedback_closed = bool(cycle_context.get("market_feedback_handled"))
    if not market_feedback_closed:
        market_feedback_closed = (
            market_data_available
            and certification_recorded
            and (promotion_recorded or market_ok or repair_orchestration or predicted_retention > 0.0 or business_feedback.get("business_feedback_present"))
        )

    lineage_present = bool(latest_episode.get("episode_attribution")) or bool(latest_episode.get("meta", {}).get("episode_attribution")) or bool(state.get("story_state_v2"))
    runtime_sidecar_evidence = _runtime_sidecar_evidence(queue_state, supervisor_state)
    append_only_ready = bool(metrics_rows) and (
        len(metrics_rows) >= 2 or _bool_path(events_path) or bool(latest_eval) or runtime_sidecar_evidence
    ) and lineage_present

    criteria: Dict[str, Dict[str, Any]] = {
        "closed_loop_cycle_completion": _criteria_result(
            bool(cycle_context.get("task_generated", True))
            and bool(cycle_context.get("execution_recorded", True))
            and (not bool(cycle_context.get("failed")) or failure_recorded)
            and next_step_recorded,
            "cycle generated, executed, recorded, and advanced or scheduled the next step"
            if next_step_recorded
            else "cycle did not record a next-step transition",
            {
                "action": action,
                "failure_recorded": failure_recorded,
                "next_step_recorded": next_step_recorded,
                "queue_status": queue_state.get("queue_status"),
            },
        ),
        "quality_gate_fail_closed": _criteria_result(
            gate_passed
            or (
                policy_decision in {"hold", "reject", "rewrite"}
                and (failure_recorded or repair_orchestration)
                and not os.path.exists(os.path.join(out_dir, f"episode_{int(cycle_context.get('episode', latest_rejection.get('episode', 0)) or 0):03}.txt"))
            ),
            "quality failure stayed fail-closed with rejection or repair scheduling"
            if (gate_passed or failure_recorded or repair_orchestration)
            else "quality failure lacked fail-closed handling",
            {
                "gate_passed": gate_passed,
                "policy_decision": policy_decision,
                "repair_jobs": len(queued_repairs),
                "failed_checks": list(last_quality_gate.get("failed_checks", latest_rejection.get("failed_checks", [])) or []),
            },
        ),
        "append_only_truth_lineage_replayability": _criteria_result(
            append_only_ready and bool(queue_state) and bool(supervisor_state),
            "metrics, event log, lineage, queue, and supervisor snapshots remain replayable"
            if append_only_ready and bool(queue_state) and bool(supervisor_state)
            else "append-only truth or lineage evidence is incomplete",
            {
                "metrics_rows": len(metrics_rows),
                "events_path_exists": _bool_path(events_path) or bool(latest_eval),
                "runtime_sidecar_evidence": runtime_sidecar_evidence,
                "lineage_present": lineage_present,
                "queue_snapshot_present": bool(queue_state),
                "supervisor_snapshot_present": bool(supervisor_state),
            },
        ),
        "metaos_identity_priority": _criteria_result(
            append_only_ready and not bool(cycle_context.get("prefer_production_convenience")),
            "append-only truth and replayability remained above convenience shortcuts"
            if append_only_ready
            else "MetaOS identity was not evidenced strongly enough in this cycle",
            {
                "append_only_truth_lineage_replayability": append_only_ready,
                "prefer_production_convenience": bool(cycle_context.get("prefer_production_convenience")),
            },
        ),
        "story_quality_stability": _criteria_result(
            gate_passed
            and causal_score >= min_causal
            and content_ceiling_total >= min_ceiling
            and gate_checks.get("world_instability", True),
            "story stability signals passed across gate, causality, ceiling, and world coherence"
            if gate_passed
            else "story stability gate failed",
            {
                "gate_passed": gate_passed,
                "causal_score": causal_score,
                "causal_score_min": min_causal,
                "content_ceiling_total": content_ceiling_total,
                "ceiling_total_min": min_ceiling,
                "world_instability_check": gate_checks.get("world_instability", True),
            },
        ),
        "early_hook_strength": _criteria_result(
            gate_passed
            and hook_score_value >= min_early_hook
            and predicted_retention >= min_retention
            and retention_signal >= min_episode_hook,
            "opening pressure, retention expectation, and immediate hook strength met upper-tier reader expectations"
            if gate_passed
            else "early hook quality did not clear the bundled threshold",
            {
                "hook_score": hook_score_value,
                "hook_score_min": min_early_hook,
                "predicted_retention": predicted_retention,
                "predicted_retention_min": min_retention,
                "retention_signal": retention_signal,
                "retention_signal_min": min_episode_hook,
            },
        ),
        "episode_end_hook_strength": _criteria_result(
            gate_passed
            and gate_checks.get("cliffhanger_valid", True)
            and retention_signal >= min_episode_hook
            and predicted_retention >= min_retention,
            "episode ending maintained addictive carryover pressure"
            if gate_passed
            else "episode ending did not preserve enough next-step compulsion",
            {
                "cliffhanger_valid_check": gate_checks.get("cliffhanger_valid", True),
                "retention_signal": retention_signal,
                "retention_signal_min": min_episode_hook,
                "predicted_retention": predicted_retention,
            },
        ),
        "long_arc_payoff_stability": _criteria_result(
            gate_passed
            and payoff_signal >= min_payoff_signal
            and payoff_integrity >= min_payoff_signal
            and not payoff_corruption_flags,
            "promise graph and payoff integrity stayed stable enough for long-arc trust"
            if gate_passed
            else "long-arc payoff stability did not clear the threshold",
            {
                "payoff_signal": payoff_signal,
                "payoff_signal_min": min_payoff_signal,
                "payoff_integrity": payoff_integrity,
                "payoff_corruption_flags": payoff_corruption_flags,
            },
        ),
        "protagonist_fantasy_persistence": _criteria_result(
            gate_passed
            and protagonist_momentum >= min_protagonist_momentum,
            "protagonist momentum remained persuasive enough to sustain fantasy fulfilment"
            if gate_passed
            else "protagonist fantasy pressure was too weak for upper-tier serial expectations",
            {
                "protagonist_momentum": round(protagonist_momentum, 4),
                "protagonist_momentum_min": min_protagonist_momentum,
                "protagonist_progress": protagonist_progress,
                "protagonist_backlash": protagonist_backlash,
                "protagonist_urgency": protagonist_urgency,
            },
        ),
        "reader_retention_stability": _criteria_result(
            gate_passed
            and predicted_retention >= min_retention
            and gate_checks.get("hook_score", True)
            and gate_checks.get("cliffhanger_valid", True),
            "reader retention signals passed hook, cliffhanger, and retention thresholds"
            if gate_passed
            else "reader retention signals did not clear the final bundle",
            {
                "predicted_retention": predicted_retention,
                "predicted_retention_min": min_retention,
                "hook_score_check": gate_checks.get("hook_score", True),
                "cliffhanger_valid_check": gate_checks.get("cliffhanger_valid", True),
                "reader_quality_debt": {
                    "hook_debt": _as_float(reader_quality.get("hook_debt"), 0.0),
                    "retention_debt": _as_float(reader_quality.get("retention_debt"), 0.0),
                    "thinness_debt": _as_float(reader_quality.get("thinness_debt"), 0.0),
                    "fake_urgency_debt": _as_float(reader_quality.get("fake_urgency_debt"), 0.0),
                },
            },
        ),
        "serialization_fatigue_control": _criteria_result(
            gate_passed
            and fatigue_signal <= max_fatigue_signal
            and pacing_signal >= min_pacing_signal
            and pacing_score_value >= min_pacing_signal
            and repetition_score_value <= max(0.35, max_fatigue_signal + 0.1),
            "serialization rhythm stayed strong without accumulating excessive fatigue"
            if gate_passed
            else "serialization fatigue or pacing instability remained too high",
            {
                "fatigue_signal": fatigue_signal,
                "fatigue_signal_max": max_fatigue_signal,
                "pacing_signal": pacing_signal,
                "pacing_signal_min": min_pacing_signal,
                "pacing_score": pacing_score_value,
                "repetition_score": repetition_score_value,
                "reader_quality_debt": {
                    "fatigue_debt": _as_float(reader_quality.get("fatigue_debt"), 0.0),
                    "repetition_debt": _as_float(reader_quality.get("repetition_debt"), 0.0),
                    "deja_vu_debt": _as_float(reader_quality.get("deja_vu_debt"), 0.0),
                    "compression_debt": _as_float(reader_quality.get("compression_debt"), 0.0),
                },
            },
        ),
        "adaptive_edit_governance": _criteria_result(
            (not gate_passed and policy_decision in {"hold", "reject", "rewrite"})
            or (gate_passed and policy_decision in {"continue", "promote", "accept"}),
            "policy decisions matched degradation or promotion signals"
            if ((not gate_passed and policy_decision in {"hold", "reject", "rewrite"}) or (gate_passed and policy_decision in {"continue", "promote", "accept"}))
            else "policy response did not match the detected quality state",
            {
                "gate_passed": gate_passed,
                "policy_decision": policy_decision,
                "repair_jobs": len(queued_repairs),
            },
        ),
        "soak_steady_noop_dominance": _criteria_result(
            bool(soak_report.get("tested"))
            and _as_float(soak_report.get("steady_noop_ratio"), 0.0) >= 0.5
            and str(soak_report.get("dominant_mode") or "") in {"steady", "noop"},
            "soak report proved steady or noop dominance"
            if soak_report.get("tested")
            else "no soak evidence was available for this cycle",
            soak_report,
        ),
        "autonomous_convergence_trend": _criteria_result(
            convergence_ready,
            "recent unattended cycles show converging steady/noop dominance and low human-lift trend"
            if convergence_ready
            else "recent unattended cycles do not yet prove convergence toward the autonomous target",
            {
                "observed_cycles": len(convergence_history),
                "recent_history": convergence_history[-3:],
                "final_threshold_history": threshold_history,
            },
        ),
        "fault_injection_resilience": _criteria_result(
            bool(fault_injection.get("tested"))
            and (bool(fault_injection.get("recovered")) or bool(fault_injection.get("safe_blocked"))),
            "fault injection recovered or safely blocked without opening the loop"
            if fault_injection.get("tested")
            else "fault injection evidence was missing",
            fault_injection,
        ),
        "human_quality_lift_near_zero": _criteria_result(
            human_lift <= _as_float(cycle_context.get("human_lift_threshold"), DEFAULT_HUMAN_LIFT_THRESHOLD),
            "human intervention no longer provides meaningful quality lift"
            if human_lift <= _as_float(cycle_context.get("human_lift_threshold"), DEFAULT_HUMAN_LIFT_THRESHOLD)
            else "human intervention still appears to add meaningful quality",
            {
                "quality_lift_if_human_intervenes": human_lift,
                "threshold": _as_float(cycle_context.get("human_lift_threshold"), DEFAULT_HUMAN_LIFT_THRESHOLD),
            },
        ),
        "automatic_scope_authority_policy_handling": _criteria_result(
            scope_auto,
            "scope, authority, and policy handling closed automatically"
            if scope_auto
            else "automatic scope/authority/policy handling lacks evidence",
            {
                "admission_last_decision": admission_state.get("last_scope_decision"),
                "promotion_last_decision": promotion_state.get("last_promotion_decision"),
                "scope_authority_policy_ok": bool(cycle_context.get("scope_authority_policy_ok")),
            },
        ),
        "control_loop_state_closure": _criteria_result(
            (bool(state.get("story_state_v2")) or bool(latest_episode) or bool(episode_attribution))
            and bool(queue_state)
            and bool(supervisor_state)
            and _queue_is_consistent(queue_state, supervisor_state)
            and next_step_recorded,
            "control-state, queue, and supervisor stayed in a closed loop"
            if (bool(state.get("story_state_v2")) or bool(latest_episode) or bool(episode_attribution)) and bool(queue_state) and bool(supervisor_state)
            else "control-state or runtime sidecars were not closed",
            {
                "story_state_present": bool(state.get("story_state_v2")),
                "episode_state_evidence": bool(latest_episode) or bool(episode_attribution),
                "queue_status": queue_state.get("queue_status"),
                "supervisor_status": supervisor_state.get("status"),
                "next_step_recorded": next_step_recorded,
            },
        ),
        "market_feedback_autoloop": _criteria_result(
            market_feedback_closed,
            "market and reader feedback fed the next policy or repair step"
            if market_feedback_closed
            else "market feedback was not closed back into policy generation",
            {
                "market_ok": market_ok,
                "market_data_available": market_data_available,
                "certification_recorded": certification_recorded,
                "promotion_recorded": promotion_recorded,
                "business_feedback_present": business_feedback.get("business_feedback_present"),
                "predicted_retention": predicted_retention,
                "repair_jobs": len(queued_repairs),
            },
        ),
    }

    failed_criteria = [name for name, result in criteria.items() if not result["passed"]]
    capability_bundles = _capability_bundle_summary(criteria)
    failed_bundles = [bundle_id for bundle_id, bundle in capability_bundles.items() if not bundle.get("passed")]
    blocking_evidence = [
        {
            "criterion": name,
            "evidence": criteria[name]["evidence"],
            "details": criteria[name]["details"],
        }
        for name in failed_criteria
    ]
    next_required_repairs = [_repair_entry_for_criterion(name, criteria) for name in failed_criteria]

    report = {
        "schema_version": 1,
        "track_id": track_id,
        "out_dir": out_dir,
        "final_threshold_ready": len(failed_criteria) == 0,
        "failed_criteria": failed_criteria,
        "failed_bundles": failed_bundles,
        "blocking_evidence": blocking_evidence,
        "next_required_repairs": next_required_repairs,
        "quality_lift_if_human_intervenes": human_lift,
        "criteria": criteria,
        "capability_bundles": capability_bundles,
        "cycle_context": cycle_context,
    }

    safe_write_text(
        final_path,
        json.dumps(report, ensure_ascii=False, indent=2),
        safe_mode=safe_mode,
        project_dir_for_backup=out_dir,
    )
    append_jsonl(
        metrics_path,
        {
            "type": "final_threshold_eval",
            "track_id": track_id,
            "final_threshold_ready": report["final_threshold_ready"],
            "failed_criteria": failed_criteria,
            "failed_bundles": failed_bundles,
        },
        safe_mode=safe_mode,
        project_dir_for_backup=out_dir,
    )
    log_event(
        out_dir,
        "final_threshold_evaluated",
        {
            "track_id": track_id,
            "final_threshold_ready": report["final_threshold_ready"],
            "failed_criteria": failed_criteria,
            "failed_bundles": failed_bundles,
        },
        safe_mode=safe_mode,
    )
    threshold_history = _record_final_threshold_history(state, report, state_path=state_path, safe_mode=safe_mode)
    report["threshold_history"] = threshold_history

    if queue_path:
        queue_state = _upsert_repair_jobs(queue_state, report, track_id, out_dir, queue_path, safe_mode=safe_mode)
    if supervisor_path:
        if queue_state:
            update_supervisor_from_queue(queue_state, path=supervisor_path, safe_mode=safe_mode)
        _sync_supervisor_threshold(load_supervisor_state(supervisor_path), report, supervisor_path, safe_mode=safe_mode)
    return report


def _upsert_repair_jobs(
    queue_state: Dict[str, Any],
    report: Dict[str, Any],
    track_id: str,
    out_dir: str,
    queue_path: str,
    *,
    safe_mode: bool,
) -> Dict[str, Any]:
    state = deepcopy(queue_state or load_job_queue_state(queue_path))
    for repair in report.get("next_required_repairs", []):
        criterion = str(repair.get("criterion") or "")
        job_id = f"repair:{track_id}:{criterion}"
        upsert_job(
            state,
            str(repair.get("repair_job_type") or "repair_final_threshold"),
            job_id,
            payload={
                "track_id": track_id,
                "criterion": criterion,
                "repair_action": repair.get("repair_action"),
                "repair_context": dict(repair.get("repair_context") or {}),
                "evidence_details": dict(repair.get("evidence_details") or {}),
                "out_dir": out_dir,
                "final_threshold_eval_path": os.path.join(out_dir, FINAL_THRESHOLD_FILENAME),
            },
            priority=int(repair.get("priority", 100) or 100),
        )
    save_job_queue_state(state, path=queue_path, safe_mode=safe_mode)
    return state


def ensure_final_threshold_repairs(
    report: Dict[str, Any],
    *,
    queue_path: str = JOB_QUEUE_PATH,
    safe_mode: bool = True,
) -> Dict[str, Any]:
    out_dir = str(report.get("out_dir") or "")
    track_id = str(report.get("track_id") or _track_id_from_out_dir(out_dir))
    return _upsert_repair_jobs(
        load_job_queue_state(queue_path),
        report,
        track_id,
        out_dir,
        queue_path,
        safe_mode=safe_mode,
    )


def _sync_supervisor_threshold(
    supervisor_state: Dict[str, Any],
    report: Dict[str, Any],
    supervisor_path: str,
    *,
    safe_mode: bool,
) -> Dict[str, Any]:
    state = deepcopy(supervisor_state or load_supervisor_state(supervisor_path))
    repairs = list(report.get("next_required_repairs", []) or [])
    runtime_repairs: Dict[str, Any] = {}
    for repair in repairs:
        runtime_repairs.update(dict(repair.get("repair_context") or {}))
    failed_bundles = list(report.get("failed_bundles", []) or [])
    if any(bundle in {"truth_capability", "recovery_capability"} for bundle in failed_bundles):
        bundle_priority_mode = "critical_repair"
    elif any(bundle in {"judgment_capability", "operations_capability", "generation_capability", "self_evolution_capability"} for bundle in failed_bundles):
        bundle_priority_mode = "caution_repair"
    elif repairs:
        bundle_priority_mode = "criterion_repair"
    else:
        bundle_priority_mode = None
    reader_quality_priority = None
    if runtime_repairs.get("hook_bias") or runtime_repairs.get("payoff_bias") or runtime_repairs.get("rewrite_pressure"):
        reader_quality_priority = "critical" if runtime_repairs.get("hook_bias", 0.0) or runtime_repairs.get("rewrite_pressure") == "high" else "high"
    state["final_threshold_ready"] = bool(report.get("final_threshold_ready"))
    state["final_threshold_path"] = os.path.join(report.get("out_dir", ""), FINAL_THRESHOLD_FILENAME)
    state["failed_criteria"] = list(report.get("failed_criteria", []) or [])
    state["failed_bundles"] = failed_bundles
    state["bundle_priority_mode"] = bundle_priority_mode
    state["reader_quality_priority"] = reader_quality_priority
    state["runtime_repairs"] = runtime_repairs
    state["quality_lift_if_human_intervenes"] = _as_float(report.get("quality_lift_if_human_intervenes"), 1.0)
    if report.get("final_threshold_ready"):
        if state.get("status") == "blocked" and state.get("stop_reason") == "final_threshold_failed":
            state["status"] = "running"
        if state.get("stop_reason") == "final_threshold_failed":
            state["stop_reason"] = None
    else:
        state["status"] = "blocked"
        state["stop_reason"] = "final_threshold_failed"
    return save_supervisor_state(state, path=supervisor_path, safe_mode=safe_mode)
