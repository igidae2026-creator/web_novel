# METAOS_VERSIONING_AND_RECOVERY

## Purpose

This document fixes three runtime rules:

- missing adapter handling
- contract version mismatch handling
- recovery verdicts for replay instability

## Missing Adapter Rule

If a project type has no registered adapter:

- default verdict: `hold`
- reason: `missing_project_adapter`

The runtime should not silently guess project-specific normalization.

## Version Mismatch Rule

If an adapter contract version does not match the locked MetaOS runtime contract version:

- default verdict: `reject`
- reason: `adapter_contract_version_mismatch`

Any unstated version jump is incompatible until proven otherwise.

## Recovery Rule

The runtime should produce explicit recovery verdicts for at least:

- partial write
- duplicate event
- stale snapshot
- replay mismatch / replay resume inconsistency

Default interpretation:

- if any of the above is detected: `recover`
- if none is detected and replay is consistent: `resume`
