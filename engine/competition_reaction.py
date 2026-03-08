
from __future__ import annotations
from typing import Dict, Any
from engine.competition_density import estimate_density
from engine.competition_difficulty import difficulty_factor

def apply_competition_reaction(cfg: dict, state: dict, knobs: dict) -> dict:
    out_dir = state.get("out_dir",".")
    density = estimate_density(out_dir)
    diff = difficulty_factor(cfg)
    density = min(1.0, density * diff)
    state["competition_density"]=density
    
    # if density high reduce boost strength
    if density > 0.7:
        knobs["hook_intensity"] *= 0.9
        knobs["payoff_intensity"] *= 0.9
        state["competition_mode"]="HIGH"
    elif density < 0.3:
        knobs["hook_intensity"] *= 1.05
        state["competition_mode"]="LOW"
    else:
        state["competition_mode"]="MID"
    return knobs
