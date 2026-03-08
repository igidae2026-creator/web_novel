from engine.conflict_memory import prepare_conflict_memory, update_conflict_memory, conflict_prompt_payload


def test_conflict_engine_tracks_threads_and_modes():
    state = {
        "score_history": [{"hook_score": 0.61, "escalation": 0.6}],
        "character_arcs": {"protagonist": {"urgency": 9}},
    }
    engine = prepare_conflict_memory(state, episode=5)

    assert engine["threat_pressure"] >= 6
    assert engine["consequence_level"] >= 4
    assert engine["escalation_mode"]
    assert engine["threads"]


def test_conflict_engine_adds_fallout_thread_on_loss():
    state = {}
    prepare_conflict_memory(state, episode=1)
    engine = update_conflict_memory(
        state,
        2,
        score_obj={"hook_score": 0.65, "escalation": 0.66},
        event_plan={"type": "loss"},
    )

    payload = conflict_prompt_payload(state)
    assert engine["recent_losses"] >= 2
    assert any(thread["id"].startswith("thread-2-loss") for thread in payload["threads"])
