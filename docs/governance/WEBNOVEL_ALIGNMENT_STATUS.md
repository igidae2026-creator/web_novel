# Web Novel Alignment Status

## Purpose

This document records how the imported governance stack currently aligns, or fails to align, with the actual `web_novel` repository.

It exists because the imported Layer 3 checklist is generic MetaOS repo mapping, while this repository currently exposes a different runtime structure.

## Current Canonical Runtime Mapping

- user-facing runtime entrypoint: `app.py`
- generation core: `engine/`
- market support: `market_layer/`
- portfolio support: `portfolio_layer/`
- business dashboards: `metaos_business/`
- tests: `tests/`
- configuration: `config.yaml`, `runtime_config*.json`

## Canonical Goal Mapping

- user task goal: `GOAL.md`
- system objective: `SYSTEM_OBJECTIVE.md`
- governance anchor: `METAOS_ANCHOR.md`

## Confirmed Mismatches Against Imported Layer 3

- imported Layer 3 references `tools/loop.py`, `tools/meta_loop.py`, and `tools/system_evolver.py`
- those files do not exist in this repository
- imported Layer 3 assumes a more generic MetaOS runtime topology than the current web-novel app exposes
- imported Layer 3 therefore cannot yet be treated as fully implemented repo truth for this repository

## Immediate Interpretation Rule

Until Layer 3 is rewritten through the patch method for this repository, use the imported Layer 3 as a governance target and use this document as the live mapping bridge.

## Priority Gaps

- no repo-specific canonical Layer 3 mapping yet
- no explicit semantic quality gate document tied to top-tier web-novel reader perception
- no single documented quality scoring contract for hook, payoff, cliffhanger, pacing, and coherence
- no explicit coverage status proving each governance quality axis is enforced by code

## Next Structural Work

- rewrite Layer 3 through the patch method for this repository
- map each quality axis to concrete `engine/` modules and tests
- define measurable pass criteria for upper-tier web-novel quality
