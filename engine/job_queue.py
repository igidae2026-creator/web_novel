from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any, Dict, List, Optional

from engine.event_log import log_event
from engine.metaos_contracts import JOB_TYPES
from engine.safe_io import safe_write_text
from engine.webnovel_adapter import track_job_payload

JOB_QUEUE_PATH = os.path.join("domains", "webnovel", "runtime", "job_queue.json")

VALID_QUEUE_STATUS = {"idle", "running", "paused", "blocked", "done"}
VALID_JOB_STATUS = {"queued", "running", "completed", "failed", "rejected", "cancelled"}
VALID_JOB_TYPES = set(JOB_TYPES)


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _default_queue_state() -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "queue_status": "idle",
        "active_job_id": None,
        "jobs": [],
        "counters": {
            "queued": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "rejected": 0,
            "cancelled": 0,
        },
        "sources": {
            "track_queue_path": os.path.join("domains", "webnovel", "tracks", "queue_state.json"),
        },
        "last_sync": None,
        "last_error": None,
    }


def _job_dict(job_type: str, job_id: str, payload: Optional[Dict[str, Any]] = None, priority: int = 100) -> Dict[str, Any]:
    return {
        "job_id": job_id,
        "job_type": job_type,
        "status": "queued",
        "priority": int(priority),
        "attempts": 0,
        "payload": payload or {},
        "result": None,
        "error": None,
    }


def validate_job_queue_state(state: Dict[str, Any]) -> tuple[bool, str]:
    if not isinstance(state, dict):
        return False, "state_not_dict"
    if state.get("queue_status") not in VALID_QUEUE_STATUS:
        return False, "invalid_queue_status"
    jobs = state.get("jobs", [])
    if not isinstance(jobs, list):
        return False, "jobs_not_list"
    seen_ids = set()
    for job in jobs:
        if not isinstance(job, dict):
            return False, "job_not_dict"
        job_id = str(job.get("job_id") or "")
        if not job_id:
            return False, "missing_job_id"
        if job_id in seen_ids:
            return False, "duplicate_job_id"
        seen_ids.add(job_id)
        if job.get("job_type") not in VALID_JOB_TYPES:
            return False, "invalid_job_type"
        if job.get("status") not in VALID_JOB_STATUS:
            return False, "invalid_job_status"
    return True, "ok"


def repair_job_queue_state(state: Dict[str, Any]) -> Dict[str, Any]:
    repaired = deepcopy(_default_queue_state())
    if not isinstance(state, dict):
        repaired["last_error"] = "job_queue_repaired_from_non_dict"
        return repaired
    repaired.update({k: v for k, v in state.items() if k in repaired and k not in {"jobs", "counters", "sources"}})
    jobs = []
    for raw in state.get("jobs", []):
        if not isinstance(raw, dict):
            continue
        job_id = str(raw.get("job_id") or "")
        job_type = str(raw.get("job_type") or "unknown")
        if not job_id:
            continue
        if job_type not in VALID_JOB_TYPES:
            job_type = "repair_final_threshold" if job_id.startswith("repair:") else "generate_episode_track"
        job = _job_dict(job_type, job_id, payload=raw.get("payload") or {}, priority=int(raw.get("priority", 100) or 100))
        job["status"] = raw.get("status") if raw.get("status") in VALID_JOB_STATUS else "queued"
        job["attempts"] = max(0, int(raw.get("attempts", 0) or 0))
        job["result"] = raw.get("result")
        job["error"] = raw.get("error")
        jobs.append(job)
    repaired["jobs"] = jobs
    repaired["sources"] = state.get("sources") if isinstance(state.get("sources"), dict) else repaired["sources"]
    repaired["counters"] = _compute_counters(jobs)
    repaired["queue_status"] = repaired["queue_status"] if repaired["queue_status"] in VALID_QUEUE_STATUS else "paused"
    repaired["last_error"] = "job_queue_repaired"
    return repaired


def load_job_queue_state(path: str = JOB_QUEUE_PATH) -> Dict[str, Any]:
    if not os.path.exists(path):
        return _default_queue_state()
    with open(path, "r", encoding="utf-8") as handle:
        state = json.load(handle)
    ok, _ = validate_job_queue_state(state)
    return state if ok else repair_job_queue_state(state)


def _queued_job_sort_key(job: Dict[str, Any]) -> tuple:
    job_type = str(job.get("job_type") or "")
    repair_context = dict(job.get("payload", {}).get("repair_context") or {})
    repair_rank = 0 if job_type == "repair_final_threshold" else 1
    trend_rank = 0 if repair_context.get("hidden_reader_risk_trend", 0.0) >= 0.35 else 1
    signal_rank = 0 if (0.0 < float(repair_context.get("heavy_reader_signal_trend", 1.0) or 1.0) < 0.72) else 1
    business_rank = 0 if repair_context.get("business_feedback_rebind_required") else 1
    reader_quality_rank = 0 if (
        repair_context.get("hook_bias")
        or repair_context.get("payoff_bias")
        or repair_context.get("rewrite_pressure")
    ) else 1
    return (
        trend_rank,
        signal_rank,
        business_rank,
        reader_quality_rank,
        int(job.get("priority", 100) or 100),
        repair_rank,
        str(job.get("job_id") or ""),
    )


def _normalize_job_order(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    queued = [job for job in jobs if job.get("status") == "queued"]
    nonqueued = [job for job in jobs if job.get("status") != "queued"]
    queued = sorted(queued, key=_queued_job_sort_key)
    return nonqueued + queued


def save_job_queue_state(state: Dict[str, Any], path: str = JOB_QUEUE_PATH, safe_mode: bool = True) -> Dict[str, Any]:
    _ensure_dir(path)
    normalized = repair_job_queue_state(state)
    normalized["jobs"] = _normalize_job_order(list(normalized.get("jobs", []) or []))
    normalized["counters"] = _compute_counters(normalized["jobs"])
    safe_write_text(
        path,
        json.dumps(normalized, ensure_ascii=False, indent=2),
        safe_mode=safe_mode,
        project_dir_for_backup=os.path.dirname(path),
    )
    return normalized


def _compute_counters(jobs: List[Dict[str, Any]]) -> Dict[str, int]:
    counters = {key: 0 for key in ["queued", "running", "completed", "failed", "rejected", "cancelled"]}
    for job in jobs:
        status = job.get("status")
        if status in counters:
            counters[status] += 1
    return counters


def upsert_job(
    state: Dict[str, Any],
    job_type: str,
    job_id: str,
    payload: Optional[Dict[str, Any]] = None,
    priority: int = 100,
) -> Dict[str, Any]:
    payload = payload or {}
    for job in state.get("jobs", []):
        if job.get("job_id") == job_id:
            job["job_type"] = job_type
            job["priority"] = int(priority)
            job["payload"] = payload
            if job.get("status") not in VALID_JOB_STATUS:
                job["status"] = "queued"
            return state
    state.setdefault("jobs", []).append(_job_dict(job_type, job_id, payload=payload, priority=priority))
    return state


def mark_job_status(
    state: Dict[str, Any],
    job_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if status not in VALID_JOB_STATUS:
        raise ValueError(f"invalid job status: {status}")
    for job in state.get("jobs", []):
        if job.get("job_id") != job_id:
            continue
        job["status"] = status
        job["result"] = result
        job["error"] = error
        if status == "running":
            job["attempts"] = max(1, int(job.get("attempts", 0) or 0) + 1)
            state["active_job_id"] = job_id
        elif state.get("active_job_id") == job_id:
            state["active_job_id"] = None
        return state
    raise KeyError(job_id)


def sync_track_queue_to_job_queue(
    track_queue_state: Dict[str, Any],
    path: str = JOB_QUEUE_PATH,
    safe_mode: bool = True,
) -> Dict[str, Any]:
    state = load_job_queue_state(path)
    state["queue_status"] = str(track_queue_state.get("status") or "idle")
    state["last_sync"] = {
        "current_index": int(track_queue_state.get("current_index", 0) or 0),
        "track_count": len(track_queue_state.get("track_dirs", []) or []),
    }
    for index, track_dir in enumerate(track_queue_state.get("track_dirs", []) or []):
        job_id = f"track:{index}"
        payload = track_job_payload(track_dir)
        payload["track_index"] = index
        state = upsert_job(state, "generate_episode_track", job_id, payload=payload, priority=index)
        if index < int(track_queue_state.get("current_index", 0) or 0):
            mark_job_status(state, job_id, "completed", result={"source": "track_queue_sync"})
        elif index == int(track_queue_state.get("current_index", 0) or 0) and state["queue_status"] == "running":
            mark_job_status(state, job_id, "running", result=None)
        elif state["queue_status"] == "done":
            mark_job_status(state, job_id, "completed", result={"source": "track_queue_sync"})
        else:
            mark_job_status(state, job_id, "queued", result=None)
    state = save_job_queue_state(state, path=path, safe_mode=safe_mode)
    runtime_dir = os.path.dirname(path)
    log_event(runtime_dir, "job_queue_synced", state["last_sync"], safe_mode=safe_mode)
    return state
