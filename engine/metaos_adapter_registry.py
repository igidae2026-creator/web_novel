from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from engine.metaos_contracts import CONTRACT_VERSION, compatibility_report
from engine.webnovel_adapter import adapter_manifest as webnovel_adapter_manifest


AdapterFactory = Callable[[], Dict[str, Any]]

_REGISTRY: Dict[str, AdapterFactory] = {
    "web_novel": webnovel_adapter_manifest,
}


def registered_adapters() -> Dict[str, str]:
    return {project_type: factory().get("adapter_name", project_type) for project_type, factory in _REGISTRY.items()}


def get_adapter_manifest(project_type: str) -> Optional[Dict[str, Any]]:
    factory = _REGISTRY.get(str(project_type or ""))
    return factory() if factory else None


def adapter_resolution(project_type: str) -> Dict[str, Any]:
    manifest = get_adapter_manifest(project_type)
    if not manifest:
        return {
            "status": "missing",
            "project_type": project_type,
            "verdict": "hold",
            "reason": "missing_project_adapter",
        }
    report = compatibility_report(CONTRACT_VERSION, str(manifest.get("contract_version") or ""))
    if report.get("migration_required"):
        return {
            "status": "incompatible",
            "project_type": project_type,
            "verdict": "reject",
            "reason": "adapter_contract_version_mismatch",
            "compatibility": report,
            "adapter_manifest": manifest,
        }
    return {
        "status": "ready",
        "project_type": project_type,
        "verdict": "accept",
        "reason": "adapter_ready",
        "compatibility": report,
        "adapter_manifest": manifest,
    }
