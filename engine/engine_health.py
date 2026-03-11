from __future__ import annotations
from typing import Dict

def compute_engine_health(state: Dict) -> Dict:
    return {
        "phase": state.get("phase"),
        "phase_cooldown": state.get("phase_cooldown", 0),
        "rebuild_level": state.get("rebuild_level", 0),
        "rebuild_cooldown": state.get("rebuild_cooldown", 0),
        "decline_streak": state.get("decline_streak", 0),
        "rebuild_events_count": len(state.get("rebuild_events", [])),
        "rebuild_feedback_count": len(state.get("rebuild_feedback", [])),
    }
