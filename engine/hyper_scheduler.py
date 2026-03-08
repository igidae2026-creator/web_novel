def schedule_knobs(ep: int, total: int, knobs: dict):
    progress = ep / max(1,total)
    if progress > 0.7:
        knobs["hook_intensity"] = min(0.99, knobs.get("hook_intensity",0.7)+0.05)
        knobs["payoff_intensity"] = min(0.99, knobs.get("payoff_intensity",0.7)+0.08)
    if progress > 0.9:
        knobs["compression"] = min(0.99, knobs.get("compression",0.7)+0.1)
    return knobs
