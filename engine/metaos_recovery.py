from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence, Tuple


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(sorted((k, _freeze(v)) for k, v in value.items()))
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def detect_duplicate_events(events: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[Tuple[Any, Any, Any]] = set()
    duplicates: List[Dict[str, Any]] = []
    for event in events:
        key = (
            event.get("type"),
            event.get("ts"),
            _freeze(event.get("payload")) if isinstance(event.get("payload"), dict) else None,
        )
        if key in seen:
            duplicates.append(event)
            continue
        seen.add(key)
    return duplicates


def snapshot_staleness(snapshot: Dict[str, Any], queue_state: Dict[str, Any]) -> Dict[str, Any]:
    queue = dict(queue_state or {})
    snapshot_obj = dict(snapshot or {})
    queue_last_sync = dict(queue.get("last_sync") or {})
    snapshot_last_sync = dict(snapshot_obj.get("last_sync") or {})
    queue_index = int(queue_last_sync.get("current_index", queue.get("current_index", 0)) or 0)
    snapshot_index = int(snapshot_last_sync.get("current_index", snapshot_obj.get("current_index", 0)) or 0)
    stale = snapshot_index < queue_index
    return {
        "stale": stale,
        "snapshot_index": snapshot_index,
        "queue_index": queue_index,
        "reason": "stale_snapshot" if stale else "fresh_snapshot",
    }


def partial_write_detected(snapshot: Dict[str, Any], required_fields: Iterable[str]) -> Dict[str, Any]:
    missing = [field for field in required_fields if field not in (snapshot or {})]
    return {
        "partial": bool(missing),
        "missing_fields": missing,
        "reason": "partial_write" if missing else "complete_snapshot",
    }


def replay_resume_decision(
    *,
    events: Sequence[Dict[str, Any]],
    snapshot: Dict[str, Any],
    queue_state: Dict[str, Any],
    required_snapshot_fields: Iterable[str],
) -> Dict[str, Any]:
    partial = partial_write_detected(snapshot, required_snapshot_fields)
    stale = snapshot_staleness(snapshot, queue_state)
    duplicates = detect_duplicate_events(events)

    if partial["partial"]:
        return {"verdict": "recover", "reason": "partial_write_detected", "details": partial}
    if stale["stale"]:
        return {"verdict": "recover", "reason": "stale_snapshot_detected", "details": stale}
    if duplicates:
        return {"verdict": "recover", "reason": "duplicate_event_detected", "details": {"duplicate_count": len(duplicates)}}
    return {"verdict": "resume", "reason": "replay_consistent"}
