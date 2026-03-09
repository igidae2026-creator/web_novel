import json
import os
import tempfile

from engine.story_state import ensure_story_state
from engine.business_operator import (
    apply_recommendation_to_runtime,
    build_business_action_recommendations,
    record_business_adjustment,
    sync_business_adjustment_outcomes,
)
from engine.platform_genre_spec import resolve_platform_genre_spec
from engine.episode_milestones import evaluate_episode_milestones
from engine.monetization_transition import evaluate_monetization_transition
from engine.protagonist_guard import evaluate_protagonist_guard
from engine.title_optimizer import build_title_strategy, generate_title_candidates
from engine.narrative_debt import evaluate_narrative_debt
from engine.emotion_wave import evaluate_emotion_wave
from engine.ip_expansion_readiness import evaluate_ip_expansion_readiness
from engine.multi_objective import build_multi_objective_scores
from engine.regression_guard import regression_decision
from engine.reliability import update_system_status
from engine.causal_repair import build_business_axis_repair_plan, build_causal_repair_plan
from engine.control_console import build_history_trends, build_studio_os_dashboard, execute_policy_action, request_policy_action


def _base_cfg():
    return {
        "project": {"name": "StudioOS", "platform": "Munpia", "genre_bucket": "B", "title": "배신 뒤의 회귀자"},
        "novel": {"total_episodes": 300, "early_focus_episodes": 3, "paywall_window": [20, 25]},
    }


def test_platform_genre_spec_loads_presets_and_overrides():
    spec = resolve_platform_genre_spec(
        _base_cfg(),
        runtime_cfg={"project_setup": {"platform_genre_overrides": {"free_episode_count_target": 23}}},
        project_overrides={"target_title_length_range": [10, 18]},
    )

    assert spec["platform"] == "Munpia"
    assert spec["genre_bucket"] == "B"
    assert spec["free_episode_count_target"] == 23
    assert spec["target_title_length_range"] == [10, 18]
    assert spec["major_payoff_timing_target"] == 10


def test_episode_milestones_detect_missing_early_hook_and_win():
    state = {}
    ensure_story_state(state, cfg=_base_cfg())
    state["story_state_v2"]["rewards"]["delivered_rewards"] = []
    state["story_state_v2"]["rewards"]["reward_density"] = 3

    hook = evaluate_episode_milestones(1, state["story_state_v2"], {"major_payoff_timing_target": 10}, event_plan={}, score_obj={"hook_score": 0.4})
    win = evaluate_episode_milestones(3, state["story_state_v2"], {"major_payoff_timing_target": 10}, event_plan={"type": "loss"}, score_obj={"hook_score": 0.7})

    assert "episode_1_hook" in hook["missing_milestones"]
    assert "episode_3_first_win" in win["missing_milestones"]


def test_episode_milestones_detect_conversion_variation_and_reset_points():
    state = {}
    ensure_story_state(state, cfg=_base_cfg())
    state["story_state_v2"]["market"]["paywall_pressure"] = 5
    state["story_state_v2"]["promise_graph"]["payoff_integrity"] = 0.35
    state["story_state_v2"]["pattern_memory"]["overused_events"] = ["betrayal"]
    state["story_state_v2"]["pacing"]["release_debt"] = 4
    spec = resolve_platform_genre_spec(_base_cfg())

    conversion = evaluate_episode_milestones(22, state["story_state_v2"], spec, event_plan={"type": "betrayal"}, score_obj={"hook_score": 0.8})
    variation = evaluate_episode_milestones(15, state["story_state_v2"], spec, event_plan={"type": "betrayal"}, score_obj={"hook_score": 0.8})
    reset = evaluate_episode_milestones(45, state["story_state_v2"], spec, event_plan={"type": "betrayal"}, score_obj={"hook_score": 0.8})

    assert "conversion_zone_trigger" in conversion["missing_milestones"]
    assert "structural_variation_checkpoint" in variation["missing_milestones"]
    assert "reset_refresh_zone" in reset["missing_milestones"]


def test_monetization_transition_distinguishes_weak_and_strong_readiness():
    state = {}
    ensure_story_state(state, cfg=_base_cfg())
    spec = resolve_platform_genre_spec(_base_cfg())

    weak = evaluate_monetization_transition(22, state["story_state_v2"], spec, milestone_report={"milestone_readiness": 0.2})
    state["story_state_v2"]["market"]["paywall_pressure"] = 8
    state["story_state_v2"]["market"]["reader_trust"] = 7
    state["story_state_v2"]["rewards"]["reward_density"] = 7
    state["story_state_v2"]["rewards"]["expectation_alignment"] = 7
    state["story_state_v2"]["serialization"]["retention_pressure"] = 8
    state["story_state_v2"]["promise_graph"]["payoff_integrity"] = 0.72
    strong = evaluate_monetization_transition(22, state["story_state_v2"], spec, milestone_report={"milestone_readiness": 0.8})

    assert weak["conversion_readiness"] < strong["conversion_readiness"]
    assert "low_conversion_pressure" in weak["missing_conversion_signals"]


def test_protagonist_guard_detects_takeover_and_preserves_sovereignty_when_strong():
    state = {}
    ensure_story_state(state, cfg=_base_cfg())
    weak = evaluate_protagonist_guard(state["story_state_v2"], score_obj={"character_score": 0.55})

    state["story_state_v2"]["cast"]["protagonist"]["urgency"] = 9
    state["story_state_v2"]["cast"]["protagonist"]["decision_pressure"] = 9
    state["story_state_v2"]["cast"]["protagonist"]["progress"] = 7
    state["story_state_v2"]["cast"]["rival"]["urgency"] = 4
    state["story_state_v2"]["promise_graph"]["character_promises"] = {"protagonist": [{"status": "open"}, {"status": "resolved"}]}
    state["story_state_v2"]["promise_graph"]["payoff_integrity"] = 0.8
    state["story_state_v2"]["rewards"]["reward_density"] = 7
    strong = evaluate_protagonist_guard(state["story_state_v2"], score_obj={"character_score": 0.82})

    assert weak["secondary_takeover_risk"] >= 0.35
    assert strong["protagonist_sovereignty"] > weak["protagonist_sovereignty"]
    assert strong["protagonist_agency_score"] > weak["protagonist_agency_score"]


def test_title_optimizer_enforces_length_and_ranks_stronger_titles_higher():
    spec = resolve_platform_genre_spec(_base_cfg(), project_overrides={"target_title_length_range": [10, 18]})
    candidates = generate_title_candidates("배신당한 황자가 회귀 후 진실과 복수를 동시에 쥔다", spec, current_title="기억")

    assert candidates[0]["title_fitness"] >= candidates[-1]["title_fitness"]
    assert any(item["weak_title"] for item in candidates if item["candidate"] == "기억")
    assert any(10 <= len(item["candidate"]) <= 18 for item in candidates[:3])


def test_business_axis_repair_plan_emits_directives_for_weak_axes():
    state = {}
    ensure_story_state(state, cfg=_base_cfg())
    story_state = state["story_state_v2"]
    story_state["title"] = {"best_title": {"candidate": "기억", "title_fitness": 0.3}}
    story_state["monetization"] = {"missing_conversion_signals": ["low_conversion_pressure"]}
    objective = {
        "title_fitness": 0.3,
        "milestone_compliance": 0.4,
        "conversion_readiness": 0.42,
        "protagonist_sovereignty": 0.45,
        "narrative_debt_health": 0.4,
        "emotion_wave_health": 0.44,
        "ip_readiness": 0.41,
    }

    business = build_business_axis_repair_plan(objective, story_state, episode=22)
    repair = build_causal_repair_plan({"issues": ["causal_link"], "score": 0.5}, story_state=story_state, event_plan={"type": "betrayal"}, cliffhanger_plan={"mode": "choice_lock"}, objective_scores=objective, episode=22)

    assert "conversion_readiness" in [item["axis"] for item in business["business_axis_failures"]]
    assert business["blocking_business_failures"]
    assert repair["business_directives"]
    assert repair["revision_triggers"]


def test_narrative_debt_and_emotion_wave_flag_overload_and_reset_deficit():
    state = {}
    ensure_story_state(state, cfg=_base_cfg())
    state["story_state_v2"]["promise_graph"]["unresolved_count"] = 6
    state["story_state_v2"]["promise_graph"]["resolution_rate"] = 0.2
    state["story_state_v2"]["rewards"]["pending_promises"] = ["a", "b", "c", "d", "e"]
    state["story_state_v2"]["world"]["power_rules"] = ["a", "b", "c", "d"]
    state["story_state_v2"]["history"]["events"] = ["power_shift", "collapse", "false_victory", "collapse", "power_shift"]
    state["story_state_v2"]["pacing"]["current_tension"] = 9
    state["story_state_v2"]["pacing"]["release_debt"] = 4
    state["story_state_v2"]["pacing"]["spike_debt"] = 3
    state["story_state_v2"]["information"]["emotional_reservoir"] = 2

    debt = evaluate_narrative_debt(state["story_state_v2"])
    wave = evaluate_emotion_wave(state["story_state_v2"])

    assert debt["narrative_debt_score"] > 0.6
    assert "unresolved_setup_overload" in debt["debt_sources"]
    assert wave["emotion_wave_balance"] < 0.6
    assert wave["reset_need"] > 0.5


def test_ip_readiness_hook_activates_after_scale_up_zone():
    state = {}
    ensure_story_state(state, cfg=_base_cfg())
    state["story_state_v2"]["world"]["recent_changes"] = ["a", "b", "c"]
    state["story_state_v2"]["promise_graph"]["payoff_integrity"] = 0.7
    state["story_state_v2"]["promise_graph"]["resolution_rate"] = 0.6
    state["story_state_v2"]["protagonist_guard"] = {"protagonist_sovereignty": 0.8}
    state["story_state_v2"]["narrative_debt"] = {"expansion_friction_risk": 0.2}
    ip = evaluate_ip_expansion_readiness(120, state["story_state_v2"], {"best_title": {"title_fitness": 0.8}})

    assert ip["ip_readiness"] > 0.5
    assert ip["webtoon_adaptability"] > 0.4


def test_title_strategy_connects_candidates_to_launch_logic():
    spec = resolve_platform_genre_spec(_base_cfg())
    package = build_title_strategy(
        "배신당한 황자가 회귀 후 진실과 복수를 동시에 쥔다",
        spec,
        current_title="배신 뒤의 회귀자",
        runtime_release_learning={"trust_signal": 0.7, "retention_signal": 0.72},
    )

    assert package["selected_title"]
    assert package["selected_title_rationale"]
    assert package["launch_recommendation"]["preferred_release_timing_windows"]
    assert package["launch_recommendation"]["launch_fit_score"] > 0.5


def test_runtime_status_and_regression_guard_include_new_business_axes():
    state = {}
    ensure_story_state(state, cfg=_base_cfg())
    story_state = state["story_state_v2"]
    story_state["title"] = {"best_title": {"title_fitness": 0.84}}
    story_state["milestones"] = {"milestone_readiness": 0.8}
    story_state["monetization"] = {"conversion_readiness": 0.78}
    story_state["protagonist_guard"] = {
        "protagonist_sovereignty": 0.82,
        "protagonist_agency_score": 0.8,
        "secondary_takeover_risk": 0.18,
        "reward_loop_integrity": 0.76,
    }
    story_state["narrative_debt"] = {"narrative_debt_score": 0.22, "payoff_recovery_rate": 0.7, "expansion_friction_risk": 0.2}
    story_state["emotion_wave"] = {"emotion_wave_balance": 0.74, "fatigue_projection": 0.24}
    story_state["ip_readiness"] = {"ip_readiness": 0.66, "canon_consistency": 0.72, "franchise_expandability": 0.64}
    story_state["serialization"]["sustainability"] = 8
    story_state["market"]["release_confidence"] = 7

    base_scores = {
        "hook_score": 0.78,
        "escalation": 0.76,
        "emotion_density": 0.72,
        "coherence": 0.75,
        "world_logic": 0.78,
        "chemistry_score": 0.7,
        "character_score": 0.74,
        "payoff_score": 0.73,
        "repetition_score": 0.12,
        "pacing_score": 0.74,
        "logic_score": 0.75,
    }
    objective = build_multi_objective_scores(
        base_scores,
        retention_state={"unresolved_thread_pressure": 7, "curiosity_debt": 7, "information_gap": 7},
        story_state=story_state,
        causal_report={"score": 0.8, "checks": {"world_consequence": 1.0, "goal_pressure": 1.0, "emotional_trace": 1.0, "cliffhanger_alignment": 1.0}},
    )
    status = update_system_status(state, episode=24, objective_scores=objective, portfolio_signals={"release_guard": 7})

    assert "title_fitness" in objective
    assert "conversion_readiness" in objective
    assert status["latest_business_signals"]["title_fitness"] == 0.84

    improved = dict(objective)
    improved["title_fitness"] += 0.05
    improved["milestone_compliance"] += 0.04
    improved["conversion_readiness"] += 0.04
    improved["protagonist_sovereignty"] += 0.04
    improved["narrative_debt_health"] += 0.03
    improved["emotion_wave_health"] += 0.03
    accepted, report = regression_decision(objective, improved)

    assert accepted
    assert report["accepted"]


def test_console_builders_expose_business_signals_and_trends():
    payload = {
        "updated_at": "2026-03-09T12:00:00",
        "system_status": {
            "axis_history": {
                "title_fitness": [0.6, 0.7],
                "milestone_compliance": [0.5, 0.65],
                "conversion_readiness": [0.52, 0.68],
                "protagonist_sovereignty": [0.58, 0.7],
                "narrative_debt_health": [0.44, 0.6],
                "emotion_wave_health": [0.5, 0.63],
                "ip_readiness": [0.4, 0.55],
            },
            "latest_business_signals": {
                "title_fitness": 0.7,
                "milestone_readiness": 0.65,
                "conversion_readiness": 0.68,
                "protagonist_sovereignty": 0.7,
                "narrative_debt_score": 0.35,
                "emotion_wave_balance": 0.63,
                "ip_readiness": 0.55,
            },
            "latest_title_state": {
                "selected_title": "배신 뒤의 회귀자",
                "selected_title_rationale": ["장르 신호가 선명함"],
                "launch_recommendation": {"launch_fit_score": 0.74},
                "ranked_candidates": [{"candidate": "배신 뒤의 회귀자", "title_fitness": 0.7}],
            },
            "latest_revision_triggers": ["conversion_readiness", "protagonist_sovereignty"],
            "warnings": [{"type": "business_axis", "axes": ["conversion_readiness"]}],
            "balanced_total_history": [0.6, 0.64],
            "repair_rate_history": [0.7, 0.8],
            "portfolio_signal_history": [],
            "drift": {"drop": 0.0, "warning": False},
        },
    }

    studio = build_studio_os_dashboard(payload)
    history = build_history_trends(payload, {"history": []})

    assert studio["cards"]
    assert studio["latest_title_state"]["selected_title"] == "배신 뒤의 회귀자"
    assert "title_fitness" in history["business_axis_trends"]
    assert studio["latest_revision_triggers"] == ["conversion_readiness", "protagonist_sovereignty"]


def test_business_recommendations_map_weak_axes_to_operator_actions():
    system_status = {
        "latest_business_signals": {
            "title_fitness": 0.4,
            "milestone_readiness": 0.45,
            "conversion_readiness": 0.5,
            "protagonist_sovereignty": 0.5,
            "narrative_debt_score": 0.7,
            "emotion_wave_balance": 0.45,
            "ip_readiness": 0.42,
        },
        "latest_title_state": {"best_title": {"candidate": "배신 뒤의 회귀자"}},
    }
    recs = build_business_action_recommendations(system_status, runtime_cfg={})
    action_types = {item["action_type"] for item in recs}

    assert "title_package_change" in action_types
    assert "stronger_milestone_enforcement" in action_types
    assert "stagger_or_hold_release" in action_types
    assert "protagonist_centered_rewrite" in action_types
    assert "soft_recovery_mode" in action_types
    assert "reduce_release_cadence" in action_types
    assert "ip_scene_density_enforcement" in action_types


def test_bounded_operator_adjustment_application_is_reversible_and_capped():
    runtime_cfg = {
        "project_setup": {"title": "기억"},
        "release_cadence": {"steps_per_run": 2},
        "evaluation": {"milestone_enforcement_level": 0.5, "protagonist_focus_enforcement": 0.5, "ip_expansion_enforcement": 0.4},
        "business": {"recovery_mode": "normal"},
    }
    title_runtime = apply_recommendation_to_runtime(runtime_cfg, {"config_patch": {"project_setup": {"title": "배신 뒤의 회귀자"}}})
    cadence_runtime = apply_recommendation_to_runtime(runtime_cfg, {"config_patch": {"release_cadence": {"steps_per_run": -1}, "business": {"recovery_mode": "soft_recovery"}}})
    milestone_runtime = apply_recommendation_to_runtime(runtime_cfg, {"config_patch": {"evaluation": {"milestone_enforcement_level": 0.15}}})

    assert title_runtime["project_setup"]["title"] == "배신 뒤의 회귀자"
    assert cadence_runtime["release_cadence"]["steps_per_run"] == 1
    assert cadence_runtime["business"]["recovery_mode"] == "soft_recovery"
    assert milestone_runtime["evaluation"]["milestone_enforcement_level"] == 0.65


def test_adjustment_outcome_logging_and_learning_updates_effectiveness():
    runtime_cfg = {"business_control": {"adjustment_history": [], "pending_adjustments": [], "learning": {}}}
    recommendation = {"id": "title_fitness:title_package_change", "action_type": "title_package_change", "axis": "title_fitness", "payload": {}}
    logged = record_business_adjustment(runtime_cfg, recommendation, {"title_fitness": 0.4}, "2026-03-09T12:00:00")
    synced = sync_business_adjustment_outcomes(logged, {"latest_business_signals": {"title_fitness": 0.7}})

    history = synced["business_control"]["adjustment_history"]
    learning = synced["business_control"]["learning"]
    assert history[-1]["outcome"] == "improved"
    assert history[-1]["improvement"] == 0.3
    assert learning["title_fitness"]["successful_actions"] == 1


def test_policy_action_can_apply_business_adjustment_and_record_runtime_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.yaml")
        runtime_path = os.path.join(tmpdir, "runtime_config.json")
        policy_path = os.path.join(tmpdir, "outputs", "policy_action.json")
        system_status_path = os.path.join(tmpdir, "outputs", "system_status.json")
        os.makedirs(os.path.dirname(policy_path), exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(
                "project:\n"
                "  name: TempProject\n"
                "  platform: Munpia\n"
                "  genre_bucket: B\n"
                "model:\n"
                "  name: test\n"
                "  mode: batch\n"
                "limits:\n"
                "  max_revision_passes: 1\n"
                "novel:\n"
                "  total_episodes: 100\n"
                "  words_per_episode_min: 1000\n"
                "  words_per_episode_max: 1500\n"
                "  early_focus_episodes: 3\n"
                "  paywall_window: [20, 25]\n"
                "quality:\n"
                "  viral_required: false\n"
                "output:\n"
                "  root_dir: outputs\n"
                "safe_mode: false\n"
            )
        runtime_cfg = {
            "project_setup": {"name": "TempProject", "platform": "Munpia", "genre_bucket": "B", "title": "기억"},
            "paths": {
                "tracks_root": os.path.join(tmpdir, "tracks"),
                "system_status_path": system_status_path,
                "policy_action_path": policy_path,
                "project_output_dir": os.path.join(tmpdir, "outputs", "TempProject"),
            },
            "release_cadence": {"mode": "queue_loop", "steps_per_run": 2},
            "evaluation": {"milestone_enforcement_level": 0.5, "protagonist_focus_enforcement": 0.5, "ip_expansion_enforcement": 0.4},
            "business": {"recovery_mode": "normal"},
            "business_control": {"adjustment_history": [], "pending_adjustments": [], "learning": {}},
        }
        with open(runtime_path, "w", encoding="utf-8") as f:
            json.dump(runtime_cfg, f)
        with open(system_status_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "updated_at": "2026-03-09T12:00:00",
                    "system_status": {
                        "latest_business_signals": {
                            "title_fitness": 0.4,
                            "milestone_readiness": 0.8,
                            "conversion_readiness": 0.8,
                            "protagonist_sovereignty": 0.8,
                            "narrative_debt_score": 0.2,
                            "emotion_wave_balance": 0.8,
                            "ip_readiness": 0.8,
                        },
                        "latest_title_state": {"best_title": {"candidate": "배신 뒤의 회귀자"}},
                    },
                },
                f,
            )

        request_policy_action("apply_business_adjustment", payload={"recommendation_id": "title_fitness:title_package_change"}, path=policy_path)
        result = execute_policy_action(config_path=config_path, runtime_config_path=runtime_path, policy_action_path=policy_path)

        assert result["result"]["applied_adjustment"]["action_type"] == "title_package_change"
        updated_runtime = result["result"]["runtime_config"]
        assert updated_runtime["project_setup"]["title"] == "배신 뒤의 회귀자"
        assert updated_runtime["business_control"]["adjustment_history"]
