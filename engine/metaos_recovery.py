from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence, Tuple


def detect_duplicate_events(events: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[Tuple[Any, Any, Any]] = set()
    duplicates: List[Dict[str, Any]] = []
    for event in events:
        key = (
            event.get("type"),
            event.get("ts"),
            tuple(sorted((event.get("payload") or {}).items())) if isinstance(event.get("payload"), dict) else None,
        )
        if key in seen:
            duplicates.append(event)
            continue
        seen.add(key)
    return duplicates


def snapshot_staleness(snapshot: Dict[str, Any], queue_state: Dict[str, Any]) -> Dict[str, Any]:
    queue_index = int((queue_state or {}).get("last_sync", {}).get("current_index", queue_state.get("current_index", 0)) or 0)
    snapshot_index = int((snapshot or {}).get("last_sync", {}).get("current_index", snapshot.get("current_index", 0)) or 0)
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
