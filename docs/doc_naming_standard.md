# Document Naming Standard

## Purpose

This file defines a practical naming rule for repository documents so humans and models can identify canonical files faster and with less ambiguity.

## Current Judgment

- canonical governance filenames are stable enough to keep for now
- non-canonical and proposal filenames are not efficient enough yet
- the main problems are mixed case, mixed language, duplicate naming families, and weak role signaling

## Naming Rules

### Rule 1

Do not rename files listed as canonical authority in `/home/meta_os/web_novel/AGENTS.md` unless the governance stack is patched together with all references.

### Rule 2

For non-canonical docs, prefer ASCII lowercase snake_case.

Good:

- `reader_perception_contract.md`
- `document_system_audit.md`
- `ops_policy_and_backup.md`

Avoid:

- `SomeDoc.md`
- `documentSystem.md`
- `mixed-Style_Name.md`

### Rule 3

Filename should signal role, not just topic.

Preferred role prefixes:

- `index_` for navigation
- `plan_` for active design plans
- `audit_` for audit or gap analysis
- `contract_` for measurable rules
- `policy_` for enforced behavior and guardrails
- `runbook_` for operational procedure
- `archive_` for historical or deprecated material

### Rule 4

One subsystem should not have two parallel filename families.

Bad:

- `agentCharacter.md`
- `character-agent.md`

Preferred:

- `agent_character_contract.md`
- `agent_character_audit.md`

### Rule 5

If a document is temporary, the filename should show that it is temporary or archival.

Examples:

- `archive_fun_engine_plan_2026q1.md`
- `temporary_gap_log.md`

## Canonical Filename Freeze

Treat these as frozen unless the governance stack is patched:

- `/home/meta_os/web_novel/GOAL.md`
- `/home/meta_os/web_novel/SYSTEM_OBJECTIVE.md`
- `/home/meta_os/web_novel/METAOS_ANCHOR.md`
- `/home/meta_os/web_novel/docs/governance/`

## Recommended Renames

These are recommendation targets, not yet executed renames.

| Current | Recommended |
| --- | --- |
| `/home/meta_os/web_novel/docs/document_system_audit.md` | keep |
| `/home/meta_os/web_novel/docs/archive/archive_fun_engine_master_plan.md` | keep as archived historical pointer |
| `/home/meta_os/web_novel/docs/archive/archive_fun_ceiling_audit.md` | keep as archived historical pointer |
| `/home/meta_os/web_novel/POLICY_GUARDRAILS.md` | `/home/meta_os/web_novel/docs/policy_ops_guardrails.md` after merge |
| `/home/meta_os/web_novel/BACKUP_POLICY.md` | `/home/meta_os/web_novel/docs/policy_ops_guardrails.md` after merge |
| `/home/meta_os/web_novel/SECURITY.md` | `/home/meta_os/web_novel/docs/policy_ops_guardrails.md` after merge |
| `/home/meta_os/web_novel/scaling_notes.md` | `/home/meta_os/web_novel/docs/archive_scaling_notes.md` or remove |
| `/home/meta_os/web_novel/docs/agents/agent_character_contract.md` | keep |
| `/home/meta_os/web_novel/docs/agents/agent_character_audit.md` | keep |

## Decision Rule

Before renaming a file:

1. verify whether it is canonical
2. update all references
3. update any path lists in governance docs
4. only then rename the file
