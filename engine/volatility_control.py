def adjust_volatility(knobs: dict, volatility: float):
    if volatility > 0.7:
        knobs["novelty_boost"] = min(0.99, knobs.get("novelty_boost",0.5)+0.1)
    if volatility < 0.3:
        knobs["compression"] = min(0.99, knobs.get("compression",0.6)+0.05)
    return knobs
