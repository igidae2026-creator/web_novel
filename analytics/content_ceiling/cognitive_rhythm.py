from __future__ import annotations
import re, statistics
from dataclasses import dataclass
from typing import List

SENT_SPLIT = re.compile(r"(?<=[.!?。！？])\s+|\n+")

def _sentences(text: str) -> List[str]:
    return [s.strip() for s in SENT_SPLIT.split(text) if s and s.strip()]

@dataclass
class Rhythm:
    mean_len: float
    std_len: float
    inversion_hits: int
    attention_resets: int

INVERSION = ["하지만", "그러나", "오히려", "반대로", "그런데"]

def compute_rhythm(text: str) -> Rhythm:
    sents = _sentences(text)
    lens = [len(s) for s in sents] or [0]
    mean = float(statistics.mean(lens))
    std = float(statistics.pstdev(lens)) if len(lens) > 1 else 0.0
    inv = sum(text.count(w) for w in INVERSION)
    # attention reset proxy: count of punctuation spikes per ~30-60s chunk (sentence blocks)
    resets = 0
    block = 0
    for s in sents:
        block += 1
        if ("?" in s) or ("!" in s) or ("…" in s):
            resets += 1
        if block >= 6:
            block = 0
    return Rhythm(mean_len=mean, std_len=std, inversion_hits=inv, attention_resets=resets)
