import re
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class StyleVector:
    sentence_len_mean: float = 20.0
    sentence_len_std: float = 8.0
    dialogue_ratio: float = 0.45
    exclamation_density: float = 0.04
    question_density: float = 0.04
    ellipsis_density: float = 0.02

def _sentences(text: str):
    # crude segmentation
    parts = re.split(r"[\n\r]+", text)
    sents = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        ss = re.split(r"(?<=[\.!?。！？])\s+", p)
        for s in ss:
            s = s.strip()
            if s:
                sents.append(s)
    return sents

def _dialogue_lines(text: str):
    # heuristic: lines containing quotes or leading dash
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    dlg = []
    for l in lines:
        if any(q in l for q in ['"','“','”','『','』','「','」']) or l.startswith("-") or l.startswith("—"):
            dlg.append(l)
    return dlg, lines

def compute_style_vector(text: str) -> StyleVector:
    sents = _sentences(text)
    if not sents:
        return StyleVector()
    lens = [max(1, len(re.sub(r"\s+","", s))) for s in sents]  # char count without spaces
    mean = sum(lens)/len(lens)
    var = sum((x-mean)**2 for x in lens)/len(lens)
    std = var**0.5
    dlg, lines = _dialogue_lines(text)
    dialogue_ratio = (len(dlg) / max(1, len(lines)))
    total_chars = max(1, len(text))
    exclam = text.count("!") / total_chars
    qmark = text.count("?") / total_chars
    ell = (text.count("...") + text.count("…")) / total_chars
    return StyleVector(
        sentence_len_mean=float(mean),
        sentence_len_std=float(std),
        dialogue_ratio=float(dialogue_ratio),
        exclamation_density=float(exclam),
        question_density=float(qmark),
        ellipsis_density=float(ell),
    )

def blend(prev: StyleVector, new: StyleVector, alpha: float = 0.15) -> StyleVector:
    def b(a, c):
        return (1-alpha)*a + alpha*c
    return StyleVector(
        sentence_len_mean=b(prev.sentence_len_mean, new.sentence_len_mean),
        sentence_len_std=b(prev.sentence_len_std, new.sentence_len_std),
        dialogue_ratio=b(prev.dialogue_ratio, new.dialogue_ratio),
        exclamation_density=b(prev.exclamation_density, new.exclamation_density),
        question_density=b(prev.question_density, new.question_density),
        ellipsis_density=b(prev.ellipsis_density, new.ellipsis_density),
    )

def to_dict(v: StyleVector) -> dict:
    return asdict(v)

def from_dict(d: Optional[dict]) -> StyleVector:
    if not d:
        return StyleVector()
    return StyleVector(**{k: float(d.get(k)) for k in StyleVector().__dict__.keys() if k in d})

def constraints_text(v: StyleVector) -> str:
    # widen a bit to avoid overfitting
    return (
        f"- 문장 길이 평균은 대략 {v.sentence_len_mean:.1f}±{max(6.0, v.sentence_len_std):.1f} 범위 유지\n"
        f"- 대사 비율(대사 라인 비율)은 대략 {v.dialogue_ratio:.2f} 근처로 유지(±0.10)\n"
        f"- 과도한 느낌표/물음표 남발 금지(현재 밀도 참고: ! {v.exclamation_density:.3f}, ? {v.question_density:.3f})\n"
        f"- 말줄임표 남발 금지(현재 밀도 참고: {v.ellipsis_density:.3f})\n"
        f"- 주인공 음성/말투 일관성 유지\n"
    )
