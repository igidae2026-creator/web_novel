from __future__ import annotations

import re
from typing import Any, Dict, List


GENRE_TITLE_TEMPLATES = {
    "A": ["{reward}한 {role}", "{loss}했다가 {reward}한 {role}", "{keyword} {role}의 {reward}"],
    "B": ["{keyword} 뒤에 {reward}한 {role}", "{loss}한 {role}는 {keyword}을 본다", "{reward}는 {keyword}에서 시작된다"],
    "F": ["{keyword}을 숨긴 {role}", "{reward}를 모르는 {role}", "{loss} 후 {keyword}한 관계"],
}


def _keywords(platform_spec: Dict[str, Any]) -> List[str]:
    return list(platform_spec.get("ctr_keywords", []) or []) + list(platform_spec.get("genre_signal_keywords", []) or [])


def _extract_terms(outline: str) -> Dict[str, str]:
    words = [token for token in re.findall(r"[A-Za-z0-9가-힣]+", outline or "") if len(token) >= 2]
    reward = next((word for word in words if any(key in word for key in ["복수", "성장", "진실", "각성", "회귀", "지배", "구원"])), "회귀")
    keyword = next((word for word in words if any(key in word for key in ["배신", "비밀", "계약", "운명", "아카데미", "탑"])), "비밀")
    role = next((word for word in words if any(key in word for key in ["헌터", "황자", "공녀", "마검사", "주인공", "영웅"])), "주인공")
    loss = next((word for word in words if any(key in word for key in ["망한", "버림", "추락", "배신", "죽은"])), "망한")
    return {"reward": reward, "keyword": keyword, "role": role, "loss": loss}


def score_title_candidate(candidate: str, platform_spec: Dict[str, Any]) -> Dict[str, Any]:
    length_min, length_max = list(platform_spec.get("target_title_length_range", [14, 28]) or [14, 28])[:2]
    keywords = _keywords(platform_spec)
    readability = 1.0 if re.search(r"\s", candidate) else 0.82
    genre_signal = 1.0 if any(keyword in candidate for keyword in keywords) else 0.42
    reward_signal = 1.0 if any(token in candidate for token in ["회귀", "복수", "성장", "각성", "진실", "최강", "지배", "구원"]) else 0.38
    length_score = 1.0 if length_min <= len(candidate) <= length_max else max(0.25, 1.0 - abs(len(candidate) - ((length_min + length_max) / 2.0)) / max(10.0, float(length_max)))
    promise_density = min(1.0, len([token for token in ["회귀", "복수", "비밀", "최강", "계약", "성장", "진실"] if token in candidate]) / 2.0)
    total = round(length_score * 0.28 + genre_signal * 0.24 + reward_signal * 0.24 + readability * 0.10 + promise_density * 0.14, 4)
    return {
        "candidate": candidate,
        "title_fitness": total,
        "length_score": round(length_score, 4),
        "genre_signal": round(genre_signal, 4),
        "reward_signal": round(reward_signal, 4),
        "readability": round(readability, 4),
        "promise_density": round(promise_density, 4),
        "weak_title": total < 0.62,
    }


def generate_title_candidates(
    outline: str,
    platform_spec: Dict[str, Any],
    current_title: str = "",
    limit: int = 5,
) -> List[Dict[str, Any]]:
    bucket = str(platform_spec.get("genre_bucket", "DEFAULT") or "DEFAULT")
    templates = GENRE_TITLE_TEMPLATES.get(bucket, ["{reward}한 {role}", "{keyword}의 {reward}", "{loss}한 {role}"])
    terms = _extract_terms(outline)
    raw_candidates = []
    if current_title:
        raw_candidates.append(str(current_title))
    raw_candidates.extend(template.format(**terms).strip() for template in templates)
    raw_candidates.extend([f"{terms['keyword']} {terms['role']}의 {terms['reward']}", f"{terms['loss']} {terms['role']}는 {terms['reward']}한다"])
    deduped: List[str] = []
    for candidate in raw_candidates:
        if candidate and candidate not in deduped:
            deduped.append(candidate)
    scored = [score_title_candidate(candidate, platform_spec) for candidate in deduped]
    scored.sort(key=lambda item: item["title_fitness"], reverse=True)
    selected = scored[:limit]
    if current_title:
        current_entry = next((item for item in scored if item["candidate"] == current_title), None)
    if current_entry and not any(item["candidate"] == current_title for item in selected):
        selected = selected[:-1] + [current_entry]
    return selected


def build_title_strategy(
    outline: str,
    platform_spec: Dict[str, Any],
    current_title: str = "",
    runtime_release_learning: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    candidates = generate_title_candidates(outline, platform_spec, current_title=current_title, limit=5)
    best = dict(candidates[0] if candidates else {})
    runtime_release_learning = dict(runtime_release_learning or {})
    trust = float(runtime_release_learning.get("trust_signal", 0.0) or 0.0)
    retention = float(runtime_release_learning.get("retention_signal", 0.0) or 0.0)
    launch_fit = round(
        min(
            1.0,
            float(best.get("title_fitness", 0.0) or 0.0) * 0.68
            + trust * 0.16
            + retention * 0.16,
        ),
        4,
    )
    rationale = []
    if best:
        if float(best.get("genre_signal", 0.0) or 0.0) >= 0.9:
            rationale.append("장르 신호가 선명함")
        if float(best.get("reward_signal", 0.0) or 0.0) >= 0.9:
            rationale.append("보상/반전 약속이 직접 보임")
        if float(best.get("length_score", 0.0) or 0.0) >= 0.9:
            rationale.append("플랫폼 길이 규격 적합")
    return {
        "current_title": current_title,
        "selected_title": best.get("candidate", current_title),
        "selected_title_rationale": rationale or ["가장 높은 구조 점수"],
        "best_title": best,
        "ranked_candidates": candidates,
        "weak_title": bool(best.get("weak_title", False)),
        "launch_recommendation": {
            "preferred_release_cadence": platform_spec.get("preferred_release_cadence"),
            "preferred_release_timing_windows": list(platform_spec.get("preferred_release_timing_windows", []) or []),
            "launch_fit_score": launch_fit,
            "launch_note": "초기 공개 구간은 제목 약속과 1~3화 보상 타이밍을 함께 맞출 것.",
        },
    }
