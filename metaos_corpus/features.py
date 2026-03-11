from __future__ import annotations
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

@dataclass
class TextFeatures:
    chars: int
    lines: int
    sentences: int
    sentence_len_mean: float
    sentence_len_std: float
    dialogue_ratio: float
    cliff_density: float
    exclam_density: float
    question_density: float
    ellipsis_density: float
    emotion_proxy: float

_SENT_SPLIT = re.compile(r"(?<=[\.!?。！？])\s+")
_NONSPACE = re.compile(r"\s+")

def _sentences(text: str) -> List[str]:
    parts = [p.strip() for p in re.split(r"[\r\n]+", text) if p.strip()]
    sents: List[str] = []
    for p in parts:
        for s in _SENT_SPLIT.split(p):
            s = s.strip()
            if s:
                sents.append(s)
    return sents

def _dialogue_lines(text: str) -> Tuple[int,int]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return 0, 0
    dlg = 0
    for l in lines:
        if any(q in l for q in ['"','“','”','『','』','「','」']) or l.startswith("-") or l.startswith("—"):
            dlg += 1
    return dlg, len(lines)

def compute_features(text: str) -> TextFeatures:
    text = text or ""
    chars = len(text)
    lines = len(text.splitlines())
    sents = _sentences(text)
    if sents:
        lens = [max(1, len(_NONSPACE.sub("", s))) for s in sents]
        mean = sum(lens)/len(lens)
        var = sum((x-mean)**2 for x in lens)/len(lens)
        std = var**0.5
    else:
        mean, std = 0.0, 0.0

    dlg, total_lines = _dialogue_lines(text)
    dialogue_ratio = (dlg / total_lines) if total_lines else 0.0

    tail = text[-500:] if len(text) > 500 else text
    cliff_markers = 0
    if re.search(r"(다음|계속|to be continued|continued)", tail, re.IGNORECASE):
        cliff_markers += 1
    if tail.strip().endswith(("?", "!", "…", "...", "?!", "!!")):
        cliff_markers += 1
    cliff_density = cliff_markers / 2.0

    total = max(1, chars)
    exclam_density = text.count("!") / total
    question_density = text.count("?") / total
    ellipsis_density = (text.count("...") + text.count("…")) / total

    emo_words = len(re.findall(r"(심장|눈물|떨|분노|사랑|절망|환희|미친|미쳤|죽을|살아|무서|두려|행복)", text))
    emotion_proxy = min(1.0, (exclam_density*50 + question_density*40 + ellipsis_density*60 + emo_words/max(1, chars/1000)) / 3.0)

    return TextFeatures(
        chars=chars, lines=lines, sentences=len(sents),
        sentence_len_mean=float(mean), sentence_len_std=float(std),
        dialogue_ratio=float(dialogue_ratio),
        cliff_density=float(cliff_density),
        exclam_density=float(exclam_density),
        question_density=float(question_density),
        ellipsis_density=float(ellipsis_density),
        emotion_proxy=float(emotion_proxy),
    )

def to_dict(f: TextFeatures) -> Dict:
    return asdict(f)
