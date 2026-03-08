from engine.character_arc import prepare_character_arc, update_character_arc, character_prompt_payload


def test_character_engine_uses_pressure_not_episode_timer():
    state = {
        "score_history": [{"hook_score": 0.6, "escalation": 0.6}],
        "conflict_engine": {"threads": [{"id": "t1"}, {"id": "t2"}], "threat_pressure": 3},
    }
    cfg = {"project": {"genre_bucket": "A"}}

    arcs = prepare_character_arc(state, cfg=cfg, outline="몰락 직전의 천재 검사", episode=4)

    protagonist = arcs["protagonist"]
    assert protagonist["core_desire"]
    assert protagonist["fear_trigger"]
    assert protagonist["weakness"]
    assert protagonist["urgency"] >= 8
    assert protagonist["decision_pressure"] >= protagonist["urgency"] - 1


def test_character_engine_updates_from_outcome_and_event():
    state = {}
    prepare_character_arc(state, cfg={"project": {"genre_bucket": "B"}}, outline="추락한 황자의 복수", episode=1)

    arcs = update_character_arc(
        state,
        1,
        score_obj={"hook_score": 0.8, "escalation": 0.8},
        event_plan={"type": "reversal"},
    )

    protagonist = arcs["protagonist"]
    payload = character_prompt_payload(state)
    assert protagonist["progress"] >= 1
    assert payload["protagonist"]["dominant_need"]
    assert payload["rival"]["core_desire"]
