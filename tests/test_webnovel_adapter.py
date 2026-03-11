from engine.webnovel_adapter import (
    adapter_manifest,
    artifact_from_episode_result,
    material_from_source,
    track_job_payload,
    validate_adapter_decision_surface,
)


def test_adapter_manifest_declares_expected_capabilities():
    manifest = adapter_manifest()

    assert manifest["adapter_name"] == "web_novel"
    assert manifest["supports"]["episode_runtime"] is True
    assert "generate_episode_track" in manifest["job_mappings"]


def test_material_from_source_normalizes_webnovel_track_input():
    material = material_from_source(
        {
            "project": {"platform": "Munpia", "genre_bucket": "A"},
            "track": {"id": "munpia_a"},
            "material_id": "source:munpia_a",
            "quality_score": 0.88,
            "scope_fit_score": 0.82,
            "risk_score": 0.2,
            "novelty_score": 0.61,
        }
    )

    assert material["project_type"] == "web_novel"
    assert material["track_id"] == "munpia_a"
    assert material["platform"] == "Munpia"
    assert material["genre_bucket"] == "A"


def test_material_from_source_carries_hidden_reader_risk_into_metadata_and_risk():
    material = material_from_source(
        {
            "project": {"platform": "Munpia", "genre_bucket": "A"},
            "track": {"id": "munpia_hidden"},
            "material_id": "source:hidden",
            "quality_score": 0.88,
            "scope_fit_score": 0.82,
            "risk_score": 0.2,
            "novelty_score": 0.61,
            "hidden_reader_risk": 0.4,
            "hidden_reader_risk_trend": 0.36,
            "heavy_reader_signal_trend": 0.58,
        }
    )

    assert material["metadata"]["hidden_reader_risk"] == 0.4
    assert material["metadata"]["hidden_reader_risk_trend"] == 0.36
    assert material["metadata"]["heavy_reader_signal_trend"] == 0.58
    assert material["risk_score"] > 0.2


def test_artifact_from_episode_result_normalizes_episode_output(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = {
        "project": {"name": "adapter-check", "platform": "Munpia", "genre_bucket": "A"},
        "output": {"root_dir": str(tmp_path / "outputs")},
    }
    artifact = artifact_from_episode_result(
        cfg,
        {
            "episode": 12,
            "predicted_retention": 0.84,
            "quality_score": 0.79,
            "quality_gate": {"passed": True, "failed_checks": []},
            "story_state": {"world": {"instability": 4}, "control": {"final_threshold_history": {"hidden_reader_risk_trend": 0.41, "heavy_reader_signal_trend": 0.59}}},
        },
    )

    assert artifact["artifact_id"].endswith("ep012")
    assert artifact["artifact_type"] == "episode_output"
    assert artifact["stability_score"] == 1.0
    assert artifact["metadata"]["world_instability"] == 4
    assert artifact["metadata"]["hidden_reader_risk_trend"] == 0.41
    assert artifact["metadata"]["heavy_reader_signal_trend"] == 0.59


def test_track_job_payload_and_decision_surface_are_contract_safe():
    payload = track_job_payload("/tmp/tracks/munpia_a")

    assert payload["job_hint"] == "generate_episode_track"
    assert payload["track_id"] == "munpia_a"
    assert validate_adapter_decision_surface("promote") is True
    assert validate_adapter_decision_surface("custom") is False
