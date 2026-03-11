from __future__ import annotations

from typing import Any, Dict

from engine.webnovel_adapter import material_from_source


def adapter_manifest() -> Dict[str, Any]:
    return {
        "adapter_name": "web_novel",
        "contract_version": "1.0.0",
        "material_from_source": material_from_source,
        "artifact_from_output": artifact_from_output,
    }


def artifact_from_output(output: Dict[str, Any]) -> Dict[str, Any]:
    cfg = dict(output.get("cfg") or {})
    episode_result = dict(output.get("episode_result") or {})
    project = dict(cfg.get("project") or {})
    episode = int(episode_result.get("episode") or 0)
    artifact_id = f"{project.get('platform', 'unknown').lower()}:{project.get('genre_bucket', 'x').lower()}:ep{episode:03}"
    gate = dict(episode_result.get("quality_gate") or {})
    state = dict(episode_result.get("story_state") or {})
    return {
        "artifact_id": artifact_id,
        "artifact_type": "episode_output",
        "project_type": "web_novel",
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
