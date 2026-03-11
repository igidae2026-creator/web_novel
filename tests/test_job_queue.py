from engine.job_queue import load_job_queue_state, save_job_queue_state, sync_track_queue_to_job_queue
from engine.runtime_supervisor import (
    load_admission_state,
    load_promotion_state,
    load_supervisor_state,
    record_admission_event,
    record_promotion_event,
    update_supervisor_from_queue,
)


def test_job_queue_sync_creates_typed_jobs(tmp_path):
    queue_path = tmp_path / "job_queue.json"
    track_queue_state = {
        "status": "running",
        "track_dirs": ["domains/webnovel/tracks/a", "domains/webnovel/tracks/b"],
        "current_index": 1,
        "last_error": None,
    }

    state = sync_track_queue_to_job_queue(track_queue_state, path=str(queue_path), safe_mode=False)

    assert state["queue_status"] == "running"
    assert len(state["jobs"]) == 2
    assert state["jobs"][0]["status"] == "completed"
    assert state["jobs"][1]["status"] == "running"
    assert state["active_job_id"] == "track:1"


def test_job_queue_round_trip_repairs_invalid_status(tmp_path):
    queue_path = tmp_path / "job_queue.json"
    save_job_queue_state({"queue_status": "broken", "jobs": []}, path=str(queue_path), safe_mode=False)

    state = load_job_queue_state(str(queue_path))

    assert state["queue_status"] == "paused"
    assert state["last_error"] == "job_queue_repaired"


def test_supervisor_and_policy_snapshots_round_trip(tmp_path):
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"

    supervisor = update_supervisor_from_queue(
        {"queue_status": "running", "active_job_id": "track:3", "last_error": None},
        path=str(supervisor_path),
        safe_mode=False,
    )
    admission = record_admission_event(
        material_id="source:foo",
        decision="accepted",
        reason="scope_fit",
        path=str(admission_path),
        safe_mode=False,
    )
    promotion = record_promotion_event(
        artifact_id="artifact:bar",
        decision="promoted",
        reason="top_tier_quality",
        path=str(promotion_path),
        safe_mode=False,
    )

    assert supervisor["status"] == "running"
    assert load_supervisor_state(str(supervisor_path))["active_job_id"] == "track:3"
    assert admission["accepted_materials"][-1]["material_id"] == "source:foo"
    assert load_admission_state(str(admission_path))["last_scope_decision"]["decision"] == "accepted"
    assert promotion["promoted_artifacts"][-1]["artifact_id"] == "artifact:bar"
    assert load_promotion_state(str(promotion_path))["last_promotion_decision"]["decision"] == "promoted"
