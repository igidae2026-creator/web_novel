from __future__ import annotations

import re
from typing import Any, Dict


CLIFFHANGER_MODES = {
    "reveal": "revelation_cut",
    "betrayal": "choice_lock",
    "reversal": "reversal_afterglow",
    "loss": "sacrifice_fallout",
    "arrival": "arrival_shock",
    "sacrifice": "moral_cost_cut",
    "timer": "deadline_cut",
    "power_shift": "order_flip_cut",
    "false_victory": "trap_snap",
    "collapse": "collapse_edge",
    "misunderstanding": "relational_breach",
}

_TOKEN_RE = re.compile(r"[A-Za-z0-9가-힣]+")
_STOPWORDS = {
    "그리고",
    "그러나",
    "그럼",
    "그때",
    "다음",
    "선택",
    "대가",
    "누가",
    "무엇",
    "어디",
    "언제",
    "어떻게",
    "왜",
    "이번",
    "아직",
    "정말",
    "먼저",
    "이제",
    "계속",
    "끝",
    "끝나지",
}


def _anchor_tokens(text: Any) -> set[str]:
    tokens = {
        token
        for token in _TOKEN_RE.findall(str(text or "").strip().lower())
        if len(token) >= 2 and token not in _STOPWORDS
    }
    return tokens


def _has_question_pressure(text: str, open_question: str) -> bool:
    normalized = str(text or "").strip()
    if "?" in normalized:
        return True
    return bool(_anchor_tokens(open_question).intersection(_anchor_tokens(normalized)))


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
        "sacrifice": "살리기 위해 버린 것이 어떤 형태로 돌아올까",
        "timer": "남은 시간이 닫히기 전에 누가 먼저 움직일까",
        "power_shift": "새 규칙의 첫 희생자는 누가 될까",
        "false_victory": "이 승리가 왜 함정이었는지 누가 가장 늦게 깨달을까",
        "collapse": "무너진 자리에서 무엇이 먼저 사라질까",
        "misunderstanding": "엇갈린 믿음이 누구를 먼저 적으로 만들까",
    }.get(event_type, "다음 선택의 대가는 누가 치를까")
    withheld = str((event_plan or {}).get("consequence") or lead_thread.get("consequence") or "더 큰 대가가 회수된다")
    target = lead_thread.get("label") or event_plan.get("target_label") or protagonist.get("surface_goal") or "주 갈등"
    carryover = int((event_plan or {}).get("carryover_pressure", 6) or 6)
    irreversible = str((event_plan or {}).get("irreversible_if_lost") or lead_thread.get("irreversible_if_lost") or "이번 선택은 관계나 질서를 되돌릴 수 없게 바꾼다.")

    suggested_line = (
        f"{target}은 아직 끝나지 않았다. "
        f"{withheld}. "
        f"{irreversible} "
        f"그리고 {open_question}."
    )
    return {
        "mode": mode,
        "open_question": open_question,
        "withheld_consequence": withheld,
        "target": target,
        "carryover_pressure": carryover,
        "irreversible_cost": irreversible,
        "suggested_line": suggested_line,
    }


def validate_cliffhanger(meta: Dict[str, Any], cliffhanger_plan: Dict[str, Any] | None = None) -> tuple[bool, str]:
    cliffhanger = str((meta or {}).get("cliffhanger", "")).strip()
    if len(cliffhanger) < 12:
        return False, "cliffhanger missing/too short"

    plan = dict(cliffhanger_plan or {})
    if not plan:
        return ("?" in cliffhanger or "!" in cliffhanger or "…" in cliffhanger), "cliffhanger lacks structure"

    target_tokens = _anchor_tokens(plan.get("target"))
    consequence_tokens = _anchor_tokens(plan.get("withheld_consequence")) | _anchor_tokens(plan.get("irreversible_cost"))
    cliffhanger_tokens = _anchor_tokens(cliffhanger)
    question_pressure = _has_question_pressure(cliffhanger, str(plan.get("open_question", "")))
    target_link = bool(target_tokens.intersection(cliffhanger_tokens))
    consequence_link = bool(consequence_tokens.intersection(cliffhanger_tokens))

    checks = [
        len(str(plan.get("open_question", "")).strip()) >= 4,
        int(plan.get("carryover_pressure", 0) or 0) >= 5,
        bool(str(plan.get("irreversible_cost", "")).strip()),
        question_pressure,
        target_link or consequence_link,
    ]
    if all(checks):
        return True, "ok"
    if not question_pressure:
        return False, "cliffhanger missing explicit next-question pressure"
    if not (target_link or consequence_link):
        return False, "cliffhanger not specific to planned conflict"
    return False, "cliffhanger missing withheld consequence or next-step pressure"


def enforce_cliffhanger(meta: Dict[str, Any], cliffhanger_plan: Dict[str, Any]) -> Dict[str, Any]:
    patched = dict(meta or {})
    valid, _ = validate_cliffhanger(patched, cliffhanger_plan)
    if valid:
        return patched
    patched["cliffhanger"] = str(cliffhanger_plan.get("suggested_line", patched.get("cliffhanger", ""))).strip()
    return patched
