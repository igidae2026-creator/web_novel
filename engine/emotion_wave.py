from __future__ import annotations

from typing import Any, Dict


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def evaluate_emotion_wave(story_state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = dict(story_state or {})
    pacing = dict(story_state.get("pacing", {}) or {})
    information = dict(story_state.get("information", {}) or {})
    burn_level = _clamp(int(pacing.get("current_tension", 0) or 0) / 10.0 * 0.55 + int(pacing.get("spike_debt", 0) or 0) * 0.10)
    reset_need = _clamp(int(pacing.get("release_debt", 0) or 0) * 0.22 + max(0, int(pacing.get("current_tension", 0) or 0) - 7) * 0.06)
    reservoir = int(information.get("emotional_reservoir", 0) or 0) / 10.0
    fatigue_projection = _clamp(burn_level * 0.46 + reset_need * 0.34 + max(0.0, 0.45 - reservoir) * 0.30)
    balance = _clamp(0.92 - abs(burn_level - 0.58) * 0.48 - reset_need * 0.20 - fatigue_projection * 0.20 + reservoir * 0.12)
    return {
        "emotion_wave_balance": round(balance, 4),
        "burn_level": round(burn_level, 4),
        "reset_need": round(reset_need, 4),
        "fatigue_projection": round(fatigue_projection, 4),
    }
