from __future__ import annotations
import os, json, copy
from typing import Dict, Any, Tuple
from engine.track_queue import load_queue_state, save_queue_state, current_track_dir, advance
from engine.track_loader import load_track
from engine.state import StateStore
from engine.openai_client import LLM
from engine.cost import CostTracker
from engine.external_rank import ExternalRankSignals
from engine.pipeline import generate_episode, ensure_project_dirs
from engine.cross_track_release import apply_queue_release_outcome, apply_runtime_release_to_state, refresh_queue_release_runtime, resolve_queue_release_action

MAX_TRACK_ERRORS = 3
from engine.safe_guard import UnsafeOperationError, require_safe_mode
from engine.io_utils import append_jsonl

def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(a)
    def merge(x, y):
        for k, v in y.items():
            if isinstance(v, dict) and isinstance(x.get(k), dict):
                merge(x[k], v)
            else:
                x[k] = v
    merge(out, b)
    return out


def run_queue_step(cfg: Dict[str, Any]) -> Tuple[bool, str]:
    """Run exactly one track-step: generate next episode for current track, then advance queue.
    Returns (ok, message).
    """
    # Require safe mode for automation
    require_safe_mode(cfg)

    q = load_queue_state()
    if q.get("status") != "running":
        return False, f"Queue not running (status={q.get('status')})"

    tdir = current_track_dir(q)
    if not tdir:
        q["status"] = "done"
        save_queue_state(q)
        return False, "No more tracks"

    try:
        tracks_root = os.path.dirname(tdir)
        q = refresh_queue_release_runtime(q, tracks_root)
        runtime_entry = resolve_queue_release_action(q, tdir)
        tcfg = load_track(tdir)  # minimal track.json created by generator
        # Merge track config into runtime cfg (do not override model/limits by default)
        merged = _deep_merge(cfg, tcfg)
        merged.setdefault("track", {})
        merged["track"]["dir"] = tdir

        # Track-local state store
        state_path = os.path.join(tdir, "state.json")
        out_dir = ensure_project_dirs(merged)  # -> <tdir>/outputs
        state = StateStore(state_path, safe_mode=bool(merged.get("safe_mode", False)), project_dir_for_backup=out_dir)
        state.load()
        apply_runtime_release_to_state(state.data, runtime_entry)

        if runtime_entry.get("action") == "hold":
            outcome = apply_queue_release_outcome(q, tdir, executed=False)
            save_queue_state(outcome["queue_state"])
            append_jsonl(
                os.path.join(tdir, 'outputs', 'metrics.jsonl'),
                {"type": "queue_step_skipped", "track": os.path.basename(tdir), "reason": "release_hold", "runtime_release": outcome["runtime_action"]},
                safe_mode=bool(merged.get('safe_mode', False)),
                project_dir_for_backup=tdir,
            )
            advance(outcome["queue_state"])
            return True, f"Held track {os.path.basename(tdir)} for staggered release"

        llm = LLM(merged)
        cost = CostTracker(merged, out_dir)
        ext = ExternalRankSignals(merged)

        ep = int(state.get("next_episode", 1) or 1)
        generate_episode(merged, state, llm, cost, ext, ep)
        state.save()
        cost.write_summary()

        # Advance queue
        outcome = apply_queue_release_outcome(q, tdir, executed=True)
        save_queue_state(outcome["queue_state"])
        append_jsonl(os.path.join(tdir, 'outputs', 'metrics.jsonl'),
    {"type":"queue_step","track":os.path.basename(tdir),"episode":ep,"runtime_release": outcome["runtime_action"]},
    safe_mode=bool(merged.get('safe_mode', False)), project_dir_for_backup=tdir)
        if outcome["should_advance"]:
            advance(outcome["queue_state"])
            return True, f"Ran track {os.path.basename(tdir)} episode {ep}"
        save_queue_state(outcome["queue_state"])
        return True, f"Accelerated track {os.path.basename(tdir)} episode {ep}"
    except UnsafeOperationError as ue:
        q["last_error"] = str(ue)
        q["status"] = "paused"
        save_queue_state(q)
        return False, f"Blocked: {ue}"
    except Exception as e:
        # error accounting
        try:
            errs = q.get('track_errors', {})
            key = os.path.basename(tdir)
            errs[key] = int(errs.get(key, 0) or 0) + 1
            q['track_errors'] = errs
            if errs[key] >= MAX_TRACK_ERRORS:
                # skip this track for now
                advance(q)
                q['status'] = 'running'
                q['last_error'] = f'skipped {key} after {errs[key]} errors'
                save_queue_state(q)
                return False, q['last_error']
        except Exception:
            pass
        
        q["last_error"] = repr(e)
        q["status"] = "paused"
        save_queue_state(q)
        return False, f"Error: {e}"


def retry_current(cfg: dict) -> tuple[bool,str]:
    q = load_queue_state()
    if q.get("status") != "paused":
        return False, "Queue not paused"
    tdir = current_track_dir(q)
    if not tdir:
        return False, "No current track"
    try:
        ok,msg = run_queue_step(cfg)
        return ok,msg
    except Exception as e:
        # error accounting
        try:
            errs = q.get('track_errors', {})
            key = os.path.basename(tdir)
            errs[key] = int(errs.get(key, 0) or 0) + 1
            q['track_errors'] = errs
            if errs[key] >= MAX_TRACK_ERRORS:
                # skip this track for now
                advance(q)
                q['status'] = 'running'
                q['last_error'] = f'skipped {key} after {errs[key]} errors'
                save_queue_state(q)
                return False, q['last_error']
        except Exception:
            pass
        
        return False,str(e)
