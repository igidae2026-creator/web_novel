from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from .track_loader import list_track_dirs

PLATFORM_RELEASE_POLICY = {
    "Munpia": {"primary_slot_cap": 1, "accelerate_retention": 0.70, "fatigue_limit": 0.20, "cadence_floor": 1, "trust_bonus": 0.08},
    "KakaoPage": {"primary_slot_cap": 1, "accelerate_retention": 0.76, "fatigue_limit": 0.18, "cadence_floor": 2, "trust_bonus": 0.10},
    "NaverSeries": {"primary_slot_cap": 1, "accelerate_retention": 0.74, "fatigue_limit": 0.19, "cadence_floor": 2, "trust_bonus": 0.09},
    "DEFAULT": {"primary_slot_cap": 1, "accelerate_retention": 0.72, "fatigue_limit": 0.20, "cadence_floor": 1, "trust_bonus": 0.07},
}

DEFAULT_OUTCOME_MEMORY = {
    "observed": 0,
    "success": 0.0,
    "retention_lift": 0.0,
    "pacing_health": 0.0,
    "trust": 0.0,
    "fatigue": 0.0,
    "coordination": 0.0,
    "window_wins": 0.0,
}


def _load_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return rows
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return rows


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _track_runtime_outcome_memory(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    outcomes = [row.get("runtime_outcome") for row in rows if isinstance(row, dict) and isinstance(row.get("runtime_outcome"), dict)]
    if not outcomes:
        return dict(DEFAULT_OUTCOME_MEMORY)
    observed = len(outcomes)
    return {
        "observed": observed,
        "success": round(sum(float(item.get("success_signal", 0.0) or 0.0) for item in outcomes) / observed, 4),
        "retention_lift": round(sum(float(item.get("retention_signal", 0.0) or 0.0) for item in outcomes) / observed, 4),
        "pacing_health": round(sum(float(item.get("pacing_signal", 0.0) or 0.0) for item in outcomes) / observed, 4),
        "trust": round(sum(float(item.get("trust_signal", 0.0) or 0.0) for item in outcomes) / observed, 4),
        "fatigue": round(sum(float(item.get("fatigue_signal", 0.0) or 0.0) for item in outcomes) / observed, 4),
        "coordination": round(sum(float(item.get("coordination_signal", 0.0) or 0.0) for item in outcomes) / observed, 4),
        "window_wins": round(sum(float(item.get("strong_window", 0.0) or 0.0) for item in outcomes), 4),
    }


def _track_episode_attribution_memory(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    attributions = [row.get("episode_attribution") for row in rows if isinstance(row, dict) and isinstance(row.get("episode_attribution"), dict)]
    if not attributions:
        return {"observed": 0, "retention_signal": 0.0, "pacing_signal": 0.0, "fatigue_signal": 0.0, "payoff_signal": 0.0}
    observed = len(attributions)
    return {
        "observed": observed,
        "retention_signal": round(sum(float(item.get("retention_signal", 0.0) or 0.0) for item in attributions) / observed, 4),
        "pacing_signal": round(sum(float(item.get("pacing_signal", 0.0) or 0.0) for item in attributions) / observed, 4),
        "fatigue_signal": round(sum(float(item.get("fatigue_signal", 0.0) or 0.0) for item in attributions) / observed, 4),
        "payoff_signal": round(sum(float(item.get("payoff_signal", 0.0) or 0.0) for item in attributions) / observed, 4),
    }


def build_runtime_release_learning_snapshot(tracks_root: str, last_n: int = 8) -> Dict[str, Any]:
    by_track: Dict[str, Dict[str, Any]] = {}
    by_platform: Dict[str, Dict[str, float]] = {}
    for track_dir in list_track_dirs(tracks_root):
        track = _load_json(os.path.join(track_dir, "track.json"))
        platform = str((track.get("project", {}) or {}).get("platform", "UNKNOWN") or "UNKNOWN")
        rows = _load_jsonl(os.path.join(track_dir, "outputs", "metrics.jsonl"))[-last_n * 3:]
        memory = _track_runtime_outcome_memory(rows)
        track_key = os.path.basename(track_dir)
        by_track[track_key] = memory
        platform_memory = by_platform.setdefault(platform, {"success": 0.0, "trust": 0.0, "fatigue": 0.0, "coordination": 0.0, "observed": 0.0})
        platform_memory["success"] += float(memory["success"])
        platform_memory["trust"] += float(memory["trust"])
        platform_memory["fatigue"] += float(memory["fatigue"])
        platform_memory["coordination"] += float(memory["coordination"])
        platform_memory["observed"] += 1.0 if memory["observed"] else 0.0
    for platform, memory in by_platform.items():
        observed = max(1.0, float(memory.get("observed", 0.0) or 0.0))
        memory["success"] = round(memory["success"] / observed, 4)
        memory["trust"] = round(memory["trust"] / observed, 4)
        memory["fatigue"] = round(memory["fatigue"] / observed, 4)
        memory["coordination"] = round(memory["coordination"] / observed, 4)
        memory["observed"] = int(observed)
    return {"track_outcomes": by_track, "platform_outcomes": by_platform}


def _build_multi_window_reservations(tracks: List[Dict[str, Any]], windows: int = 3) -> Dict[str, Any]:
    per_platform_window_counts: Dict[str, Dict[int, int]] = {}
    per_track_reserved: Dict[str, int] = {}
    reservations: List[Dict[str, Any]] = []
    for track in tracks:
        platform = str(track.get("platform", "UNKNOWN") or "UNKNOWN")
        adaptive_score = float(track.get("adaptive_score", 0.0) or 0.0)
        monopoly_risk = float((track.get("runtime_learning", {}) or {}).get("window_wins", 0.0) or 0.0)
        episode_payoff = float((track.get("episode_learning", {}) or {}).get("payoff_signal", 0.0) or 0.0)
        coordination = float((track.get("runtime_learning", {}) or {}).get("coordination", 0.0) or 0.0)
        pressure = per_platform_window_counts.setdefault(platform, {})
        best_window = 0
        best_score = -999.0
        for window in range(max(1, int(windows))):
            occupancy_penalty = float(pressure.get(window, 0) or 0) * 0.18
            monopoly_penalty = monopoly_risk * (0.16 if window == 0 else 0.08)
            payoff_bonus = episode_payoff * (0.08 if window == 0 else 0.05)
            coordination_bonus = coordination * (0.06 if window <= 1 else 0.04)
            window_score = adaptive_score + payoff_bonus + coordination_bonus - occupancy_penalty - monopoly_penalty - window * 0.03
            if window_score > best_score:
                best_score = window_score
                best_window = window
        pressure[best_window] = pressure.get(best_window, 0) + 1
        per_track_reserved[str(track.get("track"))] = best_window
        reservations.append(
            {
                "track": str(track.get("track")),
                "platform": platform,
                "window": best_window,
                "reservation_score": round(best_score, 4),
                "reason": "high_value_window" if best_window == 0 else "staggered_balance" if best_window == 1 else "cooldown_balance",
            }
        )
    long_horizon_pressure = {
        platform: max(counts.values()) if counts else 0
        for platform, counts in per_platform_window_counts.items()
    }
    return {
        "reservations": reservations,
        "reservation_map": per_track_reserved,
        "long_horizon_pressure": long_horizon_pressure,
    }


def build_cross_track_release_plan(tracks_root: str, last_n: int = 8) -> Dict[str, Any]:
    runtime_learning = build_runtime_release_learning_snapshot(tracks_root, last_n=last_n)
    tracks: List[Dict[str, Any]] = []
    for track_dir in list_track_dirs(tracks_root):
        track = _load_json(os.path.join(track_dir, "track.json"))
        platform = (track.get("project", {}) or {}).get("platform", "UNKNOWN")
        policy = PLATFORM_RELEASE_POLICY.get(str(platform), PLATFORM_RELEASE_POLICY["DEFAULT"])
        rows = _load_jsonl(os.path.join(track_dir, "outputs", "metrics.jsonl"))[-last_n:]
        track_learning = dict(runtime_learning.get("track_outcomes", {}).get(os.path.basename(track_dir), DEFAULT_OUTCOME_MEMORY) or DEFAULT_OUTCOME_MEMORY)
        platform_learning = dict(runtime_learning.get("platform_outcomes", {}).get(str(platform), {}) or {})
        episode_learning = _track_episode_attribution_memory(rows)
        if rows:
            mean_retention = sum(float((row.get("retention", {}) or {}).get("predicted_next_episode", 0.0) or 0.0) for row in rows) / len(rows)
            mean_repetition = sum(float((row.get("scores", {}) or {}).get("repetition_score", 0.0) or 0.0) for row in rows) / len(rows)
        else:
            mean_retention = 0.0
            mean_repetition = 0.0
        adaptive_score = (
            mean_retention * 0.44
            + float(track_learning.get("success", 0.0) or 0.0) * 0.20
            + float(track_learning.get("trust", 0.0) or 0.0) * 0.10
            + float(track_learning.get("coordination", 0.0) or 0.0) * 0.08
            + float(track_learning.get("retention_lift", 0.0) or 0.0) * 0.08
            + float(episode_learning.get("retention_signal", 0.0) or 0.0) * 0.08
            + float(episode_learning.get("payoff_signal", 0.0) or 0.0) * 0.07
            + float(platform_learning.get("success", 0.0) or 0.0) * 0.05
            - mean_repetition * 0.24
            - float(track_learning.get("fatigue", 0.0) or 0.0) * 0.12
            - float(episode_learning.get("fatigue_signal", 0.0) or 0.0) * 0.12
            - min(0.35, float(track_learning.get("window_wins", 0.0) or 0.0) * 0.08)
        )
        tracks.append(
            {
                "track": os.path.basename(track_dir),
                "platform": platform,
                "bucket": (track.get("project", {}) or {}).get("genre_bucket", "UNKNOWN"),
                "mean_retention": mean_retention,
                "fatigue": mean_repetition,
                "policy": policy,
                "adaptive_score": round(adaptive_score, 4),
                "runtime_learning": track_learning,
                "episode_learning": episode_learning,
            }
        )
    tracks.sort(key=lambda item: (item["platform"], -item["adaptive_score"], -item["mean_retention"], item["fatigue"], item["track"]))
    reservation_state = _build_multi_window_reservations(tracks)
    reservation_map = dict(reservation_state.get("reservation_map", {}) or {})
    per_platform_slot: Dict[str, int] = {}
    release_plan: List[Dict[str, Any]] = []
    interference = 0
    platform_slot_pressure: Dict[str, int] = {}
    policy_directives: List[str] = []
    for track in tracks:
        platform = str(track["platform"])
        policy = dict(track.get("policy", {}) or PLATFORM_RELEASE_POLICY["DEFAULT"])
        slot = per_platform_slot.get(platform, 0)
        per_platform_slot[platform] = slot + 1
        platform_slot_pressure[platform] = max(platform_slot_pressure.get(platform, 0), max(0, slot + 1 - int(policy.get("primary_slot_cap", 1) or 1)))
        learned_fatigue = float((track.get("runtime_learning", {}) or {}).get("fatigue", 0.0) or 0.0)
        learned_success = float((track.get("runtime_learning", {}) or {}).get("success", 0.0) or 0.0)
        learned_trust = float((track.get("runtime_learning", {}) or {}).get("trust", 0.0) or 0.0)
        monopoly_risk = float((track.get("runtime_learning", {}) or {}).get("window_wins", 0.0) or 0.0)
        episode_fatigue = float((track.get("episode_learning", {}) or {}).get("fatigue_signal", 0.0) or 0.0)
        reserved_window = int(reservation_map.get(str(track.get("track")), 0) or 0)
        if track["fatigue"] + learned_fatigue * 0.25 + episode_fatigue * 0.15 >= float(policy.get("fatigue_limit", 0.20) or 0.20):
            action = "hold"
        elif reserved_window >= 2:
            action = "hold"
        elif reserved_window == 1:
            action = "stagger"
        elif slot < int(policy.get("primary_slot_cap", 1) or 1) and track["mean_retention"] + learned_success * 0.08 + float((track.get("episode_learning", {}) or {}).get("retention_signal", 0.0) or 0.0) * 0.05 >= float(policy.get("accelerate_retention", 0.72) or 0.72) and monopoly_risk < 2.2:
            action = "accelerate"
        elif slot == 0 and learned_trust >= 0.72 and learned_success >= 0.68:
            action = "accelerate"
        else:
            action = "stagger"
        if slot >= 1:
            interference += 1
        if slot == 0 and monopoly_risk >= 2.2 and action == "accelerate":
            action = "stagger"
        release_plan.append(
            {
                "track": track["track"],
                "platform": platform,
                "slot_offset": slot,
                "action": action,
                "cadence_floor": int(policy.get("cadence_floor", 1) or 1),
                "slot_pressure": platform_slot_pressure[platform],
                "adaptive_score": track["adaptive_score"],
                "runtime_learning": dict(track.get("runtime_learning", {}) or {}),
                "episode_learning": dict(track.get("episode_learning", {}) or {}),
                "reserved_window": reserved_window,
            }
        )
        if platform_slot_pressure[platform] >= 1:
            directive = f"{platform} 슬롯 과밀을 피하기 위해 강한 트랙도 동일 윈도우에 집중 배치하지 않는다"
            if directive not in policy_directives:
                policy_directives.append(directive)
        if action == "hold":
            directive = f"{platform}에서는 피로 누적 트랙의 신뢰 하락을 막기 위해 홀드 후 재배치한다"
            if directive not in policy_directives:
                policy_directives.append(directive)
        if monopoly_risk >= 2.2:
            directive = f"{platform} 강세 트랙 독점을 막기 위해 최근 강창구 승리 기록이 높은 트랙은 우선 stagger로 완충한다"
            if directive not in policy_directives:
                policy_directives.append(directive)
    return {
        "release_plan": release_plan,
        "interference_pressure": min(10, interference * 2),
        "platform_clusters": {platform: count for platform, count in per_platform_slot.items()},
        "platform_slot_pressure": platform_slot_pressure,
        "policy_directives": policy_directives[:4],
        "runtime_learning": runtime_learning,
        "window_reservations": reservation_state.get("reservations", []),
        "long_horizon_pressure": reservation_state.get("long_horizon_pressure", {}),
    }


def refresh_queue_release_runtime(queue_state: Dict[str, Any], tracks_root: str) -> Dict[str, Any]:
    queue_state = dict(queue_state or {})
    plan = build_cross_track_release_plan(tracks_root)
    runtime: Dict[str, Dict[str, Any]] = {}
    for item in plan.get("release_plan", []) or []:
        runtime[str(item.get("track"))] = {
            "action": str(item.get("action", "stagger") or "stagger"),
            "slot_offset": int(item.get("slot_offset", 0) or 0),
            "hold_budget": 1 if item.get("action") == "hold" else 0,
            "accelerate_budget": 1 if item.get("action") == "accelerate" else 0,
            "executed": 0,
        }
    queue_state["release_runtime"] = runtime
    queue_state["release_runtime_meta"] = {
        "interference_pressure": int(plan.get("interference_pressure", 0) or 0),
        "platform_clusters": dict(plan.get("platform_clusters", {}) or {}),
    }
    return queue_state


def resolve_queue_release_action(queue_state: Dict[str, Any], track_dir: str) -> Dict[str, Any]:
    queue_state = dict(queue_state or {})
    runtime = dict(queue_state.get("release_runtime", {}) or {})
    entry = dict(runtime.get(os.path.basename(track_dir), {}) or {})
    if not entry:
        return {"action": "stagger", "slot_offset": 0, "hold_budget": 0, "accelerate_budget": 0}
    if int(entry.get("hold_budget", 0) or 0) > 0:
        return entry
    if int(entry.get("accelerate_budget", 0) or 0) > 0:
        return entry
    entry["action"] = "stagger"
    return entry


def apply_queue_release_outcome(queue_state: Dict[str, Any], track_dir: str, executed: bool) -> Dict[str, Any]:
    queue_state = dict(queue_state or {})
    runtime = dict(queue_state.get("release_runtime", {}) or {})
    key = os.path.basename(track_dir)
    entry = dict(runtime.get(key, {}) or {})
    action = str(entry.get("action", "stagger") or "stagger")
    should_advance = True
    alignment = 0.55
    if action == "hold":
        entry["hold_budget"] = max(0, int(entry.get("hold_budget", 0) or 0) - 1)
        should_advance = True
        alignment = 0.78
    elif action == "accelerate" and executed and int(entry.get("accelerate_budget", 0) or 0) > 0:
        entry["accelerate_budget"] = max(0, int(entry.get("accelerate_budget", 0) or 0) - 1)
        entry["executed"] = int(entry.get("executed", 0) or 0) + 1
        should_advance = False
        alignment = 0.9
    elif action == "accelerate":
        should_advance = True
        alignment = 0.75
    else:
        alignment = 0.7
    runtime[key] = entry
    success_signal = _clamp(
        alignment * 0.55
        + (0.20 if action == "accelerate" and executed else 0.14 if action == "hold" and not executed else 0.12)
        - min(0.15, int(entry.get("slot_offset", 0) or 0) * 0.05)
    )
    retention_signal = _clamp(alignment * 0.7 + (0.12 if action == "accelerate" and executed else 0.08 if action == "stagger" else 0.10))
    pacing_signal = _clamp(0.68 if action == "hold" else 0.74 if action == "stagger" else 0.8 - int(entry.get("executed", 0) or 0) * 0.04)
    trust_signal = _clamp(alignment * 0.65 + (0.14 if action == "hold" else 0.08 if action == "stagger" else 0.10))
    fatigue_signal = _clamp((0.18 if action == "accelerate" and executed else 0.08 if action == "stagger" else 0.04) + int(entry.get("executed", 0) or 0) * 0.03)
    coordination_signal = _clamp(0.78 - int(entry.get("slot_offset", 0) or 0) * 0.08 + (0.04 if action != "accelerate" else 0.0))
    strong_window = 1.0 if action == "accelerate" and int(entry.get("slot_offset", 0) or 0) == 0 else 0.0
    runtime_outcome = {
        "track": key,
        "action": action,
        "alignment": alignment,
        "executed": bool(executed),
        "slot_offset": int(entry.get("slot_offset", 0) or 0),
        "success_signal": round(success_signal, 4),
        "retention_signal": round(retention_signal, 4),
        "pacing_signal": round(pacing_signal, 4),
        "trust_signal": round(trust_signal, 4),
        "fatigue_signal": round(fatigue_signal, 4),
        "coordination_signal": round(coordination_signal, 4),
        "strong_window": strong_window,
    }
    queue_state["release_runtime"] = runtime
    queue_state["last_release_action"] = {
        "track": key,
        "action": action,
        "alignment": alignment,
        "executed": bool(executed),
        "slot_offset": int(entry.get("slot_offset", 0) or 0),
    }
    history = list(queue_state.get("release_outcomes", []) or [])
    history.append(runtime_outcome)
    queue_state["release_outcomes"] = history[-24:]
    queue_state["runtime_release_learning"] = {
        "observed": len(queue_state["release_outcomes"]),
        "latest_outcome": runtime_outcome,
    }
    return {"queue_state": queue_state, "should_advance": should_advance, "runtime_action": queue_state["last_release_action"], "runtime_outcome": runtime_outcome}


def apply_runtime_release_to_state(state_data: Dict[str, Any], runtime_action: Dict[str, Any]) -> Dict[str, Any]:
    story_state = state_data.setdefault("story_state_v2", {})
    control = story_state.setdefault("control", {})
    runtime = control.setdefault("runtime_release", {
        "action": "balanced",
        "alignment": 0.0,
        "slot_offset": 0,
        "hold_budget": 0,
        "accelerate_budget": 0,
        "history": [],
    })
    memory = story_state.setdefault("portfolio_memory", {})
    runtime.update(
        {
            "action": str(runtime_action.get("action", "balanced") or "balanced"),
            "alignment": float(runtime_action.get("alignment", 0.0) or 0.0),
            "slot_offset": int(runtime_action.get("slot_offset", 0) or 0),
            "hold_budget": int(runtime_action.get("hold_budget", 0) or 0),
            "accelerate_budget": int(runtime_action.get("accelerate_budget", 0) or 0),
            "history": (list(runtime.get("history", []) or []) + [dict(runtime_action)])[-6:],
        }
    )
    memory["release_strategy"] = "focused" if runtime["action"] == "accelerate" else "staggered" if runtime["action"] == "hold" else memory.get("release_strategy", "balanced")
    memory["release_guard"] = min(10, max(0, int(memory.get("release_guard", 5) or 5) + int(runtime["alignment"] >= 0.75)))
    return runtime


def learn_runtime_release_outcome_in_state(state_data: Dict[str, Any], runtime_outcome: Dict[str, Any]) -> Dict[str, Any]:
    story_state = state_data.setdefault("story_state_v2", {})
    control = story_state.setdefault("control", {})
    runtime = control.setdefault("runtime_release", {
        "action": "balanced",
        "alignment": 0.0,
        "slot_offset": 0,
        "hold_budget": 0,
        "accelerate_budget": 0,
        "history": [],
        "outcome_history": [],
    })
    memory = story_state.setdefault("portfolio_memory", {})
    learning = dict(memory.get("runtime_release_learning", {}) or {})
    action_scores = dict(learning.get("action_scores", {"accelerate": 0.5, "stagger": 0.5, "hold": 0.5}) or {"accelerate": 0.5, "stagger": 0.5, "hold": 0.5})
    observed = int(learning.get("observed", 0) or 0) + 1
    action = str(runtime_outcome.get("action", "stagger") or "stagger")
    success_signal = float(runtime_outcome.get("success_signal", 0.0) or 0.0)
    prior_action_score = float(action_scores.get(action, 0.5) or 0.5)
    action_scores[action] = round(prior_action_score * 0.7 + success_signal * 0.3, 4)
    blend = 0.0 if observed == 1 else 0.65
    learning.update(
        {
            "observed": observed,
            "action_scores": action_scores,
            "retention_signal": round(float(learning.get("retention_signal", 0.0) or 0.0) * blend + float(runtime_outcome.get("retention_signal", 0.0) or 0.0) * (1.0 - blend), 4),
            "pacing_signal": round(float(learning.get("pacing_signal", 0.0) or 0.0) * blend + float(runtime_outcome.get("pacing_signal", 0.0) or 0.0) * (1.0 - blend), 4),
            "trust_signal": round(float(learning.get("trust_signal", 0.0) or 0.0) * blend + float(runtime_outcome.get("trust_signal", 0.0) or 0.0) * (1.0 - blend), 4),
            "fatigue_signal": round(float(learning.get("fatigue_signal", 0.0) or 0.0) * blend + float(runtime_outcome.get("fatigue_signal", 0.0) or 0.0) * (1.0 - blend), 4),
            "coordination_signal": round(float(learning.get("coordination_signal", 0.0) or 0.0) * blend + float(runtime_outcome.get("coordination_signal", 0.0) or 0.0) * (1.0 - blend), 4),
            "last_outcome": dict(runtime_outcome),
        }
    )
    memory["runtime_release_learning"] = learning
    memory["runtime_outcome_memory"] = {
        "retention_signal": learning["retention_signal"],
        "pacing_signal": learning["pacing_signal"],
        "trust_signal": learning["trust_signal"],
        "fatigue_signal": learning["fatigue_signal"],
        "coordination_signal": learning["coordination_signal"],
        "observed": observed,
    }
    memory["release_guard"] = min(10, max(0, int(memory.get("release_guard", 5) or 5) + int(learning["trust_signal"] >= 0.72) - int(learning["fatigue_signal"] >= 0.22)))
    memory["cadence_guard"] = min(10, max(0, int(memory.get("cadence_guard", 5) or 5) + int(learning["pacing_signal"] >= 0.72) - int(learning["fatigue_signal"] >= 0.24)))
    memory["coordination_health"] = min(10, max(0, int(memory.get("coordination_health", 5) or 5) + int(learning["coordination_signal"] >= 0.72) - int(int(runtime_outcome.get("slot_offset", 0) or 0) >= 2)))
    if learning["fatigue_signal"] >= 0.22 and memory.get("release_strategy") == "focused":
        memory["release_strategy"] = "balanced"
    runtime["outcome_history"] = (list(runtime.get("outcome_history", []) or []) + [dict(runtime_outcome)])[-8:]
    return learning
