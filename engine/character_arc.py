from __future__ import annotations
from typing import Dict

def update_character_arc(state: Dict, episode: int) -> None:
    arcs = state.get("character_arcs", {})
    stage = arcs.get("protagonist_stage", 0)
    if episode % 10 == 0:
        stage += 1
    arcs["protagonist_stage"] = stage
    state["character_arcs"] = arcs
