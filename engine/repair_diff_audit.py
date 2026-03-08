from __future__ import annotations

from typing import Any, Dict, List


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _tokenize(text: str) -> List[str]:
    return [token.strip(".,!?;:\"'()[]{}") for token in str(text or "").split() if token.strip()]


SCENE_ROLE_KEYWORDS = {
    "intent": ["위해", "하려", "목표", "원했다", "결심", "의도", "지키기", "막기"],
    "cause": ["때문", "그래서", "결국", "대가", "그 결과", "여파", "탓에", "덕분"],
    "world": ["세계", "규칙", "세력", "질서", "왕국", "도시", "법칙", "균형"],
    "relationship": ["조력자", "라이벌", "동맹", "관계", "신뢰", "배신", "동료"],
    "payoff": ["대가", "보상", "회수", "약속", "복수", "수확", "파국", "회복"],
    "emotion": ["두려", "분노", "망설", "후회", "떨", "울", "숨", "심장"],
}

FAILURE_AXIS_HINTS = {
    "intent_loss": "character_persuasiveness",
    "semantic_drift": "coherence",
    "causal_fix_failed": "coherence",
    "character_inconsistency": "character_persuasiveness",
    "payoff_corruption": "reader_retention",
    "scene_structure_drift": "pacing",
    "world_logic_regression": "world_logic",
}


def _split_sentences(text: str) -> List[str]:
    cleaned = str(text or "").replace("?", ".").replace("!", ".").replace("\n", ".")
    parts = [part.strip() for part in cleaned.split(".")]
    return [part for part in parts if part]


def _sentence_role(sentence: str) -> str:
    score_by_role: Dict[str, int] = {}
    for role, keywords in SCENE_ROLE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in sentence)
        if score:
            score_by_role[role] = score
    if not score_by_role:
        return "beat"
    return sorted(score_by_role.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _scene_signature(text: str) -> Dict[str, Any]:
    sentences = _split_sentences(text)
    roles = [_sentence_role(sentence) for sentence in sentences]
    transitions = [role for role in roles if role != "beat"]
    role_counts: Dict[str, int] = {}
    for role in roles:
        role_counts[role] = role_counts.get(role, 0) + 1
    dominant_roles = [role for role, _ in sorted(role_counts.items(), key=lambda item: (-item[1], item[0])) if role != "beat"][:4]
    return {
        "sentence_count": len(sentences),
        "roles": roles,
        "dominant_roles": dominant_roles,
        "role_counts": role_counts,
    }


def _overlap_ratio(left: List[str], right: List[str]) -> float:
    left_set = set(left)
    right_set = set(right)
    union = left_set | right_set
    if not union:
        return 1.0
    return len(left_set & right_set) / len(union)


def _classify_semantic_failures(
    repair_plan: Dict[str, Any],
    pre_report: Dict[str, Any],
    post_report: Dict[str, Any],
    pre_signature: Dict[str, Any],
    post_signature: Dict[str, Any],
    lexical_shift: float,
) -> List[Dict[str, Any]]:
    targeted = list(repair_plan.get("critical_issues", []) or pre_report.get("issues", [])[:3])
    post_issues = set(post_report.get("issues", []) or [])
    failures: List[Dict[str, Any]] = []
    dominant_overlap = _overlap_ratio(pre_signature.get("dominant_roles", []), post_signature.get("dominant_roles", []))
    role_delta = abs(int(post_signature.get("sentence_count", 0) or 0) - int(pre_signature.get("sentence_count", 0) or 0))

    if targeted and all(issue in post_issues for issue in targeted):
        failures.append({"type": "causal_fix_failed", "severity": 1.0, "axis": FAILURE_AXIS_HINTS["causal_fix_failed"]})
    if pre_signature.get("dominant_roles") and dominant_overlap < 0.34 and (post_issues or lexical_shift < 0.85):
        failures.append({"type": "semantic_drift", "severity": round(1.0 - dominant_overlap, 4), "axis": FAILURE_AXIS_HINTS["semantic_drift"]})
    if "intent" in pre_signature.get("dominant_roles", []) and "intent" not in post_signature.get("dominant_roles", []):
        failures.append({"type": "intent_loss", "severity": 0.82, "axis": FAILURE_AXIS_HINTS["intent_loss"]})
    if "relationship" in pre_signature.get("dominant_roles", []) and "relationship" not in post_signature.get("dominant_roles", []):
        failures.append({"type": "character_inconsistency", "severity": 0.68, "axis": FAILURE_AXIS_HINTS["character_inconsistency"]})
    if "payoff" in pre_signature.get("dominant_roles", []) and "payoff" not in post_signature.get("dominant_roles", []):
        failures.append({"type": "payoff_corruption", "severity": 0.74, "axis": FAILURE_AXIS_HINTS["payoff_corruption"]})
    if "world" in pre_signature.get("dominant_roles", []) and "world" not in post_signature.get("dominant_roles", []):
        failures.append({"type": "world_logic_regression", "severity": 0.64, "axis": FAILURE_AXIS_HINTS["world_logic_regression"]})
    if role_delta >= 3 and lexical_shift >= 0.45:
        failures.append({"type": "scene_structure_drift", "severity": 0.58, "axis": FAILURE_AXIS_HINTS["scene_structure_drift"]})
    return failures[:4]


def audit_repair_diff(
    pre_text: str,
    post_text: str,
    pre_report: Dict[str, Any],
    post_report: Dict[str, Any],
    repair_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    pre_report = dict(pre_report or {})
    post_report = dict(post_report or {})
    repair_plan = dict(repair_plan or {})

    pre_issues = list(pre_report.get("issues", []) or [])
    post_issues = list(post_report.get("issues", []) or [])
    targeted = list(repair_plan.get("critical_issues", []) or pre_issues[:3])
    resolved_targets = [issue for issue in targeted if issue not in post_issues]
    persistent_targets = [issue for issue in targeted if issue in post_issues]
    new_issues = [issue for issue in post_issues if issue not in pre_issues]

    pre_tokens = set(_tokenize(pre_text))
    post_tokens = set(_tokenize(post_text))
    union = pre_tokens | post_tokens
    lexical_shift = 0.0 if not union else len(pre_tokens ^ post_tokens) / len(union)
    score_delta = float(post_report.get("score", 0.0) or 0.0) - float(pre_report.get("score", 0.0) or 0.0)
    pre_signature = _scene_signature(pre_text)
    post_signature = _scene_signature(post_text)
    structure_overlap = _overlap_ratio(pre_signature.get("roles", []), post_signature.get("roles", []))
    intent_overlap = _overlap_ratio(
        [role for role in pre_signature.get("dominant_roles", []) if role in {"intent", "cause", "payoff", "relationship", "world"}],
        [role for role in post_signature.get("dominant_roles", []) if role in {"intent", "cause", "payoff", "relationship", "world"}],
    )
    failures = _classify_semantic_failures(
        repair_plan=repair_plan,
        pre_report=pre_report,
        post_report=post_report,
        pre_signature=pre_signature,
        post_signature=post_signature,
        lexical_shift=lexical_shift,
    )
    semantic_failure_types = [item["type"] for item in failures]
    semantic_penalty = min(0.35, sum(float(item.get("severity", 0.0) or 0.0) for item in failures) * 0.12)
    intent_preservation_score = _clamp(
        0.42
        + intent_overlap * 0.34
        + structure_overlap * 0.14
        + max(0.0, score_delta) * 0.12
        - semantic_penalty
    )
    semantic_repair_effectiveness = _clamp(
        0.36
        + len(resolved_targets) * 0.14
        - len(persistent_targets) * 0.10
        - len(new_issues) * 0.06
        + intent_preservation_score * 0.18
        + max(0.0, score_delta) * 0.16
        - semantic_penalty * 0.5
    )

    if persistent_targets:
        mismatch_type = "unresolved_target"
    elif new_issues:
        mismatch_type = "collateral_regression"
    elif semantic_failure_types:
        mismatch_type = "semantic_drift"
    elif lexical_shift < 0.08 and score_delta < 0.08:
        mismatch_type = "superficial_rewrite"
    elif score_delta < 0:
        mismatch_type = "overcorrection"
    else:
        mismatch_type = "resolved"

    defect_resolution_score = _clamp(
        0.48
        + len(resolved_targets) * 0.12
        - len(persistent_targets) * 0.10
        - len(new_issues) * 0.06
        + score_delta * 0.40
        + lexical_shift * 0.12
        + intent_preservation_score * 0.08
        - semantic_penalty
    )
    strategy_effectiveness = _clamp(
        0.42
        + len(resolved_targets) * 0.14
        - len(persistent_targets) * 0.12
        - len(new_issues) * 0.08
        + score_delta * 0.30
        + semantic_repair_effectiveness * 0.18
        - semantic_penalty * 0.3
    )
    return {
        "mismatch_type": mismatch_type,
        "resolved_targets": resolved_targets,
        "persistent_targets": persistent_targets,
        "new_issues": new_issues,
        "lexical_shift": lexical_shift,
        "score_delta": score_delta,
        "defect_resolution_score": defect_resolution_score,
        "strategy_effectiveness": strategy_effectiveness,
        "semantic_audit": {
            "pre_scene_signature": pre_signature,
            "post_scene_signature": post_signature,
            "structure_overlap": structure_overlap,
            "intent_overlap": intent_overlap,
            "intent_preservation_score": intent_preservation_score,
            "semantic_failure_types": semantic_failure_types,
            "semantic_failures": failures,
            "semantic_repair_effectiveness": semantic_repair_effectiveness,
        },
    }
