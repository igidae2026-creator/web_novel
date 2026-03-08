from engine.event_generator import generate_event_plan, register_story_event, event_prompt_payload


def test_event_generator_returns_typed_event_payload():
    state = {
        "conflict_engine": {
            "threads": [{"id": "t1", "label": "추격", "stake": "생존", "consequence": "붕괴", "heat": 7, "status": "open"}],
            "consequence_level": 7,
            "threat_pressure": 8,
            "escalation_mode": "power_reversal",
        },
        "character_arcs": {"protagonist": {"urgency": 8}},
        "story_events": ["loss"],
    }

    plan = generate_event_plan(state, episode=6)
    payload = event_prompt_payload(plan)
    assert payload["type"] in {"reveal", "betrayal", "reversal", "loss", "arrival"}
    assert payload["target_thread"] == "t1"
    assert payload["consequence"]
    assert payload["carryover_pressure"] >= 7


def test_event_generator_registers_history():
    state = {}
    register_story_event(state, {"type": "arrival"})
    assert state["story_events"] == ["arrival"]
