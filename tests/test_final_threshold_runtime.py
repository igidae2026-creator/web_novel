import json
import os

from engine.final_threshold_runtime import build_fault_injection_report, run_final_threshold_repairs
from engine.job_queue import load_job_queue_state, save_job_queue_state
from engine.state import StateStore


def test_run_final_threshold_repairs_applies_directives_and_completes_jobs(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_r"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)
    state = StateStore(str(track_dir / "state.json"), safe_mode=False, project_dir_for_backup=str(out_dir))
    state.load()
    state.set("next_episode", 3)

    queue_path = tmp_path / "job_queue.json"
    save_job_queue_state(
        {
            "queue_status": "paused",
            "jobs": [
                {
                    "job_id": "repair:track_r:reader_retention_stability",
                    "job_type": "repair_final_threshold",
                    "status": "queued",
                    "priority": 20,
                    "attempts": 0,
                    "payload": {
                        "track_id": "track_r",
                        "criterion": "reader_retention_stability",
                        "repair_action": "repair_reader_retention_stability",
                    },
                    "result": None,
                    "error": None,
                }
            ],
        },
        path=str(queue_path),
        safe_mode=False,
    )

    result = run_final_threshold_repairs(
        state=state,
        out_dir=str(out_dir),
        track_id="track_r",
        queue_path=str(queue_path),
        safe_mode=False,
    )

    assert result["executed"] is True
    assert result["blocked_generation"] is False
    assert state.data["story_state_v2"]["control"]["final_threshold_repairs"]["rewrite_pressure"] == "high"
    queue_state = load_job_queue_state(str(queue_path))
    assert queue_state["jobs"][0]["status"] == "completed"


def test_run_final_threshold_repairs_blocks_generation_for_critical_failed_bundle(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_block"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)
    with open(out_dir / "final_threshold_eval.json", "w", encoding="utf-8") as handle:
        json.dump({"failed_bundles": ["truth_capability"]}, handle, ensure_ascii=False, indent=2)

    state = StateStore(str(track_dir / "state.json"), safe_mode=False, project_dir_for_backup=str(out_dir))
    state.load()
    queue_path = tmp_path / "job_queue.json"
    save_job_queue_state(
        {
            "queue_status": "paused",
            "jobs": [
                {
                    "job_id": "repair:track_block:append_only_truth_lineage_replayability",
                    "job_type": "repair_final_threshold",
                    "status": "queued",
                    "priority": 5,
                    "attempts": 0,
                    "payload": {
                        "track_id": "track_block",
                        "criterion": "append_only_truth_lineage_replayability",
                        "repair_action": "repair_append_only_lineage_replayability",
                    },
                    "result": None,
                    "error": None,
                }
            ],
        },
        path=str(queue_path),
        safe_mode=False,
    )

    result = run_final_threshold_repairs(
        state=state,
        out_dir=str(out_dir),
        track_id="track_block",
        queue_path=str(queue_path),
        safe_mode=False,
    )

    assert result["blocked_generation"] is True
    assert result["bundle_priority_mode"] == "critical_repair"
    assert state.data["story_state_v2"]["control"]["final_threshold_repairs"]["failed_bundles"] == ["truth_capability"]


def test_run_final_threshold_repairs_applies_business_feedback_rebind_context(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_market"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)
    state = StateStore(str(track_dir / "state.json"), safe_mode=False, project_dir_for_backup=str(out_dir))
    state.load()

    queue_path = tmp_path / "job_queue.json"
    save_job_queue_state(
        {
            "queue_status": "paused",
            "jobs": [
                {
                    "job_id": "repair:track_market:market_feedback_autoloop",
                    "job_type": "repair_final_threshold",
                    "status": "queued",
                    "priority": 15,
                    "attempts": 0,
                    "payload": {
                        "track_id": "track_market",
                        "criterion": "market_feedback_autoloop",
                        "repair_action": "repair_market_feedback_autoloop",
                        "repair_context": {"business_feedback_rebind_required": True},
                    },
                    "result": None,
                    "error": None,
                }
            ],
        },
        path=str(queue_path),
        safe_mode=False,
    )

    result = run_final_threshold_repairs(
        state=state,
        out_dir=str(out_dir),
        track_id="track_market",
        queue_path=str(queue_path),
        safe_mode=False,
    )

    assert result["executed"] is True
    control = state.data["story_state_v2"]["control"]["final_threshold_repairs"]
    assert control["market_rebind_required"] is True
    assert control["business_feedback_rebind_required"] is True


def test_run_final_threshold_repairs_marks_reader_quality_priority(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_reader"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)
    state = StateStore(str(track_dir / "state.json"), safe_mode=False, project_dir_for_backup=str(out_dir))
    state.load()

    queue_path = tmp_path / "job_queue.json"
    save_job_queue_state(
        {
            "queue_status": "paused",
            "jobs": [
                {
                    "job_id": "repair:track_reader:early_hook_strength",
                    "job_type": "repair_final_threshold",
                    "status": "queued",
                    "priority": 35,
                    "attempts": 0,
                    "payload": {
                        "track_id": "track_reader",
                        "criterion": "early_hook_strength",
                        "repair_action": "repair_early_hook_strength",
                        "repair_context": {"hook_bias": 0.14, "rewrite_pressure": "high"},
                    },
                    "result": None,
                    "error": None,
                }
            ],
        },
        path=str(queue_path),
        safe_mode=False,
    )

    result = run_final_threshold_repairs(
        state=state,
        out_dir=str(out_dir),
        track_id="track_reader",
        queue_path=str(queue_path),
        safe_mode=False,
    )

    assert result["executed"] is True
    control = state.data["story_state_v2"]["control"]["final_threshold_repairs"]
    assert control["reader_quality_priority"] == "critical"
    assert control["reader_quality_repair_required"] is True
    assert state.data["quality_lift_if_human_intervenes"] == 0.06


def test_build_fault_injection_report_marks_recovery_when_replay_is_consistent(tmp_path):
    out_dir = tmp_path / "outputs"
    out_dir.mkdir(parents=True)
    with open(out_dir / "events.jsonl", "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"ts": "2026-03-11 00:00:00", "type": "job_queue_synced", "payload": {"x": 1}}) + "\n")

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    save_job_queue_state({"queue_status": "idle", "jobs": [], "last_sync": {"current_index": 0}}, path=str(queue_path), safe_mode=False)
    with open(supervisor_path, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 1, "mode": "observe", "status": "idle", "last_sync": {"current_index": 0}}, handle)

    report = build_fault_injection_report(str(out_dir), queue_path=str(queue_path), supervisor_path=str(supervisor_path))

    assert report["tested"] is True
    assert report["recovered"] is True
