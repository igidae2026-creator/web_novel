from __future__ import annotations

import importlib
import os
import py_compile
import sys
from typing import Dict, List


REQUIRED_FILES = [
    "app.py",
    "GOAL.md",
    "SYSTEM_OBJECTIVE.md",
    "METAOS_ANCHOR.md",
    "engine/pipeline.py",
    "engine/quality_gate.py",
    "engine/runtime_config.py",
    "engine/state.py",
    "engine/predictive_retention.py",
    "engine/scene_causality.py",
    "engine/regression_guard.py",
    "engine/metaos_contracts.py",
    "engine/webnovel_adapter.py",
    "engine/metaos_adapter_registry.py",
    "engine/metaos_conformance.py",
    "engine/metaos_recovery.py",
    "engine/job_queue.py",
    "engine/runtime_supervisor.py",
    "docs/governance/CHECKLIST_LAYER3_REPO매핑.md",
    "docs/governance/COVERAGE_AUDIT.csv",
    "docs/governance/METAOS_RUNTIME_CONTRACTS.md",
    "docs/governance/WEBNOVEL_METAOS_ADAPTER.md",
    "docs/governance/METAOS_CONFORMANCE.md",
    "docs/governance/METAOS_CONFORMANCE_MATRIX.csv",
    "docs/governance/METAOS_VERSIONING_AND_RECOVERY.md",
    "docs/governance/CONTRACTS_GOVERNANCE.md",
]

CORE_IMPORTS = [
    "engine.quality_gate",
    "engine.predictive_retention",
    "engine.scene_causality",
    "engine.regression_guard",
    "engine.metaos_contracts",
    "engine.webnovel_adapter",
    "engine.metaos_adapter_registry",
    "engine.metaos_conformance",
    "engine.metaos_recovery",
    "analytics.content_ceiling",
]

OPTIONAL_IMPORTS = [
    "engine.pipeline",
    "engine.market_policy_engine",
    "engine.portfolio_orchestrator",
]


def check_files(root: str) -> Dict[str, object]:
    missing = [path for path in REQUIRED_FILES if not os.path.exists(os.path.join(root, path))]
    return {"ok": len(missing) == 0, "missing": missing}


def compile_selected(root: str) -> Dict[str, object]:
    targets = [
        "engine/quality_gate.py",
        "engine/pipeline.py",
        "engine/predictive_retention.py",
        "engine/scene_causality.py",
        "engine/regression_guard.py",
        "tests/test_quality_gate.py",
        "tests/test_absolute_ceiling_regression.py",
    ]
    errors: List[Dict[str, str]] = []
    for rel_path in targets:
        abs_path = os.path.join(root, rel_path)
        if not os.path.exists(abs_path):
            errors.append({"file": rel_path, "error": "missing"})
            continue
        try:
            with open(abs_path, "r", encoding="utf-8") as handle:
                source = handle.read()
            compile(source, abs_path, "exec")
        except Exception as exc:
            errors.append({"file": rel_path, "error": repr(exc)})
    return {"ok": len(errors) == 0, "errors": errors}


def import_checks(root: str) -> Dict[str, object]:
    sys.path.insert(0, root)
    core_errors: List[str] = []
    optional_errors: List[str] = []
    try:
        for mod in CORE_IMPORTS:
            try:
                importlib.import_module(mod)
            except Exception as exc:
                core_errors.append(f"{mod}: {exc!r}")
        for mod in OPTIONAL_IMPORTS:
            try:
                importlib.import_module(mod)
            except Exception as exc:
                optional_errors.append(f"{mod}: {exc!r}")
    finally:
        if sys.path and sys.path[0] == root:
            sys.path.pop(0)
    return {
        "ok": len(core_errors) == 0,
        "core_errors": core_errors,
        "optional_errors": optional_errors,
    }


def governance_checks(root: str) -> Dict[str, object]:
    audit_path = os.path.join(root, "docs", "governance", "COVERAGE_AUDIT.csv")
    alignment_path = os.path.join(root, "docs", "governance", "WEBNOVEL_ALIGNMENT_STATUS.md")
    contracts_path = os.path.join(root, "docs", "governance", "METAOS_RUNTIME_CONTRACTS.md")
    issues: List[str] = []
    if os.path.exists(audit_path):
        with open(audit_path, "r", encoding="utf-8") as handle:
            body = handle.read()
        if "end_to_end_top_tier_reader_perception" not in body:
            issues.append("coverage audit is missing top-tier perception coverage row")
    else:
        issues.append("coverage audit file missing")
    if not os.path.exists(alignment_path):
        issues.append("webnovel alignment status file missing")
    if not os.path.exists(contracts_path):
        issues.append("metaos runtime contracts file missing")
    return {"ok": len(issues) == 0, "issues": issues}


def run_all(root: str) -> Dict[str, object]:
    out = {"files": check_files(root)}
    out["compile"] = compile_selected(root)
    out["imports"] = import_checks(root)
    out["governance"] = governance_checks(root)
    out["ok"] = all(
        [
            out["files"]["ok"],
            out["compile"]["ok"],
            out["imports"]["ok"],
            out["governance"]["ok"],
        ]
    )
    return out
