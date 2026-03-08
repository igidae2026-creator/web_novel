def multi_objective_balance(scores: dict):
    hook = scores.get("hook_score",0.5)
    emotion = scores.get("emotion_density",0.5)
    escalation = scores.get("escalation",0.5)
    repetition = scores.get("repetition_score",0.5)
    fitness = hook*0.3 + emotion*0.3 + escalation*0.3 - repetition*0.1
    return max(0.0, min(1.0, fitness))
