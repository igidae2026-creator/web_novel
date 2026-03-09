from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


PLATFORM_PRESETS: Dict[str, Dict[str, Any]] = {
    "Munpia": {
        "target_title_length_range": [16, 30],
        "target_episode_length_range": [2600, 3600],
        "preferred_release_cadence": "daily",
        "preferred_release_timing_windows": ["06:00-08:00", "18:00-22:00"],
        "free_episode_count_target": 25,
        "first_hook_timing_target": 1,
        "first_reward_timing_target": 3,
        "major_payoff_timing_target": 10,
        "conversion_zone_timing_target": [20, 25],
        "reward_style": "power proof + status reversal",
        "ctr_keywords": ["회귀", "천재", "망나니", "압도", "성장"],
    },
    "KakaoPage": {
        "target_title_length_range": [14, 28],
        "target_episode_length_range": [2200, 3200],
        "preferred_release_cadence": "high-frequency",
        "preferred_release_timing_windows": ["07:00-09:00", "20:00-23:00"],
        "free_episode_count_target": 20,
        "first_hook_timing_target": 1,
        "first_reward_timing_target": 2,
        "major_payoff_timing_target": 10,
        "conversion_zone_timing_target": [20, 24],
        "reward_style": "spiky cliff + accelerated reveal",
        "ctr_keywords": ["각성", "복수", "레벨업", "독점", "최강"],
    },
    "NaverSeries": {
        "target_title_length_range": [14, 28],
        "target_episode_length_range": [2400, 3400],
        "preferred_release_cadence": "steady",
        "preferred_release_timing_windows": ["07:00-09:00", "19:00-21:00"],
        "free_episode_count_target": 24,
        "first_hook_timing_target": 1,
        "first_reward_timing_target": 3,
        "major_payoff_timing_target": 10,
        "conversion_zone_timing_target": [21, 25],
        "reward_style": "clear reward + readable progression",
        "ctr_keywords": ["귀환", "천재", "헌터", "재벌", "운명"],
    },
    "Novelpia": {
        "target_title_length_range": [12, 26],
        "target_episode_length_range": [2200, 3200],
        "preferred_release_cadence": "burst",
        "preferred_release_timing_windows": ["12:00-14:00", "21:00-24:00"],
        "free_episode_count_target": 20,
        "first_hook_timing_target": 1,
        "first_reward_timing_target": 2,
        "major_payoff_timing_target": 9,
        "conversion_zone_timing_target": [20, 23],
        "reward_style": "high-velocity payoff and fantasy validation",
        "ctr_keywords": ["하렘", "집착", "빙의", "아카데미", "최강"],
    },
    "DEFAULT": {
        "target_title_length_range": [14, 28],
        "target_episode_length_range": [2400, 3400],
        "preferred_release_cadence": "steady",
        "preferred_release_timing_windows": ["07:00-09:00", "19:00-22:00"],
        "free_episode_count_target": 22,
        "first_hook_timing_target": 1,
        "first_reward_timing_target": 3,
        "major_payoff_timing_target": 10,
        "conversion_zone_timing_target": [20, 25],
        "reward_style": "clear promise + periodic reward",
        "ctr_keywords": ["회귀", "성장", "비밀"],
    },
}


GENRE_PRESETS: Dict[str, Dict[str, Any]] = {
    "A": {
        "genre_specific_pacing_expectations": "fast escalation, visible competence rewards",
        "genre_specific_prose_density_expectations": "lean and forward-driving",
        "genre_specific_emotional_emphasis": "humiliation reversal and dominance recovery",
        "genre_platform_reward_style": "power reveal, status correction, audience validation",
        "genre_signal_keywords": ["회귀", "성장", "압도", "최강"],
    },
    "B": {
        "genre_specific_pacing_expectations": "mystery pressure with trust shocks",
        "genre_specific_prose_density_expectations": "compact but clue-aware",
        "genre_specific_emotional_emphasis": "betrayal, paranoia, truth shock",
        "genre_platform_reward_style": "truth reveal and agency reclamation",
        "genre_signal_keywords": ["배신", "진실", "복수", "비밀"],
    },
    "F": {
        "genre_specific_pacing_expectations": "relationship progression with frequent emotional turns",
        "genre_specific_prose_density_expectations": "dialogue-heavy and emotionally legible",
        "genre_specific_emotional_emphasis": "longing, jealousy, recognition",
        "genre_platform_reward_style": "social recognition and relationship payoff",
        "genre_signal_keywords": ["계약", "집착", "후회", "로맨스"],
    },
    "DEFAULT": {
        "genre_specific_pacing_expectations": "steady serialized escalation",
        "genre_specific_prose_density_expectations": "commercially readable",
        "genre_specific_emotional_emphasis": "clear emotional movement",
        "genre_platform_reward_style": "promise-payoff clarity",
        "genre_signal_keywords": ["운명", "성장", "반전"],
    },
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(base)
    for key, value in dict(override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def resolve_platform_genre_spec(
    cfg: Dict[str, Any],
    runtime_cfg: Dict[str, Any] | None = None,
    project_overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    project = dict(cfg.get("project", {}) or {})
    novel = dict(cfg.get("novel", {}) or {})
    runtime_setup = dict((runtime_cfg or {}).get("project_setup", {}) or {})
    runtime_overrides = dict(runtime_setup.get("platform_genre_overrides", {}) or {})
    effective_overrides = _deep_merge(runtime_overrides, dict(project.get("platform_genre_overrides", {}) or {}))
    effective_overrides = _deep_merge(effective_overrides, dict(project_overrides or {}))

    platform = str(project.get("platform", runtime_setup.get("platform", "DEFAULT")) or "DEFAULT")
    bucket = str(project.get("genre_bucket", runtime_setup.get("genre_bucket", "DEFAULT")) or "DEFAULT")
    platform_preset = PLATFORM_PRESETS.get(platform, PLATFORM_PRESETS["DEFAULT"])
    genre_preset = GENRE_PRESETS.get(bucket, GENRE_PRESETS["DEFAULT"])
    merged = _deep_merge(platform_preset, genre_preset)
    merged = _deep_merge(merged, effective_overrides)
    merged["platform"] = platform
    merged["genre_bucket"] = bucket
    merged["project_title"] = str(project.get("title", runtime_setup.get("title", "")) or "")
    merged["target_total_episodes"] = int(novel.get("total_episodes", runtime_setup.get("target_total_episodes", 300)) or 300)
    merged["project_level_overrides"] = effective_overrides
    return merged
