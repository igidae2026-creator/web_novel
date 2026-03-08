from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

MEANING = ["진실","의미","가치","선택","운명","존재","정체","신념","원칙"]
RISK = ["죽","파멸","위험","대가","희생","잃","끝","무너","붕괴","멸망"]
AGENCY = ["결정","선택","각성","행동","거부","돌파","주도","맞서","선언"]
SENSORY = ["차갑","뜨겁","떨","숨","피","어둠","빛","냄새","맛","촉감"]

def _count(text, words):
    return sum(text.count(w) for w in words)

@dataclass
class Axes:
    meaning_depth: int
    risk_intensity: int
    character_agency: int
    sensory_density: int

def compute_axes(text: str) -> Axes:
    return Axes(
        meaning_depth=_count(text, MEANING),
        risk_intensity=_count(text, RISK),
        character_agency=_count(text, AGENCY),
        sensory_density=_count(text, SENSORY),
    )
