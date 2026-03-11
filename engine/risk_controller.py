def apply_risk_control(knobs: dict, risk_level: float):
    if risk_level > 0.7:
        knobs["compression"] = min(0.99, knobs.get("compression",0.7)+0.1)
        knobs["hook_intensity"] = min(0.99, knobs.get("hook_intensity",0.7)+0.05)
    return knobs
