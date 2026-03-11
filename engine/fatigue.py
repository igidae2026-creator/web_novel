from typing import List, Dict

def fatigue_index(last_scores: List[Dict]) -> float:
    # scores expected: repetition_score (higher bad), emotion_density (higher good), escalation (higher good)
    if not last_scores:
        return 0.0
    reps = [float(s.get("repetition_score", 0.35)) for s in last_scores]
    emos = [float(s.get("emotion_density", 0.65)) for s in last_scores]
    escs = [float(s.get("escalation", 0.65)) for s in last_scores]
    rep = sum(reps)/len(reps)
    emo = sum(emos)/len(emos)
    esc = sum(escs)/len(escs)
    # fatigue increases with repetition and with low emotion/escalation
    return 0.4*rep + 0.3*(1-emo) + 0.3*(1-esc)

def fatigue_directives(fatigue: float, threshold: float) -> dict:
    if fatigue <= threshold:
        return {"needs_reset": False, "reset_level": 0.0, "directive": ""}
    # reset level scales beyond threshold
    reset_level = min(1.0, (fatigue - threshold) / max(0.05, 1.0 - threshold))
    directive = (
        "피로도 상승 감지. 다음 회차에서 새 갈등 축/새 인물/새 장소/새 규칙 중 최소 2개를 도입하고, "
        "기존 갈등은 승격(상위 세력/숨은 배후/새 제약)으로 단계 상승시켜라."
    )
    return {"needs_reset": True, "reset_level": reset_level, "directive": directive}
