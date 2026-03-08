from analytics.content_ceiling import evaluate_episode


def test_content_ceiling_uses_structural_pressure():
    text = "그는 승리 직전이었다. 하지만 배신은 더 깊은 대가를 남겼다."
    result = evaluate_episode(
        text,
        {
            "genre_bucket": "A",
            "platform": "Munpia",
            "event_plan": {"type": "betrayal"},
            "cliffhanger": "배신은 아직 끝나지 않았다. 누가 먼저 무너질까?",
            "cliffhanger_plan": {"carryover_pressure": 8, "mode": "choice_lock"},
            "conflict": {"threads": [{"id": "t1"}], "consequence_level": 7},
            "retention": {"unresolved_thread_pressure": 8, "curiosity_debt": 8},
            "tension": {"target_tension": 8},
        },
    )
    assert result["ceiling_total"] > 0
    assert result["events"]["typed_event"] == "betrayal"
    assert result["retention"]["unresolved_thread_pressure"] == 8
