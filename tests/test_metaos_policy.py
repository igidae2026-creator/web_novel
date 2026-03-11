from engine.job_queue import load_job_queue_state
from engine.metaos_policy import apply_promotion_policy, apply_scope_policy
from engine.runtime_supervisor import load_admission_state, load_promotion_state


def test_scope_policy_accepts_normal_case_without_human(tmp_path):
    admission_path = tmp_path / "admission.json"
    queue_path = tmp_path / "job_queue.json"

    result = apply_scope_policy(
        {
            "material_id": "mat:good",
            "quality_score": 0.9,
            "scope_fit_score": 0.88,
            "risk_score": 0.2,
            "novelty_score": 0.7,
            "source": "feed_a",
        },
        admission_path=str(admission_path),
        queue_path=str(queue_path),
        safe_mode=False,
    )

    assert result["decision"]["verdict"] == "accept"
    assert load_admission_state(str(admission_path))["accepted_materials"][-1]["decision"] == "accepted"
    assert any(job["job_id"] == "scope:mat:good" for job in load_job_queue_state(str(queue_path))["jobs"])


def test_scope_policy_holds_borderline_case_automatically(tmp_path):
    admission_path = tmp_path / "admission.json"
    queue_path = tmp_path / "job_queue.json"

    result = apply_scope_policy(
        {
            "material_id": "mat:border",
            "quality_score": 0.75,
            "scope_fit_score": 0.68,
            "risk_score": 0.4,
            "novelty_score": 0.52,
        },
        admission_path=str(admission_path),
        queue_path=str(queue_path),
        safe_mode=False,
    )

    assert result["decision"]["verdict"] == "hold"
    assert load_admission_state(str(admission_path))["pending_materials"][-1]["decision"] == "held"
    assert any(job["job_id"] == "ingest:mat:border" for job in load_job_queue_state(str(queue_path))["jobs"])


def test_scope_policy_escalates_true_exception(tmp_path):
    admission_path = tmp_path / "admission.json"
    queue_path = tmp_path / "job_queue.json"

    result = apply_scope_policy(
        {
            "material_id": "mat:exception",
            "quality_score": 0.81,
            "scope_fit_score": 0.85,
            "risk_score": 0.95,
        },
        admission_path=str(admission_path),
        queue_path=str(queue_path),
        safe_mode=False,
    )

    assert result["decision"]["verdict"] == "escalate"
    state = load_admission_state(str(admission_path))
    assert state["escalated_materials"][-1]["decision"] == "escalated"
    assert load_job_queue_state(str(queue_path))["jobs"] == []


def test_promotion_policy_promotes_normal_case_without_human(tmp_path):
    promotion_path = tmp_path / "promotion.json"
    queue_path = tmp_path / "job_queue.json"

    result = apply_promotion_policy(
        {
            "artifact_id": "art:good",
            "quality_score": 0.91,
            "relevance_score": 0.86,
            "stability_score": 0.82,
            "risk_score": 0.18,
        },
        promotion_path=str(promotion_path),
        queue_path=str(queue_path),
        safe_mode=False,
    )

    assert result["decision"]["verdict"] == "promote"
    assert load_promotion_state(str(promotion_path))["promoted_artifacts"][-1]["decision"] == "promoted"
    assert any(job["job_id"] == "promote:art:good" for job in load_job_queue_state(str(queue_path))["jobs"])
