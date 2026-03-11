import json
import os

from engine.preflight_gate import apply_preflight_runtime_policy, assess_preflight_bundle


def test_preflight_raises_risk_when_capability_bundles_are_open(tmp_path):
    out_dir = tmp_path / "outputs"
    out_dir.mkdir(parents=True)
    with open(out_dir / "final_threshold_eval.json", "w", encoding="utf-8") as handle:
        json.dump(
            {
                "failed_bundles": ["truth_capability", "recovery_capability"],
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )

    state_data = {
        "out_dir": str(out_dir),
        "story_state_v2": {"control": {}, "portfolio_memory": {}},
        "predicted_retention": 0.8,
    }
    cfg = {"quality": {"predicted_retention_min": 0.62, "world_instability_max": 7}, "model": {"mode": "batch"}}
    runtime_cfg = {
        "evaluation": {
            "preflight_gate": {"enabled": True},
            "risk_tiers": {
                "critical": {
                    "max_revision_passes": 3,
                    "causal_repair_retry_budget": 3,
                    "request_timeout_seconds": 240,
                    "mode": "priority",
                }
            },
        }
    }

    preflight = assess_preflight_bundle(cfg, state_data, runtime_cfg=runtime_cfg, episode=5)

    assert preflight["risk_tier"] == "critical"
    assert "truth_capability_not_closed" in preflight["blocking_reasons"]
    assert preflight["runtime_policy"]["mode"] == "priority"


def test_apply_preflight_runtime_policy_overrides_timeout_and_budget():
    cfg = {
        "limits": {"max_revision_passes": 2, "causal_repair_retry_budget": 2},
        "model": {"mode": "batch"},
    }
    preflight = {
        "runtime_policy": {
            "max_revision_passes": 1,
            "causal_repair_retry_budget": 1,
            "request_timeout_seconds": 90,
            "mode": "batch",
        }
    }

    adjusted = apply_preflight_runtime_policy(cfg, preflight)

    assert adjusted["limits"]["max_revision_passes"] == 1
    assert adjusted["limits"]["causal_repair_retry_budget"] == 1
    assert adjusted["limits"]["request_timeout_seconds"] == 90
    assert adjusted["model"]["request_timeout_seconds"] == 90


def test_preflight_uses_runtime_repair_context_to_harden_policy():
    state_data = {
        "story_state_v2": {
            "control": {
                "final_threshold_repairs": {
                    "business_feedback_rebind_required": True,
                    "human_lift_sampling_required": True,
                }
            },
            "portfolio_memory": {},
        },
        "predicted_retention": 0.8,
    }
    cfg = {"quality": {"predicted_retention_min": 0.62, "world_instability_max": 7}, "model": {"mode": "batch"}}
    runtime_cfg = {
        "evaluation": {
            "preflight_gate": {"enabled": True},
            "risk_tiers": {
                "medium": {
                    "max_revision_passes": 1,
                    "causal_repair_retry_budget": 1,
                    "request_timeout_seconds": 90,
                    "mode": "batch",
                }
            },
        }
    }

    preflight = assess_preflight_bundle(cfg, state_data, runtime_cfg=runtime_cfg, episode=3)

    assert preflight["runtime_policy"]["max_revision_passes"] >= 3
    assert preflight["runtime_policy"]["causal_repair_retry_budget"] >= 3
    assert preflight["runtime_policy"]["request_timeout_seconds"] >= 180
    assert preflight["runtime_policy"]["mode"] == "priority"


def test_preflight_blocks_for_hidden_reader_risk_trend_repair_context():
    state_data = {
        "story_state_v2": {
            "control": {
                "final_threshold_repairs": {
                    "reader_risk_trend_repair_required": True,
                    "reader_risk_trend_block_required": True,
                    "hidden_reader_risk_trend": 0.52,
                }
            },
            "portfolio_memory": {},
        },
        "predicted_retention": 0.8,
    }
    cfg = {"quality": {"predicted_retention_min": 0.62, "world_instability_max": 7}, "model": {"mode": "batch"}}

    preflight = assess_preflight_bundle(cfg, state_data, runtime_cfg={}, episode=4)

    assert preflight["risk_tier"] == "critical"
    assert "hidden_reader_risk_trend_block" in preflight["blocking_reasons"]
    assert preflight["runtime_policy"]["mode"] == "priority"
    assert preflight["runtime_policy"]["request_timeout_seconds"] >= 180


def test_preflight_blocks_for_low_heavy_reader_signal_repair_context():
    state_data = {
        "story_state_v2": {
            "control": {
                "final_threshold_repairs": {
                    "heavy_reader_signal_repair_required": True,
                    "heavy_reader_signal_block_required": True,
                    "heavy_reader_signal_trend": 0.58,
                }
            },
            "portfolio_memory": {},
        },
        "predicted_retention": 0.8,
    }
    cfg = {"quality": {"predicted_retention_min": 0.62, "world_instability_max": 7}, "model": {"mode": "batch"}}

    preflight = assess_preflight_bundle(cfg, state_data, runtime_cfg={}, episode=4)

    assert preflight["risk_tier"] == "critical"
    assert "heavy_reader_signal_trend_block" in preflight["blocking_reasons"]
    assert preflight["runtime_policy"]["mode"] == "priority"
    assert preflight["runtime_policy"]["request_timeout_seconds"] >= 180
    assert preflight["signals"]["heavy_reader_signal_trend"] == 0.58


def test_preflight_escalates_for_reader_quality_repairs_and_failed_criteria(tmp_path):
    out_dir = tmp_path / "outputs"
    out_dir.mkdir(parents=True)
    with open(out_dir / "final_threshold_eval.json", "w", encoding="utf-8") as handle:
        json.dump(
            {
                "failed_bundles": ["generation_capability"],
                "failed_criteria": ["early_hook_strength", "reader_retention_stability"],
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )

    state_data = {
        "out_dir": str(out_dir),
        "story_state_v2": {
            "control": {
                "final_threshold_repairs": {
                    "reader_quality_repair_required": True,
                    "reader_quality_priority": "critical",
                }
            },
            "portfolio_memory": {},
        },
        "predicted_retention": 0.7,
    }
    cfg = {"quality": {"predicted_retention_min": 0.62, "world_instability_max": 7}, "model": {"mode": "batch"}}

    preflight = assess_preflight_bundle(cfg, state_data, runtime_cfg={}, episode=3)

    assert preflight["risk_tier"] in {"high", "critical"}
    assert preflight["runtime_policy"]["mode"] == "priority"
    assert preflight["runtime_policy"]["max_revision_passes"] >= 3
    assert preflight["signals"]["reader_quality_pressure"] > 0


def test_preflight_escalates_for_accumulated_reader_quality_debt():
    state_data = {
        "story_state_v2": {
            "control": {
                "reader_quality": {
                    "hook_debt": 0.22,
                    "payoff_debt": 0.18,
                    "fatigue_debt": 0.14,
                    "retention_debt": 0.19,
                }
            },
            "portfolio_memory": {},
        },
        "predicted_retention": 0.76,
    }
    cfg = {"quality": {"predicted_retention_min": 0.62, "world_instability_max": 7}, "model": {"mode": "batch"}}

    preflight = assess_preflight_bundle(cfg, state_data, runtime_cfg={}, episode=5)

    assert preflight["risk_tier"] in {"medium", "high", "critical"}
    assert preflight["signals"]["reader_quality_debt"] > 0.4


def test_preflight_escalates_for_accumulated_arc_debt():
    state_data = {
        "story_state_v2": {
            "control": {
                "arc_pressure": {
                    "payoff_debt": 0.26,
                    "momentum_debt": 0.22,
                }
            },
            "portfolio_memory": {},
        },
        "predicted_retention": 0.78,
    }
    cfg = {"quality": {"predicted_retention_min": 0.62, "world_instability_max": 7}, "model": {"mode": "batch"}}

    preflight = assess_preflight_bundle(cfg, state_data, runtime_cfg={}, episode=6)

    assert preflight["signals"]["arc_debt"] > 0.5
    assert preflight["risk_tier"] in {"medium", "high", "critical"}
