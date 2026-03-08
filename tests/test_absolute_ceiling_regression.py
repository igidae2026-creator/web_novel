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
    repair_prompt_payload,
    start_causal_repair_cycle,
    store_causal_repair_plan,
)
from engine.portfolio_memory import learn_portfolio_snapshot, update_portfolio_memory, portfolio_prompt_payload
from engine.portfolio_signals import compute_portfolio_signals
from engine.regression_guard import portfolio_signal_decision
from engine.portfolio_orchestrator import build_portfolio_runtime_snapshot, rebalance_platform
from engine.cross_track_release import build_cross_track_release_plan
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

        snapshot = learn_portfolio_snapshot(tracks_root)
        state = {}
        cfg = {"project": {"platform": "Munpia", "genre_bucket": "B"}}
        ensure_story_state(state, cfg=cfg)
        memory = update_portfolio_memory(state, cfg=cfg, tracks_root=tracks_root)

        assert snapshot
        assert snapshot[0]["winning_pattern"] == "betrayal"
        assert memory["learned_from_logs"] is True
        assert "betrayal" in memory["winning_patterns"]
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
