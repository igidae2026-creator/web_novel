from __future__ import annotations

from typing import Any, Dict, List


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _tokenize(text: str) -> List[str]:
    return [token.strip(".,!?;:\"'()[]{}") for token in str(text or "").split() if token.strip()]


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

    if persistent_targets:
        mismatch_type = "unresolved_target"
    elif new_issues:
        mismatch_type = "collateral_regression"
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
    )
    strategy_effectiveness = _clamp(
        0.42
        + len(resolved_targets) * 0.14
        - len(persistent_targets) * 0.12
        - len(new_issues) * 0.08
        + score_delta * 0.30
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
    }
