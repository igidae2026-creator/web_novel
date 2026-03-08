from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Guidance:
    focus: List[str]
    edits: List[str]

def generate(stats: Dict[str, Any]) -> Guidance:
    focus = []
    edits = []
    curve = stats.get("curve", {})
    if curve and curve.get("peaks", 0) < 2:
        focus.append("감정 변곡점 부족")
        edits.append("중반에 반전/위기 1개 추가 (한 문단 단위)")
    if stats.get("cliff", {}).get("dominant") == "none":
        focus.append("클리프행어 약함")
        edits.append("마지막 2~3문장: 질문형 또는 '그 순간/하지만…' 컷 추가")
    if stats.get("rhythm", {}).get("std_len", 0) < 5:
        focus.append("리듬 변화 부족")
        edits.append("짧은 문장 3연타 → 긴 문장 1개 → 짧은 문장 2개로 리듬 재배치")
    if stats.get("events", {}).get("escalation_steps", 0) < 2:
        focus.append("갈등 상승 계단 부족")
        edits.append("외부 압박 1단계 추가(추격/감시/제한) 후 즉시 비용(대가) 명시")
    if not focus:
        focus.append("유지")
        edits.append("초반 500자만 더 압축하고, 마지막 1문장 클리프 강화")
    return Guidance(focus=focus, edits=edits)
