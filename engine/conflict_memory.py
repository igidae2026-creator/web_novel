from __future__ import annotations
from typing import Dict

def update_conflict_memory(state: Dict, episode: int) -> None:
    mem = state.get("conflict_memory", 0)
    if episode % 7 == 0:
        mem += 1
    state["conflict_memory"] = mem
