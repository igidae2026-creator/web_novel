from __future__ import annotations

import os
from typing import Any, Dict

from engine.metaos_contracts import POLICY_VERDICTS


def adapter_manifest() -> Dict[str, Any]:
    return {
        "adapter_name": "web_novel",
        "contract_version": "1.0.0",
        "supports": {
            "material_intake": True,
            "artifact_promotion": True,
            "track_generation": True,
            "episode_runtime": True,
        },
        "job_mappings": {
            "ingest_material": "track candidate intake",
            "scope_evaluate": "scope fit evaluation for source material",
            "promote_material": "artifact promotion into active runtime",
            "generate_episode": "episode generation orchestration",
            "generate_episode_track": "track queue driven episode generation",
        },
    }


def material_from_source(source: Dict[str, Any]) -> Dict[str, Any]:
    project = dict(source.get("project") or {})
    platform = str(project.get("platform") or source.get("platform") or "UNKNOWN")
    genre_bucket = str(project.get("genre_bucket") or source.get("genre_bucket") or "X")
    track_id = str((source.get("track") or {}).get("id") or f"{platform}_{genre_bucket}".lower())
    return {
        "material_id": str(source.get("material_id") or f"track:{track_id}"),
        "source": str(source.get("source") or "webnovel_track"),
        "project_type": "web_novel",
        "platform": platform,
        "genre_bucket": genre_bucket,
        "track_id": track_id,
        "quality_score": float(source.get("quality_score", 0.0) or 0.0),
        "scope_fit_score": float(source.get("scope_fit_score", 0.0) or 0.0),
        "risk_score": float(source.get("risk_score", 0.0) or 0.0),
        "novelty_score": float(source.get("novelty_score", 0.0) or 0.0),
        "metadata": {"project": project, "track": dict(source.get("track") or {})},
    }


def artifact_from_episode_result(cfg: Dict[str, Any], episode_result: Dict[str, Any]) -> Dict[str, Any]:
    from engine.pipeline import ensure_project_dirs

    project = dict(cfg.get("project") or {})
    out_dir = ensure_project_dirs(cfg)
    episode = int(episode_result.get("episode") or cfg.get("next_episode") or 0)
    artifact_id = f"{project.get('platform', 'unknown').lower()}:{project.get('genre_bucket', 'x').lower()}:ep{episode:03}"
    gate = dict(episode_result.get("quality_gate") or {})
    state = dict(episode_result.get("story_state") or {})
    return {
        "artifact_id": artifact_id,
        "artifact_type": "episode_output",
        "project_type": "web_novel",
        "out_dir": out_dir,
        "episode": episode,
        "platform": project.get("platform"),
        "genre_bucket": project.get("genre_bucket"),
        "quality_score": float(episode_result.get("predicted_retention", 0.0) or 0.0),
        "relevance_score": float(episode_result.get("quality_score", episode_result.get("payoff_score", 0.0)) or 0.0),
        "stability_score": 1.0 if gate.get("passed", False) else 0.0,
        "risk_score": float(len(list(gate.get("failed_checks", []) or []))) / 10.0,
        "metadata": {
            "failed_checks": list(gate.get("failed_checks", []) or []),
            "world_instability": ((state.get("world") or {}).get("instability")),
        },
    }


def track_job_payload(track_dir: str) -> Dict[str, Any]:
    track_id = os.path.basename(track_dir.rstrip(os.sep))
    return {
        "track_dir": track_dir,
        "track_id": track_id,
        "project_type": "web_novel",
        "job_hint": "generate_episode_track",
    }


def validate_adapter_decision_surface(verdict: str) -> bool:
    return verdict in POLICY_VERDICTS
