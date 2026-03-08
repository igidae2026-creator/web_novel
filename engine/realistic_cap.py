def enforce_realistic_cap(cfg: dict, state: dict, knobs: dict):
    cap = float(cfg.get("realistic_cap_top_percent", 3.0))
    # If predicted median below cap, freeze boost growth
    current_p50 = float(state.get("last_p50_estimate", 999))
    if current_p50 <= cap:
        # prevent further aggressive boosts
        knobs["hook_intensity"] = min(knobs.get("hook_intensity",0.7), 0.93)
        knobs["payoff_intensity"] = min(knobs.get("payoff_intensity",0.7), 0.95)
        knobs["compression"] = min(knobs.get("compression",0.6), 0.88)
    return knobs
