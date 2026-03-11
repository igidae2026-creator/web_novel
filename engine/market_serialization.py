from __future__ import annotations

import json
import os
from typing import Any, Dict

from .story_state import ensure_story_state, sync_story_state


PLATFORM_PACING = {
    "Joara": "aggressive",
    "Munpia": "aggressive",
    "NaverSeries": "balanced",
    "KakaoPage": "spiky",
    "Ridibooks": "character",
    "Novelpia": "aggressive",
}


def _clamp(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def _load_business_feedback(out_dir: str) -> Dict[str, Any]:
    if not out_dir:
        return {}
    cert_path = os.path.join(out_dir, "certification_report.json")
    if not os.path.exists(cert_path):
        return {}
    try:
        with open(cert_path, "r", encoding="utf-8") as handle:
            report = json.load(handle)
    except Exception:
        return {}
    business = dict(report.get("business_feedback", {}) or {})
    market = dict(report.get("market", {}) or {})
    stats = dict(market.get("stats", {}) or {})
    return {
        "available": bool(business.get("available")),
        "total_revenue": float(business.get("total_revenue", 0.0) or 0.0),
        "campaign_spend": float(business.get("total_campaign_spend", 0.0) or 0.0),
        "best_campaign_roi": float(business.get("best_campaign_roi", 0.0) or 0.0),
        "market_ok": bool(market.get("ok")),
        "latest_top_percent": float(stats.get("latest_top_percent", 999.0) or 999.0) if stats else 999.0,
        "failure_reason": str(report.get("failure_reason") or ""),
    }


def update_market_serialization(
    state: Dict[str, Any],
    episode: int,
    cfg: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state, cfg=cfg)
    serialization = story_state["serialization"]
    market = story_state["market"]
    rewards = story_state["rewards"]
    tension = story_state["pacing"]
    cfg = dict(cfg or state.get("_cfg_for_models", {}) or {})
    event_plan = dict(event_plan or {})
    out_dir = str(state.get("out_dir") or "")

    project = cfg.get("project", {})
    novel = cfg.get("novel", {})
    platform = str(project.get("platform", "Munpia"))
    pacing_mode = PLATFORM_PACING.get(platform, "balanced")
    paywall_window = novel.get("paywall_window", [20, 30])
    early_focus = int(novel.get("early_focus_episodes", 5) or 5)
    paywall_pressure = 4
    if episode <= early_focus:
        paywall_pressure += 1
    if len(paywall_window) >= 2 and int(paywall_window[0]) <= episode <= int(paywall_window[1]):
        paywall_pressure += 3

    reward_density = int(rewards.get("reward_density", 5) or 5)
    expectation = int(rewards.get("expectation_alignment", 5) or 5)
    tension_target = int(tension.get("target_tension", 7) or 7)
    event_type = str(event_plan.get("type", "")).strip()
    feedback = _load_business_feedback(out_dir)
    campaign_roi = float(feedback.get("best_campaign_roi", 0.0) or 0.0)
    latest_top_percent = float(feedback.get("latest_top_percent", 999.0) or 999.0)
    market_pressure = 0
    if feedback.get("available"):
        if not bool(feedback.get("market_ok")):
            market_pressure += 2
        if campaign_roi < 0.2:
            market_pressure += 1
        if latest_top_percent > 5.0:
            market_pressure += 1
    reader_exit_risk = min(10, max(0, market_pressure + max(0, 6 - expectation)))

    market["platform_pacing"] = pacing_mode
    market["paywall_pressure"] = _clamp(paywall_pressure)
    market["reader_trust"] = _clamp(5 + expectation - max(0, reward_density - 7) - market_pressure // 2)
    market["bingeability"] = _clamp(4 + reward_density // 2 + int(tension_target >= 7))
    market["serialization_heat"] = _clamp(4 + int(event_type in {"betrayal", "arrival", "power_shift", "collapse"}) + tension_target // 2 + market_pressure // 2)
    market["release_confidence"] = _clamp(market["reader_trust"] + serialization.get("sustainability", 5) // 2 - max(0, paywall_pressure - 6) - market_pressure // 2)
    market["market_pressure"] = _clamp(market_pressure)
    market["reader_exit_risk"] = _clamp(reader_exit_risk)
    market["campaign_roi_signal"] = round(campaign_roi, 4)
    market["market_feedback_active"] = bool(feedback.get("available"))
    market.setdefault("market_signals", []).append(
        {
            "episode": episode,
            "platform": platform,
            "paywall_pressure": market["paywall_pressure"],
            "reader_trust": market["reader_trust"],
            "serialization_heat": market["serialization_heat"],
            "market_pressure": market["market_pressure"],
            "reader_exit_risk": market["reader_exit_risk"],
        }
    )
    market["market_signals"] = market["market_signals"][-8:]

    serialization["market_fit"] = _clamp(
        market["reader_trust"] // 2
        + market["bingeability"] // 3
        + market["serialization_heat"] // 3
        + int(pacing_mode in {"aggressive", "spiky"})
    )
    serialization["sustainability"] = _clamp(
        serialization.get("sustainability", 5)
        + market["reader_trust"] // 4
        - max(0, market["paywall_pressure"] - market["reader_trust"]) // 2
    )
    serialization["retention_pressure"] = _clamp(
        serialization.get("retention_pressure", 5)
        + market["serialization_heat"] // 3
        + int(market["bingeability"] >= 7)
    )

    state["story_state_v2"] = story_state
    sync_story_state(state)
    return {
        "market": market,
        "serialization": serialization,
    }


def market_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    market = story_state["market"]
    return {
        "platform_pacing": market.get("platform_pacing"),
        "paywall_pressure": market.get("paywall_pressure"),
        "reader_trust": market.get("reader_trust"),
        "bingeability": market.get("bingeability"),
        "serialization_heat": market.get("serialization_heat"),
        "release_confidence": market.get("release_confidence"),
        "market_pressure": market.get("market_pressure"),
        "reader_exit_risk": market.get("reader_exit_risk"),
        "campaign_roi_signal": market.get("campaign_roi_signal"),
        "market_feedback_active": market.get("market_feedback_active"),
    }
