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


def test_generate_episode_persists_final_gate_state_on_success(tmp_path, monkeypatch):
    _patch_generation_stack(monkeypatch, gate_passed=True)

    cfg = load_config("config.yaml")
    cfg["project"]["name"] = "quality-gate-pass"
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
                    "episode_text": "강한 도입과 선명한 갈등이 있는 회차다.\n\n\"이번엔 내가 고른다.\"\n\n황태자가 검을 들었다.",
                    "quote_line": "",
                    "comment_hook": "",
                    "cliffhanger": "문이 다시 열렸다.",
                },
                ensure_ascii=False,
            ),
            json.dumps(
                {
                    "hook_score": 0.88,
                    "paywall_score": 0.84,
                    "emotion_density": 0.8,
                    "escalation": 0.81,
                    "character_score": 0.79,
                    "payoff_score": 0.8,
                    "pacing_score": 0.78,
                    "chemistry_score": 0.74,
                    "repetition_score": 0.08,
                },
                ensure_ascii=False,
            ),
        ]
    )
    cost = CostTracker(cfg, out_dir)
    ext = ExternalRankSignals(cfg)

    record = generate_episode(cfg, state, llm, cost, ext, 1)

    assert record["retention"]["predicted_next_episode"] == 0.81
    assert state.get("predicted_retention") == 0.81
    assert state.get("last_quality_gate")["passed"] is True
    assert state.get("last_quality_gate")["content_ceiling_total"] == 66
    assert state.get("preflight_bundle")["preflight_ready"] is True


def test_generate_episode_fail_closed_on_preflight_gate(tmp_path, monkeypatch):
    _patch_generation_stack(monkeypatch, gate_passed=True)

    cfg = load_config("config.yaml")
    cfg["project"]["name"] = "preflight-gate-reject"
    cfg["output"]["root_dir"] = str(tmp_path / "outputs")
    cfg["external"]["rank_signals_csv"] = str(tmp_path / "rank_signals.csv")
    cfg["safe_mode"] = False

    out_dir = ensure_project_dirs(cfg)
    state = StateStore(os.path.join(out_dir, "state.json"), safe_mode=False, project_dir_for_backup=out_dir)
    state.load()
    state.set("outline", "몰락한 천재 검사가 배신 이후 제국을 되찾는다")
    state.data["predicted_retention"] = 0.2
    state.data.setdefault("story_state_v2", {}).setdefault("world", {})["instability"] = 12

    llm = _FakeLLM(
        [
            "계획",
            json.dumps(
                {
                    "episode_text": "이 초안은 실제로 생성되면 안 된다.",
                    "quote_line": "",
                    "comment_hook": "",
                    "cliffhanger": "막는다.",
                },
                ensure_ascii=False,
            ),
            json.dumps(
                {
                    "hook_score": 0.9,
                    "paywall_score": 0.88,
                    "emotion_density": 0.82,
                    "escalation": 0.84,
                    "character_score": 0.83,
                    "payoff_score": 0.82,
                    "pacing_score": 0.81,
                    "chemistry_score": 0.78,
                    "repetition_score": 0.08,
                },
                ensure_ascii=False,
            ),
        ]
    )
    cost = CostTracker(cfg, out_dir)
    ext = ExternalRankSignals(cfg)

    with pytest.raises(EpisodeRejectedError) as excinfo:
        generate_episode(cfg, state, llm, cost, ext, 1)

    assert excinfo.value.reason == "preflight_gate_failed"
    assert excinfo.value.audit["failed_checks"]
    with open(os.path.join(out_dir, "metrics.jsonl"), "r", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    assert rows[0]["type"] == "preflight_eval"
    assert rows[-1]["reason"] == "preflight_gate_failed"


def test_generate_episode_applies_final_threshold_repairs_to_generation_runtime(tmp_path, monkeypatch):
    _patch_generation_stack(monkeypatch, gate_passed=True)

    import engine.pipeline as pipeline

    captured = {}

    class _CapturingPrompts:
        @staticmethod
        def episode_plan(cfg, outline, episode, knobs, snap, fatigue_directive, sub_key, story_state=None):
            captured["plan_knobs"] = dict(knobs)
            captured["plan_story_state"] = dict(story_state or {})
            return "EPISODE_PLAN"

        @staticmethod
        def episode_draft_json(cfg, plan, episode, knobs, style, sub_key, story_state=None):
            captured["draft_knobs"] = dict(knobs)
            captured["draft_story_state"] = dict(story_state or {})
            return "EPISODE_DRAFT_JSON"

        @staticmethod
        def scoring_json(cfg, episode_text, episode):
            return "EPISODE_SCORE_JSON"

        @staticmethod
        def episode_rewrite_json(*args, **kwargs):
            return "EPISODE_REWRITE_JSON"

    monkeypatch.setattr(pipeline, "PROMPTS", _CapturingPrompts())

    cfg = load_config("config.yaml")
    cfg["project"]["name"] = "final-threshold-repair-runtime"
    cfg["output"]["root_dir"] = str(tmp_path / "outputs")
    cfg["external"]["rank_signals_csv"] = str(tmp_path / "rank_signals.csv")
    cfg["safe_mode"] = False
    cfg["limits"]["max_revision_passes"] = 1
    cfg["limits"]["causal_repair_retry_budget"] = 1
    cfg["limits"]["request_timeout_seconds"] = 90
    cfg["model"]["mode"] = "batch"

    out_dir = ensure_project_dirs(cfg)
    state = StateStore(os.path.join(out_dir, "state.json"), safe_mode=False, project_dir_for_backup=out_dir)
    state.load()
    state.set("outline", "몰락한 천재 검사가 배신 이후 제국을 되찾는다")
    state.data.setdefault("story_state_v2", {}).setdefault("control", {})["final_threshold_repairs"] = {
        "hook_bias": 0.12,
        "payoff_bias": 0.08,
        "rewrite_pressure": "high",
        "market_rebind_required": True,
        "business_feedback_rebind_required": True,
    }

    llm = _FakeLLM(
        [
            "계획",
            json.dumps(
                {
                    "episode_text": "강한 도입과 선명한 갈등이 있는 회차다.\n\n\"이번엔 내가 고른다.\"\n\n황태자가 검을 들었다.",
                    "quote_line": "",
                    "comment_hook": "",
                    "cliffhanger": "문이 다시 열렸다.",
                },
                ensure_ascii=False,
            ),
            json.dumps(
                {
                    "hook_score": 0.88,
                    "paywall_score": 0.84,
                    "emotion_density": 0.8,
                    "escalation": 0.81,
                    "character_score": 0.79,
                    "payoff_score": 0.8,
                    "pacing_score": 0.78,
                    "chemistry_score": 0.74,
                    "repetition_score": 0.08,
                },
                ensure_ascii=False,
            ),
        ]
    )
    cost = CostTracker(cfg, out_dir)
    ext = ExternalRankSignals(cfg)

    record = generate_episode(cfg, state, llm, cost, ext, 1)

    assert record["knobs"]["hook_intensity"] == pytest.approx(0.99)
    assert record["knobs"]["payoff_intensity"] == pytest.approx(0.78)
    assert record["knobs"]["business_feedback_rebind_required"] is True
    assert record["final_threshold_repairs_applied"]["hook_bias"] == pytest.approx(0.12)
    assert record["final_threshold_repairs_applied"]["business_feedback_rebind_required"] is True
    assert record["generation_runtime_policy"]["max_revision_passes"] == 3
    assert record["generation_runtime_policy"]["causal_repair_retry_budget"] == 3
    assert record["generation_runtime_policy"]["request_timeout_seconds"] == 180
    assert record["generation_runtime_policy"]["mode"] == "priority"
    assert captured["draft_story_state"]["market"]["rebind_required"] is True
    assert captured["draft_story_state"]["market"]["runtime_repairs"]["hook_bias"] == pytest.approx(0.12)


def test_generate_episode_applies_reader_quality_debt_to_generation_runtime(tmp_path, monkeypatch):
    _patch_generation_stack(monkeypatch, gate_passed=True)

    import engine.pipeline as pipeline

    captured = {}

    class _CapturingPrompts:
        @staticmethod
        def episode_plan(cfg, outline, episode, knobs, snap, fatigue_directive, sub_key, story_state=None):
            captured["plan_knobs"] = dict(knobs)
            captured["plan_story_state"] = dict(story_state or {})
            return "EPISODE_PLAN"

        @staticmethod
        def episode_draft_json(cfg, plan, episode, knobs, style, sub_key, story_state=None):
            captured["draft_knobs"] = dict(knobs)
            captured["draft_story_state"] = dict(story_state or {})
            return "EPISODE_DRAFT_JSON"

        @staticmethod
        def scoring_json(cfg, episode_text, episode):
            return "EPISODE_SCORE_JSON"

        @staticmethod
        def episode_rewrite_json(*args, **kwargs):
            return "EPISODE_REWRITE_JSON"

    monkeypatch.setattr(pipeline, "PROMPTS", _CapturingPrompts())

    cfg = load_config("config.yaml")
    cfg["project"]["name"] = "reader-quality-debt-runtime"
    cfg["output"]["root_dir"] = str(tmp_path / "outputs")
    cfg["external"]["rank_signals_csv"] = str(tmp_path / "rank_signals.csv")
    cfg["safe_mode"] = False

    out_dir = ensure_project_dirs(cfg)
    state = StateStore(os.path.join(out_dir, "state.json"), safe_mode=False, project_dir_for_backup=out_dir)
    state.load()
    state.set("outline", "몰락한 천재 검사가 배신 이후 제국을 되찾는다")
    state.data.setdefault("story_state_v2", {}).setdefault("control", {})["reader_quality"] = {
        "hook_debt": 0.2,
        "payoff_debt": 0.16,
        "fatigue_debt": 0.12,
        "retention_debt": 0.18,
        "thinness_debt": 0.24,
        "repetition_debt": 0.22,
        "deja_vu_debt": 0.2,
        "fake_urgency_debt": 0.19,
        "compression_debt": 0.17,
    }

    llm = _FakeLLM(
        [
            "계획",
            json.dumps(
                {
                    "episode_text": "강한 도입과 선명한 갈등이 있는 회차다.\n\n\"이번엔 내가 고른다.\"\n\n황태자가 검을 들었다.",
                    "quote_line": "",
                    "comment_hook": "",
                    "cliffhanger": "문이 다시 열렸다.",
                },
                ensure_ascii=False,
            ),
            json.dumps(
                {
                    "hook_score": 0.88,
                    "paywall_score": 0.84,
                    "emotion_density": 0.8,
                    "escalation": 0.81,
                    "character_score": 0.79,
                    "payoff_score": 0.8,
                    "pacing_score": 0.78,
                    "chemistry_score": 0.74,
                    "repetition_score": 0.08,
                },
                ensure_ascii=False,
            ),
        ]
    )
    cost = CostTracker(cfg, out_dir)
    ext = ExternalRankSignals(cfg)

    record = generate_episode(cfg, state, llm, cost, ext, 1)

    assert record["reader_quality_debt_applied"]["reader_quality_debt"]["hook_debt"] == pytest.approx(0.2)
    assert record["reader_quality_debt_applied"]["reader_quality_debt"]["thinness_debt"] == pytest.approx(0.24)
    assert record["reader_quality_debt_applied"]["reader_quality_debt"]["deja_vu_debt"] == pytest.approx(0.2)
    assert record["knobs"]["hook_intensity"] > 0.9
    assert record["knobs"]["payoff_intensity"] > 0.7
    assert record["knobs"]["novelty_boost"] > 0.5
    assert record["knobs"]["compression"] > 0.8
    assert captured["draft_story_state"]["reader_quality_debt"]["reader_quality_debt"]["retention_debt"] == pytest.approx(0.18)
    assert captured["draft_story_state"]["reader_quality_debt"]["reader_quality_debt"]["fake_urgency_debt"] == pytest.approx(0.19)


def test_generate_episode_applies_market_feedback_pressure_to_generation_runtime(tmp_path, monkeypatch):
    _patch_generation_stack(monkeypatch, gate_passed=True)

    import engine.pipeline as pipeline
    from engine.market_serialization import update_market_serialization as real_update_market_serialization

    captured = {}

    class _CapturingPrompts:
        @staticmethod
        def episode_plan(cfg, outline, episode, knobs, snap, fatigue_directive, sub_key, story_state=None):
            captured["plan_knobs"] = dict(knobs)
            captured["plan_story_state"] = dict(story_state or {})
            return "EPISODE_PLAN"

        @staticmethod
        def episode_draft_json(cfg, plan, episode, knobs, style, sub_key, story_state=None):
            captured["draft_knobs"] = dict(knobs)
            captured["draft_story_state"] = dict(story_state or {})
            return "EPISODE_DRAFT_JSON"

        @staticmethod
        def scoring_json(cfg, episode_text, episode):
            return "EPISODE_SCORE_JSON"

        @staticmethod
        def episode_rewrite_json(*args, **kwargs):
            return "EPISODE_REWRITE_JSON"

    monkeypatch.setattr(pipeline, "PROMPTS", _CapturingPrompts())
    monkeypatch.setattr(pipeline, "update_market_serialization", real_update_market_serialization)

    cfg = load_config("config.yaml")
    cfg["project"]["name"] = "market-feedback-pressure-runtime"
    cfg["output"]["root_dir"] = str(tmp_path / "outputs")
    cfg["external"]["rank_signals_csv"] = str(tmp_path / "rank_signals.csv")
    cfg["safe_mode"] = False

    out_dir = ensure_project_dirs(cfg)
    with open(os.path.join(out_dir, "certification_report.json"), "w", encoding="utf-8") as handle:
        json.dump(
            {
                "market": {"ok": False, "stats": {"latest_top_percent": 7.2}},
                "business_feedback": {
                    "available": True,
                    "total_revenue": 200.0,
                    "total_campaign_spend": 190.0,
                    "best_campaign_roi": 0.03,
                },
                "failure_reason": "target_not_met",
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )

    state = StateStore(os.path.join(out_dir, "state.json"), safe_mode=False, project_dir_for_backup=out_dir)
    state.load()
    state.set("outline", "몰락한 천재 검사가 배신 이후 제국을 되찾는다")

    llm = _FakeLLM(
        [
            "계획",
            json.dumps(
                {
                    "episode_text": "강한 도입과 선명한 갈등이 있는 회차다.\n\n\"이번엔 내가 고른다.\"\n\n황태자가 검을 들었다.",
                    "quote_line": "",
                    "comment_hook": "",
                    "cliffhanger": "문이 다시 열렸다.",
                },
                ensure_ascii=False,
            ),
            json.dumps(
                {
                    "hook_score": 0.88,
                    "paywall_score": 0.84,
                    "emotion_density": 0.8,
                    "escalation": 0.81,
                    "character_score": 0.79,
                    "payoff_score": 0.8,
                    "pacing_score": 0.78,
                    "chemistry_score": 0.74,
                    "repetition_score": 0.08,
                },
                ensure_ascii=False,
            ),
        ]
    )
    cost = CostTracker(cfg, out_dir)
    ext = ExternalRankSignals(cfg)

    record = generate_episode(cfg, state, llm, cost, ext, 1)

    assert record["market_feedback_pressure_applied"]["market_pressure_response"] > 0
    assert record["knobs"]["hook_intensity"] > 0.9
    assert record["knobs"]["compression"] > 0.8
    assert captured["draft_story_state"]["market_feedback_pressure"]["reader_exit_risk_response"] > 0


def test_prompt_surfaces_reader_and_market_pressure_directives():
    from engine.prompts import PROMPTS
    from engine.style import StyleVector

    cfg = load_config("config.yaml")
    text = PROMPTS.episode_draft_json(
        cfg,
        "씬 플랜",
        1,
        {"hook_intensity": 0.9},
        StyleVector(),
        "AUTO",
        story_state={
            "reader_quality_debt": {
                "reader_quality_debt": {
                    "hook_debt": 0.2,
                    "payoff_debt": 0.15,
                    "fatigue_debt": 0.1,
                    "retention_debt": 0.18,
                }
            },
            "market_feedback_pressure": {
                "market_pressure_response": 0.06,
                "reader_exit_risk_response": 0.04,
                "campaign_roi_response": 0.03,
            },
        },
    )

    assert "상위독자 압력 지시" in text
    assert "초반 1~3문단" in text
    assert "회차 말미" in text
    assert "시장 반응이 약하므로" in text


def test_generate_episode_applies_arc_pressure_to_generation_runtime(tmp_path, monkeypatch):
    _patch_generation_stack(monkeypatch, gate_passed=True)

    import engine.pipeline as pipeline

    captured = {}

    class _CapturingPrompts:
        @staticmethod
        def episode_plan(cfg, outline, episode, knobs, snap, fatigue_directive, sub_key, story_state=None):
            captured["plan_story_state"] = dict(story_state or {})
            return "EPISODE_PLAN"

        @staticmethod
        def episode_draft_json(cfg, plan, episode, knobs, style, sub_key, story_state=None):
            captured["draft_knobs"] = dict(knobs)
            captured["draft_story_state"] = dict(story_state or {})
            return "EPISODE_DRAFT_JSON"

        @staticmethod
        def scoring_json(cfg, episode_text, episode):
            return "EPISODE_SCORE_JSON"

        @staticmethod
        def episode_rewrite_json(*args, **kwargs):
            return "EPISODE_REWRITE_JSON"

    monkeypatch.setattr(pipeline, "PROMPTS", _CapturingPrompts())

    cfg = load_config("config.yaml")
    cfg["project"]["name"] = "arc-pressure-runtime"
    cfg["output"]["root_dir"] = str(tmp_path / "outputs")
    cfg["external"]["rank_signals_csv"] = str(tmp_path / "rank_signals.csv")
    cfg["safe_mode"] = False

    out_dir = ensure_project_dirs(cfg)
    state = StateStore(os.path.join(out_dir, "state.json"), safe_mode=False, project_dir_for_backup=out_dir)
    state.load()
    state.set("outline", "몰락한 천재 검사가 배신 이후 제국을 되찾는다")
    state.data.setdefault("story_state_v2", {}).setdefault("control", {})["arc_pressure"] = {
        "payoff_debt": 0.24,
        "momentum_debt": 0.2,
    }

    llm = _FakeLLM(
        [
            "계획",
            json.dumps(
                {
                    "episode_text": "강한 도입과 선명한 갈등이 있는 회차다.\n\n\"이번엔 내가 고른다.\"\n\n황태자가 검을 들었다.",
                    "quote_line": "",
                    "comment_hook": "",
                    "cliffhanger": "문이 다시 열렸다.",
                },
                ensure_ascii=False,
            ),
            json.dumps(
                {
                    "hook_score": 0.88,
                    "paywall_score": 0.84,
                    "emotion_density": 0.8,
                    "escalation": 0.81,
                    "character_score": 0.79,
                    "payoff_score": 0.8,
                    "pacing_score": 0.78,
                    "chemistry_score": 0.74,
                    "repetition_score": 0.08,
                },
                ensure_ascii=False,
            ),
        ]
    )
    cost = CostTracker(cfg, out_dir)
    ext = ExternalRankSignals(cfg)

    record = generate_episode(cfg, state, llm, cost, ext, 1)

    assert record["arc_pressure_applied"]["arc_pressure"]["payoff_debt"] == pytest.approx(0.24)
    assert record["knobs"]["payoff_intensity"] > 0.8
    assert record["knobs"]["hook_intensity"] > 0.9
    assert captured["draft_story_state"]["arc_pressure"]["arc_pressure"]["momentum_debt"] == pytest.approx(0.2)
