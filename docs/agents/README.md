# Agent Docs Index

## Purpose

This directory currently contains two overlapping families of agent documents.
This file defines how to read them until they are normalized.

Canonical starting point:

- `/home/meta_os/web_novel/docs/agents/AGENT_SUBSYSTEM_CONTRACTS.md`

## Current Families

### Diagnostic Family

Files named like:

- `agent_character_audit.md`
- `agent_conflict_audit.md`
- `agent_event_audit.md`

These documents are diagnosis-oriented.
They describe bottlenecks, missing architecture, integration points, and regression risks.

### Contract Family

Files named like:

- `agent_character_contract.md`
- `agent_conflict_contract.md`
- `agent_event_contract.md`

These documents are responsibility-oriented.
They describe required state, outputs, and failure modes.

## Temporary Reading Rule

When both families exist for the same subsystem:

1. read the `agent_*` file for diagnosis
2. read the `*_agent` file for operational contract

Do not treat both as independent long-term canonical surfaces.

Current pairings:

- `agent_character_audit.md` + `agent_character_contract.md`
- `agent_conflict_audit.md` + `agent_conflict_contract.md`
- `agent_event_audit.md` + `agent_event_contract.md`
- `agent_cliffhanger_tension_audit.md` + `agent_cliffhanger_contract.md` + `agent_tension_contract.md`

Standalone audit-heavy docs:

- `agent_state_architecture_audit.md`
- `agent_adaptation_exploration_audit.md`
- `agent_information_emotion_audit.md`
- `agent_regression_guard_audit.md`
- `agent_tests_docs_audit.md`
- `agent_webnovel_fit_audit.md`

Standalone contract-heavy doc:

- `agent_retention_contract.md`

## Normalization Target

The directory should eventually move toward one naming family:

- `agent_<name>_audit.md`
- `agent_<name>_contract.md`

until then, this directory is transitional rather than canonical.
