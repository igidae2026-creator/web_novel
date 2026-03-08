from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from .portfolio_signals import compute_portfolio_signals
from .portfolio_orchestrator import build_portfolio_runtime_snapshot
from .cross_track_release import build_cross_track_release_plan, build_runtime_release_learning_snapshot
from .story_state import ensure_story_state, sync_story_state
from .track_loader import list_track_dirs


def _clamp(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def _track_signature(cfg: Dict[str, Any] | None) -> str:
    cfg = dict(cfg or {})
    project = cfg.get("project", {})
    return f"{project.get('platform', 'unknown')}::{project.get('genre_bucket', 'X')}"


def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path or not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def learn_portfolio_snapshot(tracks_root: str, last_n: int = 8) -> List[Dict[str, Any]]:
    snapshot: List[Dict[str, Any]] = []
    for tdir in list_track_dirs(tracks_root):
        metrics_path = os.path.join(tdir, "outputs", "metrics.jsonl")
        rows = _load_jsonl(metrics_path)[-last_n:]
        if not rows:
            continue
        event_types = [str((row.get("meta", {}) or {}).get("event_plan", {}).get("type", "")).strip() for row in rows]
        event_types = [evt for evt in event_types if evt]
        if not event_types:
            continue
        dominant = max(set(event_types), key=event_types.count)
        mean_ceiling = sum(int((row.get("content_ceiling", {}) or {}).get("ceiling_total", 0) or 0) for row in rows) / len(rows)
        mean_retention = sum(float((row.get("retention", {}) or {}).get("predicted_next_episode", 0.0) or 0.0) for row in rows) / len(rows)
        repetition_scores = [float((row.get("scores", {}) or {}).get("repetition_score", 0.0) or 0.0) for row in rows]
        mean_repetition = sum(repetition_scores) / len(repetition_scores) if repetition_scores else 0.0
        snapshot.append(
            {
                "track": os.path.basename(tdir),
                "pattern": dominant,
                "winning_pattern": dominant if mean_ceiling >= 60 and mean_retention >= 0.6 else "",
                "crowding": min(10, event_types.count(dominant) * 3 + int(mean_repetition >= 0.22) * 2),
                "fatigue": min(10, int(mean_repetition * 10) + int(mean_retention < 0.55) * 3),
                "heat": min(10, int(mean_ceiling / 10) + int(mean_retention * 5)),
            }
        )
    return snapshot


def update_portfolio_memory(
    state: Dict[str, Any],
    cfg: Dict[str, Any] | None = None,
    event_plan: Dict[str, Any] | None = None,
    portfolio_snapshot: List[Dict[str, Any]] | None = None,
    tracks_root: str | None = None,
) -> Dict[str, Any]:
    story_state = ensure_story_state(state, cfg=cfg)
    memory = story_state["portfolio_memory"]
    metrics = story_state["portfolio_metrics"]
    pattern_memory = story_state["pattern_memory"]
    market = story_state["market"]
    serialization = story_state["serialization"]
    event_plan = dict(event_plan or {})
    if portfolio_snapshot is None:
        root = tracks_root or os.path.join("domains", "webnovel", "tracks")
        portfolio_snapshot = learn_portfolio_snapshot(root)
        metrics.update(compute_portfolio_signals(root))
        runtime_snapshot = build_portfolio_runtime_snapshot(root)
        release_snapshot = build_cross_track_release_plan(root)
        runtime_release_snapshot = build_runtime_release_learning_snapshot(root)
    else:
        runtime_snapshot = {"tracks": [], "boost_ready_tracks": 0, "stable_tracks": 0, "mean_portfolio_score": 0.0}
        release_snapshot = {"release_plan": [], "interference_pressure": 0, "platform_clusters": {}, "platform_slot_pressure": {}, "policy_directives": []}
        runtime_release_snapshot = {"track_outcomes": {}, "platform_outcomes": {}}
    portfolio_snapshot = list(portfolio_snapshot or [])

    event_type = str(event_plan.get("type", "")).strip()
    signature = _track_signature(cfg or state.get("_cfg_for_models", {}))
    crowded = set(pattern_memory.get("overused_events", []) or [])
    winners = set(pattern_memory.get("recent_event_types", [])[-2:])
    fatigue = set()

    for item in portfolio_snapshot:
        if int(item.get("heat", 0) or 0) >= 7 and item.get("winning_pattern"):
            winners.add(str(item.get("winning_pattern")))
        if int(item.get("crowding", 0) or 0) >= 7 and item.get("pattern"):
            crowded.add(str(item.get("pattern")))
        if int(item.get("fatigue", 0) or 0) >= 6 and item.get("pattern"):
            fatigue.add(str(item.get("pattern")))

    if event_type and event_type not in crowded:
        winners.add(event_type)

    memory["track_signature"] = signature
    memory["winning_patterns"] = sorted(winners)[:6]
    memory["crowded_patterns"] = sorted(crowded)[:6]
    memory["fatigue_patterns"] = sorted(fatigue)[:6]
    memory["diversity_pressure"] = _clamp(4 + len(crowded) + int(event_type in crowded))
    memory["portfolio_fit"] = _clamp(
        market.get("reader_trust", 5) // 2
        + serialization.get("market_fit", 5) // 2
        + int(event_type in winners)
        - int(event_type in crowded)
    )
    memory["shared_risk_alert"] = _clamp(
        len(crowded) + max(0, 6 - market.get("release_confidence", 5)) // 2
    )
    memory["learned_from_logs"] = bool(portfolio_snapshot)
    memory["observed_tracks"] = len(portfolio_snapshot)
    memory["learning_confidence"] = _clamp(
        len(portfolio_snapshot) * 2 + sum(int(item.get("heat", 0) or 0) >= 7 for item in portfolio_snapshot)
    )
    crowding = int(metrics.get("pattern_crowding", 0) or 0)
    shared_risk = int(metrics.get("shared_risk", 0) or 0)
    novelty_debt = int(metrics.get("novelty_debt", 0) or 0)
    cadence_pressure = int(metrics.get("cadence_pressure", 0) or 0)
    market_overlap = int(metrics.get("market_overlap", 0) or 0)
    release_interference = int(metrics.get("release_timing_interference", 0) or 0)
    memory["coordination_health"] = _clamp(
        9
        - (crowding + shared_risk + market_overlap) // 5
        - max(0, cadence_pressure - 4) // 2
        - max(0, release_interference - 4) // 2
        + min(2, memory["learning_confidence"] // 4)
    )
    memory["novelty_guard"] = _clamp(10 - max(crowding, novelty_debt))
    memory["cadence_guard"] = _clamp(10 - cadence_pressure)
    memory["release_guard"] = _clamp(10 - max(release_interference, market_overlap))
    boost_ready = int(runtime_snapshot.get("boost_ready_tracks", 0) or 0)
    stable_tracks = int(runtime_snapshot.get("stable_tracks", 0) or 0)
    mean_runtime_score = float(runtime_snapshot.get("mean_portfolio_score", 0.0) or 0.0)
    if boost_ready or stable_tracks:
        memory["portfolio_fit"] = _clamp(memory["portfolio_fit"] + min(3, boost_ready + int(mean_runtime_score >= 0.65)))
        memory["coordination_health"] = _clamp(memory["coordination_health"] + min(3, stable_tracks + int(boost_ready >= 2)))
        memory["learning_confidence"] = _clamp(memory["learning_confidence"] + int(mean_runtime_score >= 0.65) + int(boost_ready >= 2))
        memory["shared_risk_alert"] = _clamp(memory["shared_risk_alert"] - int(stable_tracks >= 2))
        memory["release_guard"] = _clamp(memory["release_guard"] + int(stable_tracks >= 2))
    runtime_learning = dict(story_state["portfolio_memory"].get("runtime_release_learning", {}) or {})
    runtime_outcomes = dict(story_state["portfolio_memory"].get("runtime_outcome_memory", {}) or {})
    observed_runtime = sum(int((item or {}).get("observed", 0) or 0) for item in list(runtime_release_snapshot.get("track_outcomes", {}).values()))
    if observed_runtime:
        mean_success = sum(float((item or {}).get("success", 0.0) or 0.0) for item in list(runtime_release_snapshot.get("track_outcomes", {}).values())) / max(1, len(runtime_release_snapshot.get("track_outcomes", {})))
        mean_trust = sum(float((item or {}).get("trust", 0.0) or 0.0) for item in list(runtime_release_snapshot.get("track_outcomes", {}).values())) / max(1, len(runtime_release_snapshot.get("track_outcomes", {})))
        mean_fatigue = sum(float((item or {}).get("fatigue", 0.0) or 0.0) for item in list(runtime_release_snapshot.get("track_outcomes", {}).values())) / max(1, len(runtime_release_snapshot.get("track_outcomes", {})))
        mean_coordination = sum(float((item or {}).get("coordination", 0.0) or 0.0) for item in list(runtime_release_snapshot.get("track_outcomes", {}).values())) / max(1, len(runtime_release_snapshot.get("track_outcomes", {})))
        runtime_learning["observed"] = int(runtime_learning.get("observed", 0) or 0) + observed_runtime
        runtime_learning["retention_signal"] = round(max(float(runtime_learning.get("retention_signal", 0.0) or 0.0), mean_success), 4)
        runtime_learning["trust_signal"] = round(max(float(runtime_learning.get("trust_signal", 0.0) or 0.0), mean_trust), 4)
        runtime_learning["fatigue_signal"] = round(max(float(runtime_learning.get("fatigue_signal", 0.0) or 0.0), mean_fatigue), 4)
        runtime_learning["coordination_signal"] = round(max(float(runtime_learning.get("coordination_signal", 0.0) or 0.0), mean_coordination), 4)
        runtime_outcomes = {
            "retention_signal": round(mean_success, 4),
            "pacing_signal": round(sum(float((item or {}).get("pacing_health", 0.0) or 0.0) for item in list(runtime_release_snapshot.get("track_outcomes", {}).values())) / max(1, len(runtime_release_snapshot.get("track_outcomes", {}))), 4),
            "trust_signal": round(mean_trust, 4),
            "fatigue_signal": round(mean_fatigue, 4),
            "coordination_signal": round(mean_coordination, 4),
            "observed": observed_runtime,
        }
        memory["learning_confidence"] = _clamp(memory["learning_confidence"] + min(3, observed_runtime // 2 + int(mean_success >= 0.7)))
        memory["release_guard"] = _clamp(memory["release_guard"] + int(mean_trust >= 0.72) - int(mean_fatigue >= 0.2))
        memory["cadence_guard"] = _clamp(memory["cadence_guard"] + int(runtime_outcomes["pacing_signal"] >= 0.72) - int(mean_fatigue >= 0.24))
        memory["coordination_health"] = _clamp(memory["coordination_health"] + int(mean_coordination >= 0.72))
    memory["runtime_release_learning"] = runtime_learning
    memory["runtime_outcome_memory"] = runtime_outcomes
    release_plan = list(release_snapshot.get("release_plan", []) or [])
    interference_pressure = int(release_snapshot.get("interference_pressure", 0) or 0)
    hold_tracks = sum(1 for item in release_plan if item.get("action") == "hold")
    accelerate_tracks = sum(1 for item in release_plan if item.get("action") == "accelerate")
    memory["release_strategy"] = "staggered" if interference_pressure >= 4 else "focused" if accelerate_tracks >= 1 else "balanced"
    memory["release_plan"] = release_plan[:6]
    slot_pressure = dict(release_snapshot.get("platform_slot_pressure", {}) or {})
    memory["platform_slot_pressure"] = max(slot_pressure.values()) if slot_pressure else 0
    memory["release_guard"] = _clamp(memory["release_guard"] + int(accelerate_tracks >= 1) - int(hold_tracks >= 2))
    memory["shared_risk_alert"] = _clamp(memory["shared_risk_alert"] + int(interference_pressure >= 6))
    directives: List[str] = []
    if crowding >= 6 or novelty_debt >= 6:
        directives.append("과밀 이벤트 패턴을 피하고 변주 또는 대체 보상 구조를 선택한다")
    if shared_risk >= 6:
        directives.append("여러 트랙이 같은 리스크 축에 몰리지 않도록 감정/사회/전략 위험을 분산한다")
    if cadence_pressure >= 6:
        directives.append("회차 압축은 유지하되 연속 폭발 대신 완급을 섞어 연재 피로를 낮춘다")
    if release_interference >= 6 or market_overlap >= 6:
        directives.append("동일 시장 포지션과 출시 타이밍 충돌을 피하도록 차별적 훅과 관계 구도를 강조한다")
    if interference_pressure >= 4:
        directives.append("교차 트랙 릴리스 간섭을 낮추기 위해 강한 트랙은 선행 배치하고 나머지는 간격을 둔다")
    directives.extend([str(item) for item in list(release_snapshot.get("policy_directives", []) or [])[:2]])
    if not directives:
        directives.append("현재 포트폴리오 분산이 안정적이므로 강한 보상과 차별화를 함께 유지한다")
    if boost_ready >= 2:
        directives.append("실로그상 성과가 검증된 트랙에는 공격적 노출을, 피로 누적 트랙에는 안정화 운용을 적용한다")
    memory["slot_policy_directives"] = [str(item) for item in list(release_snapshot.get("policy_directives", []) or [])[:4]]
    memory["policy_directives"] = directives[:4]

    state["story_state_v2"] = story_state
    sync_story_state(state)
    return memory


def portfolio_prompt_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    story_state = ensure_story_state(state)
    memory = story_state["portfolio_memory"]
    return {
        "track_signature": memory.get("track_signature"),
        "winning_patterns": memory.get("winning_patterns", [])[:4],
        "crowded_patterns": memory.get("crowded_patterns", [])[:4],
        "fatigue_patterns": memory.get("fatigue_patterns", [])[:4],
        "diversity_pressure": memory.get("diversity_pressure", 0),
        "portfolio_fit": memory.get("portfolio_fit", 0),
        "shared_risk_alert": memory.get("shared_risk_alert", 0),
        "learned_from_logs": memory.get("learned_from_logs", False),
        "learning_confidence": memory.get("learning_confidence", 0),
        "observed_tracks": memory.get("observed_tracks", 0),
        "coordination_health": memory.get("coordination_health", 0),
        "novelty_guard": memory.get("novelty_guard", 0),
        "cadence_guard": memory.get("cadence_guard", 0),
        "release_guard": memory.get("release_guard", 0),
        "release_strategy": memory.get("release_strategy", "balanced"),
        "release_plan": memory.get("release_plan", [])[:4],
        "platform_slot_pressure": memory.get("platform_slot_pressure", 0),
        "slot_policy_directives": memory.get("slot_policy_directives", [])[:4],
        "policy_directives": memory.get("policy_directives", [])[:4],
        "runtime_release_learning": memory.get("runtime_release_learning", {}),
        "runtime_outcome_memory": memory.get("runtime_outcome_memory", {}),
        "portfolio_metrics": story_state.get("portfolio_metrics", {}),
    }
