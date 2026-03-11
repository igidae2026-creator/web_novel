from analytics.content_ceiling import evaluate_episode
from engine.quality_gate import quality_gate_report
from engine.scene_causality import validate_scene_causality
from engine.story_state import ensure_story_state


def test_top_tier_perception_stack_prefers_hooked_coherent_episode():
    state = {}
    ensure_story_state(state, cfg={"project": {"genre_bucket": "A"}}, outline="몰락한 천재 검사가 배신의 밤 이후 제국을 되찾는다")
    story_state = state["story_state_v2"]

    strong_text = (
        "황자는 무너진 제단 앞에서 숨을 삼켰다. 스승을 살리려면 왕가의 인장을 포기해야 했다. "
        "그는 망설였지만 결국 인장을 깨뜨렸고, 그 대가로 봉인된 진실이 드러났다. "
        "등을 맡겼던 동맹은 그 순간 칼끝을 거두지 못했고 신뢰는 갈라졌다. "
        "무너진 규칙 탓에 제국의 질서가 흔들리자, 황자는 복수를 미루고 사람들을 살릴지 왕좌를 향해 돌진할지 선택해야 했다. "
        "하지만 마지막 문이 열리며, 배신자가 누구의 명령을 받았는지가 밝혀지기 직전 모든 불빛이 꺼졌다. "
        "이제 먼저 대가를 치를 사람은 누구일까."
    )
    weak_text = "황자는 걸었다. 하늘은 맑았다. 사람들은 밥을 먹었다. 별일은 없었다. 끝."

    strong_causal = validate_scene_causality(
        strong_text,
        story_state=story_state,
        event_plan={"type": "betrayal"},
        cliffhanger_plan={"open_question": "이제 먼저 대가를 치를 사람은 누구일까", "target": "동맹"},
    )
    weak_causal = validate_scene_causality(
        weak_text,
        story_state=story_state,
        event_plan={"type": "betrayal"},
        cliffhanger_plan={"open_question": "이제 먼저 대가를 치를 사람은 누구일까", "target": "동맹"},
    )

    strong_ceiling = evaluate_episode(
        strong_text,
        {
            "genre_bucket": "A",
            "platform": "KakaoPage",
            "retention": {"unresolved_thread_pressure": 8, "curiosity_debt": 8},
            "tension": {"target_tension": 8},
            "story_state": story_state,
            "multi_objective": {
                "fun": 0.8,
                "coherence": 0.82,
                "character_persuasiveness": 0.8,
                "pacing": 0.77,
                "retention": 0.83,
                "emotional_immersion": 0.8,
                "information_design": 0.78,
                "emotional_payoff": 0.79,
                "long_run_sustainability": 0.76,
                "world_logic": 0.8,
                "chemistry": 0.75,
                "stability": 0.77,
            },
        },
    )
    weak_ceiling = evaluate_episode(
        weak_text,
        {
            "genre_bucket": "A",
            "platform": "KakaoPage",
            "retention": {"unresolved_thread_pressure": 2, "curiosity_debt": 1},
            "tension": {"target_tension": 2},
            "story_state": story_state,
            "multi_objective": {
                "fun": 0.4,
                "coherence": 0.35,
                "character_persuasiveness": 0.3,
                "pacing": 0.32,
                "retention": 0.28,
                "emotional_immersion": 0.3,
                "information_design": 0.25,
                "emotional_payoff": 0.24,
                "long_run_sustainability": 0.45,
                "world_logic": 0.34,
                "chemistry": 0.2,
                "stability": 0.3,
            },
        },
    )

    strong_gate = quality_gate_report(
        {
            "hook_score": 0.82,
            "paywall_score": 0.78,
            "emotion_density": 0.77,
            "escalation": 0.8,
            "character_score": 0.79,
            "payoff_score": 0.76,
            "pacing_score": 0.75,
            "chemistry_score": 0.71,
            "repetition_score": 0.16,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_open_threads_min": 2,
            "protagonist_momentum_min": 0.52,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={"unresolved_thread_pressure": 8, "curiosity_debt": 8},
        predicted_retention=0.79,
        content_ceiling=strong_ceiling,
        causal_report=strong_causal,
        story_state={
            "promise_graph": {"payoff_integrity": 0.84, "payoff_corruption_flags": []},
            "world": {"instability": 4},
            "conflict": {
                "threads": [
                    {"id": "main", "status": "open"},
                    {"id": "betrayal", "status": "open"},
                ]
            },
            "cast": {
                "protagonist": {"progress": 2, "backlash": 1, "urgency": 8},
                "rival": {"progress": 1},
            },
        },
        objective_scores=strong_ceiling["multi_objective"],
    )
    weak_gate = quality_gate_report(
        {
            "hook_score": 0.44,
            "paywall_score": 0.41,
            "emotion_density": 0.32,
            "escalation": 0.25,
            "character_score": 0.3,
            "payoff_score": 0.22,
            "pacing_score": 0.28,
            "chemistry_score": 0.18,
            "repetition_score": 0.52,
        },
        {
            "hook_score_min": 0.7,
            "paywall_score_min": 0.7,
            "emotion_density_min": 0.65,
            "escalation_min": 0.65,
            "character_score_min": 0.66,
            "payoff_score_min": 0.68,
            "pacing_score_min": 0.66,
            "chemistry_score_min": 0.6,
            "repetition_max": 0.35,
            "predicted_retention_min": 0.62,
            "thread_pressure_min": 6,
            "curiosity_debt_min": 5,
            "ceiling_total_min": 58,
            "causal_score_min": 0.72,
            "causal_issues_max": 2,
            "payoff_integrity_min": 0.72,
            "payoff_corruption_flags_max": 0,
            "world_instability_max": 7,
            "conflict_open_threads_min": 2,
            "protagonist_momentum_min": 0.52,
            "balanced_objective_min": 0.66,
            "objective_variance_max": 0.33,
            "weakest_objective_axis_min": 0.55,
        },
        retention_state={"unresolved_thread_pressure": 2, "curiosity_debt": 1},
        predicted_retention=0.31,
        content_ceiling=weak_ceiling,
        causal_report=weak_causal,
        story_state={
            "promise_graph": {
                "payoff_integrity": 0.31,
                "payoff_corruption_flags": [{"type": "overdue_payoff"}],
            },
            "world": {"instability": 9},
            "conflict": {"threads": [{"id": "main", "status": "open"}]},
            "cast": {
                "protagonist": {"progress": 0, "backlash": 3, "urgency": 8},
                "rival": {"progress": 2},
            },
        },
        objective_scores=weak_ceiling["multi_objective"],
    )

    assert strong_causal["score"] > weak_causal["score"]
    assert strong_ceiling["ceiling_total"] > weak_ceiling["ceiling_total"]
    assert strong_gate["passed"] is True
    assert weak_gate["passed"] is False
