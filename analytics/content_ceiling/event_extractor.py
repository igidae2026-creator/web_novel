from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Any

SENT_SPLIT = re.compile(r"(?<=[.!?。！？])\s+|\n+")

REWARD = ["해냈", "성공", "해결", "끝났다", "드디어", "마침내", "손에 넣", "이겼", "승리", "안도"]
SETBACK = ["실패", "망했", "끝", "파멸", "무너", "잃", "죽", "배신", "함정", "위기", "절망"]
STATUS_UP = ["각성", "깨달", "레벨", "승급", "인정", "권한", "지위", "왕", "귀족", "대표", "우두머리", "상위"]
ESCALATE = ["더", "점점", "결국", "마침내", "이제", "돌이킬 수", "끝내", "완전히", "폭발"]


def sentences(text: str) -> List[str]:
    return [s.strip() for s in SENT_SPLIT.split(text) if s and s.strip()]


def _positions(text: str, markers: List[str]) -> List[int]:
    pos = []
    sents = sentences(text)
    for i, s in enumerate(sents):
        if any(m in s for m in markers):
            pos.append(i)
    return pos


def _intervals(pos: List[int]) -> List[int]:
    if len(pos) < 2:
        return []
    return [pos[i] - pos[i - 1] for i in range(1, len(pos))]


@dataclass
class EventStats:
    reward_positions: List[int]
    reward_intervals: List[int]
    status_positions: List[int]
    status_intervals: List[int]
    escalation_steps: int
    escalation_hits: int
    typed_event: str
    unresolved_threads: int
    consequence_level: int
    carryover_pressure: int


def extract_events(text: str, meta: Dict[str, Any] | None = None) -> EventStats:
    meta = dict(meta or {})
    rpos = _positions(text, REWARD)
    spos = _positions(text, STATUS_UP)
    rint = _intervals(rpos)
    sint = _intervals(spos)

    sents = sentences(text)
    hits = [sum(1 for m in ESCALATE if m in s) + sum(1 for m in SETBACK if m in s) for s in sents]
    steps = 0
    prev = 0
    for h in hits:
        if h >= 2 and prev < 2:
            steps += 1
        prev = h

    conflict = meta.get("conflict", {}) or {}
    event_plan = meta.get("event_plan", {}) or {}
    retention = meta.get("retention", {}) or {}
    structural_steps = 0
    if event_plan.get("type"):
        structural_steps += 1
    if int(conflict.get("consequence_level", 0) or 0) >= 6:
        structural_steps += 1
    if int(retention.get("unresolved_thread_pressure", 0) or 0) >= 7:
        structural_steps += 1

    return EventStats(
        reward_positions=rpos,
        reward_intervals=rint,
        status_positions=spos,
        status_intervals=sint,
        escalation_steps=max(steps, structural_steps),
        escalation_hits=sum(hits) + structural_steps,
        typed_event=str(event_plan.get("type", "")),
        unresolved_threads=len(conflict.get("threads", []) or []),
        consequence_level=int(conflict.get("consequence_level", 0) or 0),
        carryover_pressure=int((meta.get("cliffhanger_plan", {}) or {}).get("carryover_pressure", 0) or 0),
    )
