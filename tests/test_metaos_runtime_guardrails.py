from engine.metaos_adapter_registry import adapter_resolution, get_adapter_manifest
from engine.metaos_conformance import run_project_conformance
from engine.metaos_recovery import detect_duplicate_events, partial_write_detected, replay_resume_decision, snapshot_staleness


def test_missing_adapter_defaults_to_hold():
    result = adapter_resolution("nonexistent_project")

    assert result["verdict"] == "hold"
    assert result["reason"] == "missing_project_adapter"


def test_version_mismatch_rejects_adapter(monkeypatch):
    import engine.metaos_adapter_registry as registry

    monkeypatch.setitem(
        registry._REGISTRY,
        "broken_project",
        lambda: {
            "adapter_name": "broken_project",
            "contract_version": "2.0.0",
            "supports": {},
            "job_mappings": {},
        },
    )

    result = adapter_resolution("broken_project")

    assert result["verdict"] == "reject"
    assert result["reason"] == "adapter_contract_version_mismatch"


def test_conformance_harness_runs_end_to_end_for_webnovel(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = run_project_conformance(
        project_type="web_novel",
        source={
            "project": {"platform": "Munpia", "genre_bucket": "A"},
            "track": {"id": "munpia_a"},
            "material_id": "src:munpia_a",
            "source": "feed_a",
            "quality_score": 0.91,
            "scope_fit_score": 0.84,
            "risk_score": 0.18,
            "novelty_score": 0.62,
        },
        episode_result={
            "episode": 7,
            "predicted_retention": 0.89,
            "quality_score": 0.83,
            "quality_gate": {"passed": True, "failed_checks": []},
            "story_state": {"world": {"instability": 3}},
        },
        cfg={
            "project": {"name": "adapter-check", "platform": "Munpia", "genre_bucket": "A"},
            "output": {"root_dir": str(tmp_path / "outputs")},
        },
        admission_path=str(tmp_path / "admission_state.json"),
        promotion_path=str(tmp_path / "promotion_state.json"),
        supervisor_path=str(tmp_path / "supervisor_state.json"),
        queue_path=str(tmp_path / "job_queue.json"),
        safe_mode=False,
    )

    assert result["ok"] is True
    assert result["scope_decision"]["verdict"] == "accept"
    assert result["promotion_decision"]["verdict"] == "promote"


def test_recovery_detects_duplicate_event_partial_write_stale_snapshot():
    events = [
        {"ts": "2026-03-11 10:00:00", "type": "scope_evaluate", "payload": {"material_id": "x"}},
        {"ts": "2026-03-11 10:00:00", "type": "scope_evaluate", "payload": {"material_id": "x"}},
    ]

    duplicates = detect_duplicate_events(events)
    partial = partial_write_detected({"schema_version": 1}, ["schema_version", "queue_status", "jobs"])
    stale = snapshot_staleness({"last_sync": {"current_index": 1}}, {"last_sync": {"current_index": 3}})

    assert len(duplicates) == 1
    assert partial["partial"] is True
    assert stale["stale"] is True


def test_recovery_returns_resume_only_when_replay_is_consistent():
    decision = replay_resume_decision(
        events=[{"ts": "2026-03-11 10:00:00", "type": "scope_evaluate", "payload": {"material_id": "x"}}],
        snapshot={"schema_version": 1, "queue_status": "running", "jobs": [], "last_sync": {"current_index": 2}},
        queue_state={"last_sync": {"current_index": 2}},
        required_snapshot_fields=["schema_version", "queue_status", "jobs"],
    )

    assert decision["verdict"] == "resume"


def test_snapshot_staleness_handles_null_last_sync():
    stale = snapshot_staleness({"schema_version": 1, "last_sync": None}, {"last_sync": None, "current_index": 0})

    assert stale["stale"] is False
    assert stale["snapshot_index"] == 0


def test_detect_duplicate_events_handles_nested_payload_lists():
    events = [
        {"ts": "2026-03-11 10:00:00", "type": "final_threshold_evaluated", "payload": {"failed_criteria": ["a", "b"]}},
        {"ts": "2026-03-11 10:00:00", "type": "final_threshold_evaluated", "payload": {"failed_criteria": ["a", "b"]}},
    ]

    duplicates = detect_duplicate_events(events)

    assert len(duplicates) == 1
