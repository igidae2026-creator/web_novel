from __future__ import annotations
import os, json, re
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
from .ingest import collect_texts
from .features import compute_features, to_dict

_BUCKET_RE = re.compile(r"\b([A-I])\b", re.IGNORECASE)
_PLATFORM_KEYS = ["Joara","Munpia","NaverSeries","KakaoPage","Ridibooks","Novelpia"]

def _guess_bucket(path: str) -> Optional[str]:
    m = _BUCKET_RE.search(os.path.basename(path))
    return m.group(1).upper() if m else None

def _guess_platform(path: str) -> Optional[str]:
    low = path.lower()
    for p in _PLATFORM_KEYS:
        if p.lower() in low:
            return p
    return None

@dataclass
class Profile:
    platform: str
    genre_bucket: str
    n_texts: int
    target_dialogue_ratio: float
    target_sentence_len_mean: float
    target_sentence_len_std: float
    target_cliff_density: float
    target_emotion_proxy: float

def build_profiles(inputs_dir: str, out_dir: str, scratch_dir: str, default_platform: str = "GLOBAL") -> List[Dict]:
    texts = collect_texts(inputs_dir, scratch_dir)
    groups: Dict[Tuple[str,str], List[Dict]] = {}

    for path, text in texts:
        platform = _guess_platform(path) or default_platform
        bucket = _guess_bucket(path) or "GLOBAL"
        feats = to_dict(compute_features(text))
        groups.setdefault((platform, bucket), []).append(feats)

    profiles: List[Dict] = []
    os.makedirs(out_dir, exist_ok=True)
    for (platform, bucket), feats_list in groups.items():
        n = len(feats_list)
        def avg(k: str) -> float:
            return sum(float(x.get(k,0.0)) for x in feats_list)/max(1,n)
        prof = Profile(
            platform=platform, genre_bucket=bucket, n_texts=n,
            target_dialogue_ratio=avg("dialogue_ratio"),
            target_sentence_len_mean=avg("sentence_len_mean"),
            target_sentence_len_std=max(4.0, avg("sentence_len_std")),
            target_cliff_density=avg("cliff_density"),
            target_emotion_proxy=avg("emotion_proxy"),
        )
        d = asdict(prof)
        profiles.append(d)
        with open(os.path.join(out_dir, f"profile_{platform}_{bucket}.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "profiles_index.json"), "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)
    return profiles
