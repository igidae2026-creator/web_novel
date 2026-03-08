import os, time, json
from datetime import datetime
from .io_utils import ensure_dir, write_text, append_jsonl, safe_filename
from .external_rank import ExternalRankSignals
from .strategy import PLATFORM_STRATEGY, pick_subengine
from .style import compute_style_vector, blend, from_dict, to_dict, StyleVector
from .fatigue import fatigue_index, fatigue_directives
from .viral import validate_viral
from .json_parse import parse_json_strict
from .prompts import PROMPTS
from .profile import load_profiles, select_profile
from .character_arc import prepare_character_arc, character_prompt_payload, update_character_arc
from .conflict_memory import prepare_conflict_memory, conflict_prompt_payload, update_conflict_memory
from .competition_model import update_competition_state
from .market_policy_engine import apply_market_policy
from .damping_controller import damp_knobs
from .intensity_lock import clamp_knobs, apply_freeze, register_change
from .quality_gate import quality_gate
from .event_generator import generate_event_plan, event_prompt_payload, register_story_event
from .cliffhanger_engine import generate_cliffhanger_plan, enforce_cliffhanger
from .tension_wave import prepare_tension_wave, apply_tension_wave, update_tension_wave, tension_prompt_payload
from .predictive_retention import build_retention_state, predict_retention, retention_prompt_payload
from .information_emotion import prepare_information_emotion, information_prompt_payload
from .world_logic import update_world_state, world_prompt_payload
from .reward_serialization import update_reward_serialization
from .story_state import ensure_story_state
from .multi_objective import build_multi_objective_scores, multi_objective_balance
from .regression_guard import regression_decision
from .scene_causality import validate_scene_causality
from .antagonist_planner import prepare_antagonist_plan, antagonist_prompt_payload
from .pattern_memory import update_pattern_memory, pattern_prompt_payload
from .market_serialization import market_prompt_payload, update_market_serialization
from .causal_repair import build_causal_repair_plan, store_causal_repair_plan
from .portfolio_memory import portfolio_prompt_payload, update_portfolio_memory
from analytics.content_ceiling import evaluate_episode

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
    pj = cfg["project"]
    sub_key = pj.get("sub_engine", "AUTO")

    profiles_dir = os.path.join("data","profiles")
    profiles = load_profiles(profiles_dir)

    snap = ext.latest(pj["platform"], pj["genre_bucket"]) or {}
    prompt = PROMPTS.master_outline(cfg, snap, sub_key)
    resp = llm.call(prompt, temperature=0.45)
    cost.add_usage(resp)
    outline = resp.output_text
    state.set("outline", outline)
    return outline

from .backup_manager import backup_file

from .full_backup_manager import snapshot_project

def generate_episode(cfg, state, llm, cost, ext: ExternalRankSignals, episode: int) -> dict:
    pj = cfg["project"]
    out_dir = ensure_project_dirs(cfg)
    state.data['out_dir'] = out_dir
    state.data['_cfg_for_models'] = cfg

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
    cur_obj = draft_obj
    for _ in range(max_passes):
        rewrite_repair_plan = build_causal_repair_plan(
            validate_scene_causality(
                str(cur_obj.get("episode_text", "")),
                story_state=state.data.get("story_state_v2", {}),
                event_plan=event_plan,
                cliffhanger_plan=cliffhanger_plan,
            ),
            story_state=state.data.get("story_state_v2", {}),
            event_plan=event_plan,
            cliffhanger_plan=cliffhanger_plan,
        )
        rewrite_prompt = PROMPTS.episode_rewrite_json(
            cfg, cur_obj, episode, knobs, style, sub_key, viral_required, story_state=story_state, repair_plan=rewrite_repair_plan
        )
        rewrite_resp = llm.call(rewrite_prompt, temperature=0.55)
        cost.add_usage(rewrite_resp)
        ok2, obj2 = parse_json_strict(rewrite_resp.output_text)
        if ok2 and isinstance(obj2, dict):
            cur_obj = obj2
        # validate viral if required
        if not viral_required:
            break
        valid, _msg = validate_viral(cur_obj, cliffhanger_plan=cliffhanger_plan)
        if valid:
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
    predicted_retention = predict_retention(score_obj, fat, state.data.get("retention_engine"))
    state.set("predicted_retention", predicted_retention)
    causal_report = validate_scene_causality(
        episode_text,
        story_state=state.data.get("story_state_v2", {}),
        event_plan=event_plan,
        cliffhanger_plan=cliffhanger_plan,
    )
    repair_plan = build_causal_repair_plan(
        causal_report,
        story_state=state.data.get("story_state_v2", {}),
        event_plan=event_plan,
        cliffhanger_plan=cliffhanger_plan,
    )
    store_causal_repair_plan(state.data, repair_plan)
    objective_scores = build_multi_objective_scores(
        score_obj,
        retention_state=state.data.get("retention_engine", {}),
        story_state=state.data.get("story_state_v2", {}),
        causal_report=causal_report,
    )
    objective_balance = multi_objective_balance(
        score_obj,
        retention_state=state.data.get("retention_engine", {}),
        story_state=state.data.get("story_state_v2", {}),
        causal_report=causal_report,
    )
    ceiling_meta = {
        "genre_bucket": pj["genre_bucket"],
        "platform": pj["platform"],
        "event_plan": event_plan,
        "cliffhanger": meta.get("cliffhanger", ""),
        "cliffhanger_plan": meta.get("cliffhanger_plan", {}),
        "conflict": story_state.get("conflict", {}),
        "retention": state.data.get("retention_engine", {}),
        "tension": state.data.get("tension_wave", {}),
        "story_state": state.data.get("story_state_v2", {}),
        "multi_objective": objective_scores,
        "scene_causality": causal_report,
    }
    content_ceiling = evaluate_episode(episode_text, ceiling_meta)
    meta["content_ceiling"] = content_ceiling
    meta["multi_objective"] = {
        "axes": objective_scores,
        "balance": objective_balance,
    }
    meta["scene_causality"] = causal_report
    meta["causal_repair"] = repair_plan

    # update score history
    hist = state.get("score_history", [])
    hist.append(score_obj)
    state.set("score_history", hist)

    # write episode file
    full_text = (
        episode_text
        + "\n\n[META]\n"
        + json.dumps(meta, ensure_ascii=False, indent=2)
        + "\n\n[SCORES]\n"
        + json.dumps(score_obj, ensure_ascii=False, indent=2)
        + "\n"
    )
    write_text(os.path.join(out_dir, f"episode_{episode:03}.txt"), full_text, safe_mode=cfg.get('safe_mode', False), project_dir_for_backup=out_dir)

    # metrics log
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "episode": episode,
        "platform": pj["platform"],
        "genre_bucket": pj["genre_bucket"],
        "sub_engine": pick_subengine(pj["genre_bucket"], sub_key).key,
        "knobs": knobs,
        "external": snap,
        "meta": meta,
        "scores": score_obj,
        "style_vector": state.get("style_vector"),
        "fatigue": fat_pack,
        "retention": {
            "predicted_next_episode": predicted_retention,
            "pressure_state": state.data.get("retention_engine", {}),
        },
        "content_ceiling": content_ceiling,
        "cost": cost.snapshot(),
    }
    if cfg["output"].get("save_metrics_jsonl", True):
        append_jsonl(os.path.join(out_dir, "metrics.jsonl"), record, safe_mode=cfg.get("safe_mode", False), project_dir_for_backup=out_dir)

    # update state
    register_story_event(state.data, event_plan)
    update_character_arc(state.data, episode, score_obj=score_obj, event_plan=event_plan)
    update_conflict_memory(state.data, episode, score_obj=score_obj, event_plan=event_plan)
    update_tension_wave(state.data, episode, score_obj=score_obj, event_plan=event_plan)
    update_world_state(state.data, episode, event_plan=event_plan)
    update_reward_serialization(state.data, episode, event_plan=event_plan)
    prepare_information_emotion(state.data, episode=episode, event_plan=event_plan)
    update_pattern_memory(state.data, episode=episode, event_plan=event_plan, cliffhanger_plan=cliffhanger_plan)
    update_market_serialization(state.data, episode=episode, cfg=cfg, event_plan=event_plan)
    update_portfolio_memory(state.data, cfg=cfg, event_plan=event_plan)
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
    thresholds = cfg.get('quality',{})
    if not quality_gate(score_obj, thresholds):
        knobs['hook_intensity'] = min(0.99, knobs.get('hook_intensity',0.7)+0.1)
        knobs['payoff_intensity'] = min(0.99, knobs.get('payoff_intensity',0.7)+0.1)
    knobs = apply_freeze(cfg, state.data, knobs)
    register_change(cfg, state.data, knobs)
    state.set("next_episode", episode + 1)

    # save cost summary incrementally
    cost.enforce_token_ceiling()

    return record
