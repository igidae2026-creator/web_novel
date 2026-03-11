from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


EVENT_TYPES = [
    "reveal",
    "betrayal",
    "reversal",
    "loss",
    "arrival",
    "sacrifice",
    "timer",
    "power_shift",
    "false_victory",
    "collapse",
    "misunderstanding",
]


def _clamp_int(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, int(value)))


def _genre_defaults(bucket: str | None) -> Dict[str, str]:
    presets = {
        "A": {
            "desire": "압도적 성장을 통해 무시당하던 질서를 뒤집는다",
            "fear": "결정적 순간에 약자로 되돌아간다",
            "wound": "무력했던 과거의 낙인",
            "lie": "강해지기만 하면 관계도 세계도 통제할 수 있다",
        },
        "B": {
            "desire": "숨겨진 진실을 해독해 자신의 상실을 되찾는다",
            "fear": "진실이 자신을 먼저 파괴한다",
            "wound": "배신당한 기억과 신뢰 붕괴",
            "lie": "누구도 믿지 않으면 상처받지 않는다",
        },
    }
    return presets.get(str(bucket or "").upper(), {
        "desire": "소중한 것을 지키면서 더 큰 자리를 차지한다",
        "fear": "가장 중요한 관계와 기회를 동시에 잃는다",
        "wound": "이전 실패에서 생긴 수치와 결핍",
        "lie": "먼저 밀어붙여야만 살아남는다",
    })


def _infer_anchor(outline: str) -> str:
    first = next((line.strip() for line in (outline or "").splitlines() if line.strip()), "")
    return first[:80] if first else "주인공"


def _default_story_state(bucket: str | None, outline: str) -> Dict[str, Any]:
    defaults = _genre_defaults(bucket)
    anchor = _infer_anchor(outline)
    return {
        "schema_version": 2,
        "cast": {
            "protagonist": {
                "id": "protagonist",
                "label": anchor,
                "role": "protagonist",
                "desire": defaults["desire"],
                "fear": defaults["fear"],
                "wound": defaults["wound"],
                "lie": defaults["lie"],
                "moral_limit": "무고한 이를 버리고 도망치지는 않는다",
                "obsession": "자신의 가치를 증명하는 승리",
                "contradiction": "지배를 원하지만 진짜로 원하는 것은 인정과 유대다",
                "surface_goal": "이번 회차 안에 밀린 주도권을 되찾는다",
                "inner_need": "힘이 아니라 관계와 선택의 책임을 받아들인다",
                "urgency": 6,
                "decision_pressure": 6,
                "backlash": 0,
                "progress": 0,
                "emotion": "pressed",
            },
            "rival": {
                "id": "rival",
                "label": "가장 위협적인 경쟁자",
                "role": "rival",
                "desire": "주인공보다 먼저 판을 장악한다",
                "fear": "주인공의 성장으로 입지를 잃는다",
                "wound": "한 번 밀리면 끝장난다는 공포",
                "lie": "상처를 깊게 주면 복종이 따라온다",
                "moral_limit": "공개적 굴욕 없이는 만족하지 못한다",
                "obsession": "주도권 독점",
                "contradiction": "우월감을 내세우지만 실제론 인정 결핍이 크다",
                "surface_goal": "주인공이 다음 선택에서 더 큰 대가를 치르게 만든다",
                "inner_need": "통제 아닌 설득의 힘을 배운다",
                "urgency": 5,
                "decision_pressure": 5,
                "backlash": 0,
                "progress": 0,
                "emotion": "predatory",
            },
            "ally": {
                "id": "ally",
                "label": "주인공을 돕지만 완전히 믿지 않는 조력자",
                "role": "ally",
                "desire": "자기 생존과 주인공 지원을 동시에 지킨다",
                "fear": "주인공 편에 섰다가 함께 추락한다",
                "wound": "한 번의 오판으로 잃은 사람",
                "lie": "거리를 유지해야 안전하다",
                "moral_limit": "쓸모 없는 희생은 거부한다",
                "obsession": "피해 최소화",
                "contradiction": "냉정한 척하지만 가장 먼저 돌아본다",
                "surface_goal": "이번 회차에서는 정보를 통제해 피해를 줄인다",
                "inner_need": "계산보다 신뢰를 택할 순간을 받아들인다",
                "urgency": 4,
                "decision_pressure": 4,
                "backlash": 0,
                "progress": 0,
                "emotion": "guarded",
            },
        },
        "relationships": {
            "protagonist:rival": {
                "pair": ["protagonist", "rival"],
                "charge": -7,
                "trust": 1,
                "dependency": 3,
                "relationship_debt": 5,
                "chemistry": 6,
                "volatile": True,
                "label": "적대적 집착",
            },
            "protagonist:ally": {
                "pair": ["protagonist", "ally"],
                "charge": 4,
                "trust": 5,
                "dependency": 6,
                "relationship_debt": 3,
                "chemistry": 5,
                "volatile": True,
                "label": "불완전한 동맹",
            },
        },
        "world": {
            "order": 6,
            "instability": 4,
            "change_rate": 3,
            "power_rules": [
                "힘의 사용은 대가를 남긴다",
                "승리할수록 더 큰 세력이 개입한다",
            ],
            "factions": [
                {"id": "incumbent", "pressure": 6, "stance": "hostile"},
                {"id": "shadow_network", "pressure": 4, "stance": "opportunistic"},
            ],
            "active_timers": [],
            "recent_changes": [],
        },
        "conflict": {
            "threads": [
                {
                    "id": "main-survival-thread",
                    "label": "주인공이 밀리면 판 전체를 잃는 주 갈등",
                    "stake": "지위와 생존",
                    "consequence": "주도권 상실과 보호 대상 붕괴",
                    "status": "open",
                    "heat": 6,
                    "irreversible_if_lost": "핵심 관계 하나가 적으로 돌아선다",
                }
            ],
            "threat_pressure": 5,
            "consequence_level": 5,
            "opposition_advantage": 4,
            "payoff_debt": 3,
            "risk_distribution": {
                "physical": 5,
                "social": 6,
                "moral": 4,
                "strategic": 5,
            },
            "escalation_mode": "complication",
            "tension_reservoir": 6,
        },
        "antagonist": {
            "master_intent": "주인공이 스스로 관계와 권력을 잃는 선택을 하게 만든다",
            "campaign_phase": "probing",
            "next_move": "주인공의 약점을 시험한다",
            "contingency": "직접 충돌이 실패하면 조력자를 흔든다",
            "pressure_clock": 4,
            "foresight": 6,
            "horizon_beats": [
                "주인공의 약점을 대중 앞에 드러낸다",
                "조력자와 주인공 사이에 불신을 심는다",
                "힘의 규칙을 자신에게 유리하게 재정의한다",
            ],
        },
        "unresolved_threads": [
            {
                "id": "main-survival-thread",
                "question": "주인공은 이번 열세를 뒤집고 관계 붕괴를 막을 수 있는가",
                "pressure": 7,
                "promised_payoff": "주도권 회복 또는 더 큰 추락",
            }
        ],
        "pacing": {
            "target_band": "pressure",
            "target_tension": 7,
            "current_tension": 6,
            "release_debt": 0,
            "spike_debt": 1,
            "rhythm_window": ["pressure", "release", "pressure"],
            "last_cliffhanger_strength": 6,
        },
        "rewards": {
            "pending_promises": [
                "주인공의 숨겨진 약점 정체 공개",
                "라이벌과의 힘 규칙 충돌",
            ],
            "delivered_rewards": [],
            "reward_density": 5,
            "expectation_alignment": 6,
            "power_integrity": 7,
        },
        "serialization": {
            "retention_pressure": 6,
            "chemistry_signal": 6,
            "novelty_budget": 5,
            "sustainability": 6,
            "market_fit": 5,
            "exploration_budget": 4,
        },
        "promise_graph": {
            "active_promises": [],
            "resolved_promises": [],
            "character_promises": {},
            "dependency_edges": [],
            "weighted_dependency_graph": {},
            "payoff_corruption_flags": [],
            "unresolved_count": 0,
            "resolution_rate": 0.0,
            "payoff_integrity": 0.0,
            "episode_history": [],
        },
        "market": {
            "platform_pacing": "balanced",
            "paywall_pressure": 4,
            "reader_trust": 6,
            "bingeability": 5,
            "serialization_heat": 5,
            "release_confidence": 5,
            "market_signals": [],
        },
        "information": {
            "hidden_truths": [
                "주인공의 약점은 외부가 아니라 내부 계약에 있다",
            ],
            "revealed_truths": [],
            "foreshadow_queue": [
                "조력자의 망설임이 훗날 배신처럼 보일 수 있다",
            ],
            "dramatic_irony": 4,
            "emotional_reservoir": 5,
        },
        "pattern_memory": {
            "recent_event_types": [],
            "recent_cliffhanger_modes": [],
            "event_counts": {},
            "overused_events": [],
            "exploration_bias": 4,
            "market_resonance": 5,
        },
        "portfolio_memory": {
            "track_signature": "default",
            "winning_patterns": [],
            "crowded_patterns": [],
            "fatigue_patterns": [],
            "diversity_pressure": 5,
            "portfolio_fit": 5,
            "shared_risk_alert": 3,
            "learned_from_logs": False,
            "learning_confidence": 0,
            "observed_tracks": 0,
            "coordination_health": 5,
            "novelty_guard": 5,
            "cadence_guard": 5,
            "release_guard": 5,
            "release_strategy": "balanced",
            "release_plan": [],
            "window_reservations": [],
            "long_horizon_pressure": 0,
            "platform_slot_pressure": 0,
            "slot_policy_directives": [],
            "policy_directives": [],
            "runtime_release_learning": {
                "observed": 0,
                "action_scores": {"accelerate": 0.5, "stagger": 0.5, "hold": 0.5},
                "retention_signal": 0.0,
                "pacing_signal": 0.0,
                "trust_signal": 0.0,
                "fatigue_signal": 0.0,
                "coordination_signal": 0.0,
                "last_outcome": {},
            },
            "runtime_outcome_memory": {
                "retention_signal": 0.0,
                "pacing_signal": 0.0,
                "trust_signal": 0.0,
                "fatigue_signal": 0.0,
                "coordination_signal": 0.0,
                "observed": 0,
            },
            "episode_attribution_memory": {
                "observed": 0,
                "retention_signal": 0.0,
                "pacing_signal": 0.0,
                "fatigue_signal": 0.0,
                "payoff_signal": 0.0,
            },
        },
        "portfolio_metrics": {
            "pattern_crowding": 0,
            "shared_risk": 0,
            "novelty_debt": 0,
            "cadence_pressure": 0,
            "market_overlap": 0,
            "release_timing_interference": 0,
        },
        "history": {
            "events": [],
            "outcomes": [],
            "world_shifts": [],
            "episode_summaries": [],
        },
        "control": {
            "last_event_type": "",
            "last_cliffhanger_mode": "",
            "regression_flags": [],
            "runtime_release": {
                "action": "balanced",
                "alignment": 0.0,
                "slot_offset": 0,
                "hold_budget": 0,
                "accelerate_budget": 0,
                "history": [],
                "outcome_history": [],
            },
            "episode_attribution": {
                "latest": {},
                "history": [],
            },
            "reader_quality": {
                "hook_debt": 0.0,
                "payoff_debt": 0.0,
                "fatigue_debt": 0.0,
                "retention_debt": 0.0,
                "thinness_debt": 0.0,
                "repetition_debt": 0.0,
                "deja_vu_debt": 0.0,
                "fake_urgency_debt": 0.0,
                "compression_debt": 0.0,
                "history": [],
            },
            "soak_history": {
                "observed": 0,
                "steady_noop_ratio": 0.0,
                "dominant_mode": "unknown",
                "quality_lift_trend": 1.0,
                "history": [],
            },
            "arc_pressure": {
                "payoff_debt": 0.0,
                "momentum_debt": 0.0,
                "history": [],
            },
            "final_threshold_history": {
                "observed": 0,
                "ready_ratio": 0.0,
                "recent_fail_ratio": 0.0,
                "history": [],
            },
            "causal_repair": {
                "critical_issues": [],
                "directives": [],
                "repair_confidence": 5,
                "retry_budget": 0,
                "attempts_used": 0,
                "status": "idle",
                "closure_score": 0.0,
                "strategy_key": "baseline",
                "strategy_coverage": 0.0,
                "failed_strategies": [],
                "next_strategy_shift": "",
                "defect_resolution_score": 0.0,
                "strategy_effectiveness": {},
                "diff_audit": {
                    "mismatch_type": "untracked",
                    "resolved_targets": [],
                    "persistent_targets": [],
                    "new_issues": [],
                    "lexical_shift": 0.0,
                    "score_delta": 0.0,
                    "defect_resolution_score": 0.0,
                    "semantic_audit": {
                        "pre_scene_signature": {"sentence_count": 0, "roles": [], "dominant_roles": [], "role_counts": {}},
                        "post_scene_signature": {"sentence_count": 0, "roles": [], "dominant_roles": [], "role_counts": {}},
                        "structure_overlap": 0.0,
                        "intent_overlap": 0.0,
                        "intent_preservation_score": 0.0,
                        "semantic_failure_types": [],
                        "semantic_failures": [],
                        "semantic_repair_effectiveness": 0.0,
                    },
                },
                "semantic_audit": {
                    "intent_preservation_score": 0.0,
                    "semantic_failure_types": [],
                    "semantic_repair_effectiveness": 0.0,
                },
                "history": [],
            },
        },
        "system_status": {
            "iteration_state": "idle",
            "balanced_total_history": [],
            "axis_history": {},
            "repair_rate_history": [],
            "portfolio_signal_history": [],
            "drift": {},
            "axis_drift": {},
            "warnings": [],
            "rollback_signal": False,
        },
    }


def ensure_story_state(
    state: Dict[str, Any],
    cfg: Dict[str, Any] | None = None,
    outline: str = "",
) -> Dict[str, Any]:
    bucket = None
    if isinstance(cfg, dict):
        bucket = cfg.get("project", {}).get("genre_bucket")

    story_state = state.get("story_state_v2")
    if not isinstance(story_state, dict):
        story_state = _default_story_state(bucket, outline)
        _migrate_legacy_state(story_state, state)
        state["story_state_v2"] = story_state
    else:
        base = _default_story_state(bucket, outline)
        story_state = _deep_merge(base, story_state)
        _migrate_legacy_state(story_state, state)
        state["story_state_v2"] = story_state

    _sync_legacy_aliases(state)
    return story_state


def sync_story_state(state: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(state.get("story_state_v2"), dict):
        return ensure_story_state(state)
    _sync_legacy_aliases(state)
    return state["story_state_v2"]


def _deep_merge(base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(base)
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _sync_legacy_aliases(state: Dict[str, Any]) -> None:
    story_state = state.get("story_state_v2", {})
    cast = story_state.get("cast", {})
    relationships = story_state.get("relationships", {})
    conflict = story_state.get("conflict", {})
    pacing = story_state.get("pacing", {})
    serialization = story_state.get("serialization", {})

    protagonist = cast.get("protagonist", {})
    rival = cast.get("rival", {})
    rival_edge = relationships.get("protagonist:rival", {})

    state["character_arcs"] = {
        "anchor": protagonist.get("label", "주인공"),
        "protagonist": {
            "label": protagonist.get("label", "protagonist"),
            "anchor": protagonist.get("label", "주인공"),
            "core_desire": protagonist.get("desire"),
            "surface_goal": protagonist.get("surface_goal"),
            "fear_trigger": protagonist.get("fear"),
            "weakness": protagonist.get("wound"),
            "misbelief": protagonist.get("lie"),
            "urgency": protagonist.get("urgency"),
            "relationship_pressure": rival_edge.get("relationship_debt", 0),
            "progress": protagonist.get("progress", 0),
            "backlash": protagonist.get("backlash", 0),
            "decision_pressure": protagonist.get("decision_pressure", 0),
            "dominant_need": protagonist.get("inner_need", ""),
            "last_outcome": state.get("story_state_v2", {}).get("history", {}).get("outcomes", ["unresolved"])[-1] if story_state.get("history", {}).get("outcomes") else "unresolved",
        },
        "rival": {
            "label": rival.get("label", "rival"),
            "anchor": rival.get("label", "rival"),
            "core_desire": rival.get("desire"),
            "surface_goal": rival.get("surface_goal"),
            "fear_trigger": rival.get("fear"),
            "weakness": rival.get("wound"),
            "misbelief": rival.get("lie"),
            "urgency": rival.get("urgency", 0),
            "relationship_pressure": rival_edge.get("relationship_debt", 0),
            "progress": rival.get("progress", 0),
            "backlash": rival.get("backlash", 0),
            "decision_pressure": rival.get("decision_pressure", 0),
            "dominant_need": rival.get("inner_need", ""),
            "last_outcome": "pressing",
        },
    }
    state["conflict_engine"] = {
        "threads": conflict.get("threads", []),
        "threat_pressure": conflict.get("threat_pressure", 0),
        "consequence_level": conflict.get("consequence_level", 0),
        "recent_losses": sum(1 for event in story_state.get("history", {}).get("events", [])[-5:] if event in {"loss", "collapse", "sacrifice"}),
        "recent_reversals": sum(1 for event in story_state.get("history", {}).get("events", [])[-5:] if event in {"reversal", "power_shift", "false_victory"}),
        "opposition_advantage": conflict.get("opposition_advantage", 0),
        "payoff_debt": conflict.get("payoff_debt", 0),
        "escalation_mode": conflict.get("escalation_mode", "complication"),
        "last_event_type": story_state.get("control", {}).get("last_event_type", ""),
        "open_thread_count": len([thread for thread in conflict.get("threads", []) if thread.get("status") != "resolved"]),
    }
    state["story_events"] = list(story_state.get("history", {}).get("events", []))
    state["tension_wave"] = {
        "target_tension": pacing.get("target_tension", 7),
        "current_tension": pacing.get("current_tension", 6),
        "peak_count": pacing.get("peak_count", sum(1 for band in pacing.get("rhythm_window", []) if band == "spike")),
        "release_debt": pacing.get("release_debt", 0),
        "spike_debt": pacing.get("spike_debt", 0),
        "band": pacing.get("target_band", "pressure"),
    }
    state["retention_engine"] = {
        "unresolved_thread_pressure": min(10, sum(int(thread.get("pressure", 0) or 0) for thread in story_state.get("unresolved_threads", [])[:3])),
        "threat_proximity": conflict.get("threat_pressure", 0),
        "payoff_debt": conflict.get("payoff_debt", 0),
        "curiosity_debt": story_state.get("information", {}).get("dramatic_irony", 0),
        "fallout_pressure": story_state.get("world", {}).get("instability", 0),
        "chemistry_pressure": serialization.get("chemistry_signal", 0),
    }


def append_history(state: Dict[str, Any], key: str, value: Any, limit: int = 12) -> List[Any]:
    story_state = ensure_story_state(state)
    history = story_state.setdefault("history", {})
    seq = list(history.get(key, []) or [])
    seq.append(value)
    history[key] = seq[-limit:]
    _sync_legacy_aliases(state)
    return history[key]


def open_threads(story_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [thread for thread in story_state.get("conflict", {}).get("threads", []) if thread.get("status") != "resolved"]


def chemistry_pressure(story_state: Dict[str, Any]) -> int:
    edges = story_state.get("relationships", {})
    if not edges:
        return 0
    return _clamp_int(
        round(
            sum(
                abs(int(edge.get("charge", 0) or 0)) + int(edge.get("dependency", 0) or 0) + int(edge.get("chemistry", 0) or 0)
                for edge in edges.values()
            )
            / (3 * len(edges))
        )
    )


def _migrate_legacy_state(story_state: Dict[str, Any], state: Dict[str, Any]) -> None:
    legacy_character = state.get("character_arcs", {}) or {}
    protagonist = legacy_character.get("protagonist", {}) or {}
    rival = legacy_character.get("rival", {}) or {}
    if protagonist:
        cast = story_state["cast"]["protagonist"]
        cast["desire"] = protagonist.get("core_desire", cast["desire"])
        cast["surface_goal"] = protagonist.get("surface_goal", cast["surface_goal"])
        cast["fear"] = protagonist.get("fear_trigger", cast["fear"])
        cast["wound"] = protagonist.get("weakness", cast["wound"])
        cast["lie"] = protagonist.get("misbelief", cast["lie"])
        cast["urgency"] = protagonist.get("urgency", cast["urgency"])
        cast["decision_pressure"] = protagonist.get("decision_pressure", cast["decision_pressure"])
        cast["progress"] = protagonist.get("progress", cast["progress"])
        cast["backlash"] = protagonist.get("backlash", cast["backlash"])
    if rival:
        rival_cast = story_state["cast"]["rival"]
        rival_cast["desire"] = rival.get("core_desire", rival_cast["desire"])
        rival_cast["surface_goal"] = rival.get("surface_goal", rival_cast["surface_goal"])
        rival_cast["fear"] = rival.get("fear_trigger", rival_cast["fear"])
        rival_cast["wound"] = rival.get("weakness", rival_cast["wound"])
        rival_cast["lie"] = rival.get("misbelief", rival_cast["lie"])
        rival_cast["urgency"] = rival.get("urgency", rival_cast["urgency"])
        rival_cast["decision_pressure"] = rival.get("decision_pressure", rival_cast["decision_pressure"])
        rival_cast["progress"] = rival.get("progress", rival_cast["progress"])

    legacy_conflict = state.get("conflict_engine", {}) or {}
    if legacy_conflict:
        conflict = story_state["conflict"]
        for key in ["threads", "threat_pressure", "consequence_level", "opposition_advantage", "payoff_debt", "escalation_mode"]:
            if key in legacy_conflict:
                conflict[key] = deepcopy(legacy_conflict[key])
        if "recent_losses" in legacy_conflict:
            story_state["history"]["events"].extend(["loss"] * int(legacy_conflict.get("recent_losses", 0) or 0))
        if "recent_reversals" in legacy_conflict:
            story_state["history"]["events"].extend(["reversal"] * int(legacy_conflict.get("recent_reversals", 0) or 0))

    legacy_tension = state.get("tension_wave", {}) or {}
    if legacy_tension:
        pacing = story_state["pacing"]
        pacing["target_tension"] = legacy_tension.get("target_tension", pacing["target_tension"])
        pacing["current_tension"] = legacy_tension.get("current_tension", pacing["current_tension"])
        pacing["release_debt"] = legacy_tension.get("release_debt", pacing["release_debt"])
        pacing["spike_debt"] = legacy_tension.get("spike_debt", pacing["spike_debt"])
        pacing["peak_count"] = legacy_tension.get("peak_count", pacing.get("peak_count", 0))
        pacing["target_band"] = legacy_tension.get("band", pacing["target_band"])

    legacy_events = state.get("story_events", []) or []
    if legacy_events:
        story_state["history"]["events"] = list(legacy_events)[-8:]

    legacy_retention = state.get("retention_engine", {}) or {}
    if legacy_retention:
        story_state["serialization"]["retention_pressure"] = legacy_retention.get("unresolved_thread_pressure", story_state["serialization"]["retention_pressure"])
        story_state["serialization"]["chemistry_signal"] = legacy_retention.get("chemistry_pressure", story_state["serialization"]["chemistry_signal"])
