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
from engine.causal_repair import build_causal_repair_plan, store_causal_repair_plan, repair_prompt_payload


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
