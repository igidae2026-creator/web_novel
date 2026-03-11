# Document System Audit

## Purpose

This file records the current documentation shape, the main duplication patterns, and the recommended reorganization path.
It is intentionally operational: keep, merge, split, rewrite, archive, or delete.

## Executive Judgment

- the repository has enough governance material
- the repository has too many overlapping strategy and proposal documents
- the largest debt is not missing text, but weak document boundaries
- the most urgent fix is to reduce duplicate planning surfaces and make one canonical path for reader-quality rules

## Current Document Buckets

### Stable Canonical

- `/home/meta_os/web_novel/AGENTS.md`
- `/home/meta_os/web_novel/GOAL.md`
- `/home/meta_os/web_novel/SYSTEM_OBJECTIVE.md`
- `/home/meta_os/web_novel/METAOS_ANCHOR.md`
- `/home/meta_os/web_novel/docs/governance/`
- `/home/meta_os/web_novel/docs/governance/WEBNOVEL_SYSTEM_BUNDLES.md`

### Strong But Overlapping

- `/home/meta_os/web_novel/docs/absolute_ceiling_master_plan.md`
- `/home/meta_os/web_novel/docs/absolute_ceiling_audit.md`
- `/home/meta_os/web_novel/docs/absolute_ceiling_gap_map.md`
- `/home/meta_os/web_novel/docs/governance/WEBNOVEL_QUALITY_MAP.md`

### Archived Legacy Pointers

- `/home/meta_os/web_novel/docs/archive/archive_fun_engine_master_plan.md`
- `/home/meta_os/web_novel/docs/archive/archive_fun_ceiling_audit.md`

### Proposal Fragments

- `/home/meta_os/web_novel/docs/agents/agent_*_audit.md`
- `/home/meta_os/web_novel/docs/agents/agent_*_contract.md`

### Thin Stubs

- `/home/meta_os/web_novel/POLICY_GUARDRAILS.md`
- `/home/meta_os/web_novel/BACKUP_POLICY.md`
- `/home/meta_os/web_novel/SECURITY.md`
- `/home/meta_os/web_novel/scaling_notes.md`

These are now treated as legacy root shims, not active policy authority.

## Main Problems

### 1. Duplicate Planning Surface

`absolute_ceiling_*`, `fun_*`, and `WEBNOVEL_QUALITY_MAP.md` all discuss quality architecture, but with different depth and different contract strength.
This increases drift risk.

### 2. Duplicate Agent Proposal Families

The underlying subsystem content is still split across many files, but the naming family is now normalized.
Diagnosis and contract roles are now easier to distinguish.

### 3. Policy Fragmentation

Operationally important policy items are spread across tiny root-level docs.
These are too small to justify separate authority.

### 4. Weak Canonical Boundary For Reader-Perceived Quality

The repo talks about upper-tier reader perception in multiple places, but there is no single document that says:

- what counts as strong early hook
- what counts as addictive episode ending
- what counts as long-arc payoff integrity
- what counts as protagonist fantasy persistence
- what counts as acceptable serialization fatigue

### 5. Filename Inefficiency

Many filenames are still suboptimal for machine retrieval and maintenance.

- canonical names are mixed with non-canonical names in the same style
- uppercase and lowercase naming conventions are mixed
- duplicate families such as `agent_*` and `*_agent` force extra disambiguation
- some names communicate topic but not role

## Recommended Actions

### Keep As Canonical

- keep `/home/meta_os/web_novel/docs/governance/METAOS_CONSTITUTION.md`
- keep `/home/meta_os/web_novel/docs/governance/AUTONOMY_TARGET.md`
- keep `/home/meta_os/web_novel/docs/governance/METAOS_RUNTIME_CONTRACTS.md`
- keep `/home/meta_os/web_novel/docs/governance/CHECKLIST_LAYER3_REPO매핑.md`
- keep `/home/meta_os/web_novel/docs/governance/WEBNOVEL_ALIGNMENT_STATUS.md`

### Merge

- merge `/home/meta_os/web_novel/docs/archive/archive_fun_engine_master_plan.md` into `/home/meta_os/web_novel/docs/absolute_ceiling_master_plan.md`
- merge `/home/meta_os/web_novel/docs/archive/archive_fun_ceiling_audit.md` into `/home/meta_os/web_novel/docs/absolute_ceiling_audit.md`
- merge `/home/meta_os/web_novel/POLICY_GUARDRAILS.md`, `/home/meta_os/web_novel/BACKUP_POLICY.md`, and `/home/meta_os/web_novel/SECURITY.md` into one operational governance surface

### Split

- split reader-quality contract out of `/home/meta_os/web_novel/docs/governance/WEBNOVEL_QUALITY_MAP.md` into a stricter measurable contract doc
- split historical patch notes from active operational docs if `PATCH_NOTES.md` keeps growing

### Rewrite

- rewrite `/home/meta_os/web_novel/docs/governance/WEBNOVEL_QUALITY_MAP.md` so it becomes a map, not a half-contract
- rewrite `/home/meta_os/web_novel/docs/absolute_ceiling_gap_map.md` into a short live gap ledger instead of a one-time analysis artifact
- rewrite `/home/meta_os/web_novel/scaling_notes.md` into either a real scaling strategy or archive it
- rewrite non-canonical filenames toward the standard in `/home/meta_os/web_novel/docs/doc_naming_standard.md`

### Archive Or Delete After Merge

- archive one side of each duplicate `docs/agents/` proposal pair after extracting the canonical contract
- delete ultra-thin stubs only after their content is absorbed elsewhere

## Recommended Target Shape

### Governance Core

- constitution
- autonomy target
- runtime contracts
- system bundles
- contracts governance
- repo mapping
- alignment status

### Product Quality Core

- reader perception contract
- webnovel quality map
- absolute ceiling master plan
- absolute ceiling audit
- gap ledger

### Operations Core

- ops runbook
- autonomous loop
- env setup
- operational safety and backup policy
- runtime scaling strategy

### Historical Or Proposal Archive

- patch notes
- agent proposals
- experimental plans that are no longer canonical

## Immediate Safe Changes

- add a docs index
- add this audit file
- add a canonical reader-perception contract
- add an agent-doc index that explains duplicate families before rename/archive
- stop treating duplicate plan docs as equal authority
- treat `docs/governance/WEBNOVEL_ALIGNMENT_STATUS.md` as the live mismatch ledger until the merge work is finished

Completed so far:

- docs index added
- reader-perception contract added
- ops policy stubs consolidated
- agent-doc index added
- canonical agent subsystem contracts added as the primary reading surface ahead of rename/archive
- fun plan and fun audit content absorbed into canonical absolute-ceiling docs, with legacy pointer docs left in place
- fun plan and fun audit pointer docs moved into `docs/archive/`
- whole-system bundle grouping added so webnovel work is not framed only as narrative generation
- live gap ledger and runtime scaling strategy added, with `scaling_notes.md` reduced to a legacy pointer
- legacy root stub register added so root compatibility files are not mistaken for active authority

## Deferred High-Value Changes

- create a canonical upper-tier reader perception contract document
- merge duplicate quality plans into a single master plan
- normalize agent proposal docs into one family and archive the other
- continue reducing subsystem duplication now that agent naming is normalized
- collapse thin root policy docs into one audited operational policy file
- normalize non-canonical filenames after references are consolidated

## Proposed Disposition Table

| Document Group | Action | Reason |
| --- | --- | --- |
| `docs/governance/` canonical stack | keep | authoritative governance surface |
| `docs/absolute_ceiling_master_plan.md` + `docs/archive/archive_fun_engine_master_plan.md` | merged, archived pointer kept | same architectural layer |
| `docs/absolute_ceiling_audit.md` + `docs/archive/archive_fun_ceiling_audit.md` | merged, archived pointer kept | same audit purpose |
| `docs/agents/agent_*_audit.md` + `docs/agents/agent_*_contract.md` | naming normalized, further consolidation pending | same subsystem described twice |
| `POLICY_GUARDRAILS.md` + `BACKUP_POLICY.md` + `SECURITY.md` | merge | too small to stand alone |
| `scaling_notes.md` | rewrite or archive | currently not useful as canonical doc |

## Decision Rule

Until the merge work is done:

- do not add new strategy docs beside existing ones unless they define a genuinely new authority surface
- prefer editing canonical docs over adding parallel notes
- if a new doc is temporary, label it as temporary and define its exit condition
