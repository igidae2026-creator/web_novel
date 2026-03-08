from __future__ import annotations

from typing import Any, Dict


CLIFFHANGER_MODES = {
    "reveal": "revelation_cut",
    "betrayal": "choice_lock",
    "reversal": "reversal_afterglow",
    "loss": "sacrifice_fallout",
    "arrival": "arrival_shock",
}


def generate_cliffhanger_plan(
    character_payload: Dict[str, Any],
    conflict_payload: Dict[str, Any],
    event_plan: Dict[str, Any],
) -> Dict[str, Any]:
    protagonist = (character_payload or {}).get("protagonist", {})
    threads = (conflict_payload or {}).get("threads", []) or []
    lead_thread = threads[0] if threads else {}
    event_type = str((event_plan or {}).get("type", "")).strip().lower()
    mode = CLIFFHANGER_MODES.get(event_type, "threat_imminent")
    open_question = {
        "reveal": "드러난 진실이 누구를 먼저 무너뜨릴까",
        "betrayal": "누가 먼저 칼을 빼들었고 누가 늦게 알아차릴까",
        "reversal": "방금 뒤집힌 판에서 누가 먼저 추락할까",
        "loss": "잃어버린 것을 되찾으려면 무엇을 더 버려야 할까",
        "arrival": "새로 도착한 압력이 누구의 편에 설까",
    }.get(event_type, "다음 선택의 대가는 누가 치를까")
    withheld = str((event_plan or {}).get("consequence") or lead_thread.get("consequence") or "더 큰 대가가 회수된다")
    target = lead_thread.get("label") or event_plan.get("target_label") or protagonist.get("surface_goal") or "주 갈등"
    carryover = int((event_plan or {}).get("carryover_pressure", 6) or 6)

    suggested_line = (
        f"{target}은 아직 끝나지 않았다. "
        f"{withheld}. "
        f"그리고 {open_question}."
    )
    return {
        "mode": mode,
        "open_question": open_question,
        "withheld_consequence": withheld,
        "target": target,
        "carryover_pressure": carryover,
        "suggested_line": suggested_line,
    }


def validate_cliffhanger(meta: Dict[str, Any], cliffhanger_plan: Dict[str, Any] | None = None) -> tuple[bool, str]:
    cliffhanger = str((meta or {}).get("cliffhanger", "")).strip()
    if len(cliffhanger) < 8:
        return False, "cliffhanger missing/too short"

    plan = dict(cliffhanger_plan or {})
    if not plan:
        return ("?" in cliffhanger or "!" in cliffhanger or "…" in cliffhanger), "cliffhanger lacks structure"

    checks = [
        any(token in cliffhanger for token in [str(plan.get("target", ""))[:6], "대가", "진실", "누가", "무엇", "끝나지"]),
        len(str(plan.get("open_question", "")).strip()) >= 4,
        int(plan.get("carryover_pressure", 0) or 0) >= 5,
    ]
    return all(checks), "ok" if all(checks) else "cliffhanger missing withheld consequence or next-step pressure"


def enforce_cliffhanger(meta: Dict[str, Any], cliffhanger_plan: Dict[str, Any]) -> Dict[str, Any]:
    patched = dict(meta or {})
    valid, _ = validate_cliffhanger(patched, cliffhanger_plan)
    if valid:
        return patched
    patched["cliffhanger"] = str(cliffhanger_plan.get("suggested_line", patched.get("cliffhanger", ""))).strip()
    return patched
