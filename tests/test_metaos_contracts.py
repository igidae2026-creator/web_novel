from engine.job_queue import load_job_queue_state
from engine.metaos_contracts import (
    CONTRACT_VERSION,
    compatibility_report,
    runtime_contract_manifest,
    validate_event_record,
    validate_job_queue_contract,
    validate_policy_decision,
    validate_supervisor_contract,
)
from engine.runtime_supervisor import load_supervisor_state


def test_runtime_contract_manifest_is_stable():
    manifest = runtime_contract_manifest()

    assert manifest["contract_version"] == CONTRACT_VERSION
    assert "generate_episode" in manifest["job_types"]
    assert "promote" in manifest["policy_verdicts"]
    assert "supervisor_state" in manifest["snapshot_types"]


def test_event_record_conforms_to_contract():
    ok, reason = validate_event_record(
        {"ts": "2026-03-11 12:00:00", "type": "scope_evaluate", "payload": {"material_id": "x"}}
    )
    assert ok is True
    assert reason == "ok"


def test_job_queue_snapshot_conforms_to_contract():
    state = load_job_queue_state()
    ok, reason = validate_job_queue_contract(state)

    assert ok is True
    assert reason == "ok"


def test_supervisor_snapshot_conforms_to_contract():
    state = load_supervisor_state()
    ok, reason = validate_supervisor_contract(state)

    assert ok is True
    assert reason == "ok"


def test_policy_verdict_conforms_to_contract():
    ok, reason = validate_policy_decision({"verdict": "escalate", "reason": "manual_exception"})

    assert ok is True
    assert reason == "ok"


def test_unknown_version_requires_migration():
    report = compatibility_report("1.0.0", "1.1.0")

    assert report["migration_required"] is True
    assert report["workers"] == "unknown"
