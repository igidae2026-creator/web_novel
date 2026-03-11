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


def test_job_queue_prioritizes_business_feedback_repairs_ahead_of_generation(tmp_path):
    queue_path = tmp_path / "job_queue.json"
    save_job_queue_state(
        {
            "queue_status": "paused",
            "jobs": [
                {
                    "job_id": "track:0",
                    "job_type": "generate_episode_track",
                    "status": "queued",
                    "priority": 0,
                    "payload": {"track_id": "track_a"},
                },
                {
                    "job_id": "repair:track_a:market_feedback_autoloop",
                    "job_type": "repair_final_threshold",
                    "status": "queued",
                    "priority": 15,
                    "payload": {
                        "track_id": "track_a",
                        "repair_context": {"business_feedback_rebind_required": True},
                    },
                },
            ],
        },
        path=str(queue_path),
        safe_mode=False,
    )

    state = load_job_queue_state(str(queue_path))

    assert state["jobs"][0]["job_id"] == "repair:track_a:market_feedback_autoloop"
    assert state["jobs"][1]["job_id"] == "track:0"


def test_job_queue_prioritizes_reader_quality_repairs_ahead_of_generation(tmp_path):
    queue_path = tmp_path / "job_queue.json"
    save_job_queue_state(
        {
            "queue_status": "paused",
            "jobs": [
                {
                    "job_id": "track:0",
                    "job_type": "generate_episode_track",
                    "status": "queued",
                    "priority": 0,
                    "payload": {"track_id": "track_a"},
                },
                {
                    "job_id": "repair:track_a:early_hook_strength",
                    "job_type": "repair_final_threshold",
                    "status": "queued",
                    "priority": 40,
                    "payload": {
                        "track_id": "track_a",
                        "repair_context": {"hook_bias": 0.14, "rewrite_pressure": "high"},
                    },
                },
            ],
        },
        path=str(queue_path),
        safe_mode=False,
    )

    state = load_job_queue_state(str(queue_path))

    assert state["jobs"][0]["job_id"] == "repair:track_a:early_hook_strength"
    assert state["jobs"][1]["job_id"] == "track:0"


def test_job_queue_prioritizes_hidden_reader_risk_trend_repairs_first(tmp_path):
    queue_path = tmp_path / "job_queue.json"
    save_job_queue_state(
        {
            "queue_status": "paused",
            "jobs": [
                {
                    "job_id": "repair:track_a:early_hook_strength",
                    "job_type": "repair_final_threshold",
                    "status": "queued",
                    "priority": 40,
                    "payload": {
                        "track_id": "track_a",
                        "repair_context": {"hook_bias": 0.14, "rewrite_pressure": "high"},
                    },
                },
                {
                    "job_id": "repair:track_a:reader_retention_stability",
                    "job_type": "repair_final_threshold",
                    "status": "queued",
                    "priority": 50,
                    "payload": {
                        "track_id": "track_a",
                        "repair_context": {"hidden_reader_risk_trend": 0.44},
                    },
                },
            ],
        },
        path=str(queue_path),
        safe_mode=False,
    )

    state = load_job_queue_state(str(queue_path))

    assert state["jobs"][0]["job_id"] == "repair:track_a:reader_retention_stability"
