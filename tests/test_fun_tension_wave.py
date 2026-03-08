from engine.tension_wave import prepare_tension_wave, apply_tension_wave, update_tension_wave


def test_tension_wave_targets_spike_when_pressure_is_high():
    state = {
        "story_events": ["loss"],
        "score_history": [{"escalation": 0.62}],
        "conflict_engine": {"threat_pressure": 8, "consequence_level": 8},
    }
    tension = prepare_tension_wave(state, episode=4)
    knobs = apply_tension_wave({"hook_intensity": 0.7, "payoff_intensity": 0.7, "compression": 0.6, "novelty_boost": 0.5}, tension)

    assert tension["band"] == "spike"
    assert knobs["hook_intensity"] > 0.7
    assert knobs["tension_target"] >= 8


def test_tension_wave_updates_peak_and_debt():
    state = {}
    prepare_tension_wave(state, episode=1)
    tension = update_tension_wave(
        state,
        1,
        score_obj={"hook_score": 0.9, "escalation": 0.85, "emotion_density": 0.8},
        event_plan={"type": "arrival"},
    )
    assert tension["current_tension"] >= 8
    assert tension["peak_count"] >= 1
