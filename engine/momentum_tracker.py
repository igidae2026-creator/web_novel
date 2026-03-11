def momentum_score(history):
    if len(history) < 3:
        return 0.0
    last = history[-3:]
    return sum(float(x.get("hook_score",0.5)) for x in last)/3
