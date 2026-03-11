from engine.job_queue import load_job_queue_state, save_job_queue_state
from engine.metaos_contracts import (
    validate_job_queue_contract,
    validate_policy_decision,
    validate_supervisor_contract,
)
from engine.metaos_policy import apply_promotion_policy, apply_scope_policy
from engine.runtime_supervisor import load_admission_state, load_promotion_state, update_supervisor_from_queue
from engine.webnovel_adapter import artifact_from_episode_result, material_from_source


def test_metaos_runtime_conformance_path_for_webnovel(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    queue_path = tmp_path / "job_queue.json"

    material = material_from_source(
        {
            "project": {"platform": "Munpia", "genre_bucket": "A"},
            "track": {"id": "munpia_a"},
            "material_id": "src:munpia_a",
            "source": "feed_a",
            "quality_score": 0.9,
            "scope_fit_score": 0.86,
            "risk_score": 0.2,
            "novelty_score": 0.66,
        }
    )

    scope_result = apply_scope_policy(
        material,
        admission_path=str(admission_path),
        queue_path=str(queue_path),
        safe_mode=False,
    )
    scope_ok, _ = validate_policy_decision(scope_result["decision"])
    assert scope_ok is True
    assert load_admission_state(str(admission_path))["accepted_materials"][-1]["material_id"] == "src:munpia_a"

    queue_state = load_job_queue_state(str(queue_path))
    queue_state["queue_status"] = "running"
    queue_state["active_job_id"] = "scope:src:munpia_a"
    save_job_queue_state(queue_state, path=str(queue_path), safe_mode=False)
    supervisor = update_supervisor_from_queue(queue_state, path=str(supervisor_path), safe_mode=False)

    queue_ok, _ = validate_job_queue_contract(load_job_queue_state(str(queue_path)))
    supervisor_ok, _ = validate_supervisor_contract(supervisor)
    assert queue_ok is True
    assert supervisor_ok is True

    artifact = artifact_from_episode_result(
        {
            "project": {"name": "adapter-check", "platform": "Munpia", "genre_bucket": "A"},
            "output": {"root_dir": str(tmp_path / "outputs")},
        },
        {
            "episode": 12,
            "predicted_retention": 0.91,
            "quality_score": 0.87,
            "quality_gate": {"passed": True, "failed_checks": []},
            "story_state": {"world": {"instability": 4}},
        },
    )
    promotion_result = apply_promotion_policy(
        artifact,
        promotion_path=str(promotion_path),
        queue_path=str(queue_path),
        safe_mode=False,
    )
    promote_ok, _ = validate_policy_decision(promotion_result["decision"])
    assert promote_ok is True
    assert load_promotion_state(str(promotion_path))["promoted_artifacts"][-1]["artifact_id"] == artifact["artifact_id"]

    final_queue = load_job_queue_state(str(queue_path))
    assert any(job["job_id"] == "promote:" + artifact["artifact_id"] for job in final_queue["jobs"])


def test_metaos_runtime_conformance_holds_when_adapter_carries_hidden_reader_risk_trend(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"
    queue_path = tmp_path / "job_queue.json"

    material = material_from_source(
        {
            "project": {"platform": "Munpia", "genre_bucket": "A"},
            "track": {"id": "munpia_a"},
            "material_id": "src:trend",
            "source": "feed_a",
            "quality_score": 0.9,
            "scope_fit_score": 0.86,
            "risk_score": 0.2,
            "novelty_score": 0.66,
            "hidden_reader_risk_trend": 0.39,
        }
    )

    scope_result = apply_scope_policy(
        material,
        admission_path=str(admission_path),
        queue_path=str(queue_path),
        safe_mode=False,
    )
    assert scope_result["decision"]["verdict"] == "hold"

    artifact = artifact_from_episode_result(
        {
            "project": {"name": "adapter-check", "platform": "Munpia", "genre_bucket": "A"},
            "output": {"root_dir": str(tmp_path / "outputs")},
        },
        {
            "episode": 12,
            "predicted_retention": 0.91,
            "quality_score": 0.87,
            "quality_gate": {"passed": True, "failed_checks": []},
            "story_state": {"world": {"instability": 4}, "control": {"final_threshold_history": {"hidden_reader_risk_trend": 0.41}}},
        },
    )
    promotion_result = apply_promotion_policy(
        artifact,
        promotion_path=str(promotion_path),
        queue_path=str(queue_path),
        safe_mode=False,
    )
    assert promotion_result["decision"]["verdict"] == "hold"
