from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple


CONTRACT_VERSION = "1.0.0"

EVENT_TYPES = {
    "ingest_material",
    "scope_evaluate",
    "promote_material",
    "reject_material",
    "defer_material",
    "generate_episode",
    "rewrite_episode",
    "episode_rejected",
    "certify_artifact",
    "pause_queue",
    "resume_queue",
    "recover_failed_track",
    "job_queue_synced",
    "supervisor_snapshot_updated",
    "admission_decision_recorded",
    "promotion_decision_recorded",
}

SNAPSHOT_TYPES = {
    "queue_state",
    "job_queue_state",
    "supervisor_state",
    "admission_state",
    "promotion_state",
    "story_state",
}

JOB_TYPES = {
    "ingest_material",
    "scope_evaluate",
    "promote_material",
    "generate_episode",
    "rewrite_episode",
    "certify_artifact",
    "recover_failed_track",
    "generate_episode_track",
}

JOB_STATUSES = {"queued", "running", "completed", "failed", "rejected", "cancelled"}
QUEUE_STATUSES = {"idle", "running", "paused", "blocked", "done"}
SUPERVISOR_MODES = {"observe", "control", "recovery_only"}
SUPERVISOR_STATUSES = {"idle", "running", "paused", "blocked", "recovering", "stopped", "done"}
POLICY_VERDICTS = {"accept", "hold", "reject", "escalate", "sandbox", "promote"}

COMPATIBILITY_RULES = {
    ("1.0.0", "1.0.0"): {
        "workers": "compatible",
        "adapters": "compatible",
        "snapshots": "compatible",
        "replay": "both",
        "migration_required": False,
    }
}


def _has_fields(obj: Dict[str, Any], fields: Iterable[str]) -> Tuple[bool, str]:
    for field in fields:
        if field not in obj:
            return False, f"missing_{field}"
    return True, "ok"


def validate_event_record(record: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(record, dict):
        return False, "record_not_dict"
    ok, reason = _has_fields(record, ["ts", "type", "payload"])
    if not ok:
        return ok, reason
    if record.get("type") not in EVENT_TYPES:
        return False, "unknown_event_type"
    if not isinstance(record.get("payload"), dict):
        return False, "payload_not_dict"
    return True, "ok"


def validate_job_queue_contract(state: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(state, dict):
        return False, "state_not_dict"
    ok, reason = _has_fields(state, ["schema_version", "queue_status", "jobs"])
    if not ok:
        return ok, reason
    if state.get("queue_status") not in QUEUE_STATUSES:
        return False, "invalid_queue_status"
    if not isinstance(state.get("jobs"), list):
        return False, "jobs_not_list"
    for job in state.get("jobs", []):
        if not isinstance(job, dict):
            return False, "job_not_dict"
        ok, reason = _has_fields(job, ["job_id", "job_type", "status", "payload"])
        if not ok:
            return ok, reason
        if job.get("job_type") not in JOB_TYPES:
            return False, "invalid_job_type"
        if job.get("status") not in JOB_STATUSES:
            return False, "invalid_job_status"
        if not isinstance(job.get("payload"), dict):
            return False, "payload_not_dict"
    return True, "ok"


def validate_supervisor_contract(state: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(state, dict):
        return False, "state_not_dict"
    ok, reason = _has_fields(state, ["schema_version", "mode", "status"])
    if not ok:
        return ok, reason
    if state.get("mode") not in SUPERVISOR_MODES:
        return False, "invalid_supervisor_mode"
    if state.get("status") not in SUPERVISOR_STATUSES:
        return False, "invalid_supervisor_status"
    return True, "ok"


def validate_policy_decision(decision: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(decision, dict):
        return False, "decision_not_dict"
    ok, reason = _has_fields(decision, ["verdict", "reason"])
    if not ok:
        return ok, reason
    if decision.get("verdict") not in POLICY_VERDICTS:
        return False, "invalid_policy_verdict"
    return True, "ok"


def compatibility_report(from_version: str, to_version: str) -> Dict[str, Any]:
    if from_version == to_version:
        return {
            "from": from_version,
            "to": to_version,
            **COMPATIBILITY_RULES[(from_version, to_version)],
        }
    return {
        "from": from_version,
        "to": to_version,
        "workers": "unknown",
        "adapters": "unknown",
        "snapshots": "unknown",
        "replay": "unknown",
        "migration_required": True,
    }


def runtime_contract_manifest() -> Dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "event_types": sorted(EVENT_TYPES),
        "snapshot_types": sorted(SNAPSHOT_TYPES),
        "job_types": sorted(JOB_TYPES),
        "job_statuses": sorted(JOB_STATUSES),
        "queue_statuses": sorted(QUEUE_STATUSES),
        "supervisor_modes": sorted(SUPERVISOR_MODES),
        "supervisor_statuses": sorted(SUPERVISOR_STATUSES),
        "policy_verdicts": sorted(POLICY_VERDICTS),
    }
