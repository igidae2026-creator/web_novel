# Ops Guardrails Policy

## Purpose

This document consolidates operational guardrails that were previously split across thin root-level policy stubs.
It is the working policy surface for safe operation, backup discipline, and basic content handling constraints.

## Data And Platform Policy

- do not scrape platforms in violation of terms of service
- use manually exported, licensed, or officially provided data where possible
- treat external ingestion as policy-scoped material, not unrestricted harvesting

## Content Policy

- do not store or output copyrighted full texts unless the repo explicitly has rights to do so
- prefer metadata, excerpts within policy, structured attributes, or derived signals over raw copied content
- when external source material is admitted, keep its lineage and policy decision auditable

## Runtime Safety Policy

- prefer fail-closed behavior when quality, scope, or policy confidence is weak
- prefer append-only logs and replayable state over convenience shortcuts
- do not let operational shortcuts outrank MetaOS truth, lineage, or replayability invariants

## Backup And Recovery Policy

- keep at least 7 daily backups of `outputs/` and `data/`
- keep at least 4 weekly backups
- backup policy is part of runtime safety, not a separate convenience feature
- recovery paths should preserve auditable state and avoid silent rollback of unrelated work

## Operator Rule

- humans may approve, audit, and patch
- humans should not be required for routine production rescue
- if a workflow requires repeated human rescue, the system has not met the autonomy target

## Transitional Note

The root-level files `/home/meta_os/web_novel/POLICY_GUARDRAILS.md`, `/home/meta_os/web_novel/BACKUP_POLICY.md`, and `/home/meta_os/web_novel/SECURITY.md` should be treated as legacy stubs until references are consolidated.
