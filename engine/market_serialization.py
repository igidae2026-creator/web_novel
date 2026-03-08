from __future__ import annotations

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

    market["platform_pacing"] = pacing_mode
    market["paywall_pressure"] = _clamp(paywall_pressure)
    market["reader_trust"] = _clamp(5 + expectation - max(0, reward_density - 7))
    market["bingeability"] = _clamp(4 + reward_density // 2 + int(tension_target >= 7))
    market["serialization_heat"] = _clamp(4 + int(event_type in {"betrayal", "arrival", "power_shift", "collapse"}) + tension_target // 2)
    market["release_confidence"] = _clamp(market["reader_trust"] + serialization.get("sustainability", 5) // 2 - max(0, paywall_pressure - 6))
    market.setdefault("market_signals", []).append(
        {
            "episode": episode,
            "platform": platform,
            "paywall_pressure": market["paywall_pressure"],
            "reader_trust": market["reader_trust"],
            "serialization_heat": market["serialization_heat"],
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
    }
