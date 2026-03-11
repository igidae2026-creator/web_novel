from typing import Dict

def entropy_adjustment(scores: Dict, knobs: Dict):
    entropy = abs(scores.get("emotion_density",0.5) - scores.get("escalation",0.5))
    if entropy < 0.05:
        knobs["novelty_boost"] = min(0.99, knobs.get("novelty_boost",0.5)+0.1)
    return knobs
