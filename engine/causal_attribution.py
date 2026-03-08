from __future__ import annotations

from typing import Any, Dict, List


EVENT_KEYWORDS = {
    "reveal": ["진실", "드러", "밝혀"],
    "betrayal": ["배신", "등을 돌", "속였"],
    "loss": ["잃", "상실", "무너졌"],
    "arrival": ["도착", "나타났", "합류"],
    "sacrifice": ["희생", "대가", "포기"],
    "power_shift": ["권력", "주도권", "재편"],
}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _split_scene_units(text: str) -> List[str]:
    cleaned = str(text or "").replace("?", ".").replace("!", ".").replace("\n", ".")
    return [item.strip() for item in cleaned.split(".") if item.strip()]


def build_scene_event_attribution(
    episode_text: str,
    event_plan: Dict[str, Any] | None = None,
    cliffhanger_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    units = _split_scene_units(episode_text)
    event_type = str((event_plan or {}).get("type", "")).strip()
    keywords = EVENT_KEYWORDS.get(event_type, [])
    open_question = str((cliffhanger_plan or {}).get("open_question", "") or "")
    scene_scores = []
    for idx, unit in enumerate(units, start=1):
        event_match = sum(1 for keyword in keywords if keyword and keyword in unit)
        causal = sum(1 for keyword in ["때문", "결국", "그래서", "대가"] if keyword in unit)
        emotional = sum(1 for keyword in ["두려", "분노", "후회", "떨", "숨"] if keyword in unit)
        question_link = 1 if open_question and any(token in unit for token in open_question.split()[:2]) else 0
        intensity = _clamp(event_match * 0.18 + causal * 0.14 + emotional * 0.10 + question_link * 0.08 + min(0.12, len(unit) / 120.0))
        scene_scores.append({"scene_index": idx, "text": unit[:80], "intensity": round(intensity, 4), "event_match": event_match, "causal_match": causal})
    scene_scores.sort(key=lambda item: (-item["intensity"], item["scene_index"]))
    top_scene = scene_scores[0] if scene_scores else {"scene_index": 0, "intensity": 0.0}
    return {
        "scene_units": scene_scores[:6],
        "top_scene_index": int(top_scene.get("scene_index", 0) or 0),
        "scene_signal": float(top_scene.get("intensity", 0.0) or 0.0),
        "scene_count": len(units),
    }
