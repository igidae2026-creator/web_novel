from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


BUSINESS_AXIS_THRESHOLDS: Dict[str, float] = {
    "title_fitness": 0.62,
    "milestone_compliance": 0.64,
    "conversion_readiness": 0.64,
    "protagonist_sovereignty": 0.66,
    "narrative_debt_health": 0.58,
    "emotion_wave_health": 0.58,
    "ip_readiness": 0.55,
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(base)
    for key, value in dict(override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def build_business_axis_snapshot(system_status: Dict[str, Any]) -> Dict[str, float]:
    latest = dict(system_status.get("latest_business_signals", {}) or {})
    return {
        "title_fitness": float(latest.get("title_fitness", 0.0) or 0.0),
        "milestone_compliance": float(latest.get("milestone_readiness", latest.get("milestone_compliance", 0.0)) or 0.0),
        "conversion_readiness": float(latest.get("conversion_readiness", 0.0) or 0.0),
        "protagonist_sovereignty": float(latest.get("protagonist_sovereignty", 0.0) or 0.0),
        "narrative_debt_health": max(0.0, 1.0 - float(latest.get("narrative_debt_score", 1.0) or 1.0)),
        "emotion_wave_health": float(latest.get("emotion_wave_balance", 0.0) or 0.0),
        "ip_readiness": float(latest.get("ip_readiness", 0.0) or 0.0),
    }


def build_business_action_recommendations(
    system_status: Dict[str, Any],
    runtime_cfg: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    system_status = dict(system_status or {})
    runtime_cfg = dict(runtime_cfg or {})
    snapshot = build_business_axis_snapshot(system_status)
    title_state = dict(system_status.get("latest_title_state", {}) or {})
    recommendations: List[Dict[str, Any]] = []

    def add(axis: str, action_type: str, rationale: str, config_patch: Dict[str, Any], payload: Dict[str, Any] | None = None) -> None:
        value = float(snapshot.get(axis, 0.0) or 0.0)
        threshold = float(BUSINESS_AXIS_THRESHOLDS[axis])
        if value >= threshold:
            return
        recommendations.append(
            {
                "id": f"{axis}:{action_type}",
                "axis": axis,
                "value": round(value, 4),
                "threshold": threshold,
                "severity": round(threshold - value, 4),
                "action_type": action_type,
                "rationale": rationale,
                "config_patch": config_patch,
                "payload": dict(payload or {}),
            }
        )

    best_title = dict(title_state.get("best_title", {}) or {})
    if best_title.get("candidate"):
        add(
            "title_fitness",
            "title_package_change",
            "제목 적합도가 낮아 추천 제목 패키지로 교체하는 것이 유입 개선에 유리함.",
            {"project_setup": {"title": str(best_title.get("candidate"))}},
            {"selected_title": str(best_title.get("candidate"))},
        )
    add(
        "milestone_compliance",
        "stronger_milestone_enforcement",
        "마일스톤 준수가 약해 초중반 보상과 전환 구간을 더 강하게 강제해야 함.",
        {"evaluation": {"milestone_enforcement_level": 0.15}},
    )
    add(
        "conversion_readiness",
        "stagger_or_hold_release",
        "유료 전환 준비도가 낮아 릴리즈를 무리하게 밀기보다 스태거/보류 추천이 안전함.",
        {"release_scheduler": {"strategy": "guarded"}},
        {"release_action": "hold_or_stagger"},
    )
    add(
        "protagonist_sovereignty",
        "protagonist_centered_rewrite",
        "주인공 중심성이 약해 주도권 회복을 강하게 요구하는 재작성 강조가 필요함.",
        {"evaluation": {"protagonist_focus_enforcement": 0.15}},
    )
    add(
        "narrative_debt_health",
        "soft_recovery_mode",
        "내러티브 부채가 높아 회수/정산 중심의 회복 모드 전환이 필요함.",
        {"business": {"recovery_mode": "soft_recovery"}},
    )
    add(
        "emotion_wave_health",
        "reduce_release_cadence",
        "감정 파형이 과열되어 있어 릴리즈 속도를 한 단계 낮추는 것이 안전함.",
        {"release_cadence": {"steps_per_run": -1}, "business": {"recovery_mode": "soft_recovery"}},
    )
    add(
        "ip_readiness",
        "ip_scene_density_enforcement",
        "IP 준비도가 낮아 적응 가능한 장면 밀도와 규칙 명료도를 더 강제해야 함.",
        {"evaluation": {"ip_expansion_enforcement": 0.15}},
    )
    recommendations.sort(key=lambda item: (-item["severity"], item["axis"], item["action_type"]))
    return recommendations


def apply_recommendation_to_runtime(
    runtime_cfg: Dict[str, Any],
    recommendation: Dict[str, Any],
) -> Dict[str, Any]:
    runtime_cfg = deepcopy(dict(runtime_cfg or {}))
    patch = dict(recommendation.get("config_patch", {}) or {})
    updated = _deep_merge(runtime_cfg, patch)

    steps_delta = int(((patch.get("release_cadence", {}) or {}).get("steps_per_run", 0) or 0))
    if steps_delta:
        current_steps = int(((runtime_cfg.get("release_cadence", {}) or {}).get("steps_per_run", 1) or 1))
        updated.setdefault("release_cadence", {})
        updated["release_cadence"]["steps_per_run"] = max(1, min(3, current_steps + steps_delta))

    eval_cfg = updated.setdefault("evaluation", {})
    if isinstance((patch.get("evaluation", {}) or {}).get("milestone_enforcement_level"), (int, float)):
        current = float(((runtime_cfg.get("evaluation", {}) or {}).get("milestone_enforcement_level", 0.5) or 0.5))
        eval_cfg["milestone_enforcement_level"] = round(min(0.9, current + float(patch["evaluation"]["milestone_enforcement_level"])), 4)
    if isinstance((patch.get("evaluation", {}) or {}).get("protagonist_focus_enforcement"), (int, float)):
        current = float(((runtime_cfg.get("evaluation", {}) or {}).get("protagonist_focus_enforcement", 0.5) or 0.5))
        eval_cfg["protagonist_focus_enforcement"] = round(min(0.9, current + float(patch["evaluation"]["protagonist_focus_enforcement"])), 4)
    if isinstance((patch.get("evaluation", {}) or {}).get("ip_expansion_enforcement"), (int, float)):
        current = float(((runtime_cfg.get("evaluation", {}) or {}).get("ip_expansion_enforcement", 0.4) or 0.4))
        eval_cfg["ip_expansion_enforcement"] = round(min(0.9, current + float(patch["evaluation"]["ip_expansion_enforcement"])), 4)
    updated.setdefault("business", {})
    if patch.get("business", {}).get("recovery_mode"):
        updated["business"]["recovery_mode"] = str(patch["business"]["recovery_mode"])
    return updated


def record_business_adjustment(
    runtime_cfg: Dict[str, Any],
    recommendation: Dict[str, Any],
    before_signals: Dict[str, float],
    executed_at: str,
) -> Dict[str, Any]:
    runtime_cfg = deepcopy(dict(runtime_cfg or {}))
    control = runtime_cfg.setdefault("business_control", {})
    history = list(control.get("adjustment_history", []) or [])
    pending = list(control.get("pending_adjustments", []) or [])
    entry = {
        "id": f"{recommendation.get('id')}@{executed_at}",
        "executed_at": executed_at,
        "action_type": recommendation.get("action_type"),
        "trigger_axis": recommendation.get("axis"),
        "recommendation_id": recommendation.get("id"),
        "before_signals": dict(before_signals),
        "after_signals": {},
        "outcome": "pending",
        "payload": dict(recommendation.get("payload", {}) or {}),
    }
    history.append(entry)
    pending.append(entry)
    control["adjustment_history"] = history[-24:]
    control["pending_adjustments"] = pending[-8:]
    return runtime_cfg


def sync_business_adjustment_outcomes(
    runtime_cfg: Dict[str, Any],
    system_status: Dict[str, Any],
) -> Dict[str, Any]:
    runtime_cfg = deepcopy(dict(runtime_cfg or {}))
    control = runtime_cfg.setdefault("business_control", {})
    pending = list(control.get("pending_adjustments", []) or [])
    history = list(control.get("adjustment_history", []) or [])
    learning = dict(control.get("learning", {}) or {})
    current = build_business_axis_snapshot(system_status)
    remaining = []
    updated_history = []
    history_by_id = {item.get("id"): deepcopy(item) for item in history}
    for item in pending:
        axis = str(item.get("trigger_axis", "") or "")
        before = float((item.get("before_signals", {}) or {}).get(axis, 0.0) or 0.0)
        after = float(current.get(axis, before) or before)
        improvement = round(after - before, 4)
        target = learning.setdefault(axis, {"observed": 0, "mean_improvement": 0.0, "successful_actions": 0})
        target["observed"] += 1
        target["mean_improvement"] = round(((float(target.get("mean_improvement", 0.0) or 0.0) * (target["observed"] - 1)) + improvement) / target["observed"], 4)
        if improvement > 0.01:
            target["successful_actions"] += 1
        stored = history_by_id.get(item.get("id"), deepcopy(item))
        stored["after_signals"] = dict(current)
        stored["outcome"] = "improved" if improvement > 0.01 else "flat_or_worse"
        stored["improvement"] = improvement
        history_by_id[stored["id"]] = stored
    updated_history = list(history_by_id.values())
    updated_history.sort(key=lambda item: str(item.get("executed_at", "")))
    control["adjustment_history"] = updated_history[-24:]
    control["pending_adjustments"] = remaining
    control["learning"] = learning
    return runtime_cfg
