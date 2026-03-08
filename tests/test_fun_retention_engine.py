from engine.predictive_retention import build_retention_state, predict_retention


def test_retention_state_uses_unresolved_thread_pressure():
    state = {
        "conflict_engine": {
            "threads": [
                {"heat": 7, "status": "open"},
                {"heat": 6, "status": "open"},
            ],
            "threat_pressure": 8,
            "payoff_debt": 4,
            "recent_losses": 2,
        },
        "tension_wave": {"target_tension": 8},
    }
    retention = build_retention_state(
        state,
        event_plan={"type": "betrayal"},
        cliffhanger_plan={"carryover_pressure": 8, "open_question": "누가 배신했는가"},
    )
    assert retention["unresolved_thread_pressure"] >= 10 or retention["unresolved_thread_pressure"] >= 9
    assert retention["curiosity_debt"] >= 8


def test_retention_prediction_rises_with_pressure():
    low = predict_retention(
        {"emotion_density": 0.7, "hook_score": 0.7, "escalation": 0.7},
        0.2,
        {"unresolved_thread_pressure": 2, "threat_proximity": 2, "payoff_debt": 1, "curiosity_debt": 1, "fallout_pressure": 0},
    )
    high = predict_retention(
        {"emotion_density": 0.7, "hook_score": 0.7, "escalation": 0.7},
        0.2,
        {"unresolved_thread_pressure": 9, "threat_proximity": 8, "payoff_debt": 7, "curiosity_debt": 8, "fallout_pressure": 6},
    )
    assert high > low
