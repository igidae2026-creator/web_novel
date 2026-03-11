# Documentation Map

## Purpose

This file is the working index for repository documents.
It exists to reduce overlap, identify canonical references, and stop strategy, governance, and historical notes from drifting into the same role.

## Canonical Reading Order

1. `/home/meta_os/web_novel/AGENTS.md`
2. `/home/meta_os/web_novel/docs/governance/RULE_CARDS.jsonl`
3. `/home/meta_os/web_novel/docs/governance/METAOS_CONSTITUTION.md`
4. `/home/meta_os/web_novel/docs/governance/CHECKLIST_LAYER1_목표조건.md`
5. `/home/meta_os/web_novel/docs/governance/CHECKLIST_LAYER2_모듈책임.md`
6. `/home/meta_os/web_novel/docs/governance/CHECKLIST_LAYER3_REPO매핑.md`
7. `/home/meta_os/web_novel/docs/governance/CHECKLIST_METHOD_패치.md`
8. `/home/meta_os/web_novel/GOAL.md`
9. `/home/meta_os/web_novel/SYSTEM_OBJECTIVE.md`
10. `/home/meta_os/web_novel/METAOS_ANCHOR.md`
11. `/home/meta_os/web_novel/docs/governance/AUTONOMY_TARGET.md`
12. `/home/meta_os/web_novel/docs/governance/WEBNOVEL_ALIGNMENT_STATUS.md`
13. `/home/meta_os/web_novel/docs/governance/WEBNOVEL_SYSTEM_BUNDLES.md`
14. `/home/meta_os/web_novel/docs/document_system_audit.md`
15. `/home/meta_os/web_novel/docs/doc_naming_standard.md`

## Canonical Buckets

### Governance

- constitution and invariants: `/home/meta_os/web_novel/docs/governance/METAOS_CONSTITUTION.md`
- runtime contracts and queue/supervisor rules: `/home/meta_os/web_novel/docs/governance/METAOS_RUNTIME_CONTRACTS.md`
- autonomy target: `/home/meta_os/web_novel/docs/governance/AUTONOMY_TARGET.md`
- whole-system bundle grouping: `/home/meta_os/web_novel/docs/governance/WEBNOVEL_SYSTEM_BUNDLES.md`
- runtime stack order: `/home/meta_os/web_novel/docs/governance/AUTONOMY_RUNTIME_STACK.md`
- repo mapping and checklist coverage: `/home/meta_os/web_novel/docs/governance/CHECKLIST_LAYER3_REPO매핑.md`
- live mismatch ledger: `/home/meta_os/web_novel/docs/governance/WEBNOVEL_ALIGNMENT_STATUS.md`

### Product Quality

- reader-perception contract: `/home/meta_os/web_novel/docs/governance/WEBNOVEL_READER_PERCEPTION_CONTRACT.md`
- web-novel quality axes: `/home/meta_os/web_novel/docs/governance/WEBNOVEL_QUALITY_MAP.md`
- ceiling architecture: `/home/meta_os/web_novel/docs/absolute_ceiling_master_plan.md`
- ceiling gap and audit: `/home/meta_os/web_novel/docs/absolute_ceiling_audit.md`
- content-only ceiling note: `/home/meta_os/web_novel/docs/CONTENT_CEILING.md`

### Operations

- runtime operation: `/home/meta_os/web_novel/OPS_RUNBOOK.md`
- autonomous loop usage: `/home/meta_os/web_novel/docs/AUTONOMOUS_LOOP.md`
- environment bootstrap: `/home/meta_os/web_novel/docs/ENV_SETUP.md`
- operational policy and backup guardrails: `/home/meta_os/web_novel/docs/policy_ops_guardrails.md`
- runtime scaling strategy: `/home/meta_os/web_novel/docs/runtime_scaling_strategy.md`
- legacy root stub register: `/home/meta_os/web_novel/docs/legacy_root_stubs.md`
- patch history: `/home/meta_os/web_novel/PATCH_NOTES.md`

### Working Design Notes

- archived fun-engine plan pointer: `/home/meta_os/web_novel/docs/archive/archive_fun_engine_master_plan.md`
- archived fun-audit pointer: `/home/meta_os/web_novel/docs/archive/archive_fun_ceiling_audit.md`
- live gap ledger: `/home/meta_os/web_novel/docs/absolute_ceiling_gap_map.md`
- agent proposal set: `/home/meta_os/web_novel/docs/agents/`
- naming rule for future cleanup: `/home/meta_os/web_novel/docs/doc_naming_standard.md`
- agent doc index: `/home/meta_os/web_novel/docs/agents/README.md`
- canonical agent subsystem contracts: `/home/meta_os/web_novel/docs/agents/AGENT_SUBSYSTEM_CONTRACTS.md`

## Non-Canonical Or Transitional Areas

- `/home/meta_os/web_novel/docs/agents/` contains overlapping agent proposals and should not be treated as a single canonical contract surface
- `/home/meta_os/web_novel/docs/archive/archive_fun_engine_master_plan.md` is archived historical context, not an active plan surface
- `/home/meta_os/web_novel/POLICY_GUARDRAILS.md`, `/home/meta_os/web_novel/BACKUP_POLICY.md`, and `/home/meta_os/web_novel/SECURITY.md` are too thin to act as standalone policy systems
- `/home/meta_os/web_novel/scaling_notes.md` is now only a legacy pointer to `/home/meta_os/web_novel/docs/runtime_scaling_strategy.md`
- root-level policy/scaling stubs are intentionally retained as legacy shims; see `/home/meta_os/web_novel/docs/legacy_root_stubs.md`

## Immediate Rule

When documents disagree:

1. governance wins over product plans
2. product plans win over historical notes
3. live alignment status wins over stale descriptive docs when the repository implementation changed
