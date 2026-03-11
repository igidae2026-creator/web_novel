from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any, Dict, Optional

from engine.event_log import log_event
from engine.safe_io import safe_write_text

RUNTIME_ROOT = os.path.join("domains", "webnovel", "runtime")
SUPERVISOR_STATE_PATH = os.path.join(RUNTIME_ROOT, "supervisor_state.json")
ADMISSION_STATE_PATH = os.path.join(RUNTIME_ROOT, "admission_state.json")
PROMOTION_STATE_PATH = os.path.join(RUNTIME_ROOT, "promotion_state.json")


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _default_supervisor_state() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "mode": "observe",
        "status": "idle",
        "active_job_id": None,
        "stop_reason": None,
        "recovery_required": False,
        "last_event_type": None,
        "final_threshold_ready": False,
        "final_threshold_path": None,
        "failed_criteria": [],
        "failed_bundles": [],
        "bundle_priority_mode": None,
        "reader_quality_priority": None,
        "runtime_repairs": {},
        "quality_lift_if_human_intervenes": None,
    }


def _default_admission_state() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "pending_materials": [],
        "accepted_materials": [],
        "rejected_materials": [],
        "sandboxed_materials": [],
        "escalated_materials": [],
        "last_scope_decision": None,
    }


def _default_promotion_state() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "pending_candidates": [],
        "promoted_artifacts": [],
        "rejected_candidates": [],
        "sandboxed_candidates": [],
        "escalated_candidates": [],
        "last_promotion_decision": None,
    }


def _load_or_default(path: str, default_factory) -> Dict[str, Any]:
    if not os.path.exists(path):
        return default_factory()
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        return default_factory()
    base = default_factory()
    base.update(data)
    return base


def _save_snapshot(path: str, state: Dict[str, Any], safe_mode: bool = True) -> Dict[str, Any]:
    _ensure_dir(path)
    safe_write_text(
        path,
        json.dumps(state, ensure_ascii=False, indent=2),
        safe_mode=safe_mode,
        project_dir_for_backup=os.path.dirname(path),
    )
    return state


def load_supervisor_state(path: str = SUPERVISOR_STATE_PATH) -> Dict[str, Any]:
    return _load_or_default(path, _default_supervisor_state)


def save_supervisor_state(state: Dict[str, Any], path: str = SUPERVISOR_STATE_PATH, safe_mode: bool = True) -> Dict[str, Any]:
    merged = deepcopy(_default_supervisor_state())
    merged.update(state or {})
    return _save_snapshot(path, merged, safe_mode=safe_mode)


def update_supervisor_from_queue(
    queue_state: Dict[str, Any],
    path: str = SUPERVISOR_STATE_PATH,
    safe_mode: bool = True,
) -> Dict[str, Any]:
    state = load_supervisor_state(path)
    state["status"] = queue_state.get("queue_status") or queue_state.get("status") or "idle"
    state["active_job_id"] = queue_state.get("active_job_id")
    state["recovery_required"] = bool(queue_state.get("last_error"))
    state["last_event_type"] = "job_queue_synced"
    saved = save_supervisor_state(state, path=path, safe_mode=safe_mode)
    log_event(os.path.dirname(path), "supervisor_snapshot_updated", {"status": saved["status"]}, safe_mode=safe_mode)
    return saved


def load_admission_state(path: str = ADMISSION_STATE_PATH) -> Dict[str, Any]:
    return _load_or_default(path, _default_admission_state)


def save_admission_state(state: Dict[str, Any], path: str = ADMISSION_STATE_PATH, safe_mode: bool = True) -> Dict[str, Any]:
    merged = deepcopy(_default_admission_state())
    merged.update(state or {})
    return _save_snapshot(path, merged, safe_mode=safe_mode)


def record_admission_event(
    material_id: str,
    decision: str,
    reason: str,
    path: str = ADMISSION_STATE_PATH,
    safe_mode: bool = True,
) -> Dict[str, Any]:
    state = load_admission_state(path)
    record = {"material_id": material_id, "decision": decision, "reason": reason}
    if decision == "accepted":
        state["accepted_materials"].append(record)
    elif decision == "rejected":
        state["rejected_materials"].append(record)
    elif decision == "sandboxed":
        state["sandboxed_materials"].append(record)
    elif decision == "escalated":
        state["escalated_materials"].append(record)
    else:
        state["pending_materials"].append(record)
    state["last_scope_decision"] = record
    saved = save_admission_state(state, path=path, safe_mode=safe_mode)
    log_event(os.path.dirname(path), "admission_decision_recorded", record, safe_mode=safe_mode)
    return saved


def load_promotion_state(path: str = PROMOTION_STATE_PATH) -> Dict[str, Any]:
    return _load_or_default(path, _default_promotion_state)


def save_promotion_state(state: Dict[str, Any], path: str = PROMOTION_STATE_PATH, safe_mode: bool = True) -> Dict[str, Any]:
    merged = deepcopy(_default_promotion_state())
    merged.update(state or {})
    return _save_snapshot(path, merged, safe_mode=safe_mode)


def record_promotion_event(
    artifact_id: str,
    decision: str,
    reason: str,
    path: str = PROMOTION_STATE_PATH,
    safe_mode: bool = True,
) -> Dict[str, Any]:
    state = load_promotion_state(path)
    record = {"artifact_id": artifact_id, "decision": decision, "reason": reason}
    if decision == "promoted":
        state["promoted_artifacts"].append(record)
    elif decision == "rejected":
        state["rejected_candidates"].append(record)
    elif decision == "sandboxed":
        state["sandboxed_candidates"].append(record)
    elif decision == "escalated":
        state["escalated_candidates"].append(record)
    else:
        state["pending_candidates"].append(record)
    state["last_promotion_decision"] = record
    saved = save_promotion_state(state, path=path, safe_mode=safe_mode)
    log_event(os.path.dirname(path), "promotion_decision_recorded", record, safe_mode=safe_mode)
    return saved
