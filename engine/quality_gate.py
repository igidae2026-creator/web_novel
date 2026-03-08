def quality_gate(scores: dict, thresholds: dict) -> bool:
    if scores.get("hook_score",0) < thresholds.get("hook_score_min",0):
        return False
    if scores.get("emotion_density",0) < thresholds.get("emotion_density_min",0):
        return False
    if scores.get("escalation",0) < thresholds.get("escalation_min",0):
        return False
    if scores.get("repetition_score",1) > thresholds.get("repetition_max",1):
        return False
    return True
