from __future__ import annotations
import os, json
from typing import Optional, Dict, List

def load_profiles(profiles_dir: str) -> List[Dict]:
    idx = os.path.join(profiles_dir, "profiles_index.json")
    if os.path.exists(idx):
        with open(idx, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def select_profile(profiles: List[Dict], platform: str, bucket: str) -> Optional[Dict]:
    def find(p, b):
        for x in profiles:
            if x.get("platform") == p and x.get("genre_bucket") == b:
                return x
        return None
    return find(platform, bucket) or find(platform, "GLOBAL") or find("GLOBAL", bucket) or find("GLOBAL", "GLOBAL")

def profile_constraints_text(profile: Optional[Dict]) -> str:
    if not profile:
        return ""
    return (
        f"- (자료기반) 대사 비율 목표: {profile.get('target_dialogue_ratio',0):.2f}\n"
        f"- (자료기반) 문장 길이 평균 목표: {profile.get('target_sentence_len_mean',0):.1f}±{profile.get('target_sentence_len_std',0):.1f}\n"
        f"- (자료기반) 클리프 강도 목표: {profile.get('target_cliff_density',0):.2f}\n"
        f"- (자료기반) 감정 프록시 목표: {profile.get('target_emotion_proxy',0):.2f}\n"
    )
