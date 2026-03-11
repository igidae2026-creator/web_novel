import json
import os

from engine.job_queue import load_job_queue_state
from engine.track_loop import run_queue_loop
from engine.track_queue import load_queue_state, save_queue_state


def _write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def test_run_queue_loop_skips_generation_when_critical_bundle_budget_is_zero(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_a"
    _write_json(track_dir / "track.json", {"project": {"platform": "Munpia", "genre_bucket": "A"}})
    _write_json(
        track_dir / "outputs" / "final_threshold_eval.json",
        {
            "failed_bundles": ["truth_capability"],
            "next_required_repairs": [
                {
                    "criterion": "append_only_truth_lineage_replayability",
                    "repair": "repair_append_only_lineage_replayability",
                    "priority": 5,
                }
            ],
        },
    )
    save_queue_state(
        {
            "status": "running",
            "track_dirs": [str(track_dir)],
            "current_index": 0,
            "last_error": None,
        },
        path=str(tmp_path / "domains" / "webnovel" / "tracks" / "queue_state.json"),
    )
    _write_json(
        tmp_path / "runtime_config.json",
        {
            "generation_enabled": True,
            "portfolio": {
                "bundle_budgeting": {
                    "enabled": True,
                    "critical_generation_cap": 0,
                    "caution_generation_cap": 1,
                    "stable_generation_cap": 3,
                }
            },
        },
    )

    ok, msg = run_queue_loop({"safe_mode": True}, max_steps=2)

    assert ok is False
    assert "Generation budget exhausted" in msg
    assert "queued_repairs=1" in msg

    queue_state = load_job_queue_state()
    repair_jobs = [job for job in queue_state["jobs"] if job["job_type"] == "repair_final_threshold"]
    assert len(repair_jobs) == 1
    assert repair_jobs[0]["job_id"] == "repair:track_a:append_only_truth_lineage_replayability"

    track_queue_state = load_queue_state()
    assert track_queue_state["status"] == "blocked"
    assert "Generation budget exhausted" in str(track_queue_state["last_error"])


def test_run_queue_loop_pauses_for_reader_quality_budget_pressure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_reader"
    _write_json(track_dir / "track.json", {"project": {"platform": "Munpia", "genre_bucket": "A"}})
    _write_json(
        track_dir / "outputs" / "final_threshold_eval.json",
        {
            "failed_bundles": [],
            "failed_criteria": ["early_hook_strength", "reader_retention_stability"],
            "next_required_repairs": [
                {
                    "criterion": "early_hook_strength",
                    "repair": "repair_early_hook_strength",
                    "priority": 35,
                    "repair_context": {"hook_bias": 0.14, "rewrite_pressure": "high"},
                }
            ],
        },
    )
    save_queue_state(
        {
            "status": "running",
            "track_dirs": [str(track_dir)],
            "current_index": 0,
            "last_error": None,
        },
        path=str(tmp_path / "domains" / "webnovel" / "tracks" / "queue_state.json"),
    )
    _write_json(
        tmp_path / "runtime_config.json",
        {
            "generation_enabled": True,
            "portfolio": {
                "bundle_budgeting": {
                    "enabled": True,
                    "critical_generation_cap": 0,
                    "caution_generation_cap": 0,
                    "stable_generation_cap": 3,
                }
            },
        },
    )

    ok, msg = run_queue_loop({"safe_mode": True}, max_steps=1)

    assert ok is False
    assert "Generation budget exhausted" in msg
    queue_state = load_job_queue_state()
    assert queue_state["jobs"][0]["job_id"] == "repair:track_reader:early_hook_strength"

    track_queue_state = load_queue_state()
    assert track_queue_state["status"] == "paused"


def test_run_queue_loop_pauses_for_hidden_reader_risk_pressure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_hidden"
    _write_json(track_dir / "track.json", {"project": {"platform": "Munpia", "genre_bucket": "A"}})
    _write_json(
        track_dir / "outputs" / "final_threshold_eval.json",
        {
            "failed_bundles": [],
            "failed_criteria": ["reader_retention_stability"],
            "criteria": {
                "reader_retention_stability": {
                    "details": {
                        "reader_quality_debt": {
                            "thinness_debt": 0.21,
                            "fake_urgency_debt": 0.14,
                        }
                    }
                },
                "serialization_fatigue_control": {
                    "details": {
                        "reader_quality_debt": {
                            "repetition_debt": 0.11,
                            "deja_vu_debt": 0.1,
                        }
                    }
                },
            },
            "next_required_repairs": [
                {
                    "criterion": "reader_retention_stability",
                    "repair": "repair_reader_retention_stability",
                    "priority": 20,
                }
            ],
        },
    )
    save_queue_state(
        {
            "status": "running",
            "track_dirs": [str(track_dir)],
            "current_index": 0,
            "last_error": None,
        },
        path=str(tmp_path / "domains" / "webnovel" / "tracks" / "queue_state.json"),
    )
    _write_json(
        tmp_path / "runtime_config.json",
        {
            "generation_enabled": True,
            "portfolio": {
                "bundle_budgeting": {
                    "enabled": True,
                    "critical_generation_cap": 0,
                    "caution_generation_cap": 0,
                    "stable_generation_cap": 3,
                }
            },
        },
    )

    ok, msg = run_queue_loop({"safe_mode": True}, max_steps=1)

    assert ok is False
    assert "Generation budget exhausted" in msg
    track_queue_state = load_queue_state()
    assert track_queue_state["status"] == "paused"
    history = json.loads((tmp_path / "domains" / "webnovel" / "tracks" / "queue_history.json").read_text(encoding="utf-8"))
    trend_summary = history["bundle_budgeting"]["hidden_reader_risk_trend_summary"]
    assert trend_summary["max"] == 0.0


def test_run_queue_loop_blocks_for_hidden_reader_risk_trend_pressure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    track_dir = tmp_path / "domains" / "webnovel" / "tracks" / "track_trend"
    _write_json(track_dir / "track.json", {"project": {"platform": "Munpia", "genre_bucket": "A"}})
    _write_json(
        track_dir / "outputs" / "final_threshold_eval.json",
        {
            "failed_bundles": [],
            "failed_criteria": ["autonomous_convergence_trend"],
            "criteria": {
                "autonomous_convergence_trend": {
                    "details": {
                        "hidden_reader_risk_trend": 0.52,
                        "heavy_reader_signal_trend": 0.58,
                    }
                }
            },
            "next_required_repairs": [
                {
                    "criterion": "autonomous_convergence_trend",
                    "repair": "repair_autonomous_convergence_trend",
                    "priority": 10,
                    "repair_context": {"hidden_reader_risk_trend": 0.52},
                }
            ],
        },
    )
    save_queue_state(
        {
            "status": "running",
            "track_dirs": [str(track_dir)],
            "current_index": 0,
            "last_error": None,
        },
        path=str(tmp_path / "domains" / "webnovel" / "tracks" / "queue_state.json"),
    )
    _write_json(
        tmp_path / "runtime_config.json",
        {
            "generation_enabled": True,
            "portfolio": {
                "bundle_budgeting": {
                    "enabled": True,
                    "critical_generation_cap": 0,
                    "caution_generation_cap": 1,
                    "stable_generation_cap": 3,
                }
            },
        },
    )

    ok, msg = run_queue_loop({"safe_mode": True}, max_steps=1)

    assert ok is False
    assert "Generation budget exhausted" in msg
    assert "hidden_reader_risk_trend_max=0.52" in msg
    assert "heavy_reader_signal_trend_min=0.58" in msg
    track_queue_state = load_queue_state()
    assert track_queue_state["status"] == "blocked"
    assert track_queue_state["bundle_budgeting"]["hidden_reader_risk_trend_summary"]["max"] == 0.52
    assert track_queue_state["bundle_budgeting"]["heavy_reader_signal_trend_summary"]["min"] == 0.58
    assert track_queue_state["bundle_budgeting"]["hidden_reader_risk_trend_summary"]["critical_tracks"] == ["track_trend"]
    assert track_queue_state["bundle_budgeting"]["heavy_reader_signal_trend_summary"]["critical_tracks"] == ["track_trend"]
    history = json.loads((tmp_path / "domains" / "webnovel" / "tracks" / "queue_history.json").read_text(encoding="utf-8"))
    trend_summary = history["bundle_budgeting"]["hidden_reader_risk_trend_summary"]
    assert trend_summary["max"] == 0.52
    assert trend_summary["top_tracks"][0]["track"] == "track_trend"
    signal_summary = history["bundle_budgeting"]["heavy_reader_signal_trend_summary"]
    assert signal_summary["min"] == 0.58
    assert signal_summary["weakest_tracks"][0]["track"] == "track_trend"
