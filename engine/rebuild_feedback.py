from __future__ import annotations
from typing import Dict, Tuple

def _get_hook(score_obj: Dict) -> float:
    try:
        return float(score_obj.get("hook_score", score_obj.get("hook", 0.0)) or 0.0)
    except Exception:
        return 0.0

def record_pre_rebuild(state: Dict, episode: int, score_obj: Dict):
    state["rebuild_last_pre"] = {
        "episode": int(episode),
        "hook": _get_hook(score_obj),
    }

def record_post_rebuild(state: Dict, episode: int, score_obj: Dict):
    # keep a rolling window of hook after rebuild
    post = state.get("rebuild_last_post", [])
    post.append({"episode": int(episode), "hook": _get_hook(score_obj)})
    if len(post) > 3:
        post = post[-3:]
    state["rebuild_last_post"] = post

def evaluate_rebuild(state: Dict) -> Tuple[bool, str]:
    """Return (evaluated, verdict). Verdict: 'improved'|'no_change'|'worse'."""
    pre = state.get("rebuild_last_pre")
    post = state.get("rebuild_last_post", [])
    if not pre or len(post) < 2:
        return False, "insufficient"
    pre_hook = float(pre.get("hook", 0.0))
    post_mean = sum(float(x.get("hook",0.0)) for x in post) / len(post)
    delta = post_mean - pre_hook
    # small deadband to avoid noise
    if delta > 0.03:
        return True, "improved"
    if delta < -0.03:
        return True, "worse"
    return True, "no_change"

def apply_feedback(cfg: Dict, state: Dict):
    """Stability-first feedback:
    - If improved: reduce rebuild_level by 1 (down to 0) to avoid runaway.
    - If worse: keep level (do not escalate here; escalation already handled by trigger logic).
    - If no_change: keep.
    Also extends cooldown slightly on worse to prevent thrash.
    """
    evaluated, verdict = evaluate_rebuild(state)
    if not evaluated:
        return

    lvl = int(state.get("rebuild_level", 0) or 0)
    if verdict == "improved":
        state["rebuild_level"] = max(0, lvl - 1)
        state.setdefault("rebuild_feedback", []).append({"verdict": verdict})
    elif verdict == "worse":
        cd = int(state.get("rebuild_cooldown", 0) or 0)
        state["rebuild_cooldown"] = max(cd, int(cfg.get("rebuild", {}).get("cooldown", 5)) + 2)
        state.setdefault("rebuild_feedback", []).append({"verdict": verdict})
    else:
        state.setdefault("rebuild_feedback", []).append({"verdict": verdict})

    # reset evaluation buffers
    state.pop("rebuild_last_pre", None)
    state.pop("rebuild_last_post", None)
