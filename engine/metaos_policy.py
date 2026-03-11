from __future__ import annotations

from typing import Any, Dict, Optional

from engine.job_queue import JOB_QUEUE_PATH, load_job_queue_state, save_job_queue_state, upsert_job
from engine.metaos_contracts import validate_policy_decision
from engine.runtime_supervisor import (
    ADMISSION_STATE_PATH,
    PROMOTION_STATE_PATH,
    record_admission_event,
    record_promotion_event,
)


def _bounded_score(value: Any, default: float = 0.0) -> float:
    try:
        score = float(value)
    except Exception:
        return default
    return max(0.0, min(1.0, score))


def classify_material_for_scope(material: Dict[str, Any]) -> Dict[str, Any]:
    quality = _bounded_score(material.get("quality_score"))
    scope_fit = _bounded_score(material.get("scope_fit_score"))
    risk = _bounded_score(material.get("risk_score"))
    novelty = _bounded_score(material.get("novelty_score"), default=0.5)
    metadata = dict(material.get("metadata") or {})
    hidden_reader_risk = _bounded_score(metadata.get("hidden_reader_risk"))
    material_id = str(material.get("material_id") or "unknown_material")

    if risk >= 0.9:
        return {"verdict": "escalate", "reason": "high_risk_exception", "material_id": material_id}
    if hidden_reader_risk >= 0.35:
        return {"verdict": "hold", "reason": "hidden_reader_risk_requires_hold", "material_id": material_id, "priority": 40}
    if quality >= 0.82 and scope_fit >= 0.78 and risk <= 0.35:
        return {"verdict": "accept", "reason": "normal_scope_fit", "material_id": material_id, "priority": 20}
    if quality >= 0.72 and scope_fit >= 0.65 and risk <= 0.55 and novelty >= 0.45:
        return {"verdict": "hold", "reason": "borderline_needs_review_buffer", "material_id": material_id, "priority": 60}
    if risk >= 0.7 or scope_fit <= 0.35:
        return {"verdict": "reject", "reason": "out_of_scope_or_risky", "material_id": material_id}
    return {"verdict": "sandbox", "reason": "uncertain_scope_fit", "material_id": material_id, "priority": 80}


def classify_artifact_for_promotion(artifact: Dict[str, Any]) -> Dict[str, Any]:
    quality = _bounded_score(artifact.get("quality_score"))
    relevance = _bounded_score(artifact.get("relevance_score"))
    stability = _bounded_score(artifact.get("stability_score"))
    risk = _bounded_score(artifact.get("risk_score"))
    metadata = dict(artifact.get("metadata") or {})
    hidden_reader_risk = _bounded_score(metadata.get("hidden_reader_risk"))
    artifact_id = str(artifact.get("artifact_id") or "unknown_artifact")

    if risk >= 0.9:
        return {"verdict": "escalate", "reason": "high_risk_exception", "artifact_id": artifact_id}
    if hidden_reader_risk >= 0.35:
        return {"verdict": "hold", "reason": "hidden_reader_risk_requires_hold", "artifact_id": artifact_id, "priority": 35}
    if quality >= 0.86 and relevance >= 0.8 and stability >= 0.78 and risk <= 0.3:
        return {"verdict": "promote", "reason": "promotion_ready", "artifact_id": artifact_id, "priority": 10}
    if quality >= 0.74 and relevance >= 0.7 and stability >= 0.65 and risk <= 0.5:
        return {"verdict": "hold", "reason": "borderline_candidate", "artifact_id": artifact_id, "priority": 50}
    if quality <= 0.45 or relevance <= 0.4 or risk >= 0.72:
        return {"verdict": "reject", "reason": "not_promotion_worthy", "artifact_id": artifact_id}
    return {"verdict": "sandbox", "reason": "needs_isolated_validation", "artifact_id": artifact_id, "priority": 75}


def _validated(decision: Dict[str, Any]) -> Dict[str, Any]:
    ok, reason = validate_policy_decision(decision)
    if not ok:
        raise ValueError(f"invalid policy decision: {reason}")
    return decision


def apply_scope_policy(
    material: Dict[str, Any],
    admission_path: str = ADMISSION_STATE_PATH,
    queue_path: str = JOB_QUEUE_PATH,
    safe_mode: bool = True,
) -> Dict[str, Any]:
    decision = _validated(classify_material_for_scope(material))
    material_id = decision["material_id"]
    verdict = decision["verdict"]
    reason = decision["reason"]

    mapped_decision = {
        "accept": "accepted",
        "hold": "held",
        "reject": "rejected",
        "sandbox": "sandboxed",
        "escalate": "escalated",
    }[verdict]
    admission = record_admission_event(material_id, mapped_decision, reason, path=admission_path, safe_mode=safe_mode)

    queue_state = load_job_queue_state(queue_path)
    if verdict == "accept":
        upsert_job(
            queue_state,
            "scope_evaluate",
            f"scope:{material_id}",
            payload={"material_id": material_id, "source": material.get("source"), "verdict": verdict},
            priority=int(decision.get("priority", 50) or 50),
        )
    elif verdict in {"hold", "sandbox"}:
        upsert_job(
            queue_state,
            "ingest_material",
            f"ingest:{material_id}",
            payload={"material_id": material_id, "source": material.get("source"), "verdict": verdict},
            priority=int(decision.get("priority", 80) or 80),
        )
    save_job_queue_state(queue_state, path=queue_path, safe_mode=safe_mode)
    return {"decision": decision, "admission_state": admission}


def apply_promotion_policy(
    artifact: Dict[str, Any],
    promotion_path: str = PROMOTION_STATE_PATH,
    queue_path: str = JOB_QUEUE_PATH,
    safe_mode: bool = True,
) -> Dict[str, Any]:
    decision = _validated(classify_artifact_for_promotion(artifact))
    artifact_id = decision["artifact_id"]
    verdict = decision["verdict"]
    reason = decision["reason"]

    mapped_decision = {
        "promote": "promoted",
        "hold": "held",
        "reject": "rejected",
        "sandbox": "sandboxed",
        "escalate": "escalated",
    }[verdict]
    promotion = record_promotion_event(artifact_id, mapped_decision, reason, path=promotion_path, safe_mode=safe_mode)

    queue_state = load_job_queue_state(queue_path)
    if verdict == "promote":
        upsert_job(
            queue_state,
            "promote_material",
            f"promote:{artifact_id}",
            payload={"artifact_id": artifact_id, "verdict": verdict},
            priority=int(decision.get("priority", 20) or 20),
        )
    elif verdict in {"hold", "sandbox"}:
        upsert_job(
            queue_state,
            "certify_artifact",
            f"certify:{artifact_id}",
            payload={"artifact_id": artifact_id, "verdict": verdict},
            priority=int(decision.get("priority", 70) or 70),
        )
    save_job_queue_state(queue_state, path=queue_path, safe_mode=safe_mode)
    return {"decision": decision, "promotion_state": promotion}
