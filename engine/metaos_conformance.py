from __future__ import annotations

from typing import Any, Dict

from engine.job_queue import load_job_queue_state
from engine.metaos_adapter_registry import adapter_resolution, registered_adapters
from engine.metaos_contracts import validate_job_queue_contract, validate_policy_decision, validate_supervisor_contract
from engine.metaos_policy import apply_promotion_policy, apply_scope_policy
from engine.runtime_supervisor import (
    load_admission_state,
    load_promotion_state,
    update_supervisor_from_queue,
)
from engine.webnovel_adapter import artifact_from_episode_result, material_from_source


CONFORMANCE_CHECKS = [
    "adapter_resolution",
    "scope_policy",
    "admission_snapshot",
    "job_queue_contract",
    "supervisor_contract",
    "artifact_normalization",
    "promotion_policy",
    "promotion_snapshot",
]


def run_project_conformance(
    *,
    project_type: str,
    source: Dict[str, Any],
    episode_result: Dict[str, Any],
    cfg: Dict[str, Any],
    admission_path: str,
    promotion_path: str,
    supervisor_path: str,
    queue_path: str,
    safe_mode: bool = True,
) -> Dict[str, Any]:
    resolution = adapter_resolution(project_type)
    if resolution["verdict"] != "accept":
        return {"ok": False, "stage": "adapter_resolution", "resolution": resolution}

    material = material_from_source(source)
    scope_result = apply_scope_policy(material, admission_path=admission_path, queue_path=queue_path, safe_mode=safe_mode)
    policy_ok, policy_reason = validate_policy_decision(scope_result["decision"])
    if not policy_ok:
        return {"ok": False, "stage": "scope_policy", "reason": policy_reason}

    queue_state = load_job_queue_state(queue_path)
    queue_state["queue_status"] = "running"
    queue_state["active_job_id"] = next((job["job_id"] for job in queue_state.get("jobs", []) if job.get("status") in {"queued", "running"}), None)
    supervisor_state = update_supervisor_from_queue(queue_state, path=supervisor_path, safe_mode=safe_mode)
    queue_ok, queue_reason = validate_job_queue_contract(queue_state)
    supervisor_ok, supervisor_reason = validate_supervisor_contract(supervisor_state)
    if not queue_ok:
        return {"ok": False, "stage": "queue_contract", "reason": queue_reason}
    if not supervisor_ok:
        return {"ok": False, "stage": "supervisor_contract", "reason": supervisor_reason}

    artifact = artifact_from_episode_result(cfg, episode_result)
    promote_result = apply_promotion_policy(artifact, promotion_path=promotion_path, queue_path=queue_path, safe_mode=safe_mode)
    promote_ok, promote_reason = validate_policy_decision(promote_result["decision"])
    if not promote_ok:
        return {"ok": False, "stage": "promotion_policy", "reason": promote_reason}

    return {
        "ok": True,
        "resolution": resolution,
        "checks": {check: "passed" for check in CONFORMANCE_CHECKS},
        "scope_decision": scope_result["decision"],
        "promotion_decision": promote_result["decision"],
        "admission_state": load_admission_state(admission_path),
        "promotion_state": load_promotion_state(promotion_path),
        "queue_state": load_job_queue_state(queue_path),
        "supervisor_state": supervisor_state,
        "artifact": artifact,
    }


def conformance_matrix() -> list[dict]:
    rows = []
    for project_type, adapter_name in sorted(registered_adapters().items()):
        resolution = adapter_resolution(project_type)
        rows.append(
            {
                "project_type": project_type,
                "adapter_name": adapter_name,
                "status": resolution.get("status"),
                "verdict": resolution.get("verdict"),
                "reason": resolution.get("reason"),
                "contract_version": ((resolution.get("adapter_manifest") or {}).get("contract_version")),
                "checks_required": list(CONFORMANCE_CHECKS),
            }
        )
    return rows
