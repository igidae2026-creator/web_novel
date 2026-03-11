from __future__ import annotations
import statistics, re, math
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple

EMO = {
  "fear": ["두렵", "무섭", "공포", "불안", "긴장", "위협", "떨"],
  "anger": ["분노", "화가", "증오", "격분", "분개"],
  "desire": ["원하", "갈망", "욕망", "바라", "필요"],
  "urgency": ["지금", "당장", "빨리", "서둘", "시간", "마감", "한계"],
  "loss": ["잃", "파멸", "끝", "죽", "망", "상처", "대가", "희생"],
}

def _hits(text: str) -> int:
    return sum(text.count(s) for stems in EMO.values() for s in stems)

def _segment(text: str, n: int = 8) -> List[str]:
    if not text:
        return [""]*n
    L = len(text)
    return [text[int(L*i/n):int(L*(i+1)/n)] for i in range(n)]

@dataclass
class Curve:
    segment_density: List[float]
    mean: float
    std: float
    slope: float
    peaks: int

def compute_curve(text: str, segments: int = 8) -> Curve:
    segs = _segment(text, segments)
    dens = []
    for s in segs:
        d = (_hits(s) / max(1, len(s))) * 1000.0
        dens.append(float(d))
    mean = float(statistics.mean(dens)) if dens else 0.0
    std = float(statistics.pstdev(dens)) if len(dens) > 1 else 0.0
    xs = list(range(len(dens)))
    if len(dens) >= 2:
        xm = statistics.mean(xs); ym = statistics.mean(dens)
        num = sum((x-xm)*(y-ym) for x,y in zip(xs,dens))
        den = sum((x-xm)**2 for x in xs) or 1.0
        slope = float(num/den)
    else:
        slope = 0.0
    peaks = 0
    for i in range(1, len(dens)-1):
        if dens[i] > dens[i-1] and dens[i] > dens[i+1]:
            peaks += 1
    return Curve(segment_density=dens, mean=mean, std=std, slope=slope, peaks=peaks)
