from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List, Any
from collections import defaultdict

# Content-only micro-pattern clustering: lightweight k-medoids on feature vectors
from .cognitive_rhythm import compute_rhythm
from .emotional_curve import compute_curve
from .axes import compute_axes

def _vec(text: str) -> List[float]:
    r = compute_rhythm(text)
    c = compute_curve(text)
    a = compute_axes(text)
    return [
        r.mean_len/30.0, r.std_len/15.0, r.inversion_hits/10.0,
        c.mean/20.0, c.std/10.0, c.slope/5.0,
        a.meaning_depth/10.0, a.risk_intensity/10.0, a.character_agency/10.0, a.sensory_density/10.0
    ]

def _cos(a: List[float], b: List[float]) -> float:
    import math
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a)) or 1.0
    nb = math.sqrt(sum(x*x for x in b)) or 1.0
    return dot/(na*nb)

def _kmedoids(ids: List[str], vecs: Dict[str, List[float]], k: int, iters: int = 12) -> Dict[int, List[str]]:
    medoids = [ids[0]]
    while len(medoids) < k:
        best_id, best_dist = None, -1.0
        for _id in ids:
            if _id in medoids: 
                continue
            dist = sum(1.0 - _cos(vecs[_id], vecs[m]) for m in medoids) / len(medoids)
            if dist > best_dist:
                best_dist, best_id = dist, _id
        medoids.append(best_id or ids[len(medoids)])
    for _ in range(iters):
        clusters = {i: [] for i in range(k)}
        for _id in ids:
            best, best_sim = 0, -1.0
            for i, m in enumerate(medoids):
                sim = _cos(vecs[_id], vecs[m])
                if sim > best_sim:
                    best, best_sim = i, sim
            clusters[best].append(_id)
        new_medoids = []
        for i in range(k):
            members = clusters[i] or [medoids[i]]
            best_m, best_score = medoids[i], -1.0
            for cand in members:
                score = sum(_cos(vecs[cand], vecs[o]) for o in members) / len(members)
                if score > best_score:
                    best_m, best_score = cand, score
            new_medoids.append(best_m)
        if new_medoids == medoids:
            break
        medoids = new_medoids
    return clusters

def cluster_by_genre(episodes: List[Dict[str, Any]], k_default: int = 3) -> Dict[str, Any]:
    by = defaultdict(list)
    for e in episodes:
        by[str(e.get("genre_bucket","UNKNOWN"))].append(e)
    out = {}
    for g, items in by.items():
        ids = [str(e.get("episode_id")) for e in items]
        vecs = {str(e.get("episode_id")): _vec(str(e.get("text",""))) for e in items}
        k = max(1, min(5, min(k_default, int(round(math.sqrt(len(ids)))) or 1)))
        out[g] = _kmedoids(ids, vecs, k=k)
    return out
