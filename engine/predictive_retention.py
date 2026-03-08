def predict_retention(scores: dict, fatigue: float) -> float:
    base = scores.get("emotion_density",0.5)*0.4 + scores.get("hook_score",0.5)*0.3 + scores.get("escalation",0.5)*0.3
    penalty = fatigue * 0.3
    return max(0.0, min(1.0, base - penalty))
