import json
import os

import pytest

from engine.config import load_config
from engine.cost import CostTracker
from engine.external_rank import ExternalRankSignals
from engine.pipeline import EpisodeRejectedError, ensure_project_dirs, generate_episode
from engine.regression_guard import PROTECTED_AXES
from engine.state import StateStore


class _FakeResponse:
    def __init__(self, output_text: str):
        self.output_text = output_text
        self.usage = None


class _FakeLLM:
    def __init__(self, responses):
        self._responses = iter(responses)

    def call(self, prompt, temperature=0.0):
        return _FakeResponse(next(self._responses))


def _patch_generation_stack(monkeypatch, gate_passed: bool) -> None:
    import engine.pipeline as pipeline

    def _noop(*args, **kwargs):
        return None

    def _identity_knobs(knobs, *args, **kwargs):
        return knobs

    def _ensure_story_state(state_data, **kwargs):
        state_data.setdefault("story_state_v2", {})

    monkeypatch.setattr(pipeline, "load_runtime_config_into_cfg", lambda cfg: (cfg, {}))
    monkeypatch.setattr(pipeline, "update_competition_state", _noop)
    monkeypatch.setattr(pipeline, "apply_market_policy", _noop)
    monkeypatch.setattr(pipeline, "ensure_story_state", _ensure_story_state)
    monkeypatch.setattr(pipeline, "load_profiles", lambda path: [])
    monkeypatch.setattr(pipeline, "select_profile", lambda profiles, platform, genre_bucket: {})
    monkeypatch.setattr(pipeline, "compute_style_vector", lambda text: {})
    monkeypatch.setattr(pipeline, "from_dict", lambda payload: {})
    monkeypatch.setattr(pipeline, "to_dict", lambda payload: {})
    monkeypatch.setattr(pipeline, "blend", lambda before, after, alpha=0.15: {})
    monkeypatch.setattr(pipeline, "prepare_tension_wave", _noop)
    monkeypatch.setattr(pipeline, "apply_tension_wave", _identity_knobs)
    monkeypatch.setattr(pipeline, "damp_knobs", lambda cfg, knobs, original: knobs)
    monkeypatch.setattr(pipeline, "clamp_knobs", lambda cfg, knobs: knobs)
    monkeypatch.setattr(pipeline, "apply_freeze", lambda cfg, state_data, knobs: knobs)
    monkeypatch.setattr(pipeline, "register_change", _noop)
    monkeypatch.setattr(pipeline, "prepare_character_arc", _noop)
    monkeypatch.setattr(pipeline, "prepare_conflict_memory", _noop)
    monkeypatch.setattr(pipeline, "prepare_antagonist_plan", _noop)
    monkeypatch.setattr(pipeline, "update_pattern_memory", _noop)
    monkeypatch.setattr(pipeline, "update_market_serialization", _noop)
    monkeypatch.setattr(pipeline, "update_portfolio_memory", _noop)
    monkeypatch.setattr(pipeline, "generate_event_plan", lambda state_data, episode: {"type": "betrayal"})
    monkeypatch.setattr(
        pipeline,
        "generate_cliffhanger_plan",
        lambda *args, **kwargs: {
            "target": "배신 추적",
            "open_question": "누가 먼저 무너질까",
            "carryover_pressure": 8,
        },
    )
    monkeypatch.setattr(pipeline, "build_retention_state", _noop)
    monkeypatch.setattr(pipeline, "character_prompt_payload", lambda state_data: {})
    monkeypatch.setattr(pipeline, "conflict_prompt_payload", lambda state_data: {})
    monkeypatch.setattr(pipeline, "event_prompt_payload", lambda event_plan: event_plan)
    monkeypatch.setattr(pipeline, "tension_prompt_payload", lambda state_data: {})
    monkeypatch.setattr(pipeline, "retention_prompt_payload", lambda state_data: {})
    monkeypatch.setattr(pipeline, "information_prompt_payload", lambda state_data: {})
    monkeypatch.setattr(pipeline, "world_prompt_payload", lambda state_data: {})
    monkeypatch.setattr(pipeline, "antagonist_prompt_payload", lambda state_data: {})
    monkeypatch.setattr(pipeline, "pattern_prompt_payload", lambda state_data: {})
    monkeypatch.setattr(pipeline, "market_prompt_payload", lambda state_data: {})
    monkeypatch.setattr(pipeline, "portfolio_prompt_payload", lambda state_data: {})
    monkeypatch.setattr(pipeline, "validate_viral", lambda payload, cliffhanger_plan=None: (True, ""))
    monkeypatch.setattr(pipeline, "validate_scene_causality", lambda *args, **kwargs: {"score": 0.88, "issues": []})
    monkeypatch.setattr(pipeline, "build_causal_repair_plan", lambda *args, **kwargs: {})
    monkeypatch.setattr(pipeline, "start_causal_repair_cycle", _noop)
    monkeypatch.setattr(pipeline, "record_causal_repair_attempt", _noop)
    monkeypatch.setattr(pipeline, "record_repair_diff_audit", _noop)
    monkeypatch.setattr(pipeline, "finalize_causal_repair_cycle", _noop)
    monkeypatch.setattr(pipeline, "store_causal_repair_plan", _noop)
    monkeypatch.setattr(pipeline, "assess_causal_closure", lambda *args, **kwargs: {"passed": True})
    monkeypatch.setattr(
        pipeline,
        "enforce_cliffhanger",
        lambda payload, cliffhanger_plan: {
            "cliffhanger": payload.get("cliffhanger", ""),
            "cliffhanger_plan": cliffhanger_plan,
        },
    )
    monkeypatch.setattr(pipeline, "register_story_event", _noop)
    monkeypatch.setattr(pipeline, "update_character_arc", _noop)
    monkeypatch.setattr(pipeline, "update_conflict_memory", _noop)
    monkeypatch.setattr(pipeline, "update_tension_wave", _noop)
    monkeypatch.setattr(pipeline, "update_world_state", _noop)
    monkeypatch.setattr(pipeline, "update_reward_serialization", _noop)
    monkeypatch.setattr(pipeline, "prepare_information_emotion", _noop)
    monkeypatch.setattr(pipeline, "predict_retention", lambda *args, **kwargs: 0.81)
    monkeypatch.setattr(
        pipeline,
        "build_multi_objective_scores",
        lambda *args, **kwargs: {axis: 0.77 for axis in PROTECTED_AXES},
    )
    monkeypatch.setattr(pipeline, "multi_objective_balance", lambda *args, **kwargs: {"balanced_total": 0.77})
    monkeypatch.setattr(pipeline, "evaluate_episode", lambda *args, **kwargs: {"ceiling_total": 66})
    monkeypatch.setattr(
        pipeline,
        "quality_gate_report",
        lambda *args, **kwargs: {
            "passed": gate_passed,
            "failed_checks": [] if gate_passed else ["hook_score"],
            "checks": {"hook_score": gate_passed},
            "prose_report": {},
            "objective_profile": {},
        },
    )
    monkeypatch.setattr(pipeline, "record_episode_attribution", lambda *args, **kwargs: {})
    monkeypatch.setattr(pipeline, "regression_decision", lambda before, after: (True, {"accepted": True, "dropped_axes": []}))
    monkeypatch.setattr(pipeline, "update_system_status", lambda *args, **kwargs: {})
    monkeypatch.setattr(pipeline, "write_system_status_snapshot", _noop)
    monkeypatch.setattr(pipeline, "simulate_long_run", lambda *args, **kwargs: {})

    class _Prompts:
        @staticmethod
        def episode_plan(*args, **kwargs):
            return "EPISODE_PLAN"

        @staticmethod
        def episode_draft_json(*args, **kwargs):
            return "EPISODE_DRAFT_JSON"

        @staticmethod
        def scoring_json(*args, **kwargs):
            return "EPISODE_SCORE_JSON"

        @staticmethod
        def episode_rewrite_json(*args, **kwargs):
            return "EPISODE_REWRITE_JSON"

    monkeypatch.setattr(pipeline, "PROMPTS", _Prompts())


def test_generate_episode_rejects_failed_quality_gate_without_writing_episode(tmp_path, monkeypatch):
    _patch_generation_stack(monkeypatch, gate_passed=False)

    cfg = load_config("config.yaml")
    cfg["project"]["name"] = "quality-gate-reject"
    cfg["output"]["root_dir"] = str(tmp_path / "outputs")
    cfg["external"]["rank_signals_csv"] = str(tmp_path / "rank_signals.csv")
    cfg["safe_mode"] = False

    out_dir = ensure_project_dirs(cfg)
    state = StateStore(os.path.join(out_dir, "state.json"), safe_mode=False, project_dir_for_backup=out_dir)
    state.load()
    state.set("outline", "몰락한 천재 검사가 배신 이후 제국을 되찾는다")

    llm = _FakeLLM(
        [
            "계획",
            json.dumps(
                {
                    "episode_text": "첫 장면은 강하지만 아직 기준 미달이다.",
                    "quote_line": "",
                    "comment_hook": "",
                    "cliffhanger": "문이 열린다.",
                },
                ensure_ascii=False,
            ),
            json.dumps(
                {
                    "hook_score": 0.81,
                    "paywall_score": 0.79,
                    "emotion_density": 0.74,
                    "escalation": 0.76,
                    "character_score": 0.75,
                    "payoff_score": 0.74,
                    "pacing_score": 0.73,
                    "chemistry_score": 0.68,
                    "repetition_score": 0.12,
                },
                ensure_ascii=False,
            ),
            json.dumps(
                {
                    "episode_text": "재작성 이후에도 품질 게이트는 통과하지 못한다.",
                    "quote_line": "",
                    "comment_hook": "",
                    "cliffhanger": "칼끝이 흔들린다.",
                },
                ensure_ascii=False,
            ),
            json.dumps(
                {
                    "hook_score": 0.83,
                    "paywall_score": 0.8,
                    "emotion_density": 0.75,
                    "escalation": 0.77,
                    "character_score": 0.76,
                    "payoff_score": 0.75,
                    "pacing_score": 0.74,
                    "chemistry_score": 0.69,
                    "repetition_score": 0.11,
                },
                ensure_ascii=False,
            ),
        ]
    )
    cost = CostTracker(cfg, out_dir)
    ext = ExternalRankSignals(cfg)

    with pytest.raises(EpisodeRejectedError) as excinfo:
        generate_episode(cfg, state, llm, cost, ext, 1)

    assert excinfo.value.reason == "quality_gate_failed"
    assert not os.path.exists(os.path.join(out_dir, "episode_001.txt"))

    metrics_path = os.path.join(out_dir, "metrics.jsonl")
    assert os.path.exists(metrics_path)
    with open(metrics_path, "r", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]

    assert rows[-1]["type"] == "episode_rejected"
    assert rows[-1]["reason"] == "quality_gate_failed"
    assert rows[-1]["failed_checks"] == ["hook_score"]
    assert "next_episode" not in state.data
