import json
import os

import pytest

from engine.final_threshold import FINAL_THRESHOLD_FILENAME, evaluate_final_threshold_bundle
from engine.job_queue import load_job_queue_state, save_job_queue_state
from engine.runtime_supervisor import (
    load_admission_state,
    load_promotion_state,
    load_supervisor_state,
    save_admission_state,
    save_promotion_state,
    save_supervisor_state,
)


def _write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def _append_jsonl(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def test_final_threshold_bundle_passes_when_all_bundle_axes_close(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_a"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)

    _write_json(
        track_dir / "state.json",
        {
            "story_state_v2": {
                "control": {"regression_flags": []},
                "promise_graph": {"payoff_integrity": 0.84, "payoff_corruption_flags": []},
                "cast": {"protagonist": {"progress": 2, "backlash": 1, "urgency": 8}},
            },
            "last_quality_gate": {
                "passed": True,
                "checks": {
                    "hook_score": True,
                    "cliffhanger_valid": True,
                    "world_instability": True,
                },
                "predicted_retention": 0.84,
                "content_ceiling_total": 71,
                "causal_score": 0.88,
            },
            "predicted_retention": 0.84,
            "quality_lift_if_human_intervenes": 0.0,
        },
    )
    _write_json(
        out_dir / "certification_report.json",
        {
            "market": {
                "available": True,
                "ok": True,
                "stats": {"latest_top_percent": 2.8},
            }
        },
    )
    _append_jsonl(out_dir / "events.jsonl", {"ts": "2026-03-11 00:00:00", "type": "queue_step", "payload": {}})
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "episode": 1,
            "episode_attribution": {
                "lineage_parent": "outline:v1",
                "retention_signal": 0.84,
                "pacing_signal": 0.76,
                "fatigue_signal": 0.11,
                "payoff_signal": 0.82,
            },
            "scores": {"hook_score": 0.9, "payoff_score": 0.79, "pacing_score": 0.76, "character_score": 0.8, "repetition_score": 0.11},
            "retention": {"predicted_next_episode": 0.84},
            "content_ceiling": {"ceiling_total": 71},
            "meta": {
                "scene_causality": {"score": 0.88},
                "episode_attribution": {"lineage_parent": "outline:v1", "retention_signal": 0.84, "pacing_signal": 0.76, "fatigue_signal": 0.11, "payoff_signal": 0.82},
            },
            "simulation": {"tested": True, "steady_noop_ratio": 0.82, "dominant_mode": "steady"},
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"

    save_job_queue_state({"queue_status": "running", "active_job_id": "track:0", "jobs": []}, path=str(queue_path), safe_mode=False)
    save_supervisor_state({"status": "running", "active_job_id": "track:0"}, path=str(supervisor_path), safe_mode=False)
    save_admission_state(
        {"last_scope_decision": {"material_id": "mat:1", "decision": "accepted", "reason": "scope_fit"}},
        path=str(admission_path),
        safe_mode=False,
    )
    save_promotion_state(
        {"last_promotion_decision": {"artifact_id": "art:1", "decision": "promoted", "reason": "quality"}},
        path=str(promotion_path),
        safe_mode=False,
    )

    cfg = {"quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65}, "safe_mode": False}
    report = evaluate_final_threshold_bundle(
        cfg,
        str(out_dir),
        cycle_context={
            "track_id": "track_a",
            "action": "generate",
            "episode": 1,
            "next_step_recorded": True,
            "scope_authority_policy_ok": True,
            "market_feedback_handled": True,
            "fault_injection": {"tested": True, "recovered": True},
            "soak_report": {"tested": True, "steady_noop_ratio": 0.82, "dominant_mode": "steady"},
            "quality_lift_if_human_intervenes": 0.0,
            "policy_decision": "continue",
        },
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    assert report["final_threshold_ready"] is True
    assert report["failed_criteria"] == []
    assert report["failed_bundles"] == []
    assert report["capability_bundles"]["generation_capability"]["passed"] is True
    assert report["criteria"]["early_hook_strength"]["passed"] is True
    assert report["criteria"]["episode_end_hook_strength"]["passed"] is True
    assert report["criteria"]["long_arc_payoff_stability"]["passed"] is True
    assert report["criteria"]["protagonist_fantasy_persistence"]["passed"] is True
    assert report["criteria"]["serialization_fatigue_control"]["passed"] is True
    assert os.path.exists(out_dir / FINAL_THRESHOLD_FILENAME)
    assert load_supervisor_state(str(supervisor_path))["final_threshold_ready"] is True
    assert load_job_queue_state(str(queue_path))["jobs"] == []
    track_state = json.load(open(track_dir / "state.json", "r", encoding="utf-8"))
    assert track_state["story_state_v2"]["control"]["final_threshold_history"]["observed"] == 1
    assert track_state["story_state_v2"]["control"]["final_threshold_history"]["history"][-1]["ready"] is True


def test_final_threshold_bundle_enqueues_only_failed_repairs(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_b"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)

    _write_json(
        track_dir / "state.json",
        {
            "story_state_v2": {
                "promise_graph": {"payoff_integrity": 0.31, "payoff_corruption_flags": [{"type": "overdue_payoff"}]},
                "cast": {"protagonist": {"progress": 0, "backlash": 3, "urgency": 8}},
            },
            "last_quality_gate": {
                "passed": False,
                "failed_checks": ["hook_score"],
                "checks": {"hook_score": False, "cliffhanger_valid": False, "world_instability": True},
                "predicted_retention": 0.55,
                "content_ceiling_total": 42,
                "causal_score": 0.4,
            },
        },
    )
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "type": "episode_rejected",
            "episode": 2,
            "failed_checks": ["hook_score"],
            "predicted_retention": 0.55,
            "content_ceiling_total": 42,
            "causal_score": 0.4,
            "scores": {"hook_score": 0.52, "payoff_score": 0.33, "pacing_score": 0.41, "character_score": 0.29, "repetition_score": 0.42},
            "episode_attribution": {"retention_signal": 0.55, "pacing_signal": 0.41, "fatigue_signal": 0.39, "payoff_signal": 0.3},
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"

    save_job_queue_state({"queue_status": "paused", "active_job_id": None, "jobs": []}, path=str(queue_path), safe_mode=False)
    save_supervisor_state({"status": "paused", "active_job_id": None}, path=str(supervisor_path), safe_mode=False)
    save_admission_state({}, path=str(admission_path), safe_mode=False)
    save_promotion_state({}, path=str(promotion_path), safe_mode=False)

    cfg = {"quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65}, "safe_mode": False}
    report = evaluate_final_threshold_bundle(
        cfg,
        str(out_dir),
        cycle_context={
            "track_id": "track_b",
            "action": "reject",
            "episode": 2,
            "failed": True,
            "failure_recorded": True,
            "next_step_recorded": True,
            "gate_passed": False,
            "policy_decision": "reject",
            "rewrite_attempted": True,
        },
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    assert report["final_threshold_ready"] is False
    assert "early_hook_strength" in report["failed_criteria"]
    assert "episode_end_hook_strength" in report["failed_criteria"]
    assert "long_arc_payoff_stability" in report["failed_criteria"]
    assert "protagonist_fantasy_persistence" in report["failed_criteria"]
    assert "serialization_fatigue_control" in report["failed_criteria"]
    assert "append_only_truth_lineage_replayability" in report["failed_criteria"]
    assert "human_quality_lift_near_zero" in report["failed_criteria"]
    assert "truth_capability" in report["failed_bundles"]
    assert report["capability_bundles"]["truth_capability"]["passed"] is False

    queue_state = load_job_queue_state(str(queue_path))
    repair_ids = {job["job_id"] for job in queue_state["jobs"]}
    assert "repair:track_b:append_only_truth_lineage_replayability" in repair_ids
    assert "repair:track_b:human_quality_lift_near_zero" in repair_ids
    assert load_supervisor_state(str(supervisor_path))["status"] == "blocked"
    assert load_admission_state(str(admission_path))["last_scope_decision"] is None
    assert load_promotion_state(str(promotion_path))["last_promotion_decision"] is None


def test_final_threshold_syncs_supervisor_with_report(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_c"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)

    _write_json(
        track_dir / "state.json",
        {
            "story_state_v2": {
                "control": {},
                "promise_graph": {"payoff_integrity": 0.82, "payoff_corruption_flags": []},
                "cast": {"protagonist": {"progress": 2, "backlash": 1, "urgency": 8}},
            },
            "last_quality_gate": {
                "passed": True,
                "checks": {"hook_score": True, "cliffhanger_valid": True, "world_instability": True},
                "predicted_retention": 0.83,
                "content_ceiling_total": 70,
                "causal_score": 0.87,
            },
            "quality_lift_if_human_intervenes": 0.0,
        },
    )
    _append_jsonl(out_dir / "events.jsonl", {"ts": "2026-03-11 00:00:00", "type": "job_queue_synced", "payload": {"current_index": 0}})
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "episode": 1,
            "episode_attribution": {"lineage_parent": "outline:v1", "retention_signal": 0.83, "pacing_signal": 0.75, "fatigue_signal": 0.1, "payoff_signal": 0.81},
            "scores": {"hook_score": 0.9, "payoff_score": 0.78, "pacing_score": 0.75, "character_score": 0.79, "repetition_score": 0.1},
            "retention": {"predicted_next_episode": 0.83},
            "content_ceiling": {"ceiling_total": 70},
            "meta": {
                "scene_causality": {"score": 0.87},
                "episode_attribution": {"lineage_parent": "outline:v1", "retention_signal": 0.83, "pacing_signal": 0.75, "fatigue_signal": 0.1, "payoff_signal": 0.81},
                "soak_report": {"tested": True, "steady_noop_ratio": 0.8, "dominant_mode": "steady"},
            },
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"

    save_job_queue_state({"queue_status": "running", "active_job_id": None, "jobs": []}, path=str(queue_path), safe_mode=False)
    save_supervisor_state({"status": "paused", "active_job_id": None}, path=str(supervisor_path), safe_mode=False)
    save_admission_state({"last_scope_decision": {"material_id": "mat:1", "decision": "accepted", "reason": "scope_fit"}}, path=str(admission_path), safe_mode=False)
    save_promotion_state({"last_promotion_decision": {"artifact_id": "art:1", "decision": "promoted", "reason": "quality"}}, path=str(promotion_path), safe_mode=False)

    report = evaluate_final_threshold_bundle(
        {"quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65}, "safe_mode": False},
        str(out_dir),
        cycle_context={
            "track_id": "track_c",
            "action": "generate",
            "next_step_recorded": True,
            "fault_injection": {"tested": True, "recovered": True},
            "market_feedback_handled": True,
            "scope_authority_policy_ok": True,
            "quality_lift_if_human_intervenes": 0.0,
            "policy_decision": "continue",
        },
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    supervisor = load_supervisor_state(str(supervisor_path))
    assert supervisor["status"] == ("running" if report["final_threshold_ready"] else "blocked")
    assert supervisor["final_threshold_path"].endswith("final_threshold_eval.json")
    assert supervisor["failed_criteria"] == report["failed_criteria"]
    assert supervisor["failed_bundles"] == report["failed_bundles"]
    assert supervisor["bundle_priority_mode"] in {None, "criterion_repair", "caution_repair", "critical_repair"}
    assert supervisor["reader_risk_trend_priority"] in {None, "high", "critical"}


def test_final_threshold_can_use_soak_history_fallback(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_soak"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)

    _write_json(
        track_dir / "state.json",
        {
            "story_state_v2": {
                "control": {
                    "soak_history": {
                        "observed": 3,
                        "steady_noop_ratio": 0.78,
                        "dominant_mode": "steady",
                        "quality_lift_trend": 0.04,
                        "hidden_reader_risk_trend": 0.18,
                        "heavy_reader_signal_trend": 0.79,
                        "history": [
                            {"episode": 1, "steady_noop_ratio": 0.74, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.05, "hidden_reader_risk": 0.22, "heavy_reader_signal": 0.75},
                            {"episode": 2, "steady_noop_ratio": 0.77, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.04, "hidden_reader_risk": 0.2, "heavy_reader_signal": 0.78},
                            {"episode": 3, "steady_noop_ratio": 0.78, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.04, "hidden_reader_risk": 0.18, "heavy_reader_signal": 0.79},
                        ],
                    }
                },
                "promise_graph": {"payoff_integrity": 0.84, "payoff_corruption_flags": []},
                "cast": {"protagonist": {"progress": 2, "backlash": 1, "urgency": 8}},
            },
            "last_quality_gate": {
                "passed": True,
                "checks": {"hook_score": True, "cliffhanger_valid": True, "world_instability": True},
                "predicted_retention": 0.84,
                "content_ceiling_total": 70,
                "causal_score": 0.88,
            },
        },
    )
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "episode": 2,
            "episode_attribution": {"lineage_parent": "outline:v9", "retention_signal": 0.84, "pacing_signal": 0.75, "fatigue_signal": 0.1, "payoff_signal": 0.8},
            "scores": {"hook_score": 0.88, "payoff_score": 0.8, "pacing_score": 0.75, "character_score": 0.79, "repetition_score": 0.1},
            "retention": {"predicted_next_episode": 0.84},
            "content_ceiling": {"ceiling_total": 70},
            "meta": {"scene_causality": {"score": 0.88}},
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"
    save_job_queue_state({"queue_status": "running", "active_job_id": None, "jobs": []}, path=str(queue_path), safe_mode=False)
    save_supervisor_state({"status": "running", "active_job_id": None}, path=str(supervisor_path), safe_mode=False)
    save_admission_state({"last_scope_decision": {"material_id": "mat:soak", "decision": "accepted"}}, path=str(admission_path), safe_mode=False)
    save_promotion_state({"last_promotion_decision": {"artifact_id": "art:soak", "decision": "promoted"}}, path=str(promotion_path), safe_mode=False)

    report = evaluate_final_threshold_bundle(
        {"quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65}, "safe_mode": False},
        str(out_dir),
        cycle_context={"track_id": "track_soak", "action": "generate", "next_step_recorded": True, "scope_authority_policy_ok": True, "market_feedback_handled": True},
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    assert report["criteria"]["soak_steady_noop_dominance"]["passed"] is True
    assert report["criteria"]["autonomous_convergence_trend"]["passed"] is True
    assert report["quality_lift_if_human_intervenes"] <= 0.04


def test_final_threshold_blocks_convergence_when_hidden_reader_risk_trend_stays_high(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_hidden_risk"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)

    _write_json(
        track_dir / "state.json",
        {
            "story_state_v2": {
                "control": {
                    "soak_history": {
                        "observed": 4,
                        "steady_noop_ratio": 0.82,
                        "dominant_mode": "steady",
                        "quality_lift_trend": 0.03,
                        "hidden_reader_risk_trend": 0.46,
                        "heavy_reader_signal_trend": 0.78,
                        "history": [
                            {"episode": 1, "steady_noop_ratio": 0.76, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.05, "hidden_reader_risk": 0.42, "heavy_reader_signal": 0.74},
                            {"episode": 2, "steady_noop_ratio": 0.8, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.04, "hidden_reader_risk": 0.44, "heavy_reader_signal": 0.76},
                            {"episode": 3, "steady_noop_ratio": 0.81, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.03, "hidden_reader_risk": 0.45, "heavy_reader_signal": 0.77},
                            {"episode": 4, "steady_noop_ratio": 0.82, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.03, "hidden_reader_risk": 0.46, "heavy_reader_signal": 0.78},
                        ],
                    }
                },
                "promise_graph": {"payoff_integrity": 0.84, "payoff_corruption_flags": []},
                "cast": {"protagonist": {"progress": 2, "backlash": 1, "urgency": 8}},
            },
            "last_quality_gate": {
                "passed": True,
                "checks": {"hook_score": True, "cliffhanger_valid": True, "world_instability": True},
                "predicted_retention": 0.84,
                "content_ceiling_total": 70,
                "causal_score": 0.88,
            },
        },
    )
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "episode": 4,
            "episode_attribution": {"lineage_parent": "outline:v12", "retention_signal": 0.84, "pacing_signal": 0.75, "fatigue_signal": 0.1, "payoff_signal": 0.8},
            "scores": {"hook_score": 0.88, "payoff_score": 0.8, "pacing_score": 0.75, "character_score": 0.79, "repetition_score": 0.1},
            "retention": {"predicted_next_episode": 0.84},
            "content_ceiling": {"ceiling_total": 70},
            "meta": {"scene_causality": {"score": 0.88}},
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"
    save_job_queue_state({"queue_status": "running", "active_job_id": None, "jobs": []}, path=str(queue_path), safe_mode=False)
    save_supervisor_state({"status": "running", "active_job_id": None}, path=str(supervisor_path), safe_mode=False)
    save_admission_state({"last_scope_decision": {"material_id": "mat:hidden", "decision": "accepted"}}, path=str(admission_path), safe_mode=False)
    save_promotion_state({"last_promotion_decision": {"artifact_id": "art:hidden", "decision": "promoted"}}, path=str(promotion_path), safe_mode=False)

    report = evaluate_final_threshold_bundle(
        {"quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65}, "safe_mode": False},
        str(out_dir),
        cycle_context={"track_id": "track_hidden_risk", "action": "generate", "next_step_recorded": True, "scope_authority_policy_ok": True, "market_feedback_handled": True},
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    assert report["criteria"]["soak_steady_noop_dominance"]["passed"] is True
    assert report["criteria"]["autonomous_convergence_trend"]["passed"] is False
    assert report["criteria"]["autonomous_convergence_trend"]["details"]["hidden_reader_risk_trend"] == 0.46
    assert load_supervisor_state(str(supervisor_path))["reader_risk_trend_priority"] == "high"
    repair = next(item for item in report["next_required_repairs"] if item["criterion"] == "autonomous_convergence_trend")
    assert repair["repair_context"]["hidden_reader_risk_trend"] == 0.46
    assert repair["repair_context"]["reader_risk_trend_repair_required"] is True
    metrics_rows = [json.loads(line) for line in (out_dir / "metrics.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    ft_row = next(row for row in metrics_rows if row.get("type") == "final_threshold_eval")
    assert ft_row["hidden_reader_risk_trend"] == 0.46
    assert ft_row["reader_risk_trend_priority"] == "high"
    event_rows = [json.loads(line) for line in (out_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    ft_event = next(row for row in event_rows if row.get("type") == "final_threshold_evaluated")
    assert ft_event["payload"]["hidden_reader_risk_trend"] == 0.46
    assert ft_event["payload"]["reader_risk_trend_priority"] == "high"


def test_final_threshold_blocks_convergence_when_heavy_reader_signal_trend_stays_low(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_reader_signal"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)

    _write_json(
        track_dir / "state.json",
        {
            "story_state_v2": {
                "control": {
                    "soak_history": {
                        "observed": 4,
                        "steady_noop_ratio": 0.81,
                        "dominant_mode": "steady",
                        "quality_lift_trend": 0.03,
                        "hidden_reader_risk_trend": 0.14,
                        "heavy_reader_signal_trend": 0.61,
                        "history": [
                            {"episode": 1, "steady_noop_ratio": 0.76, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.05, "hidden_reader_risk": 0.2, "heavy_reader_signal": 0.64},
                            {"episode": 2, "steady_noop_ratio": 0.8, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.04, "hidden_reader_risk": 0.18, "heavy_reader_signal": 0.63},
                            {"episode": 3, "steady_noop_ratio": 0.81, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.03, "hidden_reader_risk": 0.15, "heavy_reader_signal": 0.61},
                            {"episode": 4, "steady_noop_ratio": 0.82, "dominant_mode": "steady", "quality_lift_if_human_intervenes": 0.03, "hidden_reader_risk": 0.14, "heavy_reader_signal": 0.6},
                        ],
                    }
                },
                "promise_graph": {"payoff_integrity": 0.84, "payoff_corruption_flags": []},
                "cast": {"protagonist": {"progress": 2, "backlash": 1, "urgency": 8}},
            },
            "last_quality_gate": {
                "passed": True,
                "checks": {"hook_score": True, "cliffhanger_valid": True, "world_instability": True},
                "predicted_retention": 0.84,
                "content_ceiling_total": 70,
                "causal_score": 0.88,
            },
        },
    )
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "episode": 4,
            "episode_attribution": {"lineage_parent": "outline:v12", "retention_signal": 0.84, "pacing_signal": 0.75, "fatigue_signal": 0.1, "payoff_signal": 0.8},
            "scores": {"hook_score": 0.88, "payoff_score": 0.8, "pacing_score": 0.75, "character_score": 0.79, "repetition_score": 0.1},
            "retention": {"predicted_next_episode": 0.84},
            "content_ceiling": {"ceiling_total": 70},
            "meta": {"scene_causality": {"score": 0.88}},
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"
    save_job_queue_state({"queue_status": "running", "active_job_id": None, "jobs": []}, path=str(queue_path), safe_mode=False)
    save_supervisor_state({"status": "running", "active_job_id": None}, path=str(supervisor_path), safe_mode=False)
    save_admission_state({"last_scope_decision": {"material_id": "mat:reader", "decision": "accepted"}}, path=str(admission_path), safe_mode=False)
    save_promotion_state({"last_promotion_decision": {"artifact_id": "art:reader", "decision": "promoted"}}, path=str(promotion_path), safe_mode=False)

    report = evaluate_final_threshold_bundle(
        {"quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65}, "safe_mode": False},
        str(out_dir),
        cycle_context={"track_id": "track_reader_signal", "action": "generate", "next_step_recorded": True, "scope_authority_policy_ok": True, "market_feedback_handled": True},
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    assert report["criteria"]["soak_steady_noop_dominance"]["passed"] is True
    assert report["criteria"]["autonomous_convergence_trend"]["passed"] is False
    assert report["criteria"]["autonomous_convergence_trend"]["details"]["heavy_reader_signal_trend"] == 0.61
    repair = next(item for item in report["next_required_repairs"] if item["criterion"] == "autonomous_convergence_trend")
    assert repair["repair_context"]["heavy_reader_signal_trend"] == 0.61
    assert repair["repair_context"]["heavy_reader_signal_repair_required"] is True
    assert repair["repair_context"]["heavy_reader_signal_block_required"] is True


def test_final_threshold_history_accumulates_ready_ratio(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_hist"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)

    _write_json(
        track_dir / "state.json",
        {
            "story_state_v2": {
                "control": {
                    "final_threshold_history": {
                        "observed": 3,
                        "ready_ratio": 0.6667,
                        "recent_fail_ratio": 0.3333,
                        "hidden_reader_risk_trend": 0.14,
                        "history": [
                            {"ready": True, "failed_criteria_count": 0, "failed_bundle_count": 0, "quality_lift_if_human_intervenes": 0.04, "hidden_reader_risk_trend": 0.11},
                            {"ready": False, "failed_criteria_count": 2, "failed_bundle_count": 1, "quality_lift_if_human_intervenes": 0.08, "hidden_reader_risk_trend": 0.19},
                            {"ready": True, "failed_criteria_count": 0, "failed_bundle_count": 0, "quality_lift_if_human_intervenes": 0.03, "hidden_reader_risk_trend": 0.12},
                        ],
                    },
                    "soak_history": {
                        "observed": 3,
                        "steady_noop_ratio": 0.79,
                        "dominant_mode": "steady",
                        "quality_lift_trend": 0.04,
                        "hidden_reader_risk_trend": 0.16,
                        "history": [],
                    },
                },
                "promise_graph": {"payoff_integrity": 0.84, "payoff_corruption_flags": []},
                "cast": {"protagonist": {"progress": 2, "backlash": 1, "urgency": 8}},
            },
            "last_quality_gate": {
                "passed": True,
                "checks": {"hook_score": True, "cliffhanger_valid": True, "world_instability": True},
                "predicted_retention": 0.84,
                "content_ceiling_total": 70,
                "causal_score": 0.88,
            },
        },
    )
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "episode": 4,
            "episode_attribution": {"lineage_parent": "outline:v11", "retention_signal": 0.84, "pacing_signal": 0.75, "fatigue_signal": 0.1, "payoff_signal": 0.8},
            "scores": {"hook_score": 0.88, "payoff_score": 0.8, "pacing_score": 0.75, "character_score": 0.79, "repetition_score": 0.1},
            "retention": {"predicted_next_episode": 0.84},
            "content_ceiling": {"ceiling_total": 70},
            "meta": {"scene_causality": {"score": 0.88}},
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"
    save_job_queue_state({"queue_status": "running", "active_job_id": None, "jobs": []}, path=str(queue_path), safe_mode=False)
    save_supervisor_state({"status": "running", "active_job_id": None}, path=str(supervisor_path), safe_mode=False)
    save_admission_state({"last_scope_decision": {"material_id": "mat:hist", "decision": "accepted"}}, path=str(admission_path), safe_mode=False)
    save_promotion_state({"last_promotion_decision": {"artifact_id": "art:hist", "decision": "promoted"}}, path=str(promotion_path), safe_mode=False)

    report = evaluate_final_threshold_bundle(
        {"quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65}, "safe_mode": False},
        str(out_dir),
        cycle_context={"track_id": "track_hist", "action": "generate", "next_step_recorded": True, "scope_authority_policy_ok": True, "market_feedback_handled": True},
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    assert report["threshold_history"]["observed"] == 4
    assert report["threshold_history"]["ready_ratio"] == pytest.approx(0.5)
    assert report["threshold_history"]["recent_fail_ratio"] >= 0.25
    assert report["threshold_history"]["hidden_reader_risk_trend"] > 0.0


def test_final_threshold_infers_protagonist_momentum_without_rich_cast_state(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_d"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)

    _write_json(
        track_dir / "state.json",
        {
            "story_state_v2": {
                "control": {},
                "promise_graph": {"payoff_integrity": 0.8, "payoff_corruption_flags": []},
            },
            "last_quality_gate": {
                "passed": True,
                "checks": {"hook_score": True, "cliffhanger_valid": True, "world_instability": True},
                "predicted_retention": 0.85,
                "content_ceiling_total": 72,
                "causal_score": 0.89,
            },
            "quality_lift_if_human_intervenes": 0.0,
        },
    )
    _write_json(
        out_dir / "certification_report.json",
        {
            "market": {
                "available": True,
                "ok": True,
                "stats": {"latest_top_percent": 3.2},
            }
        },
    )
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "episode": 1,
            "episode_attribution": {"lineage_parent": "outline:v3", "retention_signal": 0.85, "pacing_signal": 0.76, "fatigue_signal": 0.1, "payoff_signal": 0.8},
            "scores": {"hook_score": 0.88, "payoff_score": 0.79, "pacing_score": 0.76, "character_score": 0.84, "repetition_score": 0.1},
            "retention": {"predicted_next_episode": 0.85},
            "content_ceiling": {"ceiling_total": 72},
            "meta": {"scene_causality": {"score": 0.89}, "episode_attribution": {"lineage_parent": "outline:v3", "retention_signal": 0.85, "pacing_signal": 0.76, "fatigue_signal": 0.1, "payoff_signal": 0.8}},
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"

    save_job_queue_state({"queue_status": "running", "active_job_id": None, "jobs": []}, path=str(queue_path), safe_mode=False)
    save_supervisor_state({"status": "running", "active_job_id": None}, path=str(supervisor_path), safe_mode=False)
    save_admission_state({"last_scope_decision": {"material_id": "mat:2", "decision": "accepted", "reason": "scope_fit"}}, path=str(admission_path), safe_mode=False)
    save_promotion_state({"last_promotion_decision": {"artifact_id": "art:2", "decision": "promoted", "reason": "quality"}}, path=str(promotion_path), safe_mode=False)

    report = evaluate_final_threshold_bundle(
        {"quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65}, "safe_mode": False},
        str(out_dir),
        cycle_context={
            "track_id": "track_d",
            "action": "generate",
            "next_step_recorded": True,
            "scope_authority_policy_ok": True,
            "market_feedback_handled": True,
            "fault_injection": {"tested": True, "recovered": True},
            "quality_lift_if_human_intervenes": 0.0,
            "policy_decision": "continue",
        },
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    assert report["criteria"]["protagonist_fantasy_persistence"]["passed"] is True
    assert report["criteria"]["protagonist_fantasy_persistence"]["details"]["protagonist_momentum"] >= 0.58


def test_final_threshold_accepts_runtime_sidecar_evidence_for_truth_closure(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_e"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)

    _write_json(
        track_dir / "state.json",
        {
            "last_quality_gate": {
                "passed": True,
                "checks": {"hook_score": True, "cliffhanger_valid": True, "world_instability": True},
                "predicted_retention": 0.82,
                "content_ceiling_total": 69,
                "causal_score": 0.85,
            },
            "quality_lift_if_human_intervenes": 0.0,
        },
    )
    _write_json(
        out_dir / "certification_report.json",
        {
            "market": {
                "available": True,
                "ok": True,
                "stats": {"latest_top_percent": 4.0},
            }
        },
    )
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "episode": 1,
            "episode_attribution": {"lineage_parent": "outline:v4", "retention_signal": 0.82, "pacing_signal": 0.74, "fatigue_signal": 0.11, "payoff_signal": 0.77},
            "scores": {"hook_score": 0.84, "payoff_score": 0.77, "pacing_score": 0.74, "character_score": 0.78, "repetition_score": 0.11},
            "retention": {"predicted_next_episode": 0.82},
            "content_ceiling": {"ceiling_total": 69},
            "meta": {"scene_causality": {"score": 0.85}},
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"

    save_job_queue_state(
        {"queue_status": "running", "active_job_id": "track:0", "jobs": [], "last_sync": {"current_index": 0, "track_count": 1}},
        path=str(queue_path),
        safe_mode=False,
    )
    save_supervisor_state(
        {"status": "running", "active_job_id": "track:0", "last_event_type": "job_queue_synced"},
        path=str(supervisor_path),
        safe_mode=False,
    )
    save_admission_state({"last_scope_decision": {"material_id": "mat:3", "decision": "accepted", "reason": "scope_fit"}}, path=str(admission_path), safe_mode=False)
    save_promotion_state({"last_promotion_decision": {"artifact_id": "art:3", "decision": "promoted", "reason": "quality"}}, path=str(promotion_path), safe_mode=False)

    report = evaluate_final_threshold_bundle(
        {"quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65}, "safe_mode": False},
        str(out_dir),
        cycle_context={
            "track_id": "track_e",
            "action": "generate",
            "next_step_recorded": True,
            "market_feedback_handled": True,
            "scope_authority_policy_ok": True,
            "fault_injection": {"tested": True, "recovered": True},
            "quality_lift_if_human_intervenes": 0.0,
            "policy_decision": "continue",
        },
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    assert report["criteria"]["append_only_truth_lineage_replayability"]["passed"] is True
    assert report["criteria"]["append_only_truth_lineage_replayability"]["details"]["runtime_sidecar_evidence"] is True
    assert report["criteria"]["control_loop_state_closure"]["passed"] is True


def test_final_threshold_boosts_market_feedback_repair_when_business_inputs_exist(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_f"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "revenue_input.csv").write_text("revenue\n1000\n", encoding="utf-8")

    _write_json(
        track_dir / "state.json",
        {
            "story_state_v2": {"control": {}},
            "last_quality_gate": {
                "passed": True,
                "checks": {"hook_score": True, "cliffhanger_valid": True, "world_instability": True},
                "predicted_retention": 0.81,
                "content_ceiling_total": 67,
                "causal_score": 0.83,
            },
            "quality_lift_if_human_intervenes": 0.0,
        },
    )
    _write_json(out_dir / "certification_report.json", {"market": {"available": False, "ok": False, "stats": {"latest_top_percent": 12.0}}})
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "type": "certification",
            "report": {"market": {"available": False, "ok": False}},
        },
    )
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "episode": 1,
            "episode_attribution": {"lineage_parent": "outline:v5", "retention_signal": 0.81, "pacing_signal": 0.72, "fatigue_signal": 0.12, "payoff_signal": 0.74},
            "scores": {"hook_score": 0.82, "payoff_score": 0.74, "pacing_score": 0.72, "character_score": 0.77, "repetition_score": 0.12},
            "retention": {"predicted_next_episode": 0.81},
            "content_ceiling": {"ceiling_total": 67},
            "meta": {"scene_causality": {"score": 0.83}},
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"
    save_job_queue_state({"queue_status": "running", "active_job_id": None, "jobs": []}, path=str(queue_path), safe_mode=False)
    save_supervisor_state({"status": "running", "active_job_id": None}, path=str(supervisor_path), safe_mode=False)
    save_admission_state({"last_scope_decision": {"material_id": "mat:4", "decision": "accepted", "reason": "scope_fit"}}, path=str(admission_path), safe_mode=False)
    save_promotion_state({}, path=str(promotion_path), safe_mode=False)

    report = evaluate_final_threshold_bundle(
        {"quality": {"predicted_retention_min": 0.8, "causal_score_min": 0.72, "ceiling_total_min": 65}, "safe_mode": False},
        str(out_dir),
        cycle_context={
            "track_id": "track_f",
            "action": "certify",
            "next_step_recorded": True,
            "scope_authority_policy_ok": True,
            "market_feedback_handled": False,
            "quality_lift_if_human_intervenes": 0.0,
            "policy_decision": "hold",
        },
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    repair = next(item for item in report["next_required_repairs"] if item["criterion"] == "market_feedback_autoloop")
    assert repair["priority"] == 15
    assert repair["repair_context"]["business_feedback_rebind_required"] is True


def test_reader_quality_failures_emit_direct_repair_context(tmp_path):
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_reader"
    out_dir = track_dir / "outputs"
    out_dir.mkdir(parents=True)

    _write_json(
        track_dir / "state.json",
        {
            "story_state_v2": {
                "control": {
                    "reader_quality": {
                        "thinness_debt": 0.14,
                        "repetition_debt": 0.12,
                        "deja_vu_debt": 0.11,
                        "fake_urgency_debt": 0.13,
                        "compression_debt": 0.12,
                    }
                },
                "promise_graph": {"payoff_integrity": 0.45, "payoff_corruption_flags": ["broken_payoff"]},
            },
            "last_quality_gate": {"passed": True, "checks": {"hook_score": False}, "predicted_retention": 0.58},
            "quality_lift_if_human_intervenes": 0.02,
        },
    )
    _append_jsonl(
        out_dir / "metrics.jsonl",
        {
            "episode": 1,
            "episode_attribution": {
                "lineage_parent": "outline:v8",
                "retention_signal": 0.58,
                "pacing_signal": 0.63,
                "fatigue_signal": 0.29,
                "payoff_signal": 0.46,
            },
            "scores": {
                "hook_score": 0.61,
                "payoff_score": 0.46,
                "pacing_score": 0.63,
                "character_score": 0.55,
                "repetition_score": 0.31,
            },
            "retention": {"predicted_next_episode": 0.58},
            "content_ceiling": {"ceiling_total": 61},
            "meta": {"scene_causality": {"score": 0.8}},
        },
    )

    queue_path = tmp_path / "job_queue.json"
    supervisor_path = tmp_path / "supervisor_state.json"
    admission_path = tmp_path / "admission_state.json"
    promotion_path = tmp_path / "promotion_state.json"
    save_job_queue_state({"queue_status": "running", "active_job_id": None, "jobs": []}, path=str(queue_path), safe_mode=False)
    save_supervisor_state({"status": "running", "active_job_id": None}, path=str(supervisor_path), safe_mode=False)
    save_admission_state({"last_scope_decision": {"material_id": "mat:8", "decision": "accepted"}}, path=str(admission_path), safe_mode=False)
    save_promotion_state({"last_promotion_decision": {"decision": "hold"}}, path=str(promotion_path), safe_mode=False)

    report = evaluate_final_threshold_bundle(
        {
            "quality": {
                "predicted_retention_min": 0.75,
                "causal_score_min": 0.72,
                "ceiling_total_min": 65,
                "upper_tier_early_hook_min": 0.78,
                "upper_tier_episode_hook_min": 0.74,
                "upper_tier_payoff_signal_min": 0.72,
                "upper_tier_protagonist_momentum_min": 0.58,
                "upper_tier_fatigue_signal_max": 0.22,
            },
            "safe_mode": False,
        },
        str(out_dir),
        cycle_context={"track_id": "track_reader", "action": "generate", "next_step_recorded": True},
        queue_path=str(queue_path),
        supervisor_path=str(supervisor_path),
        admission_path=str(admission_path),
        promotion_path=str(promotion_path),
        safe_mode=False,
    )

    repairs = {item["criterion"]: item for item in report["next_required_repairs"]}
    assert repairs["early_hook_strength"]["repair_context"]["hook_bias"] == pytest.approx(0.14)
    assert repairs["episode_end_hook_strength"]["repair_context"]["payoff_bias"] == pytest.approx(0.05)
    assert repairs["long_arc_payoff_stability"]["repair_context"]["payoff_bias"] == pytest.approx(0.12)
    assert repairs["protagonist_fantasy_persistence"]["repair_context"]["rewrite_pressure"] == "high"
    assert repairs["serialization_fatigue_control"]["repair_context"]["world_lock"] is True
    assert repairs["serialization_fatigue_control"]["repair_context"]["novelty_bias"] == pytest.approx(0.12)
    assert repairs["serialization_fatigue_control"]["repair_context"]["compression_bias"] == pytest.approx(0.1)
    assert repairs["reader_retention_stability"]["repair_context"]["urgency_bias"] == pytest.approx(0.08)
    assert repairs["reader_retention_stability"]["repair_context"]["compression_bias"] == pytest.approx(0.08)
    supervisor = load_supervisor_state(str(supervisor_path))
    assert supervisor["reader_quality_priority"] == "critical"
    assert supervisor["runtime_repairs"]["hook_bias"] >= 0.12
    assert supervisor["runtime_repairs"]["rewrite_pressure"] == "high"
