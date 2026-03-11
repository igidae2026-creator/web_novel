from engine.story_state import ensure_story_state
from engine.information_emotion import prepare_information_emotion, information_prompt_payload
from engine.world_logic import update_world_state
from engine.reward_serialization import update_reward_serialization
from engine.multi_objective import build_multi_objective_scores
from engine.regression_guard import regression_decision
from engine.predictive_retention import build_retention_state, predict_retention
from engine.scene_causality import validate_scene_causality
from engine.antagonist_planner import prepare_antagonist_plan, antagonist_prompt_payload
from engine.pattern_memory import update_pattern_memory, choose_event_with_memory
from engine.market_serialization import update_market_serialization, market_prompt_payload
from engine.causal_repair import (
    assess_causal_closure,
    build_causal_repair_plan,
    finalize_causal_repair_cycle,
    record_causal_repair_attempt,
    record_repair_diff_audit,
    repair_prompt_payload,
    start_causal_repair_cycle,
    store_causal_repair_plan,
)
from engine.repair_diff_audit import audit_repair_diff
from engine.promise_graph import update_promise_payoff_graph
from engine.episode_attribution import build_episode_attribution, record_episode_attribution
from engine.character_arc import update_character_arc
from engine.causal_attribution import build_scene_event_attribution
from engine.reliability import detect_axis_drift, detect_quality_drift, record_soak_history, simulate_long_run, summarize_soak_report, update_system_status
from engine.portfolio_memory import learn_portfolio_snapshot, update_portfolio_memory, portfolio_prompt_payload
from engine.portfolio_signals import compute_portfolio_signals
from engine.regression_guard import portfolio_signal_decision, release_policy_decision
from engine.portfolio_orchestrator import build_portfolio_runtime_snapshot, rebalance_platform
from engine.cross_track_release import build_cross_track_release_plan
from engine.cross_track_release import apply_queue_release_outcome, apply_runtime_release_to_state, build_runtime_release_learning_snapshot, learn_runtime_release_outcome_in_state, refresh_queue_release_runtime, resolve_queue_release_action
from engine.runtime_config import list_latest_episodes, load_runtime_config, load_runtime_config_into_cfg, read_recent_metrics, save_runtime_config, summarize_hidden_reader_risk, write_system_status_snapshot
import json
import os
import tempfile


def test_information_asymmetry_promotes_reveal_structure():
    state = {}
    ensure_story_state(state, cfg={"project": {"genre_bucket": "B"}}, outline="배신 이후 진실 추적")
    info_before = information_prompt_payload(state)
    prepare_information_emotion(state, episode=3, event_plan={"type": "reveal"})
    info_after = information_prompt_payload(state)

    assert len(info_after["revealed_truths"]) >= 1
    assert info_after["dramatic_irony"] >= len(info_before["hidden_truths"]) - 1


def test_world_state_changes_after_major_event():
    state = {}
    ensure_story_state(state)
    before = dict(state["story_state_v2"]["world"])
    world = update_world_state(state, episode=7, event_plan={"type": "collapse"})

    assert world["change_rate"] >= before["change_rate"] + 2
    assert world["instability"] >= before["instability"] + 1


def test_reward_density_does_not_force_sustainability_collapse():
    state = {}
    ensure_story_state(state)
    update_reward_serialization(state, episode=4, event_plan={"type": "arrival"})
    result = update_reward_serialization(state, episode=5, event_plan={"type": "false_victory"})

    assert result["rewards"]["reward_density"] >= 4
    assert result["serialization"]["sustainability"] >= 4


def test_retention_accounts_for_chemistry_without_losing_balance():
    state = {}
    ensure_story_state(state)
    state["story_state_v2"]["relationships"]["protagonist:rival"]["chemistry"] = 9
    state["story_state_v2"]["relationships"]["protagonist:ally"]["chemistry"] = 8
    retention = build_retention_state(
        state,
        event_plan={"type": "betrayal"},
        cliffhanger_plan={"carryover_pressure": 8, "open_question": "누가 등을 돌렸는가"},
    )
    predicted = predict_retention(
        {"emotion_density": 0.7, "hook_score": 0.72, "escalation": 0.75},
        fatigue=0.15,
        retention_state=retention,
    )

    assert retention["chemistry_pressure"] >= 5
    assert predicted > 0.5


def test_regression_guard_rejects_single_axis_overoptimization():
    before = {
        "fun": 0.70,
        "coherence": 0.72,
        "character_persuasiveness": 0.71,
        "pacing": 0.69,
        "retention": 0.70,
        "emotional_payoff": 0.68,
        "long_run_sustainability": 0.72,
        "world_logic": 0.73,
        "chemistry": 0.67,
        "stability": 0.71,
    }
    after = dict(before)
    after["fun"] = 0.92
    after["long_run_sustainability"] = 0.55
    after["coherence"] = 0.60

    accepted, report = regression_decision(before, after)
    assert not accepted
    assert "long_run_sustainability" in report["dropped_axes"]


def test_multi_objective_scores_include_sustainability_and_world_logic():
    state = {}
    ensure_story_state(state)
    state["story_state_v2"]["world"]["instability"] = 3
    state["story_state_v2"]["serialization"]["sustainability"] = 8
    scores = build_multi_objective_scores(
        {
            "hook_score": 0.78,
            "escalation": 0.74,
            "emotion_density": 0.69,
            "coherence": 0.76,
            "world_logic": 0.8,
            "chemistry_score": 0.72,
            "repetition_score": 0.15,
        },
        retention_state={"unresolved_thread_pressure": 7, "curiosity_debt": 7},
        story_state=state["story_state_v2"],
        causal_report={"score": 0.8, "checks": {"world_consequence": 1.0, "goal_pressure": 1.0, "emotional_trace": 1.0, "cliffhanger_alignment": 1.0}},
    )

    assert scores["long_run_sustainability"] >= 0.7
    assert scores["world_logic"] >= 0.7


def test_scene_causality_distinguishes_linked_from_unlinked_scene():
    state = {}
    ensure_story_state(state, cfg={"project": {"genre_bucket": "B"}}, outline="왕좌를 되찾으려는 황자")
    coherent = validate_scene_causality(
        "황자는 조력자를 지키기 위해 의식을 포기했다. 그 대가로 진실이 드러났고 동맹은 흔들렸다. 결국 무너진 신뢰가 다음 선택을 더 위험하게 만들었다.",
        story_state=state["story_state_v2"],
        event_plan={"type": "sacrifice"},
        cliffhanger_plan={"open_question": "누가 먼저 대가를 회수할까", "target": "동맹"},
    )
    incoherent = validate_scene_causality(
        "황자는 걸었다. 하늘은 맑았다. 모두가 식사를 했다. 끝.",
        story_state=state["story_state_v2"],
        event_plan={"type": "sacrifice"},
        cliffhanger_plan={"open_question": "누가 먼저 대가를 회수할까", "target": "동맹"},
    )

    assert coherent["score"] > incoherent["score"]
    assert "causal_link" in incoherent["issues"]


def test_antagonist_plan_builds_long_horizon_pressure():
    state = {}
    ensure_story_state(state)
    state["story_state_v2"]["relationships"]["protagonist:ally"]["trust"] = 3
    plan = prepare_antagonist_plan(state, episode=8, event_plan={"type": "betrayal"})
    payload = antagonist_prompt_payload(state)

    assert plan["campaign_phase"] in {"positioning", "constriction", "domination", "collapse_harvest", "probing"}
    assert "불신" in payload["next_move"] or "주도권" in payload["next_move"] or "규칙" in payload["next_move"]
    assert len(payload["horizon_beats"]) == 3


def test_pattern_memory_pushes_exploration_when_event_is_overused():
    state = {}
    ensure_story_state(state)
    for episode in range(1, 4):
        update_pattern_memory(
            state,
            episode=episode,
            event_plan={"type": "betrayal"},
            cliffhanger_plan={"mode": "choice_lock"},
        )

    memory = state["story_state_v2"]["pattern_memory"]
    picked = choose_event_with_memory(state, preferred="betrayal", fallback="arrival")

    assert "betrayal" in memory["overused_events"]
    assert memory["exploration_bias"] >= 6
    assert picked != "betrayal"


def test_market_serialization_couples_paywall_pressure_and_reader_trust():
    state = {}
    cfg = {
        "project": {"platform": "KakaoPage", "genre_bucket": "A"},
        "novel": {"paywall_window": [20, 30], "early_focus_episodes": 5},
    }
    ensure_story_state(state, cfg=cfg)
    state["story_state_v2"]["rewards"]["reward_density"] = 6
    state["story_state_v2"]["rewards"]["expectation_alignment"] = 7
    bundle = update_market_serialization(state, episode=24, cfg=cfg, event_plan={"type": "arrival"})
    payload = market_prompt_payload(state)

    assert bundle["market"]["paywall_pressure"] >= 7
    assert payload["reader_trust"] >= 5
    assert bundle["serialization"]["market_fit"] >= 5


def test_market_serialization_ingests_business_feedback_pressure(tmp_path):
    state = {"out_dir": str(tmp_path / "outputs")}
    cfg = {
        "project": {"platform": "Munpia", "genre_bucket": "A"},
        "novel": {"paywall_window": [20, 30], "early_focus_episodes": 5},
    }
    os.makedirs(state["out_dir"], exist_ok=True)
    with open(os.path.join(state["out_dir"], "certification_report.json"), "w", encoding="utf-8") as handle:
        json.dump(
            {
                "market": {"ok": False, "stats": {"latest_top_percent": 8.4}},
                "business_feedback": {
                    "available": True,
                    "total_revenue": 300.0,
                    "total_campaign_spend": 280.0,
                    "best_campaign_roi": 0.05,
                },
                "failure_reason": "band_not_reached",
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )

    ensure_story_state(state, cfg=cfg)
    bundle = update_market_serialization(state, episode=12, cfg=cfg, event_plan={"type": "arrival"})
    payload = market_prompt_payload(state)

    assert bundle["market"]["market_feedback_active"] is True
    assert bundle["market"]["market_pressure"] >= 3
    assert bundle["market"]["reader_exit_risk"] >= 3
    assert payload["market_pressure"] >= 3


def test_causal_repair_plan_targets_critical_issues():
    state = {}
    ensure_story_state(state)
    report = {"issues": ["causal_link", "goal_pressure", "world_consequence"], "score": 0.4}
    repair = build_causal_repair_plan(
        report,
        story_state=state["story_state_v2"],
        event_plan={"type": "collapse"},
        cliffhanger_plan={"mode": "collapse_edge", "open_question": "무엇이 먼저 무너질까"},
    )
    store_causal_repair_plan(state, repair)
    payload = repair_prompt_payload(state)

    assert "causal_link" in payload["critical_issues"]
    assert payload["repair_confidence"] >= 4
    assert any("인과" in directive or "대가" in directive for directive in payload["directives"])


def test_causal_repair_cycle_runs_with_bounded_retries():
    state = {}
    ensure_story_state(state)
    initial_report = {"issues": ["causal_link", "goal_pressure", "world_consequence"], "score": 0.42}
    initial_plan = build_causal_repair_plan(
        initial_report,
        story_state=state["story_state_v2"],
        event_plan={"type": "collapse"},
        cliffhanger_plan={"mode": "collapse_edge", "open_question": "무엇이 먼저 무너질까"},
    )
    start_causal_repair_cycle(state, retry_budget=2, causal_report=initial_report, repair_plan=initial_plan)
    retry_report = {"issues": ["world_consequence"], "score": 0.73}
    retry_plan = build_causal_repair_plan(
        retry_report,
        story_state=state["story_state_v2"],
        event_plan={"type": "collapse"},
        cliffhanger_plan={"mode": "collapse_edge", "open_question": "무엇이 먼저 무너질까"},
    )
    record_causal_repair_attempt(state, attempt_index=1, causal_report=retry_report, repair_plan=retry_plan)
    final_report = {"issues": [], "score": 0.9}
    final_plan = build_causal_repair_plan(
        final_report,
        story_state=state["story_state_v2"],
        event_plan={"type": "collapse"},
        cliffhanger_plan={"mode": "collapse_edge", "open_question": "무엇이 먼저 무너질까"},
    )
    control = finalize_causal_repair_cycle(state, causal_report=final_report, repair_plan=final_plan)
    closure = assess_causal_closure(final_report, final_plan)

    assert control["retry_budget"] == 2
    assert control["attempts_used"] == 1
    assert control["status"] == "closed"
    assert closure["passed"]
    assert control["closure_score"] >= 0.85
    assert control["strategy_key"] in {"baseline", "causal_chain", "desire_alignment", "world_rule_feedback"}
    assert control["strategy_coverage"] >= 0.0


def test_causal_repair_specializes_strategy_after_failed_attempt():
    state = {}
    ensure_story_state(state)
    initial_report = {"issues": ["causal_link", "world_consequence"], "score": 0.38}
    initial_plan = build_causal_repair_plan(
        initial_report,
        story_state=state["story_state_v2"],
        event_plan={"type": "collapse"},
        cliffhanger_plan={"mode": "collapse_edge", "open_question": "무엇이 먼저 무너질까"},
    )
    start_causal_repair_cycle(state, retry_budget=2, causal_report=initial_report, repair_plan=initial_plan)
    second_plan = build_causal_repair_plan(
        initial_report,
        story_state=state["story_state_v2"],
        event_plan={"type": "collapse"},
        cliffhanger_plan={"mode": "collapse_edge", "open_question": "무엇이 먼저 무너질까"},
    )
    record_causal_repair_attempt(state, attempt_index=1, causal_report=initial_report, repair_plan=second_plan)

    assert second_plan["strategy_key"] != "baseline"
    assert second_plan["strategy_coverage"] > 0.0
    assert state["story_state_v2"]["control"]["causal_repair"]["next_strategy_shift"]


def test_repair_diff_audit_detects_unresolved_target_and_updates_effectiveness():
    state = {}
    ensure_story_state(state)
    initial_report = {"issues": ["causal_link", "world_consequence"], "score": 0.32}
    repair_plan = build_causal_repair_plan(
        initial_report,
        story_state=state["story_state_v2"],
        event_plan={"type": "collapse"},
        cliffhanger_plan={"mode": "collapse_edge", "open_question": "무엇이 먼저 무너질까"},
    )
    start_causal_repair_cycle(state, retry_budget=2, causal_report=initial_report, repair_plan=repair_plan)
    retry_report = {"issues": ["world_consequence"], "score": 0.69}
    record_causal_repair_attempt(state, attempt_index=1, causal_report=retry_report, repair_plan=repair_plan)
    audit = record_repair_diff_audit(
        state,
        attempt_index=1,
        pre_text="황자는 걸었다. 세계는 그대로였다.",
        post_text="황자는 결단했다. 그러나 세계의 규칙은 여전히 변하지 않았다.",
        pre_report=initial_report,
        post_report=retry_report,
        repair_plan=repair_plan,
    )

    assert audit["mismatch_type"] == "unresolved_target"
    assert audit["resolved_targets"] == ["causal_link"]
    assert state["story_state_v2"]["control"]["causal_repair"]["defect_resolution_score"] > 0.0
    assert state["story_state_v2"]["control"]["causal_repair"]["strategy_effectiveness"]
    assert "semantic_audit" in state["story_state_v2"]["control"]["causal_repair"]


def test_repair_diff_audit_detects_semantic_intent_loss_and_payoff_corruption():
    audit = audit_repair_diff(
        pre_text="황자는 조력자를 지키기 위해 금기를 어겼다. 그 대가로 세계의 규칙이 뒤틀렸고 둘의 신뢰는 무너졌다. 이제 약속했던 복수의 회수가 더 잔혹해졌다.",
        post_text="황자는 문밖을 걸었다. 도시는 조용했고 사람들은 식사했다. 그는 별다른 생각 없이 다음 장소로 갔다.",
        pre_report={"issues": ["causal_link", "world_consequence"], "score": 0.44},
        post_report={"issues": ["causal_link", "world_consequence"], "score": 0.41},
        repair_plan={"critical_issues": ["causal_link", "world_consequence"]},
    )

    semantic = audit["semantic_audit"]
    assert audit["mismatch_type"] == "unresolved_target"
    assert "intent_loss" in semantic["semantic_failure_types"]
    assert "payoff_corruption" in semantic["semantic_failure_types"]
    assert semantic["intent_preservation_score"] < 0.5


def test_multi_objective_scores_reflect_semantic_repair_quality():
    state = {}
    ensure_story_state(state)
    story_state = state["story_state_v2"]
    base_scores = {
        "hook_score": 0.78,
        "escalation": 0.74,
        "emotion_density": 0.69,
        "coherence": 0.76,
        "world_logic": 0.8,
        "chemistry_score": 0.72,
        "repetition_score": 0.15,
        "character_score": 0.71,
        "logic_score": 0.75,
        "pacing_score": 0.73,
        "payoff_score": 0.68,
    }
    retention = {"unresolved_thread_pressure": 7, "curiosity_debt": 7, "information_gap": 6}
    causal = {"score": 0.8, "checks": {"world_consequence": 1.0, "goal_pressure": 1.0, "emotional_trace": 1.0, "cliffhanger_alignment": 1.0}}
    story_state["control"]["causal_repair"]["semantic_audit"] = {
        "intent_preservation_score": 0.82,
        "semantic_failure_types": [],
        "semantic_repair_effectiveness": 0.79,
    }
    strong = build_multi_objective_scores(base_scores, retention_state=retention, story_state=story_state, causal_report=causal)
    story_state["control"]["causal_repair"]["semantic_audit"] = {
        "intent_preservation_score": 0.28,
        "semantic_failure_types": ["intent_loss", "payoff_corruption"],
        "semantic_repair_effectiveness": 0.22,
    }
    weak = build_multi_objective_scores(base_scores, retention_state=retention, story_state=story_state, causal_report=causal)

    assert strong["coherence"] > weak["coherence"]
    assert strong["character_persuasiveness"] > weak["character_persuasiveness"]
    assert strong["stability"] > weak["stability"]


def test_promise_graph_tracks_unresolved_promises_and_payoff_corruption():
    state = {}
    ensure_story_state(state)
    update_promise_payoff_graph(state, episode=1, event_plan={"type": "betrayal"}, score_obj={"payoff_score": 0.58, "hook_score": 0.72})
    update_promise_payoff_graph(state, episode=2, event_plan={"type": "loss"}, score_obj={"payoff_score": 0.56, "hook_score": 0.7})
    graph = update_promise_payoff_graph(state, episode=5, event_plan={"type": "misunderstanding"}, score_obj={"payoff_score": 0.41, "hook_score": 0.74})

    assert graph["unresolved_count"] >= 2
    assert graph["payoff_corruption_flags"]
    assert graph["payoff_integrity"] < 0.7


def test_character_specific_promise_graph_tracks_dependencies():
    state = {}
    ensure_story_state(state)
    graph = update_promise_payoff_graph(state, episode=1, event_plan={"type": "betrayal"}, score_obj={"payoff_score": 0.55, "hook_score": 0.72})

    assert graph["character_promises"]
    assert any(items for items in graph["character_promises"].values())
    assert graph["dependency_edges"]
    assert graph["weighted_dependency_graph"]


def test_multi_objective_scores_reflect_promise_resolution_quality():
    state = {}
    ensure_story_state(state)
    story_state = state["story_state_v2"]
    base_scores = {
        "hook_score": 0.78,
        "escalation": 0.74,
        "emotion_density": 0.69,
        "coherence": 0.76,
        "world_logic": 0.8,
        "chemistry_score": 0.72,
        "repetition_score": 0.15,
        "character_score": 0.71,
        "logic_score": 0.75,
        "pacing_score": 0.73,
        "payoff_score": 0.68,
    }
    retention = {"unresolved_thread_pressure": 7, "curiosity_debt": 7, "information_gap": 6}
    causal = {"score": 0.8, "checks": {"world_consequence": 1.0, "goal_pressure": 1.0, "emotional_trace": 1.0, "cliffhanger_alignment": 1.0}}
    story_state["promise_graph"] = {"unresolved_count": 1, "resolution_rate": 0.8, "payoff_integrity": 0.84, "payoff_corruption_flags": []}
    strong = build_multi_objective_scores(base_scores, retention_state=retention, story_state=story_state, causal_report=causal)
    story_state["promise_graph"] = {"unresolved_count": 4, "resolution_rate": 0.25, "payoff_integrity": 0.34, "payoff_corruption_flags": [{"type": "overdue_payoff"}]}
    weak = build_multi_objective_scores(base_scores, retention_state=retention, story_state=story_state, causal_report=causal)

    assert strong["emotional_payoff"] > weak["emotional_payoff"]
    assert strong["long_run_sustainability"] > weak["long_run_sustainability"]
    assert strong["retention"] > weak["retention"]


def test_repair_diff_audit_marks_resolved_when_targeted_defects_clear():
    audit = audit_repair_diff(
        pre_text="황자는 망설였다. 이유는 없다.",
        post_text="황자는 조력자를 지키기 위해 망설였고, 그 대가로 규칙이 흔들렸다.",
        pre_report={"issues": ["causal_link", "world_consequence"], "score": 0.35},
        post_report={"issues": [], "score": 0.88},
        repair_plan={"critical_issues": ["causal_link", "world_consequence"]},
    )

    assert audit["mismatch_type"] == "resolved"
    assert audit["defect_resolution_score"] >= 0.7


def test_portfolio_memory_tracks_crowded_and_winning_patterns():
    state = {}
    cfg = {"project": {"platform": "Munpia", "genre_bucket": "B"}}
    ensure_story_state(state, cfg=cfg)
    state["story_state_v2"]["market"]["reader_trust"] = 7
    state["story_state_v2"]["market"]["release_confidence"] = 6
    state["story_state_v2"]["serialization"]["market_fit"] = 7
    memory = update_portfolio_memory(
        state,
        cfg=cfg,
        event_plan={"type": "arrival"},
        portfolio_snapshot=[
            {"pattern": "betrayal", "crowding": 8},
            {"winning_pattern": "arrival", "heat": 8},
        ],
    )
    payload = portfolio_prompt_payload(state)

    assert "betrayal" in memory["crowded_patterns"]
    assert "arrival" in memory["winning_patterns"]
    assert payload["portfolio_fit"] >= 5


def test_portfolio_memory_penalizes_hidden_reader_risk():
    state = {}
    cfg = {"project": {"platform": "Munpia", "genre_bucket": "B"}}
    ensure_story_state(state, cfg=cfg)
    state["story_state_v2"]["market"]["reader_trust"] = 7
    state["story_state_v2"]["market"]["release_confidence"] = 6
    state["story_state_v2"]["serialization"]["market_fit"] = 7
    state["story_state_v2"]["control"]["reader_quality"].update(
        {
            "thinness_debt": 0.16,
            "deja_vu_debt": 0.12,
            "fake_urgency_debt": 0.11,
            "compression_debt": 0.08,
        }
    )

    memory = update_portfolio_memory(
        state,
        cfg=cfg,
        event_plan={"type": "arrival"},
        portfolio_snapshot=[
            {"pattern": "betrayal", "crowding": 3},
            {"winning_pattern": "arrival", "heat": 8},
        ],
    )
    payload = portfolio_prompt_payload(state)

    assert memory["hidden_reader_risk"] >= 0.47
    assert payload["hidden_reader_risk"] >= 0.47
    assert any("얇음, 기시감, 가짜 긴장감" in directive for directive in memory["policy_directives"])
    assert memory["design_guardrails"]
    assert payload["design_guardrails"]


def test_portfolio_memory_penalizes_hidden_reader_risk_trend_from_threshold_history():
    state = {}
    cfg = {"project": {"platform": "Munpia", "genre_bucket": "B"}}
    ensure_story_state(state, cfg=cfg)
    state["story_state_v2"]["control"]["final_threshold_history"]["hidden_reader_risk_trend"] = 0.71

    memory = update_portfolio_memory(
        state,
        cfg=cfg,
        event_plan={"type": "arrival"},
        portfolio_snapshot=[{"winning_pattern": "arrival", "heat": 8}],
    )

    assert memory["hidden_reader_risk"] >= 0.71
    assert memory["release_strategy"] == "staggered"
    assert any("홀드와 재배치" in directive for directive in memory["policy_directives"])
    assert any("release 간격" in directive for directive in memory["design_guardrails"])


def test_portfolio_memory_learns_from_real_metrics_logs():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        track_dir = os.path.join(tracks_root, "track_a")
        os.makedirs(os.path.join(track_dir, "outputs"), exist_ok=True)
        with open(os.path.join(track_dir, "track.json"), "w", encoding="utf-8") as f:
            json.dump({"project": {"platform": "Munpia", "genre_bucket": "B"}}, f)
        rows = [
            {
                "meta": {"event_plan": {"type": "betrayal"}},
                "content_ceiling": {"ceiling_total": 68},
                "retention": {"predicted_next_episode": 0.72},
                "scores": {"repetition_score": 0.12},
            },
            {
                "meta": {"event_plan": {"type": "betrayal"}},
                "content_ceiling": {"ceiling_total": 66},
                "retention": {"predicted_next_episode": 0.69},
                "scores": {"repetition_score": 0.11},
            },
        ]
        with open(os.path.join(track_dir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        with open(os.path.join(track_dir, "outputs", "final_threshold_eval.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "criteria": {
                        "reader_retention_stability": {
                            "details": {
                                "reader_quality_debt": {
                                    "thinness_debt": 0.11,
                                    "fake_urgency_debt": 0.08,
                                }
                            }
                        }
                    }
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        snapshot = learn_portfolio_snapshot(tracks_root)
        state = {}
        cfg = {"project": {"platform": "Munpia", "genre_bucket": "B"}}
        ensure_story_state(state, cfg=cfg)
        memory = update_portfolio_memory(state, cfg=cfg, tracks_root=tracks_root)

        assert snapshot
        assert snapshot[0]["winning_pattern"] == "betrayal"
        assert memory["learned_from_logs"] is True
        assert "betrayal" in memory["winning_patterns"]
        assert memory["hidden_reader_risk"] >= 0.0
        assert memory["coordination_health"] >= 1
        assert memory["policy_directives"]


def test_portfolio_signals_compute_cross_track_pressure():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        for name, platform, event_type in [("track_a", "Munpia", "betrayal"), ("track_b", "Munpia", "betrayal"), ("track_c", "KakaoPage", "arrival")]:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": platform, "genre_bucket": "B"}}, f)
            rows = [{"meta": {"event_plan": {"type": event_type}}, "content_ceiling": {"ceiling_total": 64}, "retention": {"predicted_next_episode": 0.61}, "scores": {"repetition_score": 0.21}} for _ in range(2)]
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row) + "\n")
        signals = compute_portfolio_signals(tracks_root)
        accepted, report = portfolio_signal_decision(
            {"pattern_crowding": 2, "shared_risk": 2, "novelty_debt": 2, "cadence_pressure": 2, "market_overlap": 2, "release_timing_interference": 2},
            signals,
        )

        assert signals["pattern_crowding"] >= 4
        assert signals["market_overlap"] >= 3
        assert not accepted
        assert "pattern_crowding" in report["regressed_signals"] or "shared_risk" in report["regressed_signals"]


def test_portfolio_prompt_payload_exposes_coordination_guards():
    state = {}
    ensure_story_state(state)
    state["story_state_v2"]["portfolio_memory"]["coordination_health"] = 7
    state["story_state_v2"]["portfolio_memory"]["novelty_guard"] = 8
    state["story_state_v2"]["portfolio_memory"]["cadence_guard"] = 6
    state["story_state_v2"]["portfolio_memory"]["release_guard"] = 5
    state["story_state_v2"]["portfolio_memory"]["policy_directives"] = ["차별화 유지"]

    payload = portfolio_prompt_payload(state)

    assert payload["coordination_health"] == 7
    assert payload["novelty_guard"] == 8
    assert payload["policy_directives"] == ["차별화 유지"]


def test_portfolio_orchestrator_uses_real_logs_for_boost_selection():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        fixtures = [
            ("track_a", "Munpia", "B", "A", 2.4, 78, 0.76, 0.10),
            ("track_b", "Munpia", "B", "A", 3.1, 74, 0.70, 0.27),
            ("track_c", "KakaoPage", "B", "A", 2.9, 69, 0.64, 0.12),
        ]
        for name, platform, bucket, grade, top_percent, ceiling_total, retention, repetition in fixtures:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": platform, "genre_bucket": bucket}}, f)
            with open(os.path.join(tdir, "outputs", "grade_state.json"), "w", encoding="utf-8") as f:
                json.dump({"grade": grade}, f)
            with open(os.path.join(tdir, "outputs", "certification_report.json"), "w", encoding="utf-8") as f:
                json.dump({"market": {"stats": {"latest_top_percent": top_percent}}}, f)
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for _ in range(3):
                    f.write(json.dumps({
                        "meta": {"event_plan": {"type": "betrayal"}},
                        "content_ceiling": {"ceiling_total": ceiling_total},
                        "retention": {"predicted_next_episode": retention},
                        "scores": {"repetition_score": repetition},
                    }) + "\n")
        result = rebalance_platform({"safe_mode": False, "portfolio": {"max_boost_per_platform": 1, "max_boost_per_platform_bucket": 1}}, tracks_root)
        boosted = []
        for name, *_ in fixtures:
            track = os.path.join(tracks_root, name, "track.json")
            with open(track, "r", encoding="utf-8") as f:
                if json.load(f).get("phase") == "BOOST":
                    boosted.append(name)

        assert result["ok"] is True
        assert "track_a" in boosted
        assert "track_b" not in boosted


def test_portfolio_runtime_snapshot_feeds_memory_learning():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        for name, retention, repetition in [("track_a", 0.76, 0.10), ("track_b", 0.71, 0.11)]:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": "Munpia", "genre_bucket": "B"}}, f)
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for _ in range(3):
                    f.write(json.dumps({
                        "meta": {"event_plan": {"type": "arrival"}},
                        "content_ceiling": {"ceiling_total": 75},
                        "retention": {"predicted_next_episode": retention},
                        "scores": {"repetition_score": repetition},
                    }) + "\n")
        snapshot = build_portfolio_runtime_snapshot(tracks_root)
        state = {}
        ensure_story_state(state, cfg={"project": {"platform": "Munpia", "genre_bucket": "B"}})
        memory = update_portfolio_memory(state, cfg={"project": {"platform": "Munpia", "genre_bucket": "B"}}, tracks_root=tracks_root)

        assert snapshot["boost_ready_tracks"] >= 2
        assert memory["coordination_health"] >= 6
        assert any("실로그상 성과" in directive for directive in memory["policy_directives"])


def test_portfolio_runtime_snapshot_penalizes_hidden_reader_risk_trend():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        tdir = os.path.join(tracks_root, "track_a")
        os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
        with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
            json.dump({"project": {"platform": "Munpia", "genre_bucket": "B"}}, f)
        with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
            for _ in range(3):
                f.write(json.dumps({
                    "meta": {"event_plan": {"type": "arrival"}},
                    "content_ceiling": {"ceiling_total": 78},
                    "retention": {"predicted_next_episode": 0.79},
                    "scores": {"repetition_score": 0.08},
                }) + "\n")
        with open(os.path.join(tdir, "outputs", "final_threshold_eval.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "criteria": {
                        "autonomous_convergence_trend": {
                            "details": {
                                "hidden_reader_risk_trend": 0.44,
                            }
                        }
                    }
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        snapshot = build_portfolio_runtime_snapshot(tracks_root)

        assert snapshot["tracks"][0]["hidden_reader_risk"] >= 0.44
        assert snapshot["boost_ready_tracks"] == 0


def test_cross_track_release_scheduler_staggers_platform_overlap():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        fixtures = [("track_a", "Munpia", 0.78, 0.10), ("track_b", "Munpia", 0.72, 0.12), ("track_c", "Munpia", 0.58, 0.27)]
        for name, platform, retention, repetition in fixtures:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": platform, "genre_bucket": "B"}}, f)
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for _ in range(3):
                    f.write(json.dumps({
                        "meta": {"event_plan": {"type": "arrival"}},
                        "content_ceiling": {"ceiling_total": 74},
                        "retention": {"predicted_next_episode": retention},
                        "scores": {"repetition_score": repetition},
                    }) + "\n")
        plan = build_cross_track_release_plan(tracks_root)
        actions = {item["track"]: item["action"] for item in plan["release_plan"]}
        state = {}
        ensure_story_state(state, cfg={"project": {"platform": "Munpia", "genre_bucket": "B"}})
        memory = update_portfolio_memory(state, cfg={"project": {"platform": "Munpia", "genre_bucket": "B"}}, tracks_root=tracks_root)

        assert actions["track_a"] == "accelerate"
        assert actions["track_c"] == "hold"
        assert plan["interference_pressure"] >= 4
        assert memory["release_strategy"] == "staggered"


def test_cross_track_release_holds_when_hidden_reader_risk_trend_is_high():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        tdir = os.path.join(tracks_root, "track_risk")
        os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
        with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
            json.dump({"project": {"platform": "Munpia", "genre_bucket": "B"}}, f)
        with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
            for _ in range(3):
                f.write(json.dumps({
                    "retention": {"predicted_next_episode": 0.81},
                    "scores": {"repetition_score": 0.09},
                    "episode_attribution": {"fatigue_signal": 0.08, "retention_signal": 0.82, "payoff_signal": 0.78},
                }) + "\n")
        with open(os.path.join(tdir, "outputs", "final_threshold_eval.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "criteria": {
                        "autonomous_convergence_trend": {
                            "details": {
                                "hidden_reader_risk_trend": 0.44,
                            }
                        }
                    }
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        plan = build_cross_track_release_plan(tracks_root)

        assert plan["release_plan"][0]["action"] == "hold"
        assert plan["release_plan"][0]["hidden_reader_risk"] >= 0.44
        assert any("얇음/반복 피로 추세" in directive for directive in plan["policy_directives"])


def test_platform_release_policy_respects_slot_pressure():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        fixtures = [
            ("track_a", "KakaoPage", 0.79, 0.10),
            ("track_b", "KakaoPage", 0.78, 0.11),
            ("track_c", "KakaoPage", 0.62, 0.25),
        ]
        for name, platform, retention, repetition in fixtures:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": platform, "genre_bucket": "A"}}, f)
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for _ in range(3):
                    f.write(json.dumps({
                        "meta": {"event_plan": {"type": "arrival"}},
                        "content_ceiling": {"ceiling_total": 77},
                        "retention": {"predicted_next_episode": retention},
                        "scores": {"repetition_score": repetition},
                    }) + "\n")
        plan = build_cross_track_release_plan(tracks_root)
        actions = {item["track"]: item["action"] for item in plan["release_plan"]}
        state = {}
        ensure_story_state(state, cfg={"project": {"platform": "KakaoPage", "genre_bucket": "A"}})
        memory = update_portfolio_memory(state, cfg={"project": {"platform": "KakaoPage", "genre_bucket": "A"}}, tracks_root=tracks_root)
        accepted, report = release_policy_decision({"platform_slot_pressure": 2, "release_guard": 5}, {"platform_slot_pressure": memory["platform_slot_pressure"], "release_guard": memory["release_guard"]})

        assert actions["track_a"] in {"accelerate", "stagger"}
        assert actions["track_b"] in {"accelerate", "stagger"}
        assert actions["track_c"] == "hold"
        assert memory["platform_slot_pressure"] >= 1
        assert any("KakaoPage" in directive for directive in memory["slot_policy_directives"])
        assert accepted
        assert not report["regressed_signals"]


def test_release_runtime_schedule_changes_queue_behavior():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        for name, retention, repetition in [("track_a", 0.78, 0.10), ("track_b", 0.72, 0.12), ("track_c", 0.58, 0.27)]:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": "Munpia", "genre_bucket": "B"}}, f)
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for _ in range(3):
                    f.write(json.dumps({
                        "meta": {"event_plan": {"type": "arrival"}},
                        "content_ceiling": {"ceiling_total": 74},
                        "retention": {"predicted_next_episode": retention},
                        "scores": {"repetition_score": repetition},
                    }) + "\n")
        queue_state = {"status": "running", "track_dirs": [os.path.join(tracks_root, name) for name in ["track_a", "track_b", "track_c"]], "current_index": 0}
        queue_state = refresh_queue_release_runtime(queue_state, tracks_root)
        accelerate = resolve_queue_release_action(queue_state, os.path.join(tracks_root, "track_a"))
        hold = resolve_queue_release_action(queue_state, os.path.join(tracks_root, "track_c"))
        accelerate_outcome = apply_queue_release_outcome(queue_state, os.path.join(tracks_root, "track_a"), executed=True)
        hold_outcome = apply_queue_release_outcome(queue_state, os.path.join(tracks_root, "track_c"), executed=False)

        assert accelerate["action"] == "accelerate"
        assert not accelerate_outcome["should_advance"]
        assert hold["action"] == "hold"
        assert hold_outcome["should_advance"]
        hidden_summary = queue_state["release_runtime_meta"]["hidden_reader_risk_summary"]
        assert hidden_summary["track_count"] == 0
        assert hidden_summary["max"] == 0.0


def test_release_runtime_meta_carries_hidden_reader_risk_summary():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        tdir = os.path.join(tracks_root, "track_alpha")
        os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
        with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
            json.dump({"project": {"platform": "Munpia", "genre_bucket": "B"}}, f)
        with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"retention": {"predicted_next_episode": 0.61}, "scores": {"repetition_score": 0.18}}) + "\n")
        with open(os.path.join(tdir, "outputs", "final_threshold_eval.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "criteria": {
                        "reader_retention_stability": {
                            "details": {
                                "reader_quality_debt": {
                                    "thinness_debt": 0.24,
                                    "deja_vu_debt": 0.12,
                                }
                            }
                        },
                        "serialization_fatigue_control": {
                            "details": {
                                "reader_quality_debt": {
                                    "fake_urgency_debt": 0.09,
                                }
                            }
                        },
                        "autonomous_convergence_trend": {
                            "details": {
                                "hidden_reader_risk_trend": 0.08,
                            }
                        },
                    }
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        queue_state = refresh_queue_release_runtime({"status": "running", "track_dirs": [tdir], "current_index": 0}, tracks_root)

        hidden_summary = queue_state["release_runtime_meta"]["hidden_reader_risk_summary"]
        assert hidden_summary["track_count"] == 1
        assert hidden_summary["max"] >= 0.42
        assert hidden_summary["top_tracks"][0]["track"] == "track_alpha"
        assert hidden_summary["top_tracks"][0]["action"] == "hold"


def test_runtime_release_alignment_updates_story_state():
    state = {}
    ensure_story_state(state)
    runtime = apply_runtime_release_to_state(state, {"action": "accelerate", "alignment": 0.9, "slot_offset": 0, "hold_budget": 0, "accelerate_budget": 1})

    assert runtime["action"] == "accelerate"
    assert state["story_state_v2"]["portfolio_memory"]["release_strategy"] == "focused"
    assert state["story_state_v2"]["portfolio_memory"]["release_guard"] >= 6


def test_runtime_release_outcome_learning_updates_story_state_memory():
    state = {}
    ensure_story_state(state)
    learning = learn_runtime_release_outcome_in_state(
        state,
        {
            "action": "accelerate",
            "alignment": 0.88,
            "slot_offset": 0,
            "success_signal": 0.84,
            "retention_signal": 0.82,
            "pacing_signal": 0.76,
            "trust_signal": 0.8,
            "fatigue_signal": 0.12,
            "coordination_signal": 0.78,
            "strong_window": 1.0,
        },
    )

    memory = state["story_state_v2"]["portfolio_memory"]
    assert learning["observed"] == 1
    assert memory["runtime_release_learning"]["action_scores"]["accelerate"] > 0.5
    assert memory["runtime_outcome_memory"]["retention_signal"] >= 0.8
    assert state["story_state_v2"]["control"]["runtime_release"]["outcome_history"]


def test_episode_attribution_records_episode_level_signals():
    state = {}
    ensure_story_state(state)
    state["story_state_v2"]["promise_graph"] = {"unresolved_count": 1, "resolution_rate": 0.7, "payoff_integrity": 0.78, "payoff_corruption_flags": []}
    attribution = record_episode_attribution(
        state,
        episode=4,
        episode_text="황자는 금기를 어겼고 그 대가로 세계가 흔들렸다. 조력자는 숨을 삼켰다. 이제 누가 먼저 대가를 회수할 것인가.",
        event_plan={"type": "sacrifice"},
        cliffhanger_plan={"open_question": "누가 먼저 대가를 회수할 것인가"},
        score_obj={"hook_score": 0.77, "pacing_score": 0.72, "repetition_score": 0.14, "payoff_score": 0.74},
        retention_state={"unresolved_thread_pressure": 7, "payoff_debt": 3},
        content_ceiling={"ceiling_total": 76},
    )

    assert attribution["episode"] == 4
    assert attribution["retention_signal"] > 0.6
    assert state["story_state_v2"]["control"]["episode_attribution"]["latest"]["episode"] == 4
    assert state["story_state_v2"]["portfolio_memory"]["episode_attribution_memory"]["observed"] == 1
    assert state["story_state_v2"]["control"]["episode_attribution"]["latest"]["fine_grained"]["scene_units"]
    reader_quality = state["story_state_v2"]["control"]["reader_quality"]
    assert reader_quality["hook_debt"] >= 0.0
    assert reader_quality["payoff_debt"] >= 0.0
    assert reader_quality["fatigue_debt"] >= 0.0
    assert reader_quality["thinness_debt"] >= 0.0
    assert reader_quality["repetition_debt"] >= 0.0
    assert reader_quality["deja_vu_debt"] >= 0.0
    assert reader_quality["fake_urgency_debt"] >= 0.0
    assert reader_quality["compression_debt"] >= 0.0
    assert reader_quality["history"][-1]["episode"] == 4


def test_fine_grained_causal_attribution_picks_top_scene():
    attribution = build_scene_event_attribution(
        "황자는 조력자를 지키기 위해 금기를 어겼다. 그 대가로 세계의 규칙이 흔들렸고 모두가 숨을 삼켰다. 그러나 마지막 질문은 누가 먼저 복수할 것인가였다.",
        event_plan={"type": "sacrifice"},
        cliffhanger_plan={"open_question": "누가 먼저 복수할 것인가"},
    )

    assert attribution["scene_count"] >= 3
    assert attribution["top_scene_index"] >= 1
    assert attribution["scene_signal"] > 0.3
    assert attribution["event_chain_links"]
    assert attribution["event_chain_strength"] > 0.0


def test_episode_attribution_can_refine_release_allocator_from_logs():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        fixtures = [
            ("track_a", 0.72, 0.11, {"retention_signal": 0.84, "pacing_signal": 0.76, "fatigue_signal": 0.1, "payoff_signal": 0.82}),
            ("track_b", 0.74, 0.11, {"retention_signal": 0.62, "pacing_signal": 0.68, "fatigue_signal": 0.22, "payoff_signal": 0.55}),
        ]
        for name, retention, repetition, attribution in fixtures:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": "Munpia", "genre_bucket": "B"}}, f)
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for episode in range(1, 4):
                    f.write(json.dumps({
                        "episode": episode,
                        "meta": {"event_plan": {"type": "arrival"}},
                        "content_ceiling": {"ceiling_total": 73},
                        "retention": {"predicted_next_episode": retention},
                        "scores": {"repetition_score": repetition},
                        "episode_attribution": dict(attribution, episode=episode),
                    }) + "\n")
        plan = build_cross_track_release_plan(tracks_root)
        slot0 = next(item for item in plan["release_plan"] if item["slot_offset"] == 0)

        assert slot0["track"] == "track_a"
        assert slot0["episode_learning"]["retention_signal"] > plan["release_plan"][1]["episode_learning"]["retention_signal"]


def test_runtime_release_learning_snapshot_reads_real_outcome_logs():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        track_dir = os.path.join(tracks_root, "track_a")
        os.makedirs(os.path.join(track_dir, "outputs"), exist_ok=True)
        with open(os.path.join(track_dir, "track.json"), "w", encoding="utf-8") as f:
            json.dump({"project": {"platform": "Munpia", "genre_bucket": "B"}}, f)
        with open(os.path.join(track_dir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
            for row in [
                {"runtime_outcome": {"success_signal": 0.82, "retention_signal": 0.8, "pacing_signal": 0.76, "trust_signal": 0.78, "fatigue_signal": 0.11, "coordination_signal": 0.74, "strong_window": 1.0}},
                {"runtime_outcome": {"success_signal": 0.76, "retention_signal": 0.74, "pacing_signal": 0.72, "trust_signal": 0.73, "fatigue_signal": 0.09, "coordination_signal": 0.71, "strong_window": 0.0}},
            ]:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        snapshot = build_runtime_release_learning_snapshot(tracks_root)
        assert snapshot["track_outcomes"]["track_a"]["observed"] == 2
        assert snapshot["platform_outcomes"]["Munpia"]["success"] >= 0.75


def test_adaptive_slot_allocator_uses_outcomes_and_prevents_monopoly():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        fixtures = [
            ("track_a", 0.78, 0.10, [{"success_signal": 0.9, "retention_signal": 0.86, "pacing_signal": 0.77, "trust_signal": 0.82, "fatigue_signal": 0.10, "coordination_signal": 0.75, "strong_window": 1.0} for _ in range(3)]),
            ("track_b", 0.75, 0.09, [{"success_signal": 0.83, "retention_signal": 0.81, "pacing_signal": 0.75, "trust_signal": 0.8, "fatigue_signal": 0.08, "coordination_signal": 0.78, "strong_window": 0.0} for _ in range(2)]),
            ("track_c", 0.61, 0.26, [{"success_signal": 0.52, "retention_signal": 0.49, "pacing_signal": 0.66, "trust_signal": 0.58, "fatigue_signal": 0.24, "coordination_signal": 0.62, "strong_window": 0.0}]),
        ]
        for name, retention, repetition, outcomes in fixtures:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": "KakaoPage", "genre_bucket": "A"}}, f)
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for _ in range(3):
                    f.write(json.dumps({
                        "meta": {"event_plan": {"type": "arrival"}},
                        "content_ceiling": {"ceiling_total": 76},
                        "retention": {"predicted_next_episode": retention},
                        "scores": {"repetition_score": repetition},
                    }) + "\n")
                for outcome in outcomes:
                    f.write(json.dumps({"runtime_outcome": outcome}, ensure_ascii=False) + "\n")
        plan = build_cross_track_release_plan(tracks_root)
        actions = {item["track"]: item["action"] for item in plan["release_plan"]}
        slot0 = next(item for item in plan["release_plan"] if item["slot_offset"] == 0)

        assert actions["track_a"] in {"stagger", "hold"}
        assert actions["track_b"] in {"accelerate", "stagger"}
        assert actions["track_c"] == "hold"
        assert slot0["track"] == "track_b"


def test_multi_window_reservation_allocator_spreads_strong_tracks_across_windows():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        fixtures = [
            ("track_a", 0.79, 0.10, 3.0, {"retention_signal": 0.83, "pacing_signal": 0.74, "fatigue_signal": 0.10, "payoff_signal": 0.81}),
            ("track_b", 0.78, 0.10, 0.0, {"retention_signal": 0.82, "pacing_signal": 0.75, "fatigue_signal": 0.09, "payoff_signal": 0.79}),
            ("track_c", 0.73, 0.11, 0.0, {"retention_signal": 0.73, "pacing_signal": 0.72, "fatigue_signal": 0.10, "payoff_signal": 0.71}),
        ]
        for name, retention, repetition, window_wins, attribution in fixtures:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": "KakaoPage", "genre_bucket": "A"}}, f)
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for episode in range(1, 4):
                    f.write(json.dumps({
                        "episode": episode,
                        "meta": {"event_plan": {"type": "arrival"}},
                        "content_ceiling": {"ceiling_total": 77},
                        "retention": {"predicted_next_episode": retention},
                        "scores": {"repetition_score": repetition},
                        "episode_attribution": dict(attribution, episode=episode),
                        "runtime_outcome": {"success_signal": 0.84, "retention_signal": 0.81, "pacing_signal": 0.74, "trust_signal": 0.79, "fatigue_signal": 0.1, "coordination_signal": 0.76, "strong_window": 1.0 if episode <= window_wins else 0.0},
                    }) + "\n")
        plan = build_cross_track_release_plan(tracks_root)
        reservations = {item["track"]: item["window"] for item in plan["window_reservations"]}

        assert reservations["track_a"] >= 1
        assert reservations["track_b"] == 0
        assert len(plan["window_reservations"]) == 3
        assert plan["long_horizon_pressure"]["KakaoPage"] >= 1


def test_long_horizon_allocator_uses_seasonality_bias():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        for name, platform, retention in [("track_a", "KakaoPage", 0.76), ("track_b", "KakaoPage", 0.74)]:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": platform, "genre_bucket": "A"}}, f)
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for episode in range(1, 4):
                    f.write(json.dumps({
                        "episode": episode,
                        "meta": {"event_plan": {"type": "arrival"}},
                        "content_ceiling": {"ceiling_total": 75},
                        "retention": {"predicted_next_episode": retention},
                        "scores": {"repetition_score": 0.1},
                        "episode_attribution": {"episode": episode, "retention_signal": 0.78, "pacing_signal": 0.74, "fatigue_signal": 0.1, "payoff_signal": 0.77, "fine_grained": {"scene_signal": 0.6}},
                    }) + "\n")
        plan = build_cross_track_release_plan(tracks_root)
        windows = [item["window"] for item in plan["window_reservations"]]

        assert all(0 <= window <= 5 for window in windows)
        assert min(windows) <= 1


def test_external_market_rhythm_couples_into_release_allocation():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        os.makedirs(tracks_root, exist_ok=True)
        fixtures = [
            ("track_a", {"top_percent": 3.0, "slope": -0.08, "event_flag": True}),
            ("track_b", {"top_percent": 11.0, "slope": 0.22, "event_flag": False}),
        ]
        for name, external in fixtures:
            tdir = os.path.join(tracks_root, name)
            os.makedirs(os.path.join(tdir, "outputs"), exist_ok=True)
            with open(os.path.join(tdir, "track.json"), "w", encoding="utf-8") as f:
                json.dump({"project": {"platform": "Munpia", "genre_bucket": "B"}}, f)
            with open(os.path.join(tdir, "outputs", "metrics.jsonl"), "w", encoding="utf-8") as f:
                for episode in range(1, 4):
                    f.write(json.dumps({
                        "episode": episode,
                        "meta": {"event_plan": {"type": "arrival"}},
                        "content_ceiling": {"ceiling_total": 74},
                        "retention": {"predicted_next_episode": 0.72},
                        "scores": {"repetition_score": 0.11},
                        "external": external,
                        "episode_attribution": {"episode": episode, "retention_signal": 0.76, "pacing_signal": 0.74, "fatigue_signal": 0.1, "payoff_signal": 0.75, "fine_grained": {"scene_signal": 0.6, "event_chain_strength": 0.42}},
                    }) + "\n")
        plan = build_cross_track_release_plan(tracks_root)
        release = {item["track"]: item for item in plan["release_plan"]}

        assert release["track_a"]["market_rhythm"]["rhythm_score"] > release["track_b"]["market_rhythm"]["rhythm_score"]
        assert release["track_a"]["adaptive_score"] > release["track_b"]["adaptive_score"]


def test_long_run_simulation_reports_30_60_120_episode_runs():
    state = {}
    ensure_story_state(state)
    story_state = state["story_state_v2"]
    story_state["portfolio_memory"]["release_guard"] = 7
    story_state["portfolio_memory"]["coordination_health"] = 7
    story_state["promise_graph"]["payoff_integrity"] = 0.82
    story_state["control"]["causal_repair"]["closure_score"] = 0.78
    result = simulate_long_run(
        {
            "fun": 0.76,
            "coherence": 0.84,
            "character_persuasiveness": 0.82,
            "pacing": 0.81,
            "retention": 0.83,
            "emotional_immersion": 0.79,
            "information_design": 0.78,
            "emotional_payoff": 0.8,
            "long_run_sustainability": 0.82,
            "world_logic": 0.81,
            "chemistry": 0.77,
            "stability": 0.84,
        },
        story_state,
    )

    assert set(result["runs"].keys()) == {"30", "60", "120"}
    assert result["runs"]["120"]["episodes"] == 120
    assert result["runs"]["30"]["mean_balanced_total"] > 0.0
    assert result["runs"]["30"]["heavy_reader_signal_mean"] > 0.0
    assert result["runs"]["30"]["heavy_reader_signal_floor"] > 0.0


def test_system_status_records_iteration_history_and_portfolio_signals():
    state = {}
    ensure_story_state(state)
    status = update_system_status(
        state,
        episode=3,
        objective_scores={
            "fun": 0.76,
            "coherence": 0.84,
            "character_persuasiveness": 0.82,
            "pacing": 0.81,
            "retention": 0.83,
            "emotional_immersion": 0.79,
            "information_design": 0.78,
            "emotional_payoff": 0.8,
            "long_run_sustainability": 0.82,
            "world_logic": 0.81,
            "chemistry": 0.77,
            "stability": 0.84,
        },
        portfolio_signals={"release_guard": 7, "coordination_health": 6},
    )

    assert status["balanced_total_history"]
    assert status["axis_history"]["fun"]
    assert status["repair_rate_history"]
    assert status["portfolio_signal_history"][-1]["episode"] == 3


def test_record_soak_history_accumulates_stability_signal():
    state = {}
    ensure_story_state(state)
    state["story_state_v2"]["control"]["reader_quality"] = {
        "thinness_debt": 0.34,
        "repetition_debt": 0.26,
        "deja_vu_debt": 0.18,
        "fake_urgency_debt": 0.12,
        "compression_debt": 0.14,
    }

    first = record_soak_history(
        state,
        episode=1,
        soak_report={"tested": True, "steady_noop_ratio": 0.74, "dominant_mode": "steady"},
        quality_lift_if_human_intervenes=0.08,
        objective_scores={"fun": 0.78, "retention": 0.8, "pacing": 0.74, "long_run_sustainability": 0.76},
    )
    second = record_soak_history(
        state,
        episode=2,
        soak_report={"tested": True, "steady_noop_ratio": 0.82, "dominant_mode": "steady"},
        quality_lift_if_human_intervenes=0.05,
        objective_scores={"fun": 0.82, "retention": 0.84, "pacing": 0.79, "long_run_sustainability": 0.8},
    )

    assert first["observed"] == 1
    assert second["observed"] == 2
    assert second["steady_noop_ratio"] >= 0.74
    assert second["quality_lift_trend"] <= 0.08
    assert second["hidden_reader_risk_trend"] > 0.0
    assert second["heavy_reader_signal_trend"] > 0.0
    assert second["history"][-1]["hidden_reader_risk"] > 0.0
    assert second["history"][-1]["heavy_reader_signal"] > 0.0
    assert state["story_state_v2"]["control"]["soak_history"]["history"][-1]["episode"] == 2


def test_summarize_soak_report_includes_heavy_reader_signal_floor():
    simulation = {
        "runs": {
            "30": {
                "drift": {"drift_detected": False},
                "repair_rate_mean": 0.81,
                "min_balanced_total": 0.74,
                "heavy_reader_signal_floor": 0.73,
                "heavy_reader_signal_drift": {"drift_detected": False},
            },
            "60": {
                "drift": {"drift_detected": False},
                "repair_rate_mean": 0.79,
                "min_balanced_total": 0.72,
                "heavy_reader_signal_floor": 0.71,
                "heavy_reader_signal_drift": {"drift_detected": False},
            },
        }
    }

    report = summarize_soak_report(simulation)

    assert report["tested"] is True
    assert report["heavy_reader_signal_floor_mean"] >= 0.72
    assert report["heavy_reader_drift_free_run_ratio"] == 1.0


def test_reward_and_character_updates_accumulate_arc_pressure():
    state = {}
    ensure_story_state(state)

    update_character_arc(state, episode=5, score_obj={"hook_score": 0.55, "escalation": 0.52}, event_plan={"type": "loss"})
    update_reward_serialization(
        state,
        episode=5,
        event_plan={"type": "misunderstanding"},
        score_obj={"payoff_score": 0.4, "hook_score": 0.7},
    )

    arc_pressure = state["story_state_v2"]["control"]["arc_pressure"]
    assert arc_pressure["momentum_debt"] > 0
    assert arc_pressure["payoff_debt"] >= 0
    assert arc_pressure["history"][-1]["episode"] == 5


def test_quality_drift_detection_triggers_warning_and_rollback_signal():
    warning = detect_quality_drift([0.83, 0.832, 0.831, 0.805, 0.799, 0.792], lookback=3)
    severe = detect_quality_drift([0.85, 0.848, 0.847, 0.79, 0.782, 0.776], lookback=3)

    assert warning["warning"]
    assert severe["rollback_signal"]


def test_axis_drift_detection_flags_protected_axis_erosion():
    result = detect_axis_drift(
        {
            "fun": [0.82, 0.821, 0.819, 0.817, 0.816, 0.814],
            "coherence": [0.84, 0.842, 0.841, 0.78, 0.776, 0.772],
        },
        lookback=3,
    )

    assert "coherence" in result["drifted_axes"]
    assert "fun" not in result["drifted_axes"]


def test_runtime_config_roundtrip_and_pipeline_override_are_deterministic():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "runtime_config.json")
        save_runtime_config(
            {
                "generation_enabled": False,
                "track_count": 4,
                "release_cadence": {"mode": "queue_loop", "steps_per_run": 2},
                "portfolio": {"mode": "focused"},
                "evaluation": {
                    "max_revision_passes": 3,
                    "causal_repair_retry_budget": 3,
                    "viral_required": False,
                },
            },
            path=path,
        )
        loaded = load_runtime_config(path)
        merged, runtime_cfg = load_runtime_config_into_cfg(
            {
                "limits": {"max_revision_passes": 1, "causal_repair_retry_budget": 1},
                "quality": {"viral_required": True},
                "portfolio": {"mode": "balanced"},
            },
            path=path,
        )

        assert loaded["track_count"] == 4
        assert runtime_cfg["generation_enabled"] is False
        assert merged["limits"]["max_revision_passes"] == 3
        assert merged["limits"]["causal_repair_retry_budget"] == 3
        assert merged["quality"]["viral_required"] is False
        assert merged["portfolio"]["mode"] == "focused"


def test_system_status_snapshot_writes_global_and_local_outputs():
    with tempfile.TemporaryDirectory() as tmpdir:
        global_path = os.path.join(tmpdir, "outputs", "system_status.json")
        local_out_dir = os.path.join(tmpdir, "tracks", "alpha", "outputs")
        final_path = os.path.join(local_out_dir, "final_threshold_eval.json")
        os.makedirs(local_out_dir, exist_ok=True)
        with open(final_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "criteria": {
                        "autonomous_convergence_trend": {
                            "details": {
                                "hidden_reader_risk_trend": 0.38,
                            }
                        }
                    }
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        payload = write_system_status_snapshot(
            {"iteration_state": "running", "balanced_total_history": [0.82, 0.83]},
            runtime_cfg={"generation_enabled": True, "track_count": 3},
            path=global_path,
            out_dir=local_out_dir,
            tracks_root=os.path.join(tmpdir, "tracks"),
        )

        assert payload["system_status"]["iteration_state"] == "running"
        assert payload["hidden_reader_risk_summary"]["critical_tracks"] == 1
        assert os.path.exists(global_path)
        assert os.path.exists(os.path.join(local_out_dir, "system_status.json"))


def test_runtime_dashboard_helpers_read_metrics_and_latest_episodes():
    with tempfile.TemporaryDirectory() as tmpdir:
        tracks_root = os.path.join(tmpdir, "tracks")
        output_dir = os.path.join(tracks_root, "track_a", "outputs")
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "episode_001.txt"), "w", encoding="utf-8") as f:
            f.write("첫 번째 에피소드\n\n[META]\n{}")
        with open(os.path.join(output_dir, "metrics.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"episode": 1, "system_status": {"iteration_state": "running"}}) + "\n")
            f.write(json.dumps({"episode": 2, "system_status": {"iteration_state": "running"}}) + "\n")
        with open(os.path.join(output_dir, "final_threshold_eval.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "final_threshold_ready": False,
                    "failed_bundles": ["operations_capability"],
                    "criteria": {
                        "autonomous_convergence_trend": {
                            "details": {
                                "hidden_reader_risk_trend": 0.41,
                                "heavy_reader_signal_trend": 0.63,
                            }
                        }
                    },
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        latest = list_latest_episodes(tracks_root=tracks_root, limit=3)
        metrics = read_recent_metrics(os.path.join(output_dir, "metrics.jsonl"), limit=1)
        hidden_risk_summary = summarize_hidden_reader_risk(tracks_root=tracks_root, limit=3)

        assert latest
        assert latest[0]["name"] == "episode_001.txt"
        assert metrics[0]["episode"] == 2
        assert hidden_risk_summary["critical_tracks"] == 1
        assert hidden_risk_summary["weak_signal_tracks"] == 1
        assert hidden_risk_summary["tracks"][0]["hidden_reader_risk_trend"] == 0.41
        assert hidden_risk_summary["tracks"][0]["heavy_reader_signal_trend"] == 0.63
