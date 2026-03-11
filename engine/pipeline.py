import os, time, json
from copy import deepcopy
from datetime import datetime
from .io_utils import ensure_dir, write_text, append_jsonl, safe_filename
from .external_rank import ExternalRankSignals
from .strategy import PLATFORM_STRATEGY, pick_subengine
from .style import compute_style_vector, blend, from_dict, to_dict, StyleVector
from .fatigue import fatigue_index, fatigue_directives
from .viral import validate_viral
from .json_parse import parse_json_strict
from .prompts import PROMPTS
from .preflight_gate import apply_preflight_runtime_policy, assess_preflight_bundle, record_preflight_bundle
from .profile import load_profiles, select_profile
from .character_arc import prepare_character_arc, character_prompt_payload, update_character_arc
from .conflict_memory import prepare_conflict_memory, conflict_prompt_payload, update_conflict_memory
from .competition_model import update_competition_state
from .market_policy_engine import apply_market_policy
from .damping_controller import damp_knobs
from .intensity_lock import clamp_knobs, apply_freeze, register_change
from .quality_gate import quality_gate_report
from .event_generator import generate_event_plan, event_prompt_payload, register_story_event
from .cliffhanger_engine import generate_cliffhanger_plan, enforce_cliffhanger
from .tension_wave import prepare_tension_wave, apply_tension_wave, update_tension_wave, tension_prompt_payload
from .predictive_retention import build_retention_state, predict_retention, retention_prompt_payload
from .information_emotion import prepare_information_emotion, information_prompt_payload
from .world_logic import update_world_state, world_prompt_payload
from .reward_serialization import update_reward_serialization
from .episode_attribution import record_episode_attribution
from .story_state import ensure_story_state
from .multi_objective import build_multi_objective_scores, multi_objective_balance
from .regression_guard import regression_decision
from .scene_causality import validate_scene_causality
from .antagonist_planner import prepare_antagonist_plan, antagonist_prompt_payload
from .pattern_memory import update_pattern_memory, pattern_prompt_payload
from .market_serialization import market_prompt_payload, update_market_serialization
from .causal_repair import (
    assess_causal_closure,
    build_causal_repair_plan,
    finalize_causal_repair_cycle,
    record_causal_repair_attempt,
    record_repair_diff_audit,
    start_causal_repair_cycle,
    store_causal_repair_plan,
)
from .portfolio_memory import portfolio_prompt_payload, update_portfolio_memory
from .reliability import (
    estimate_human_quality_lift,
    record_soak_history,
    simulate_long_run,
    summarize_soak_report,
    update_system_status,
)
from .runtime_config import load_runtime_config_into_cfg, write_system_status_snapshot
from analytics.content_ceiling import evaluate_episode


class EpisodeRejectedError(RuntimeError):
    def __init__(self, reason: str, audit: dict):
        self.reason = reason
        self.audit = dict(audit or {})
        super().__init__(self.audit.get("message") or reason)


def _record_episode_rejection(
    *,
    cfg: dict,
    out_dir: str,
    episode: int,
    reason: str,
    thresholds: dict,
    failed_checks: list[str] | None = None,
    gate_report: dict | None = None,
    regression_report: dict | None = None,
    predicted_retention: float | None = None,
    content_ceiling: dict | None = None,
    causal_report: dict | None = None,
) -> dict:
    audit = {
        "type": "episode_rejected",
        "ts": datetime.now().isoformat(timespec="seconds"),
        "episode": episode,
        "reason": reason,
        "platform": cfg.get("project", {}).get("platform"),
        "genre_bucket": cfg.get("project", {}).get("genre_bucket"),
        "failed_checks": list(failed_checks or []),
        "thresholds": dict(thresholds or {}),
        "predicted_retention": predicted_retention,
        "content_ceiling_total": dict(content_ceiling or {}).get("ceiling_total"),
        "causal_score": dict(causal_report or {}).get("score"),
        "causal_issues": list(dict(causal_report or {}).get("issues", []) or []),
        "regression_report": dict(regression_report or {}),
        "message": f"Episode {episode} rejected: {reason}",
    }
    if gate_report:
        audit["gate_report"] = {
            "passed": bool(gate_report.get("passed")),
            "failed_checks": list(gate_report.get("failed_checks", []) or []),
            "checks": dict(gate_report.get("checks", {}) or {}),
            "prose_report": dict(gate_report.get("prose_report", {}) or {}),
            "objective_profile": dict(gate_report.get("objective_profile", {}) or {}),
        }
    append_jsonl(
        os.path.join(out_dir, "metrics.jsonl"),
        audit,
        safe_mode=bool(cfg.get("safe_mode", False)),
        project_dir_for_backup=out_dir,
    )
    return audit


def _project_episode_state(
    state_data: dict,
    *,
    cfg: dict,
    episode: int,
    event_plan: dict,
    cliffhanger_plan: dict,
    score_obj: dict,
) -> dict:
    projected = deepcopy(state_data)
    register_story_event(projected, event_plan)
    update_character_arc(projected, episode, score_obj=score_obj, event_plan=event_plan)
    update_conflict_memory(projected, episode, score_obj=score_obj, event_plan=event_plan)
    update_tension_wave(projected, episode, score_obj=score_obj, event_plan=event_plan)
    update_world_state(projected, episode, event_plan=event_plan)
    update_reward_serialization(projected, episode, event_plan=event_plan, score_obj=score_obj, cfg=cfg)
    prepare_information_emotion(projected, episode=episode, event_plan=event_plan)
    update_pattern_memory(projected, episode=episode, event_plan=event_plan, cliffhanger_plan=cliffhanger_plan)
    update_portfolio_memory(projected, cfg=cfg, event_plan=event_plan)
    build_retention_state(projected, event_plan=event_plan, cliffhanger_plan=cliffhanger_plan)
    return projected

def _internal_knobs(cfg: dict, episode: int) -> dict:
    nv = cfg["novel"]
    knobs = {"hook_intensity": 0.70, "payoff_intensity": 0.70, "compression": 0.60, "novelty_boost": 0.50}
    if episode <= int(nv["early_focus_episodes"]):
        knobs["hook_intensity"] = 0.90
        knobs["compression"] = 0.80
    pw0, pw1 = nv["paywall_window"]
    if int(pw0) <= episode <= int(pw1):
        knobs["payoff_intensity"] = 0.90
        knobs["compression"] = 0.75
    return knobs

def _apply_platform_bias(cfg: dict, knobs: dict) -> dict:
    plat = PLATFORM_STRATEGY.get(cfg["project"]["platform"], {})
    # bias compression & cliff intensity indirectly
    if plat.get("pacing") == "aggressive":
        knobs["compression"] = min(0.90, knobs.get("compression",0.6) + 0.10)
        knobs["hook_intensity"] = min(0.95, knobs.get("hook_intensity",0.7) + 0.05)
    if plat.get("pacing") == "character":
        knobs["novelty_boost"] = min(0.75, knobs.get("novelty_boost",0.5) + 0.10)
    if plat.get("pacing") == "spiky":
        knobs["novelty_boost"] = min(0.85, knobs.get("novelty_boost",0.5) + 0.15)
        knobs["payoff_intensity"] = min(0.95, knobs.get("payoff_intensity",0.7) + 0.05)
    return knobs

def _apply_external(cfg: dict, knobs: dict, ext: ExternalRankSignals, episode: int) -> dict:
    ext_cfg = cfg.get("external", {})
    enable = bool(ext_cfg.get("enable_external_adjustment", True))
    if not enable:
        return knobs
    weight = float(ext_cfg.get("external_weight", 0.65))
    slope_window = int(ext_cfg.get("slope_window", 5))
    pj = cfg["project"]
    snap = ext.latest(pj["platform"], pj["genre_bucket"])
    if not snap or not snap.get("top_percent"):
        return knobs
    p = float(snap["top_percent"])
    s = float(ext.slope(pj["platform"], pj["genre_bucket"], window=slope_window))
    event = bool(snap.get("event_flag", False))

    # Rank weak (p high) => boost hook/compression; slope positive => worsening => boost more
    if p > 10:
        knobs["hook_intensity"] = min(0.95, knobs["hook_intensity"] + 0.12*weight)
        knobs["compression"] = min(0.92, knobs["compression"] + 0.18*weight)
    elif p > 5:
        knobs["hook_intensity"] = min(0.93, knobs["hook_intensity"] + 0.08*weight)
        knobs["compression"] = min(0.90, knobs["compression"] + 0.12*weight)

    # slope > 0 means top_percent increasing (worse)
    if s > 0.15:
        knobs["hook_intensity"] = min(0.95, knobs["hook_intensity"] + 0.06*weight)
        knobs["payoff_intensity"] = min(0.95, knobs["payoff_intensity"] + 0.06*weight)
    elif s > 0.05:
        knobs["hook_intensity"] = min(0.95, knobs["hook_intensity"] + 0.03*weight)

    pw0, pw1 = cfg["novel"]["paywall_window"]
    if int(pw0) <= episode <= int(pw1) and p > 5:
        knobs["payoff_intensity"] = min(0.95, knobs["payoff_intensity"] + 0.12*weight)

    if event:
        knobs["hook_intensity"] = min(0.95, knobs["hook_intensity"] + 0.03)
        knobs["payoff_intensity"] = min(0.95, knobs["payoff_intensity"] + 0.03)

    knobs["external_top_percent"] = p
    knobs["external_slope"] = s
    knobs["external_event"] = event
    return knobs


def _apply_final_threshold_runtime_repairs(cfg: dict, state_data: dict, knobs: dict) -> tuple[dict, dict, dict]:
    story_state = dict(state_data.get("story_state_v2", {}) or {})
    control = dict(story_state.get("control", {}) or {})
    repairs = dict(control.get("final_threshold_repairs", {}) or {})
    if not repairs:
        return cfg, knobs, {}

    adjusted_cfg = {
        **cfg,
        "limits": dict(cfg.get("limits", {}) or {}),
        "model": dict(cfg.get("model", {}) or {}),
    }
    adjusted_knobs = dict(knobs or {})
    applied: dict = {}

    hook_bias = float(repairs.get("hook_bias", 0.0) or 0.0)
    if hook_bias:
        adjusted_knobs["hook_intensity"] = min(0.99, float(adjusted_knobs.get("hook_intensity", 0.7) or 0.7) + hook_bias)
        applied["hook_bias"] = round(hook_bias, 4)

    payoff_bias = float(repairs.get("payoff_bias", 0.0) or 0.0)
    if payoff_bias:
        adjusted_knobs["payoff_intensity"] = min(0.99, float(adjusted_knobs.get("payoff_intensity", 0.7) or 0.7) + payoff_bias)
        applied["payoff_bias"] = round(payoff_bias, 4)

    novelty_bias = float(repairs.get("novelty_bias", 0.0) or 0.0)
    if novelty_bias:
        adjusted_knobs["novelty_boost"] = min(0.99, float(adjusted_knobs.get("novelty_boost", 0.5) or 0.5) + novelty_bias)
        applied["novelty_bias"] = round(novelty_bias, 4)

    compression_bias = float(repairs.get("compression_bias", 0.0) or 0.0)
    if compression_bias:
        adjusted_knobs["compression"] = min(0.99, float(adjusted_knobs.get("compression", 0.6) or 0.6) + compression_bias)
        applied["compression_bias"] = round(compression_bias, 4)

    urgency_bias = float(repairs.get("urgency_bias", 0.0) or 0.0)
    if urgency_bias:
        adjusted_knobs["hook_intensity"] = min(0.99, float(adjusted_knobs.get("hook_intensity", 0.7) or 0.7) + min(0.06, urgency_bias * 0.5))
        adjusted_knobs["payoff_intensity"] = min(0.99, float(adjusted_knobs.get("payoff_intensity", 0.7) or 0.7) + urgency_bias)
        applied["urgency_bias"] = round(urgency_bias, 4)

    rewrite_pressure = str(repairs.get("rewrite_pressure", "") or "").strip().lower()
    if rewrite_pressure:
        if rewrite_pressure == "high":
            adjusted_cfg["limits"]["max_revision_passes"] = max(int(adjusted_cfg["limits"].get("max_revision_passes", 2) or 2), 3)
            adjusted_cfg["limits"]["causal_repair_retry_budget"] = max(int(adjusted_cfg["limits"].get("causal_repair_retry_budget", 2) or 2), 3)
        applied["rewrite_pressure"] = rewrite_pressure

    if repairs.get("world_lock"):
        adjusted_knobs["novelty_boost"] = max(0.2, float(adjusted_knobs.get("novelty_boost", 0.5) or 0.5) - 0.08)
        adjusted_knobs["world_lock"] = True
        applied["world_lock"] = True

    causal_priority = str(repairs.get("causal_repair_priority", "") or "").strip().lower()
    if causal_priority:
        if causal_priority == "critical":
            adjusted_cfg["limits"]["causal_repair_retry_budget"] = max(int(adjusted_cfg["limits"].get("causal_repair_retry_budget", 2) or 2), 4)
            adjusted_cfg["model"]["mode"] = "priority"
        applied["causal_repair_priority"] = causal_priority

    if repairs.get("market_rebind_required"):
        adjusted_cfg["model"]["mode"] = "priority"
        adjusted_knobs["market_rebind_required"] = True
        applied["market_rebind_required"] = True

    if repairs.get("business_feedback_rebind_required"):
        adjusted_cfg["limits"]["max_revision_passes"] = max(int(adjusted_cfg["limits"].get("max_revision_passes", 2) or 2), 3)
        adjusted_cfg["limits"]["causal_repair_retry_budget"] = max(int(adjusted_cfg["limits"].get("causal_repair_retry_budget", 2) or 2), 3)
        adjusted_cfg["limits"]["request_timeout_seconds"] = max(int(adjusted_cfg["limits"].get("request_timeout_seconds", 150) or 150), 180)
        adjusted_cfg["model"]["request_timeout_seconds"] = adjusted_cfg["limits"]["request_timeout_seconds"]
        adjusted_cfg["model"]["mode"] = "priority"
        adjusted_knobs["business_feedback_rebind_required"] = True
        applied["business_feedback_rebind_required"] = True

    if repairs.get("scope_policy_rebind_required"):
        adjusted_cfg["model"]["mode"] = "priority"
        applied["scope_policy_rebind_required"] = True

    if repairs.get("human_lift_sampling_required"):
        adjusted_cfg["limits"]["max_revision_passes"] = max(int(adjusted_cfg["limits"].get("max_revision_passes", 2) or 2), 2)
        adjusted_cfg["model"]["mode"] = "priority"
        applied["human_lift_sampling_required"] = True

    return adjusted_cfg, adjusted_knobs, applied


def _inject_runtime_repair_story_context(story_state: dict, repairs_applied: dict) -> dict:
    if not repairs_applied:
        return story_state
    enriched = dict(story_state or {})
    market_payload = dict(enriched.get("market", {}) or {})
    market_payload["runtime_repairs"] = dict(repairs_applied)
    market_payload["rebind_required"] = bool(
        repairs_applied.get("market_rebind_required") or repairs_applied.get("business_feedback_rebind_required")
    )
    enriched["market"] = market_payload
    enriched["runtime_repairs"] = dict(repairs_applied)
    return enriched


def _apply_reader_quality_debt(cfg: dict, state_data: dict, knobs: dict) -> tuple[dict, dict]:
    story_state = dict(state_data.get("story_state_v2", {}) or {})
    control = dict(story_state.get("control", {}) or {})
    reader_quality = dict(control.get("reader_quality", {}) or {})
    if not reader_quality:
        return knobs, {}

    adjusted_knobs = dict(knobs or {})
    applied: dict = {}
    hook_debt = float(reader_quality.get("hook_debt", 0.0) or 0.0)
    payoff_debt = float(reader_quality.get("payoff_debt", 0.0) or 0.0)
    fatigue_debt = float(reader_quality.get("fatigue_debt", 0.0) or 0.0)
    retention_debt = float(reader_quality.get("retention_debt", 0.0) or 0.0)
    thinness_debt = float(reader_quality.get("thinness_debt", 0.0) or 0.0)
    repetition_debt = float(reader_quality.get("repetition_debt", 0.0) or 0.0)
    deja_vu_debt = float(reader_quality.get("deja_vu_debt", 0.0) or 0.0)
    fake_urgency_debt = float(reader_quality.get("fake_urgency_debt", 0.0) or 0.0)
    compression_debt = float(reader_quality.get("compression_debt", 0.0) or 0.0)

    if hook_debt > 0:
        delta = min(0.16, hook_debt * 0.6)
        adjusted_knobs["hook_intensity"] = min(0.99, float(adjusted_knobs.get("hook_intensity", 0.7) or 0.7) + delta)
        applied["hook_debt_response"] = round(delta, 4)
    if payoff_debt > 0:
        delta = min(0.14, payoff_debt * 0.55)
        adjusted_knobs["payoff_intensity"] = min(0.99, float(adjusted_knobs.get("payoff_intensity", 0.7) or 0.7) + delta)
        applied["payoff_debt_response"] = round(delta, 4)
    if fatigue_debt > 0:
        delta = min(0.14, fatigue_debt * 0.5)
        adjusted_knobs["compression"] = min(0.95, float(adjusted_knobs.get("compression", 0.6) or 0.6) + delta)
        adjusted_knobs["novelty_boost"] = min(0.95, float(adjusted_knobs.get("novelty_boost", 0.5) or 0.5) + min(0.1, fatigue_debt * 0.35))
        applied["fatigue_debt_response"] = round(delta, 4)
    if retention_debt > 0:
        delta = min(0.12, retention_debt * 0.45)
        adjusted_knobs["hook_intensity"] = min(0.99, float(adjusted_knobs.get("hook_intensity", 0.7) or 0.7) + delta)
        adjusted_knobs["compression"] = min(0.95, float(adjusted_knobs.get("compression", 0.6) or 0.6) + min(0.08, retention_debt * 0.3))
        applied["retention_debt_response"] = round(delta, 4)
    if thinness_debt > 0:
        adjusted_knobs["hook_intensity"] = min(0.99, float(adjusted_knobs.get("hook_intensity", 0.7) or 0.7) + min(0.1, thinness_debt * 0.45))
        adjusted_knobs["payoff_intensity"] = min(0.99, float(adjusted_knobs.get("payoff_intensity", 0.7) or 0.7) + min(0.08, thinness_debt * 0.35))
        applied["thinness_debt_response"] = round(min(0.1, thinness_debt * 0.45), 4)
    if repetition_debt > 0:
        adjusted_knobs["novelty_boost"] = min(0.95, float(adjusted_knobs.get("novelty_boost", 0.5) or 0.5) + min(0.12, repetition_debt * 0.5))
        adjusted_knobs["compression"] = min(0.95, float(adjusted_knobs.get("compression", 0.6) or 0.6) + min(0.08, repetition_debt * 0.35))
        applied["repetition_debt_response"] = round(min(0.12, repetition_debt * 0.5), 4)
    if deja_vu_debt > 0:
        adjusted_knobs["novelty_boost"] = min(0.95, float(adjusted_knobs.get("novelty_boost", 0.5) or 0.5) + min(0.14, deja_vu_debt * 0.55))
        adjusted_knobs["hook_intensity"] = min(0.99, float(adjusted_knobs.get("hook_intensity", 0.7) or 0.7) + min(0.05, deja_vu_debt * 0.25))
        applied["deja_vu_debt_response"] = round(min(0.14, deja_vu_debt * 0.55), 4)
    if fake_urgency_debt > 0:
        adjusted_knobs["payoff_intensity"] = min(0.99, float(adjusted_knobs.get("payoff_intensity", 0.7) or 0.7) + min(0.12, fake_urgency_debt * 0.5))
        adjusted_knobs["compression"] = min(0.95, float(adjusted_knobs.get("compression", 0.6) or 0.6) + min(0.06, fake_urgency_debt * 0.25))
        applied["fake_urgency_debt_response"] = round(min(0.12, fake_urgency_debt * 0.5), 4)
    if compression_debt > 0:
        adjusted_knobs["compression"] = min(0.97, float(adjusted_knobs.get("compression", 0.6) or 0.6) + min(0.14, compression_debt * 0.5))
        applied["compression_debt_response"] = round(min(0.14, compression_debt * 0.5), 4)

    if applied:
        applied["reader_quality_debt"] = {
            "hook_debt": round(hook_debt, 4),
            "payoff_debt": round(payoff_debt, 4),
            "fatigue_debt": round(fatigue_debt, 4),
            "retention_debt": round(retention_debt, 4),
            "thinness_debt": round(thinness_debt, 4),
            "repetition_debt": round(repetition_debt, 4),
            "deja_vu_debt": round(deja_vu_debt, 4),
            "fake_urgency_debt": round(fake_urgency_debt, 4),
            "compression_debt": round(compression_debt, 4),
        }
    return adjusted_knobs, applied


def _apply_market_feedback_pressure(state_data: dict, knobs: dict) -> tuple[dict, dict]:
    story_state = dict(state_data.get("story_state_v2", {}) or {})
    market = dict(story_state.get("market", {}) or {})
    if not market:
        return knobs, {}

    adjusted_knobs = dict(knobs or {})
    applied: dict = {}
    market_pressure = float(market.get("market_pressure", 0.0) or 0.0)
    exit_risk = float(market.get("reader_exit_risk", 0.0) or 0.0)
    campaign_roi = float(market.get("campaign_roi_signal", 0.0) or 0.0)
    if market_pressure > 0:
        delta = min(0.12, market_pressure / 10.0 * 0.18)
        adjusted_knobs["hook_intensity"] = min(0.99, float(adjusted_knobs.get("hook_intensity", 0.7) or 0.7) + delta)
        adjusted_knobs["payoff_intensity"] = min(0.99, float(adjusted_knobs.get("payoff_intensity", 0.7) or 0.7) + min(0.1, delta * 0.8))
        applied["market_pressure_response"] = round(delta, 4)
    if exit_risk > 0:
        delta = min(0.1, exit_risk / 10.0 * 0.16)
        adjusted_knobs["compression"] = min(0.95, float(adjusted_knobs.get("compression", 0.6) or 0.6) + delta)
        applied["reader_exit_risk_response"] = round(delta, 4)
    if campaign_roi < 0.2 and market.get("market_feedback_active"):
        adjusted_knobs["novelty_boost"] = min(0.95, float(adjusted_knobs.get("novelty_boost", 0.5) or 0.5) + 0.08)
        applied["campaign_roi_response"] = round(campaign_roi, 4)
    return adjusted_knobs, applied


def _apply_arc_pressure(state_data: dict, knobs: dict) -> tuple[dict, dict]:
    story_state = dict(state_data.get("story_state_v2", {}) or {})
    control = dict(story_state.get("control", {}) or {})
    arc_pressure = dict(control.get("arc_pressure", {}) or {})
    if not arc_pressure:
        return knobs, {}

    adjusted_knobs = dict(knobs or {})
    applied: dict = {}
    payoff_debt = float(arc_pressure.get("payoff_debt", 0.0) or 0.0)
    momentum_debt = float(arc_pressure.get("momentum_debt", 0.0) or 0.0)
    if payoff_debt > 0:
        delta = min(0.14, payoff_debt * 0.55)
        adjusted_knobs["payoff_intensity"] = min(0.99, float(adjusted_knobs.get("payoff_intensity", 0.7) or 0.7) + delta)
        applied["arc_payoff_debt_response"] = round(delta, 4)
    if momentum_debt > 0:
        delta = min(0.12, momentum_debt * 0.5)
        adjusted_knobs["hook_intensity"] = min(0.99, float(adjusted_knobs.get("hook_intensity", 0.7) or 0.7) + delta)
        adjusted_knobs["novelty_boost"] = min(0.95, float(adjusted_knobs.get("novelty_boost", 0.5) or 0.5) + min(0.08, momentum_debt * 0.35))
        applied["arc_momentum_debt_response"] = round(delta, 4)
    if applied:
        applied["arc_pressure"] = {
            "payoff_debt": round(payoff_debt, 4),
            "momentum_debt": round(momentum_debt, 4),
        }
    return adjusted_knobs, applied

def ensure_project_dirs(cfg: dict) -> str:
    # Track-local outputs if track directory is provided
    tdir = None
    if isinstance(cfg.get('track'), dict):
        tdir = cfg['track'].get('dir')
    if tdir:
        out_dir = os.path.join(tdir, 'outputs')
        ensure_dir(out_dir)
        return out_dir

    base = safe_filename(cfg['project']['name'])
    track_id = ''
    if isinstance(cfg.get('track'), dict):
        track_id = safe_filename(cfg['track'].get('id', ''))
    if track_id:
        base = f"{base}__{track_id}"
    out_dir = os.path.join(cfg['output']['root_dir'], base)
    ensure_dir(out_dir)
    return out_dir

def build_outline(cfg, state, llm, cost, ext: ExternalRankSignals):
    cfg, runtime_cfg = load_runtime_config_into_cfg(cfg)
    state.data["runtime_config"] = runtime_cfg
    pj = cfg["project"]
    sub_key = pj.get("sub_engine", "AUTO")
    ensure_story_state(state.data, cfg=cfg)
    update_portfolio_memory(state.data, cfg=cfg)

    profiles_dir = os.path.join("data","profiles")
    profiles = load_profiles(profiles_dir)

    snap = ext.latest(pj["platform"], pj["genre_bucket"]) or {}
    prompt = PROMPTS.master_outline(
        cfg,
        snap,
        sub_key,
        story_state={
            "portfolio": portfolio_prompt_payload(state.data),
            "pattern_memory": pattern_prompt_payload(state.data),
        },
    )
    resp = llm.call(prompt, temperature=0.45)
    cost.add_usage(resp)
    outline = resp.output_text
    state.set("outline", outline)
    return outline

from .backup_manager import backup_file

from .full_backup_manager import snapshot_project

def generate_episode(cfg, state, llm, cost, ext: ExternalRankSignals, episode: int) -> dict:
    cfg, runtime_cfg = load_runtime_config_into_cfg(cfg)
    pj = cfg["project"]
    out_dir = ensure_project_dirs(cfg)
    state.data['out_dir'] = out_dir
    state.data['_cfg_for_models'] = cfg
    state.data["runtime_config"] = runtime_cfg

    # Competition/Reaction (26/30): update market snapshot in state
    latest_tp = None
    cert_path = os.path.join(out_dir, "certification_report.json")
    if os.path.exists(cert_path):
        try:
            cr = json.load(open(cert_path, "r", encoding="utf-8"))
            stats = cr.get("market", {}).get("stats", {})
            if isinstance(stats, dict) and stats.get("latest_top_percent") is not None:
                latest_tp = float(stats.get("latest_top_percent"))
        except Exception:
            pass
    update_competition_state(state.data, latest_tp)
    apply_market_policy(cfg, state.data)

    # Reproducibility seed (9/30)
    seed = cfg.get('engine', {}).get('random_seed')
    if seed is not None:
        try:
            import random
            random.seed(int(seed))
            state.data.setdefault('engine_seed', int(seed))
        except Exception:
            pass
    if cfg.get('safe_mode', False):
        snapshot_project(out_dir, extra_paths=[cfg.get('external',{}).get('rank_signals_csv',''), 'data/revenue_input.csv', 'data/campaign_input.csv', 'config.yaml'])
    outline = state.get("outline")
    if not outline:
        outline = build_outline(cfg, state, llm, cost, ext)
    ensure_story_state(state.data, cfg=cfg, outline=outline)
    preflight = assess_preflight_bundle(cfg, state.data, runtime_cfg=runtime_cfg, episode=episode)
    record_preflight_bundle(out_dir, preflight, episode=episode, safe_mode=bool(cfg.get("safe_mode", False)))
    state.set("preflight_bundle", preflight)
    if not preflight.get("preflight_ready"):
        rejection_audit = _record_episode_rejection(
            cfg=cfg,
            out_dir=out_dir,
            episode=episode,
            reason="preflight_gate_failed",
            thresholds=cfg.get("quality", {}),
            failed_checks=list(preflight.get("blocking_reasons", []) or []),
        )
        rejection_audit["preflight"] = preflight
        raise EpisodeRejectedError("preflight_gate_failed", rejection_audit)
    cfg = apply_preflight_runtime_policy(cfg, preflight)
    pj = cfg["project"]

    sub_key = pj.get("sub_engine", "AUTO")

    profiles_dir = os.path.join("data","profiles")
    profiles = load_profiles(profiles_dir)


    # style vector
    style = from_dict(state.get("style_vector"))
    if not state.get("style_vector"):
        # initialize using outline as weak prior
        style = compute_style_vector(outline[:4000])
        state.set("style_vector", to_dict(style))

    # fatigue from last K scores
    hist = state.get("score_history", [])
    window = int(cfg["novel"].get("fatigue_window", 12))
    last = hist[-window:] if hist else []
    fat = fatigue_index(last)
    fat_th = float(cfg["novel"].get("fatigue_threshold", 0.62))
    fat_pack = fatigue_directives(fat, fat_th)

    # knobs
    knobs = _internal_knobs(cfg, episode)
    original_knobs = knobs.copy()
    knobs = _apply_platform_bias(cfg, knobs)
    knobs = _apply_external(cfg, knobs, ext, episode)
    prepare_tension_wave(state.data, episode=episode)
    knobs = apply_tension_wave(knobs, state.data.get("tension_wave", {}))
    knobs = damp_knobs(cfg, knobs, original_knobs)
    knobs = clamp_knobs(cfg, knobs)
    cfg, knobs, runtime_repair_directives = _apply_final_threshold_runtime_repairs(cfg, state.data, knobs)
    knobs, reader_quality_debt_directives = _apply_reader_quality_debt(cfg, state.data, knobs)
    knobs, arc_pressure_directives = _apply_arc_pressure(state.data, knobs)
    prof = select_profile(profiles, pj["platform"], pj["genre_bucket"])
    knobs["profile"] = prof

    knobs["fatigue_index"] = fat
    knobs["fatigue_reset"] = fat_pack["needs_reset"]
    knobs["reset_level"] = fat_pack["reset_level"]

    prepare_character_arc(state.data, cfg=cfg, outline=outline, episode=episode)
    prepare_conflict_memory(state.data, episode=episode)
    prepare_antagonist_plan(state.data, episode=episode)
    update_pattern_memory(state.data, episode=episode)
    update_market_serialization(state.data, episode=episode, cfg=cfg)
    knobs, market_feedback_directives = _apply_market_feedback_pressure(state.data, knobs)
    update_portfolio_memory(state.data, cfg=cfg)
    event_plan = generate_event_plan(state.data, episode=episode)
    prepare_antagonist_plan(state.data, episode=episode, event_plan=event_plan)
    prepare_information_emotion(state.data, episode=episode, event_plan=event_plan)
    cliffhanger_plan = generate_cliffhanger_plan(
        character_prompt_payload(state.data),
        conflict_prompt_payload(state.data),
        event_plan,
    )
    build_retention_state(state.data, event_plan=event_plan, cliffhanger_plan=cliffhanger_plan)
    story_state = {
        "character": character_prompt_payload(state.data),
        "conflict": conflict_prompt_payload(state.data),
        "event": event_prompt_payload(event_plan),
        "cliffhanger": cliffhanger_plan,
        "tension": tension_prompt_payload(state.data),
        "retention": retention_prompt_payload(state.data),
        "information": information_prompt_payload(state.data),
        "world": world_prompt_payload(state.data),
        "antagonist": antagonist_prompt_payload(state.data),
        "pattern_memory": pattern_prompt_payload(state.data),
        "market": market_prompt_payload(state.data),
        "portfolio": portfolio_prompt_payload(state.data),
    }
    story_state = _inject_runtime_repair_story_context(story_state, runtime_repair_directives)
    if reader_quality_debt_directives:
        story_state["reader_quality_debt"] = reader_quality_debt_directives
    if arc_pressure_directives:
        story_state["arc_pressure"] = arc_pressure_directives
    if market_feedback_directives:
        story_state["market_feedback_pressure"] = market_feedback_directives

    snap = ext.latest(pj["platform"], pj["genre_bucket"]) or {}
    plan_prompt = PROMPTS.episode_plan(
        cfg,
        outline,
        episode,
        knobs,
        snap,
        fat_pack["directive"],
        sub_key,
        story_state=story_state,
    )
    plan_resp = llm.call(plan_prompt, temperature=0.35)
    cost.add_usage(plan_resp)
    plan = plan_resp.output_text

    # draft JSON
    draft_prompt = PROMPTS.episode_draft_json(cfg, plan, episode, knobs, style, sub_key, story_state=story_state)
    draft_resp = llm.call(draft_prompt, temperature=0.78)
    cost.add_usage(draft_resp)
    ok, draft_obj = parse_json_strict(draft_resp.output_text)
    if not ok or not isinstance(draft_obj, dict):
        draft_obj = {"episode_text": str(draft_obj), "quote_line": "", "comment_hook": "", "cliffhanger": ""}

    # revision passes, enforce viral
    viral_required = bool(cfg["quality"].get("viral_required", True))
    max_passes = int(cfg["limits"].get("max_revision_passes", 2))
    repair_budget = int(cfg["limits"].get("causal_repair_retry_budget", max_passes) or max_passes)
    cur_obj = draft_obj
    initial_causal_report = validate_scene_causality(
        str(cur_obj.get("episode_text", "")),
        story_state=state.data.get("story_state_v2", {}),
        event_plan=event_plan,
        cliffhanger_plan=cliffhanger_plan,
    )
    initial_repair_plan = build_causal_repair_plan(
        initial_causal_report,
        story_state=state.data.get("story_state_v2", {}),
        event_plan=event_plan,
        cliffhanger_plan=cliffhanger_plan,
    )
    start_causal_repair_cycle(state.data, retry_budget=repair_budget, causal_report=initial_causal_report, repair_plan=initial_repair_plan)
    latest_causal_report = initial_causal_report
    latest_repair_plan = initial_repair_plan
    for attempt in range(1, repair_budget + 1):
        closure = assess_causal_closure(latest_causal_report, latest_repair_plan)
        viral_ok = True
        if viral_required:
            viral_ok, _msg = validate_viral(cur_obj, cliffhanger_plan=cliffhanger_plan)
        if closure["passed"] and viral_ok:
            break
        pre_rewrite_text = str(cur_obj.get("episode_text", ""))
        pre_rewrite_report = dict(latest_causal_report or {})
        rewrite_prompt = PROMPTS.episode_rewrite_json(
            cfg, cur_obj, episode, knobs, style, sub_key, viral_required, story_state=story_state, repair_plan=latest_repair_plan
        )
        rewrite_resp = llm.call(rewrite_prompt, temperature=0.55)
        cost.add_usage(rewrite_resp)
        ok2, obj2 = parse_json_strict(rewrite_resp.output_text)
        if ok2 and isinstance(obj2, dict):
            cur_obj = obj2
        latest_causal_report = validate_scene_causality(
            str(cur_obj.get("episode_text", "")),
            story_state=state.data.get("story_state_v2", {}),
            event_plan=event_plan,
            cliffhanger_plan=cliffhanger_plan,
        )
        latest_repair_plan = build_causal_repair_plan(
            latest_causal_report,
            story_state=state.data.get("story_state_v2", {}),
            event_plan=event_plan,
            cliffhanger_plan=cliffhanger_plan,
        )
        record_causal_repair_attempt(
            state.data,
            attempt_index=attempt,
            causal_report=latest_causal_report,
            repair_plan=latest_repair_plan,
        )
        record_repair_diff_audit(
            state.data,
            attempt_index=attempt,
            pre_text=pre_rewrite_text,
            post_text=str(cur_obj.get("episode_text", "")),
            pre_report=pre_rewrite_report,
            post_report=latest_causal_report,
            repair_plan=latest_repair_plan,
        )
        if attempt >= max_passes and not viral_required and assess_causal_closure(latest_causal_report, latest_repair_plan)["passed"]:
            break

    episode_text = str(cur_obj.get("episode_text","")).strip()
    meta = enforce_cliffhanger(
        {
        "quote_line": str(cur_obj.get("quote_line","")).strip(),
        "comment_hook": str(cur_obj.get("comment_hook","")).strip(),
        "cliffhanger": str(cur_obj.get("cliffhanger","")).strip(),
        "event_plan": event_plan,
        "cliffhanger_plan": cliffhanger_plan,
        },
        cliffhanger_plan,
    )

    # style update
    new_style = compute_style_vector(episode_text)
    style = blend(style, new_style, alpha=0.15)
    state.set("style_vector", to_dict(style))

    # scoring
    scoring_prompt = PROMPTS.scoring_json(cfg, episode_text, episode)
    sc_resp = llm.call(scoring_prompt, temperature=0.2)
    cost.add_usage(sc_resp)
    ok3, score_obj = parse_json_strict(sc_resp.output_text)
    if not (ok3 and isinstance(score_obj, dict)):
        score_obj = {"raw": str(score_obj)}
    thresholds = cfg.get("quality", {})

    def evaluate_candidate(candidate_obj: dict, candidate_text: str, candidate_meta: dict) -> tuple:
        candidate_causal = validate_scene_causality(
            candidate_text,
            story_state=state.data.get("story_state_v2", {}),
            event_plan=event_plan,
            cliffhanger_plan=cliffhanger_plan,
        )
        candidate_repair = build_causal_repair_plan(
            candidate_causal,
            story_state=state.data.get("story_state_v2", {}),
            event_plan=event_plan,
            cliffhanger_plan=cliffhanger_plan,
        )
        finalize_causal_repair_cycle(state.data, causal_report=candidate_causal, repair_plan=candidate_repair)
        store_causal_repair_plan(state.data, candidate_repair)
        projected_state = _project_episode_state(
            state.data,
            cfg=cfg,
            episode=episode,
            event_plan=event_plan,
            cliffhanger_plan=cliffhanger_plan,
            score_obj=candidate_obj,
        )
        projected_retention_state = projected_state.get("retention_engine", {})
        candidate_predicted_retention = predict_retention(candidate_obj, fat, projected_retention_state)
        candidate_objective_scores = build_multi_objective_scores(
            candidate_obj,
            retention_state=projected_retention_state,
            story_state=projected_state.get("story_state_v2", {}),
            causal_report=candidate_causal,
        )
        candidate_objective_balance = multi_objective_balance(
            candidate_obj,
            retention_state=projected_retention_state,
            story_state=projected_state.get("story_state_v2", {}),
            causal_report=candidate_causal,
        )
        candidate_content_ceiling = evaluate_episode(
            candidate_text,
            {
                "genre_bucket": pj["genre_bucket"],
                "platform": pj["platform"],
                "event_plan": event_plan,
                "cliffhanger": candidate_meta.get("cliffhanger", ""),
                "cliffhanger_plan": candidate_meta.get("cliffhanger_plan", {}),
                "conflict": projected_state.get("story_state_v2", {}).get("conflict", {}),
                "retention": projected_retention_state,
                "tension": projected_state.get("tension_wave", {}),
                "story_state": projected_state.get("story_state_v2", {}),
                "multi_objective": candidate_objective_scores,
                "scene_causality": candidate_causal,
            },
        )
        candidate_gate_report = quality_gate_report(
            candidate_obj,
            thresholds,
            episode_text=candidate_text,
            cliffhanger=candidate_meta.get("cliffhanger", ""),
            cliffhanger_plan=candidate_meta.get("cliffhanger_plan", {}) or cliffhanger_plan,
            retention_state=projected_retention_state,
            predicted_retention=candidate_predicted_retention,
            content_ceiling=candidate_content_ceiling,
            causal_report=candidate_causal,
            story_state=projected_state.get("story_state_v2", {}),
            objective_scores=candidate_objective_scores,
        )
        return (
            candidate_causal,
            candidate_repair,
            projected_state,
            projected_retention_state,
            candidate_predicted_retention,
            candidate_objective_scores,
            candidate_objective_balance,
            candidate_content_ceiling,
            candidate_gate_report,
        )

    (
        causal_report,
        repair_plan,
        projected_state,
        projected_retention_state,
        predicted_retention,
        objective_scores,
        objective_balance,
        content_ceiling,
        gate_report,
    ) = evaluate_candidate(cur_obj, episode_text, meta)
    state.set("predicted_retention", predicted_retention)
    state.set(
        "last_quality_gate",
        {
            "passed": bool(gate_report.get("passed")),
            "failed_checks": gate_report.get("failed_checks", []),
            "checks": gate_report.get("checks", {}),
            "prose_report": gate_report.get("prose_report", {}),
            "predicted_retention": predicted_retention,
            "thresholds": thresholds,
            "content_ceiling_total": content_ceiling.get("ceiling_total"),
            "causal_score": causal_report.get("score"),
        },
    )

    if not gate_report.get("passed"):
        quality_feedback = {
            "failed_checks": gate_report.get("failed_checks", []),
            "checks": gate_report.get("checks", {}),
            "prose_report": gate_report.get("prose_report", {}),
            "predicted_retention": predicted_retention,
            "content_ceiling_total": content_ceiling.get("ceiling_total"),
            "causal_score": causal_report.get("score"),
            "causal_issues": causal_report.get("issues", []),
            "retention_state": projected_retention_state,
        }
        rewrite_prompt = PROMPTS.episode_rewrite_json(
            cfg,
            cur_obj,
            episode,
            knobs,
            style,
            sub_key,
            viral_required,
            story_state=story_state,
            repair_plan=repair_plan,
            quality_feedback=quality_feedback,
        )
        rewrite_resp = llm.call(rewrite_prompt, temperature=0.45)
        cost.add_usage(rewrite_resp)
        ok4, obj4 = parse_json_strict(rewrite_resp.output_text)
        if ok4 and isinstance(obj4, dict):
            cur_obj = obj4
            episode_text = str(cur_obj.get("episode_text", "")).strip()
            meta = enforce_cliffhanger(
                {
                    "quote_line": str(cur_obj.get("quote_line", "")).strip(),
                    "comment_hook": str(cur_obj.get("comment_hook", "")).strip(),
                    "cliffhanger": str(cur_obj.get("cliffhanger", "")).strip(),
                    "event_plan": event_plan,
                    "cliffhanger_plan": cliffhanger_plan,
                },
                cliffhanger_plan,
            )
            scoring_prompt = PROMPTS.scoring_json(cfg, episode_text, episode)
            sc_resp = llm.call(scoring_prompt, temperature=0.2)
            cost.add_usage(sc_resp)
            ok5, rescored = parse_json_strict(sc_resp.output_text)
            if ok5 and isinstance(rescored, dict):
                score_obj = rescored
            (
                causal_report,
                repair_plan,
                projected_state,
                projected_retention_state,
                predicted_retention,
                objective_scores,
                objective_balance,
                content_ceiling,
                gate_report,
            ) = evaluate_candidate(cur_obj, episode_text, meta)
            state.set("predicted_retention", predicted_retention)
            state.set(
                "last_quality_gate",
                {
                    "passed": bool(gate_report.get("passed")),
                    "failed_checks": gate_report.get("failed_checks", []),
                    "checks": gate_report.get("checks", {}),
                    "predicted_retention": predicted_retention,
                    "thresholds": thresholds,
                    "content_ceiling_total": content_ceiling.get("ceiling_total"),
                    "causal_score": causal_report.get("score"),
                },
            )
        knobs["hook_intensity"] = min(0.99, knobs.get("hook_intensity", 0.7) + 0.1)
        knobs["payoff_intensity"] = min(0.99, knobs.get("payoff_intensity", 0.7) + 0.1)
        if not gate_report.get("passed"):
            rejection_audit = _record_episode_rejection(
                cfg=cfg,
                out_dir=out_dir,
                episode=episode,
                reason="quality_gate_failed",
                thresholds=thresholds,
                failed_checks=gate_report.get("failed_checks", []),
                gate_report=gate_report,
                predicted_retention=predicted_retention,
                content_ceiling=content_ceiling,
                causal_report=causal_report,
            )
            raise EpisodeRejectedError("quality_gate_failed", rejection_audit)

    final_quality_gate = {
        "passed": bool(gate_report.get("passed")),
        "failed_checks": gate_report.get("failed_checks", []),
        "checks": gate_report.get("checks", {}),
        "prose_report": gate_report.get("prose_report", {}),
        "objective_profile": gate_report.get("objective_profile", {}),
        "predicted_retention": predicted_retention,
        "thresholds": thresholds,
        "content_ceiling_total": content_ceiling.get("ceiling_total"),
        "causal_score": causal_report.get("score"),
    }

    hist = state.get("score_history", [])
    hist.append(score_obj)
    state.set("score_history", hist)

    state.data = projected_state
    state.set("predicted_retention", predicted_retention)
    state.set("last_quality_gate", final_quality_gate)
    episode_attribution = record_episode_attribution(
        state.data,
        episode=episode,
        episode_text=episode_text,
        event_plan=event_plan,
        cliffhanger_plan=cliffhanger_plan,
        score_obj=score_obj,
        retention_state=state.data.get("retention_engine", {}),
        content_ceiling=content_ceiling,
    )
    next_objective = build_multi_objective_scores(
        score_obj,
        retention_state=state.data.get("retention_engine", {}),
        story_state=state.data.get("story_state_v2", {}),
        causal_report=causal_report,
    )
    accepted, regression_report = regression_decision(objective_scores, next_objective)
    state.set("regression_report", regression_report)
    if not accepted:
        state.data.setdefault("story_state_v2", {}).setdefault("control", {}).setdefault("regression_flags", []).append(
            {
                "episode": episode,
                "dropped_axes": regression_report.get("dropped_axes", []),
            }
        )
    system_status = update_system_status(
        state.data,
        episode=episode,
        objective_scores=objective_scores,
        portfolio_signals=state.data.get("story_state_v2", {}).get("portfolio_memory", {}),
    )
    state.set("system_status", system_status)
    write_system_status_snapshot(
        system_status,
        runtime_cfg=runtime_cfg,
        out_dir=out_dir,
        safe_mode=bool(cfg.get("safe_mode", False)),
        project_dir_for_backup=out_dir,
    )
    simulation = simulate_long_run(objective_scores, state.data.get("story_state_v2", {}))
    soak_report = summarize_soak_report(simulation)
    human_quality_lift = estimate_human_quality_lift(
        objective_scores=objective_scores,
        system_status=system_status,
        repair_plan=repair_plan,
        gate_passed=bool(gate_report.get("passed")),
        story_state=state.data.get("story_state_v2", {}),
    )
    soak_history = record_soak_history(
        state.data,
        episode=episode,
        soak_report=soak_report,
        quality_lift_if_human_intervenes=human_quality_lift,
    )
    state.set("quality_lift_if_human_intervenes", human_quality_lift)

    meta["content_ceiling"] = content_ceiling
    meta["episode_attribution"] = episode_attribution
    meta["multi_objective"] = {
        "axes": objective_scores,
        "balance": objective_balance,
    }
    meta["scene_causality"] = causal_report
    meta["causal_repair"] = repair_plan
    meta["system_status"] = system_status
    meta["simulation"] = simulation
    meta["soak_report"] = soak_report
    meta["quality_lift_if_human_intervenes"] = human_quality_lift
    meta["soak_history"] = soak_history
    meta["runtime_config"] = runtime_cfg
    meta["final_threshold_repairs_applied"] = runtime_repair_directives
    meta["reader_quality_debt_applied"] = reader_quality_debt_directives
    meta["arc_pressure_applied"] = arc_pressure_directives
    meta["market_feedback_pressure_applied"] = market_feedback_directives
    meta["generation_runtime_policy"] = {
        "max_revision_passes": int(cfg.get("limits", {}).get("max_revision_passes", 2) or 2),
        "causal_repair_retry_budget": int(cfg.get("limits", {}).get("causal_repair_retry_budget", 2) or 2),
        "request_timeout_seconds": int(cfg.get("limits", {}).get("request_timeout_seconds", 0) or 0),
        "mode": str(cfg.get("model", {}).get("mode", "") or ""),
    }

    full_text = (
        episode_text
        + "\n\n[META]\n"
        + json.dumps(meta, ensure_ascii=False, indent=2)
        + "\n\n[SCORES]\n"
        + json.dumps(score_obj, ensure_ascii=False, indent=2)
        + "\n"
    )
    write_text(os.path.join(out_dir, f"episode_{episode:03}.txt"), full_text, safe_mode=cfg.get("safe_mode", False), project_dir_for_backup=out_dir)

    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "episode": episode,
        "platform": pj["platform"],
        "genre_bucket": pj["genre_bucket"],
        "sub_engine": pick_subengine(pj["genre_bucket"], sub_key).key,
        "knobs": knobs,
        "external": snap,
        "preflight": preflight,
        "meta": meta,
        "scores": score_obj,
        "style_vector": state.get("style_vector"),
        "fatigue": fat_pack,
        "retention": {
            "predicted_next_episode": predicted_retention,
            "pressure_state": state.data.get("retention_engine", {}),
        },
        "content_ceiling": content_ceiling,
        "episode_attribution": episode_attribution,
        "system_status": system_status,
        "simulation": simulation,
        "soak_report": soak_report,
        "quality_lift_if_human_intervenes": human_quality_lift,
        "soak_history": soak_history,
        "runtime_config": runtime_cfg,
        "final_threshold_repairs_applied": runtime_repair_directives,
        "reader_quality_debt_applied": reader_quality_debt_directives,
        "arc_pressure_applied": arc_pressure_directives,
        "market_feedback_pressure_applied": market_feedback_directives,
        "generation_runtime_policy": meta["generation_runtime_policy"],
        "cost": cost.snapshot(),
    }
    if cfg["output"].get("save_metrics_jsonl", True):
        append_jsonl(os.path.join(out_dir, "metrics.jsonl"), record, safe_mode=cfg.get("safe_mode", False), project_dir_for_backup=out_dir)
    knobs = apply_freeze(cfg, state.data, knobs)
    register_change(cfg, state.data, knobs)
    state.set("next_episode", episode + 1)

    # save cost summary incrementally
    cost.enforce_token_ceiling()

    return record
